import docker, asyncio
from BuildScheduler.GC.core.delete_containers import batch_remove
from BuildScheduler.GC.core.fetch_overdue import get_containers_overdue
from BuildScheduler.shared.scheduler_logger import vire_logger

from docker.models.containers import Container

client = docker.from_env()

async def gc_core_loop():
    while True:
        try:
            overdue_containers: list[Container] = get_containers_overdue(client)
            await batch_remove(overdue_containers)
        except Exception as e:
            await vire_logger("critical", "[GC gc_core_loop] Unable to collect. Details: %s", e)
        asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(gc_core_loop)