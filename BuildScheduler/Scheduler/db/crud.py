from sqlalchemy.future import select
from sqlalchemy import TIMESTAMP
from typing import Literal


from BuildScheduler.Scheduler.db.db import async_session
from BuildScheduler.Scheduler.db.models import BuildData, BuildState
from BuildScheduler.Scheduler.utils.queues_locks import db_build_queue
from BuildScheduler.Scheduler.errors import db_errors
from Vire.models.pydantic_classes import BuildRequestModel

async def register_build_data(BRM: BuildRequestModel)-> None:
    """
    CRUD function for registering a build's data in the local DB.

    Args:
        BRM - Build Request Model, abbrev. The pydantic class
    """
    async with async_session() as session:
        async with session.begin():
            new_build_data = BuildData(
                job_uuid=BRM.job_uuid,
                user_uuid = BRM.user_uuid,
                remote_user = BRM.remote_user,
                remote_reponame=BRM.remote_reponame, 
                remote_link=BRM.remote_link,
                commit_id=BRM.commit_id,
                provider = BRM.provider,
                branch=BRM.branch
            )
            session.add(new_build_data)

async def register_build_state(
    job_uuid: str, user_uuid: str,
    status: Literal["queued", "running", "crashed", "finished", "cancelled"],
)-> None:
    """
    CRUD function for registering the build's state into the local DB.

    Note: Use only for queueing, updating status or marking a build as finished.
    """
    async with async_session() as session:
        async with session.begin():
            new_build_state = BuildState(job_uuid=job_uuid, user_uuid = user_uuid, status=status)
            session.add(new_build_state)


async def fetch_build_data(job_uuid: str)-> tuple[str, ...] | None:
    """
    Fetches full details of a build based on job_uuid.

    Returns - tuple[
        job_uuid: str, user_uuid: str,
        remote_link: str, commit_id: str,
        provider: str, remote_user: str,
        remote_reponame: str, branch: str
    ]
        If the provided job_uuid exists. Else it returns 'None'.
    """
    async with async_session() as session:
        query = select(BuildData).where(BuildData.job_uuid == job_uuid)
        result = await session.execute(query)
        build_data_obj: BuildData | None = result.scalar_one_or_none()
        if build_data_obj:
            return (
                build_data_obj.job_uuid,
                build_data_obj.user_uuid,
                build_data_obj.remote_link,
                build_data_obj.commit_id,
                build_data_obj.provider,
                build_data_obj.remote_user,
                build_data_obj.remote_reponame,
                build_data_obj.branch
            )
        else:
            return None

async def fetch_queued_builds(number_of_builds: int)-> None:
    """
    CRUD function for fetching builds where the build status is 'queued'.

    Args -
        number_of_buids - The number of queued functions to fetch from the db.

    Behavior - 
        Fetches all builds with status = 'queued'. Then puts them into an asyncio.Queue.
    """
    async with async_session() as session:
        query = select(BuildState).where(BuildState.status == "queued").limit(number_of_builds)
        result = await session.execute(query)
        queued_builds = result.scalars().all()

        for build_obj in queued_builds:
            await db_build_queue.put(build_obj.job_uuid)

async def update_job_status(
    job_uuid: str, status_msg: Literal["queued", "running", "crashed", "finished", "cancelled"]
)-> None:
    """
    CRUD function for updating job status in BuildState table.
    """
    
    async with async_session() as session:
        query = select(BuildState).where(
            (BuildState.job_uuid == job_uuid) & (BuildState.status == "queued")
        )
        result = await session.execute(query)
        job_state = result.scalar_one_or_none()
        if not job_state:
            raise db_errors.NoJobStateError(f"Tried to fetch job state for job_uuid {job_uuid}. But returned Null.")
        async with session.begin():
            job_state.status = status_msg