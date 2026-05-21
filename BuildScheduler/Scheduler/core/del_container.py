import asyncio, docker
from shared.scheduler_logger import vire_logger
from utils import state

async def delayed_delete(job_uuid):
    await asyncio.sleep(state.CONTAINER_REMOVAL_DELAY) # in seconds
    try:
        client = docker.from_env()
        container_obj = client.containers.get(job_uuid)
        container_obj.wait()
        container_obj.remove(force=True)
    except Exception as e:
        vire_logger("critical", "[delayed_delete] Removal of container '%s' was unsuccessful. Details: %s", job_uuid, e)