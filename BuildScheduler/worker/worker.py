# worker.py - The individual worker process. Spawns as a detached process.
# This is main

# Imports
import asyncio, docker, redis, logging, time
from cli_parser import load_parser
import state

# Defined Variables
client = docker.from_env()
r = redis.Redis.from_url(state.redis_url)
logger = logging.getLogger(__name__)
logging.basicConfig(filename=state.logfile_location, encoding='utf-8', level=logging.DEBUG)

# Helper called in the entry point.
def mark_unavailable(reason):
    """sends a 'crashed'/'failed' API request to Middleware/Core"""
    #TODO : Mark unavailable by sending an API req to a middleware instance 
    return


def cfn_log(log_type: str, obj:str, *args)-> None: #cfn is a shorthand to 'custom function'
    """log_type levels: [info | warn | error | critical | exit]"""
    try:
        l_type = log_type.lower()
        if l_type == 'info':
            logger.info(obj, *args)
        elif l_type.lower() == 'warn':
            logger.warning(obj, *args)
        elif l_type == 'error':
            logger.error(obj, *args,exc_info=True ,stack_info=True)
        elif l_type == 'critical':
            logger.critical(obj, *args, stack_info=True, exc_info=True)
        elif l_type == 'exit':
            logger.critical(obj, *args)
        else:
            logger.warning("[cfn_log] Log type '%s' is not supported by cfn_log.", l_type)
    except Exception as e:
        logger.error("[cfn_log] An error occoured in the logging function. (%s)", e, exc_info=True)


# Helper called by 'stream_logs'
def publish_log_redis(line: str)-> None:
    try:
        r.publish(f"logs:{state.job_uuid}", line)
    except Exception as e:
        cfn_log("critical", "[publish_log_redis] Unable to publish logs. Details: %s", e)


# Calls 'publish_log_redis'
def stream_logs(job_uuid: str)-> None:
    try:
        container = client.containers.get(job_uuid)
        for line in container.logs(stream=True, follow=True, stdout=True, stderr=True, timestamps=True):
            str_line = line.decode("utf-8")
            #publish_log_redis(str_line)
            print(str_line) # TODO: Remove this after redis layer is done.
    except Exception as e:
        cfn_log("critical", "[stream_logs] Error in stream_logs. Details: (%s)", e)



def remove_container(job_uuid: str):
    """Name (UUID4 used for naming) based container remover"""
    try:
        container_obj = client.containers.get(job_uuid)
    except docker.errors.NotFound:
        return None
    try:
        if container_obj:
            container_obj.wait()
            container_obj.remove(force=True)
    except docker.errors.APIError as e:
        if "is already in progress" in e:
            pass
        else:
            cfn_log("critical", "[remove_container]-> docker.errors.APIError: Removal of container '%s' was unsuccessful. Details: %s", job_uuid, e)
    except Exception as e:
        cfn_log("critical", "[remove_container] Removal of container '%s' was unsuccessful. Details: %s", job_uuid, e)


# Helper called by 'container_create'.
def sync_docker_run(job_uuid: str):
    cmd_body = f"git clone {state.remote} && cd test && npm run build" #TODO swap test in 'cd test' with repo name and 'npm run build' with toml based check
    test_command = (
    'node -e "let i = 0; setInterval(() => { '
    'const stages = [\'FETCH\', \'BUILD\', \'OPTIMIZE\', \'ASSET\', \'CACHE\']; '
    'const stage = stages[Math.floor(Math.random() * stages.length)]; '
    'const hash = Math.random().toString(16).substring(2, 8); '
    'console.log(\'[\' + new Date().toISOString() + \'] [\' + stage + \'] Compiling chunk \' + hash + \' | Step \' + (++i) + \' | Memory RSS: \' + (process.memoryUsage().rss / 1024 / 1024).toFixed(2) + \' MB\'); '
    '}, 200);"'
    ) #TODO REMOVE THIS. test command to check the functionality of worker deadlock termination methods.
    
    try:
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
            }
        )
    except Exception as e:
        cfn_log("critical", "[sync_docker_run] Job '%s' was unsuccessful. Details: %s", job_uuid, e )
        return {"container_run_error": "Container spin up unsucessful."}



async def container_create(job_uuid: str):
    try:
        container_task = asyncio.to_thread(sync_docker_run, job_uuid)
        await container_task
        await asyncio.to_thread(stream_logs,job_uuid)
    except Exception as e:
        cfn_log("critical", "[container_create] Container creation for job '%s' was unsucessful. Details: %s", job_uuid, e)



async def main():
    try:
        load_parser()
        if (state.job_uuid is None) or (state.remote is None):
            raise RuntimeError(f"Credential error. {'Remote' if state.remote else 'job_uuid'} cannot be 'None'.")
        #TODO: add pm, framework test here
        #TODO: add user_uuid test here
        await container_create(state.job_uuid)
    except Exception as e:
        if state.job_uuid:
            cfn_log("critical", "[main] worker unable to run for job '%s'. Marking as crashed. Details: %s", state.job_uuid, e)
        else:
            cfn_log("critical", "[main] worker unable to run for job. [UUID unavailable]. Marking as crashed. Details: %s", e)

# Entry point ------- aka the 'Bootstrap block' -------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        try:
            stream, stat = client.api.get_archive(state.job_uuid, "/workspace/test/dist/")
            with open("/home/vire/Vire-Core/test/test.tar", "wb") as tar_file: #TODO: Change paths in 128 and 129
                for chunk in stream:
                    tar_file.write(chunk)
        except Exception as e:
            mark_unavailable("idk") #TODO Change this
        remove_container(state.job_uuid)