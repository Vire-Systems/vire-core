"""
The main gc.py entrypoint.
"""

import asyncio
import docker
import logging
import os

from core.delete_containers import batch_remove
from core.fetch_overdue import get_containers_overdue
from docker.models.containers import Container
from logger.logger_setup import setup_async_logging, stop_async_logging
from logger.scheduler_logger import sync_vire_logger, vire_logger
from state import log_value, logfile_dir

client = docker.from_env()
logger = logging.getLogger(__name__)
assert logfile_dir is not None
logfile_location = os.path.join(logfile_dir, "gc.log")

print(log_value)


async def gc_core_loop():
    """The core GC loop. Asynchronous."""
    while True:
        try:
            setup_async_logging(log_file=logfile_location, log_level=log_value)
            sync_vire_logger("info", "GC starting.")
            overdue_containers: list[Container] | None = await get_containers_overdue(client)
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
