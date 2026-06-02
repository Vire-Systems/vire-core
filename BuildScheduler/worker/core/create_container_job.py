"""
This module (create_container_job) handles container creation.

Functions -
1. setup_creation (sync, helper)
2. sync_docker_run (sync, helper)
3. container_create (async, helper)
"""

import time, asyncio

from core.stream_redis_log import stream_logs, publish_log_redis
from schema.errors import ContainerCreationFail, UnsupportedFramework, InstallReqMismatch

from utils import state
from utils.adapter import FRAMEWORK_REGISTRY
from utils.vire_logger import cfn_log

# Helper
def setup_creation(repo_name: str, framework: str, package_manager: str)-> tuple[str]:
    """
    Args

    repo_name: Name of the repository.
    framework: Name of the framework.
    package_manager: Name of the package_manager

    Returns

    tuple : (image, cmd)

    Raises worker.schema.errors.UnsupportedFramework if framework_registry.get returns None
    """

    framework_adapter = FRAMEWORK_REGISTRY[framework]
    if not framework_adapter:
        raise UnsupportedFramework(f"{framework} is not supported.")
    try:
        image = framework_adapter.image

        build_cmd: str = framework_adapter.build_command[package_manager]
        checkout = f"git checkout {state.COMMIT_ID}"
        clone = f"git clone {state.remote}"

        cd = f"cd {repo_name}"
        base = f"{clone} && {cd}"
        if state.COMMIT_ID:
            base = f"{base} && {checkout}"

        if state.install_req:
            install_cmd = framework_adapter.install_command[package_manager]
            cmd_body = f"{base} && {install_cmd} && {build_cmd}"
        elif not state.install_req:
            cmd_body = f"{base} && {build_cmd}"
        else:
            raise InstallReqMismatch("'install_req' can only be a bool.")

        return image, cmd_body
    except Exception as e:
        cfn_log("critical", "[worker setup_creation] Unable to initialize setup. Details: %s", e)
        return None, None

# Helper called by 'container_create'.
def sync_docker_run(job_uuid: str)-> None:
    """
    Run a docker container synchronously.

    Args:
        job_uuid - Job UUID of the container job. Also used as container name.

    Raises 'worker.schema.errors.ContainerCreationFail' if container fails to spin up.
    """

    try:
        client = state.client
        expires_at = int(time.time() + state.CONTAINER_EXPIRY)
        image, cmd_body = setup_creation(state.repo_name, state.framework, state.package_manager)

        if not image or not cmd_body:
            raise ContainerCreationFail(f"{'Image' if not image else 'cmd'} Cannot be none.")
        cmd = ["sh", "-c", cmd_body]
        print(cmd)
        client.containers.run(
            name = job_uuid,
            image = image, command = cmd,
            mem_limit = '400m', cpu_quota = 50000, cpu_period = 100000,
            detach = True,
            labels = {
                "managed_by":"build_scheduler",
                "expires_at": str(expires_at)
            },
        )
    except Exception as e:
        cfn_log("critical", "[sync_docker_run] Job '%s' was unsuccessful. Details: %s", job_uuid, e )
        raise ContainerCreationFail(f"Container spin up unsucessful. Details: {e}") from e


async def container_create(job_uuid: str)-> None:
    """
    Creates a container task and streams the container logs.
    
    Catches:
        'ContainerCreationFail', 'Exception'.
    """
    try:
        container_task = asyncio.to_thread(sync_docker_run, job_uuid)
        await container_task
        await asyncio.to_thread(stream_logs,job_uuid)
    except ContainerCreationFail as e:
        await asyncio.to_thread(publish_log_redis, str(e))
    except Exception as e:
        cfn_log("critical", "[container_create] Container creation for job '%s' was unsucessful. Details: %s", job_uuid, e)
