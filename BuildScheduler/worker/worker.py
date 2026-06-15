# worker.py - The individual worker process. Spawns as a detached process.
# This is main

"""
refactor:

Add dynamic commands, check for packages, make sure to run npm ci --ignore-scripts.
Add output_dir selection, cd based on repo name, etc

Everything should be available via state.

"""

# Imports
import asyncio, logging, os
from cli_parser import load_parser

from utils import state
from schema.errors import ContainerCreationFail, CredentialError
from utils.vire_logger import cfn_log
from docker.errors import NotFound

from core.create_container_job import container_create
from core.cleanup_container import remove_container
from core.mark_unavailable import mark_unavailable
from core.stream_redis_log import publish_log_redis

client = state.client

def setup_logfile_location(job_uuid):
    """Sets up the logfile directory and locations."""
    worker_log_dir = os.path.join(state.logfile_dir, job_uuid)
    os.makedirs(worker_log_dir, exist_ok=True)
    return os.path.join(worker_log_dir,f"{job_uuid}.log")

async def main():
    """main. Handles everything."""
    try:
        if (state.job_uuid is None) or (state.user_uuid is None):
            raise CredentialError(f"Credential error. {'job_uuid' if state.job_uuid else 'user_uuid'} cannot be 'None'.")

        if (state.framework is None) or (state.package_manager is None):
            raise CredentialError(f"Credential error. {'framework' if state.framework else 'package_manager'} cannot be 'None'.")

        if (state.remote is None) or (state.repo_name is None):
            raise CredentialError(f"Credential error. {'Remote' if state.remote else 'repo_name'} cannot be 'None'.")

        await container_create(state.job_uuid)
    except CredentialError as e:
        publish_log_redis(str(e))
        print(e)
    except Exception as e:
        if state.job_uuid:
            cfn_log("critical", "[main] worker unable to run for job '%s'. Marking as crashed. Details: %s", state.job_uuid, e)
        else:
            cfn_log("critical", "[main] worker unable to run for job. [UUID unavailable]. Marking as crashed. Details: %s", e)
    finally:
        try:
            output_dir = state.OUTPUT_DIR
            if not output_dir:
                raise ContainerCreationFail("Output directory could not be resolved.")
            output_dir = os.path.join("/workspace", f"{state.repo_name}", output_dir)
            try:
                if  not state.job_uuid:
                    exit()
                stream, stat = client.api.get_archive(state.job_uuid, output_dir)
                with open(f"/home/vire/vire/test/{state.job_uuid}.tar", "wb") as tar_file: #TODO: Change this path
                    for chunk in stream:
                        tar_file.write(chunk)
            except NotFound:
                cfn_log("critical", "Toml path not found.")
                publish_log_redis("Given path in toml not found.") # TODO: Add better error
        except Exception as e:
            mark_unavailable("idk") #TODO Change this
            cfn_log("critical", "smtn happened. %s", e)
        job_uuid = state.job_uuid
        try:
            if job_uuid:
                remove_container(job_uuid=job_uuid)
        except Exception as e:
            cfn_log("critical", "[worker entry_point] remove_container unable to remove the container. Details %s", e)

def init():
    load_parser()
    logfile_location = setup_logfile_location(state.job_uuid)
    logging.basicConfig(filename=logfile_location, encoding='utf-8', level=logging.INFO)

# Entry point
if __name__ == "__main__":
    try:
        init()
        asyncio.run(main())
    except KeyError:
        publish_log_redis("Credential error: Credentials provided were incorrect.")
        print("Keyerror")
    except Exception as e:
        print(e)
