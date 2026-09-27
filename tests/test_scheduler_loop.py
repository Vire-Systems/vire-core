"""
Integration tests for the Scheduler component (BuildScheduler/Scheduler/*).

Covers end-to-end integration workflows for scheduler_iteration and core scheduler operations:
  - Dequeuing builds from SQLite DB and dispatching jobs via scheduler_iteration
  - Worker lifecycle initiation and job status transitions (queued -> running / crashed)
  - Realistic CLI command construction and JSON encoding via subprocess.Popen mock
  - Capacity & slot limit management (partial dispatch & zero capacity)
  - Error handling when get_worker_count returns None (ValueError)
  - Missing build metadata error handling (NoJobStateError -> crashed state transition)
  - Duplicate job registration handling and updating non-existent job state error handling
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from BuildScheduler.Scheduler.db.sqlite_orm.crud import create, update
from BuildScheduler.Scheduler.db.sqlite_orm.db import async_session
from BuildScheduler.Scheduler.db.sqlite_orm.models import BuildData, BuildState, init_db
from BuildScheduler.Scheduler.scheduler_loop import scheduler_iteration
from BuildScheduler.Scheduler.utils.queues import db_build_queue
from shared.errors import scheduler_errors
from shared.events.events import LogEvent
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.objects.validation_models import ParsedTOMLObject


@pytest.fixture(autouse=True)
async def clean_db_and_queue():
    """Ensure database tables are initialized and empty, and queue is clear before each test."""
    await init_db()
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(BuildState))
            await session.execute(delete(BuildData))

    while not db_build_queue.empty():
        try:
            db_build_queue.get_nowait()
        except asyncio.QueueEmpty:
            break
    yield
    while not db_build_queue.empty():
        try:
            db_build_queue.get_nowait()
        except asyncio.QueueEmpty:
            break


class TestSchedulerIntegration:

    @pytest.mark.asyncio
    async def test_scheduler_iteration_full_dispatch_flow(self, sample_build_request, sample_parsed_toml):
        """
        Integration test: Verifies that scheduler_iteration reads a queued build from SQLite DB,
        populates the queue, dispatches the job, transitions state to 'running', emits events,
        and constructs the worker subprocess execution command via subprocess.Popen.
        """
        brm = BuildRequestModel(**sample_build_request)
        await create.register_build_data(brm, sample_parsed_toml)
        await create.register_build_state(brm.job_uuid, brm.user_uuid, "queued")

        dispatched_events = []

        async def mock_dispatch_event(event, **kwargs):
            dispatched_events.append(event)

        with patch("BuildScheduler.Scheduler.scheduler_loop.get_worker_count", AsyncMock(return_value=0)), \
             patch("subprocess.Popen", MagicMock()) as mock_popen, \
             patch("BuildScheduler.Scheduler.core.make_worker.dispatch_event", side_effect=mock_dispatch_event), \
             patch("BuildScheduler.Scheduler.scheduler_loop.dispatch_event", side_effect=mock_dispatch_event):

            await scheduler_iteration()

        # 1. Verify job state updated to 'running' in DB
        async with async_session() as session:
            res = await session.execute(select(BuildState).where(BuildState.job_uuid == brm.job_uuid))
            state_obj = res.scalar_one_or_none()
            assert state_obj is not None
            assert state_obj.status == "running"

        # 2. Verify subprocess.Popen was invoked with valid command and serialized JSON struct
        mock_popen.assert_called_once()
        cmd_args = mock_popen.call_args[0][0]
        assert cmd_args[0] == "nohup"
        assert "--json_struct" in cmd_args

        json_idx = cmd_args.index("--json_struct") + 1
        json_payload = json.loads(cmd_args[json_idx])
        assert json_payload["job_uuid"] == brm.job_uuid
        assert json_payload["user_uuid"] == brm.user_uuid
        assert json_payload["remote"] == brm.remote_link
        assert json_payload["repo_name"] == brm.remote_reponame
        assert json_payload["framework"] == sample_parsed_toml.framework
        assert json_payload["pm"] == sample_parsed_toml.package_manager
        assert json_payload["output_dir"] == sample_parsed_toml.output_dir
        assert json_payload["install_req"] == sample_parsed_toml.install_req
        assert json_payload["commit_id"] == brm.commit_id

        # 3. Verify LogEvent for worker start was dispatched
        start_events = [e for e in dispatched_events if isinstance(e, LogEvent) and e.diag_code == "VC-I-WORKER_STARTED"]
        assert len(start_events) == 1
        assert start_events[0].job_uuid == brm.job_uuid

    @pytest.mark.asyncio
    async def test_scheduler_iteration_respects_capacity_limits(self, user_uuid):
        """
        Integration test: Verify scheduler_iteration loads and dispatches only up to available capacity slots.
        """
        job_uuids = [f"job-capacity-{i}" for i in range(4)]
        sample_toml = ParsedTOMLObject(
            framework="vite", package_manager="npm", framework_version="5.0", output_dir="dist", install_req=True
        )

        for jid in job_uuids:
            brm = BuildRequestModel(
                job_uuid=jid,
                user_uuid=user_uuid,
                remote_link="https://github.com/test/repo.git",
                commit_id="abc1234",
                provider="github",
                remote_user="test",
                remote_reponame="repo",
                branch="main",
            )
            await create.register_build_data(brm, sample_toml)
            await create.register_build_state(jid, user_uuid, "queued")

        # Active worker count is 3 out of MAX_BUILDS_NUMBER (5), so available slots = 2
        with patch("BuildScheduler.Scheduler.scheduler_loop.get_worker_count", AsyncMock(return_value=3)), \
             patch("subprocess.Popen", MagicMock()) as mock_popen, \
             patch("BuildScheduler.Scheduler.core.make_worker.dispatch_event", AsyncMock()):

            await scheduler_iteration()

        # Check DB states
        async with async_session() as session:
            res = await session.execute(select(BuildState))
            states = {s.job_uuid: s.status for s in res.scalars().all() if s.job_uuid in job_uuids}

        running_count = sum(1 for status in states.values() if status == "running")
        queued_count = sum(1 for status in states.values() if status == "queued")

        assert running_count == 2
        assert queued_count == 2
        assert mock_popen.call_count == 2

    @pytest.mark.asyncio
    async def test_scheduler_iteration_no_available_slots(self, user_uuid):
        """
        Integration test: When worker_count >= MAX_BUILDS_NUMBER, no jobs should be dequeued or dispatched.
        """
        jid = "job-no-slots"
        brm = BuildRequestModel(
            job_uuid=jid,
            user_uuid=user_uuid,
            remote_link="https://github.com/test/repo.git",
            commit_id="abc1234",
            provider="github",
            remote_user="test",
            remote_reponame="repo",
            branch="main",
        )
        sample_toml = ParsedTOMLObject(
            framework="vite", package_manager="npm", framework_version="5.0", output_dir="dist", install_req=True
        )
        await create.register_build_data(brm, sample_toml)
        await create.register_build_state(jid, user_uuid, "queued")

        # 5 workers active out of MAX=5
        with patch("BuildScheduler.Scheduler.scheduler_loop.get_worker_count", AsyncMock(return_value=5)), \
             patch("subprocess.Popen", MagicMock()) as mock_popen, \
             patch("BuildScheduler.Scheduler.core.make_worker.dispatch_event", AsyncMock()):

            await scheduler_iteration()

        async with async_session() as session:
            res = await session.execute(select(BuildState).where(BuildState.job_uuid == jid))
            state_obj = res.scalar_one_or_none()
            assert state_obj.status == "queued"

        mock_popen.assert_not_called()

    @pytest.mark.asyncio
    async def test_scheduler_iteration_worker_count_none_raises_value_error(self):
        """
        Integration test: If get_worker_count returns None, scheduler_iteration raises ValueError.
        """
        with patch("BuildScheduler.Scheduler.scheduler_loop.get_worker_count", AsyncMock(return_value=None)):
            with pytest.raises(ValueError, match="worker count is None"):
                await scheduler_iteration()

    @pytest.mark.asyncio
    async def test_scheduler_iteration_handles_missing_build_data_gracefully(self, user_uuid):
        """
        Integration test: If BuildState is queued but matching BuildData is missing,
        _create_helper encounters NoJobStateError, state transitions to 'crashed',
        and an error LogEvent is dispatched.
        """
        jid = "job-missing-data"
        await create.register_build_state(jid, user_uuid, "queued")

        dispatched_events = []

        async def mock_dispatch_event(event, **kwargs):
            dispatched_events.append(event)

        with patch("BuildScheduler.Scheduler.scheduler_loop.get_worker_count", AsyncMock(return_value=0)), \
             patch("BuildScheduler.Scheduler.core.make_worker.dispatch_event", side_effect=mock_dispatch_event):

            await scheduler_iteration()

        # Check state transitioned to crashed
        async with async_session() as session:
            res = await session.execute(select(BuildState).where(BuildState.job_uuid == jid))
            state_obj = res.scalar_one_or_none()
            assert state_obj is not None
            assert state_obj.status == "crashed"

        # Check error log event was dispatched
        err_events = [e for e in dispatched_events if isinstance(e, LogEvent) and e.job_uuid == jid]
        assert len(err_events) > 0
        assert err_events[0].exception_name == "NoJobStateError"

    @pytest.mark.asyncio
    async def test_register_duplicate_job_data_raises_integrity_error(self, sample_build_request, sample_parsed_toml):
        """
        Integration test: Registering duplicate build data with an existing job_uuid raises IntegrityError.
        """
        brm = BuildRequestModel(**sample_build_request)
        await create.register_build_data(brm, sample_parsed_toml)

        with pytest.raises(IntegrityError):
            await create.register_build_data(brm, sample_parsed_toml)

    @pytest.mark.asyncio
    async def test_update_nonexistent_job_status_raises_no_job_state_error(self):
        """
        Integration test: Attempting to update status for a non-existent job_uuid raises NoJobStateError.
        """
        with pytest.raises(scheduler_errors.NoJobStateError):
            await update.update_job_status(job_uuid="non-existent-uuid", status_msg="running")
