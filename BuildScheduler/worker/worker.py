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
from schema.errors import ContainerCreationFail
from utils.vire_logger import cfn_log
from utils.adapter import FRAMEWORK_REGISTRY

from core.create_container_job import container_create
from core.cleanup_container import remove_container
from core.mark_unavailable import mark_unavailable

client = state.client

def setup_logfile_location(job_uuid):
    worker_log_dir = os.path.join(state.logfile_dir, job_uuid)
    os.makedirs(worker_log_dir, exist_ok=True)
    return os.path.join(worker_log_dir,f"{job_uuid}.log")

async def main():
    try:
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
        load_parser()
        logfile_location = setup_logfile_location(state.job_uuid)
        logging.basicConfig(filename=logfile_location, encoding='utf-8', level=logging.INFO)

        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        try:
            output_dir = FRAMEWORK_REGISTRY.get(state.framework).output_dir
            if not output_dir:
                raise ContainerCreationFail("Output directory could not be resolved.")
            stream, stat = client.api.get_archive(state.job_uuid, "/workspace/test/dist/")
            with open("/home/vire/Vire-Core/test/test.tar", "wb") as tar_file: #TODO: Change paths in 128 and 129
                for chunk in stream:
                    tar_file.write(chunk)
        except Exception as e:
            mark_unavailable("idk") #TODO Change this
        job_uuid = state.job_uuid
        try:
            remove_container(job_uuid=job_uuid)
        except Exception as e:
            cfn_log("critical", "[worker entry_point] remove_container unable to remove the container. Details %s", e)