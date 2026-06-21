import asyncio

from textwrap import dedent
from docker.errors import APIError, NotFound
from datetime import datetime, timedelta, timezone
from docker.models.containers import Container

from core.gc_crud import get_user_uuid, update_job_status
from logger.scheduler_logger import vire_logger
from logger.pub_redis import publish_log_redis


async def calc_elapsed_time(con_obj: Container)-> tuple[datetime, timedelta] | None:
    """Calculates 'started_at' and 'elapsed time' of given container objects. ISO-8601 format."""
    try:
        started_at = datetime.fromisoformat(con_obj.attrs["State"].get("StartedAt"))
        now = datetime.now(timezone.utc)
        elapsed = now - started_at
        return started_at, elapsed
    except TypeError:
        await vire_logger("warn","[GC calc_elapsed_time]-> TypeError. Unable to get elapsed time.")
        return None

def return_job_uuids(con_list: list[Container])-> list[str]:
    job_uuids = []
    for con_obj in con_list:
        if con_obj.name:
            job_uuids.append(con_obj.name)

    return job_uuids

async def remove_single_container(con_obj: Container)-> None:
    try:
        job_uuid = con_obj.name
        assert job_uuid is not None

        user_uuid = await get_user_uuid(job_uuid)
        assert user_uuid is not None

        await asyncio.to_thread(con_obj.remove,force=True)
        elapsed_time_tup: tuple[datetime, timedelta] | None = await calc_elapsed_time(con_obj)

        if not elapsed_time_tup:
            return

        started_at, elapsed = elapsed_time_tup
        await vire_logger("info","[GC remove_single_container] Terminated an overdue container process (Started at: '%s', Runtime: '%s' ,Job UUID: '%s').", started_at, elapsed, con_obj.name)
        await publish_log_redis(
            dedent(
                f"""
                Error: The worker with job_uuid: {job_uuid} has been terminated for exceeding the 300s limit.
        
                Details:
                    Job UUID: {job_uuid}
        
                Suggested fixes:
                    1. Check for unoptimized dependencies. Check for that by using 'webpack-bundle-analyzer'.
                    2. Use speed measure plugin (speed-measure-plugin) to find what runs slowly.
                """
                ),
                user_uuid,
                job_uuid
                )
    except NotFound:
        pass

    except APIError as e:
        if "is already in progress" not in str(e).lower():
            await vire_logger("critical", "[GC remove_single_container]-> docker.errors.APIError: Removal of container '%s' was unsuccessful. Details: %s", con_obj.name, e)

    except Exception as e:
        await vire_logger("critical", "[GC remove_single_container] Unable to remove container process '%s'. Details: %s", con_obj.name, e)

async def batch_remove(overdue_list: list[Container] | None)-> None:
    if not overdue_list:
        return
    try:
        await update_job_status(return_job_uuids(overdue_list), error_code = "VC-GC-001 ")
        tasks = [asyncio.create_task(remove_single_container(c)) for c in overdue_list]
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        await vire_logger("critical","[GC batch_remove] Batch remove raised an exception. Details: %s", e)
