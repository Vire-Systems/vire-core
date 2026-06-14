
import asyncio

from BuildScheduler.Scheduler.core.dispatch_from_queue import dispatch_queued_job, get_worker_count
from BuildScheduler.Scheduler.utils import state
from Vire.utils.logger import vire_logger


async def scheduler_loop():
    await vire_logger("info", "Scheduler loop starting up.")
    try:
        while True:
            worker_count = await get_worker_count()
            available_slots = state.MAX_BUILDS_NUMBER - worker_count
            print("Here. avail ", available_slots)
            _ = asyncio.create_task(dispatch_queued_job(available_slots))
            print("task spawned")
            await asyncio.sleep(30)
    except Exception as e:
        await vire_logger("critical", "[scheduler_loop] Scheduler loop shutting down because of an error. Details: %s", str(e))
