"""
The main gc.py entrypoint.
"""

import docker, asyncio, logging, os
from core.delete_containers import batch_remove
from core.fetch_overdue import get_containers_overdue
from logger.scheduler_logger import vire_logger, sync_vire_logger
from logger.logger_setup import setup_async_logging, stop_async_logging
from state import logfile_dir

from docker.models.containers import Container

client = docker.from_env()
logger = logging.getLogger(__name__)
logfile_location = os.path.join(logfile_dir, "gc.log")


async def gc_core_loop():
    """The core GC loop. Asynchronous."""
    while True:
        try:
            setup_async_logging(log_file=logfile_location, log_level=logging.INFO)
            sync_vire_logger("info", "GC starting.")
            overdue_containers: list[Container] = await get_containers_overdue(client)
            await batch_remove(overdue_containers)
        except Exception as e:
            await vire_logger("critical", "[GC gc_core_loop] Unable to collect. Details: %s", e)
        await asyncio.sleep(30)


if __name__ == "__main__":
    try:
        asyncio.run(gc_core_loop())
    except KeyboardInterrupt:
        sync_vire_logger("info", "[GC] Received KeyboardIntterupt. Exiting...")
    except Exception as e:
        sync_vire_logger("critical", "[GC entry point] Unable to run GC loop. Details: %s", e)
    finally:
        stop_async_logging()
