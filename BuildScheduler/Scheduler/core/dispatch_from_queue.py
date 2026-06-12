import docker
from typing import Literal
import asyncio

from Vire.utils import state
from Vire.utils.queues_locks import db_build_queue
from Vire.core.make_worker import scheduler_create_worker
from Vire.db import crud

client = docker.from_env()

async def get_worker_count(fetch_all = False)-> int:
    containers = await asyncio.to_thread(client.containers.list, 
        all=fetch_all,
        filters={"label":"managed_by=build_scheduler"},
    )
    return len(containers)


async def launch_workers(job_uuids: list)-> None:
    task_list: list[asyncio.Task[None]] = []
    for job_uuid in job_uuids:
        job_data: tuple | None = await crud.fetch_build_data(job_uuid)
        if job_data:
            task_list.append(asyncio.create_task(scheduler_create_worker(*job_data)))
    await asyncio.gather(*task_list)


async def dispatch_queued_job()-> Literal["queued", "started"] | None:
    current_workers_count = await get_worker_count()
    available_slots = state.MAX_BUILDS_NUMBER - current_workers_count
    if not available_slots >= 0:
        return

    job_uuids: list[str] = []
    for _ in range(available_slots):
        try:
            job_uuid = db_build_queue.get_nowait()
        except asyncio.QueueEmpty
            break
        job_uuids.append(job_uuid)
    await launch_workers(job_uuids=job_uuids)
