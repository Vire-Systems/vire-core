import time, asyncio
from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.GC.state import filter_labels


from docker.client import DockerClient
from docker.models.containers import Container


async def get_containers_overdue(client: DockerClient)-> list[Container] | None:
    """Returns a list of all invalid (older than 300s) containers."""
    try:
        now_time = int(time.time())
        raw_container_list = asyncio.to_thread(client.containers.list, all=True, filters=filter_labels)
        overdue_containers = list(
            filter(
                lambda container: int(container.labels.get("expires_at", now_time)) <= now_time,
                raw_container_list
            )
        )
        return overdue_containers
    except Exception as e:
        await vire_logger("critical", "[GC get_containers_overdue] unable to get containers which are overdue. Details: %s", e)