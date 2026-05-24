import docker, asyncio
from logger.scheduler_logger import vire_logger

from docker.models.containers import Container

async def remove_single_container(con_obj: Container)-> None:
    try:
        await asyncio.to_thread(con_obj.remove,force=True)
        await vire_logger("info", "[GC remove_single_container] Terminated an overdue container process (Started at: '%s', Job UUID: %s).", con_obj.attrs["State"].get("StartedAt"), con_obj.name)
    except docker.errors.APIError as e:
        if "is already in progress" not in str(e).lower():
            await vire_logger("critical", "[GC remove_single_container]-> docker.errors.APIError: Removal of container '%s' was unsuccessful. Details: %s", con_obj.name, e)
    except docker.errors.NotFound:
        pass

async def batch_remove(overdue_list: list[Container])-> None:
    try:
        tasks = [asyncio.create_task(remove_single_container(c)) for c in overdue_list]
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        await vire_logger("critical","[GC batch_remove] Batch remove raised an exception. Details: %s", e)