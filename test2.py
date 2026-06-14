import asyncio

from BuildScheduler.Scheduler.core.dispatch_from_queue import dispatch_queued_job
from BuildScheduler.Scheduler.db.crud.read import fetch_queued_builds

async def test():
    await fetch_queued_builds(10)
    await dispatch_queued_job(10)

asyncio.run(test())