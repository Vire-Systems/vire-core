"""
This module (cleanup_container) handles container removal.

Functions -
1. remove_container (async)

"""

from utils.state import client
from utils.vire_logger import cfn_log
from docker.errors import NotFound, APIError

def remove_container(job_uuid: str):
    """Name (UUID4 used for naming) based container remover"""
    try:
        container_obj = client.containers.get(job_uuid)
    except NotFound:
        container_obj = None
        pass
    try:
        if container_obj:
            container_obj.wait()
            container_obj.remove(force=True)
    except APIError as e:
        if "is already in progress" in str(e).lower():
            cfn_log("info", "[remove_container] Conflict: GC's termination in progress")
        else:
            cfn_log("critical", "[remove_container]-> docker.errors.APIError: Removal of container '%s' was unsuccessful. Details: %s",
                    job_uuid, e
            )
    except Exception as e:
        cfn_log("critical", "[remove_container] Removal of container '%s' was unsuccessful. Details: %s", job_uuid, e)
        raise e
