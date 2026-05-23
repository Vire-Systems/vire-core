import asyncio, docker
from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.Scheduler.utils import mutex_locks, state
from BuildScheduler.Scheduler.utils.state import docker_client as client

# Types
from docker import DockerClient
from docker.models.containers import Container


# Helper called in delayed_delete_helper
async def get_container_object(job_uuid: str, docker_client: DockerClient)-> Container | None:
    """Returns container_object (type:Container) if container exists. Else returns 'None'"""
    try:
        container_obj = await asyncio.to_thread(docker_client.containers.get,job_uuid)
        return container_obj
    except docker.errors.NotFound:
        return None
    except Exception as e:
        vire_logger("critical", "[get_container_state] Unable to get the state of container '%s'. Details: %s", job_uuid, e)
        return None
    

# Helper called in delayed_delete
async def delayed_delete_helper(job_uuid: str)-> None:
    """Sleeps for 300s (state.CONTAINER_REMOVAL_DELAY) and kills the specified container if it's still alive."""
    await asyncio.sleep(state.CONTAINER_REMOVAL_DELAY) # in seconds
    try:
        async with mutex_locks.container_delete_lock:
            container_obj: Container = await get_container_object(job_uuid, client)
            if container_obj:
                await asyncio.to_thread(container_obj.remove,force=True)
                # TODO: Add a request to middleware. body = {"error":"Status: Build failed. Exit code 1. Reason: Task exceeded the 5 minute limit."}
    except Exception as e:
        vire_logger("critical", "[delayed_delete] Removal of container '%s' was unsuccessful. Details: %s", job_uuid, e)


# Gets called in core/create_worker
async def delayed_delete(job_uuid: str)-> None:
    """Create a task (asyncio.Task) scheduling the deletion of the container specified by name (job_uuid is name)."""
    task = asyncio.create_task(delayed_delete_helper(job_uuid))
    async with mutex_locks.task_removal_lock:    
        state.removal_tasks.add(task)
        task.add_done_callback(state.removal_tasks.discard)