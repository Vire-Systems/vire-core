import docker
from typing import Literal
import asyncio

from BuildScheduler.Scheduler.core.core_utilities.make_worker import scheduler_create_worker
from BuildScheduler.Scheduler.utils import queues_locks


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
        task_list.append(asyncio.create_task(scheduler_create_worker(job_uuid)))
    await asyncio.gather(*task_list)


async def dispatch_queued_job(available_slots)-> Literal["queued", "started"] | None:
    if available_slots <= 0:
        return

    async with queues_locks.scheduler_lock:
        job_uuids: list[str] = []
        for _ in range(available_slots):
            try:
                job_uuid = queues_locks.db_build_queue.get_nowait()
                job_uuids.append(job_uuid)
            except asyncio.QueueEmpty:
                break
    await launch_workers(job_uuids=job_uuids)
