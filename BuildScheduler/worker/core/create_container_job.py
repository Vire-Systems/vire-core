import time, asyncio

from core.stream_redis_log import stream_logs, publish_log_redis
from schema.errors import ContainerCreationFail

from utils import state
from utils.adapter import FRAMEWORK_REGISTRY
from utils.vire_logger import cfn_log

# Helper
def setup_creation(repo_name, framework, package_manager)-> list[str]:
    #TODO swap test in 'cd test' with repo name and 'npm run build' with toml based check
    framework_adapter = FRAMEWORK_REGISTRY.get(framework)
    
    image = framework_adapter.image
    output_dir = framework_adapter.output_dir
    

# Helper called by 'container_create'.
def sync_docker_run(job_uuid: str)-> None:
    """
    Run a docker container synchronously.

    Args:
        job_uuid - Job UUID of the container job. Also used as container name.

    Raises 'worker.schema.errors.ContainerCreationFail' if container fails to spin up.
    """

    test_command = (
    'node -e "let i = 0; setInterval(() => { '
    'const stages = [\'FETCH\', \'BUILD\', \'OPTIMIZE\', \'ASSET\', \'CACHE\']; '
    'const stage = stages[Math.floor(Math.random() * stages.length)]; '
    'const hash = Math.random().toString(16).substring(2, 8); '
    'console.log(\'[\' + new Date().toISOString() + \'] [\' + stage + \'] Compiling chunk \' + hash + \' | Step \' + (++i) + \' | Memory RSS: \' + (process.memoryUsage().rss / 1024 / 1024).toFixed(2) + \' MB\'); '
    '}, 200);"'
    ) #TODO REMOVE THIS. test command to check the functionality of worker deadlock termination methods.
    
    try:
        client = state.client
        exprires_at = int(time.time() + state.CONTAINER_EXPIRY)
        cmd = ["bash", "-c", cmd_body]     
        client.containers.run(
            name=job_uuid,
            image="vire_node-npm:v1",
            command=test_command,
            mem_limit='400m',
            cpu_quota=50000,   # These 2 are in μs (microseconds)
            cpu_period=100000,
            detach=True,
            labels={
                "managed_by":"build_scheduler",
                "expires_at": str(exprires_at)
            },
        )
    except Exception as e:
        cfn_log("critical", "[sync_docker_run] Job '%s' was unsuccessful. Details: %s", job_uuid, e )
        raise ContainerCreationFail("Container spin up unsucessful.")



async def container_create(job_uuid: str)-> None:
    try:
        container_task = asyncio.to_thread(sync_docker_run, job_uuid)
        await container_task
        await asyncio.to_thread(stream_logs,job_uuid)
    except ContainerCreationFail as e:
        await asyncio.to_thread(publish_log_redis, str(e))
    except Exception as e:
        cfn_log("critical", "[container_create] Container creation for job '%s' was unsucessful. Details: %s", job_uuid, e)