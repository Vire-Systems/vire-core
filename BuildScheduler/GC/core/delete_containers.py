import docker, asyncio
from datetime import datetime, timezone
from logger.scheduler_logger import vire_logger

from docker.models.containers import Container

async def calc_elapsed_time(con_obj: Container)-> tuple[str, str]:
    """Calculates 'started_at' and 'elapsed time' of given container objects. ISO-8601 format."""
    try:
        started_at = datetime.fromisoformat(con_obj.attrs["State"].get("StartedAt"))
        now = datetime.now(timezone.utc)
        elapsed = now - started_at
        return started_at, elapsed
    except TypeError:
        await vire_logger("warn","[GC calc_elapsed_time]-> TypeError. Unable to get elapsed time.")
        return started_at, "None"


async def remove_single_container(con_obj: Container)-> None:
    try:
        await asyncio.to_thread(con_obj.remove,force=True)
        started_at, elapsed = await calc_elapsed_time(con_obj)
        await vire_logger("info", "[GC remove_single_container] Terminated an overdue container process (Started at: '%s', Runtime: '%s' ,Job UUID: '%s').", started_at, elapsed, con_obj.name)
    except docker.errors.APIError as e:
        if "is already in progress" not in str(e).lower():
            await vire_logger("critical", "[GC remove_single_container]-> docker.errors.APIError: Removal of container '%s' was unsuccessful. Details: %s", con_obj.name, e)
    except docker.errors.NotFound:
        pass
    except Exception as e:
        await vire_logger("critical", "[GC remove_single_container] Unable to remove container process '%s'. Details: %s", con_obj.name, e)

async def batch_remove(overdue_list: list[Container])-> None:
    try:
        tasks = [asyncio.create_task(remove_single_container(c)) for c in overdue_list]
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        await vire_logger("critical","[GC batch_remove] Batch remove raised an exception. Details: %s", e)