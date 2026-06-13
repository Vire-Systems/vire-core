"""
This module handles fetching and validating the lockfile from data provided when requesting build.

Functions -
    1. fetch_and_validate_lockfile
"""

from Vire.errors import errors
from Vire.objects.dataclass_objects.validation_models import LockfileValidationParams, ValidatorContext
from Vire.utils.pub_redis import publish_log_redis
from Vire.core.core_utils.fetch_lockfile import fetch_lockfile_name

async def fetch_and_validate_lockfile(
    LVP: LockfileValidationParams,
    VC: ValidatorContext,
    ts: str,
    common_line: str
)-> str | None:
    """
    Fetch and validate lockfile against a matrix of supported package managers.

    Args -
    
        1. LVP - LockfileValidationParams, abbreviation. Core data used for validating the lockfile.
        2. TO - TOMLObjectContext, abbreviation. Dataclass for reading build related toml and general context.
        3. ts - Timestamp
        4. common_line - The common line used in the top validator function.
    """
    
    #Helper inside the fn for publishing log lines to redis.
    async def publish_redis_ln(line, job_uuid=VC.job_uuid, user_uuid=VC.user_uuid, ts=ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )

    # Main logic
    try:
        if LVP.install_req:
            lockfile_name = await fetch_lockfile_name(
            username=VC.remote_user,
            reponame=VC.remote_reponame,
            provider=VC.provider,
            commit_id=LVP.commit_id,
            pm=LVP.package_manager
        )
        else:
            return

        return lockfile_name

    # Exception handling
    except errors.EmptyLockfile as e:
        await publish_redis_ln(f"Vire fetched a lockfile ({e}) from {common_line} but found it empty.")

    except KeyError:
        await publish_redis_ln(f"Vire tried to fetch the contents from {common_line} using {LVP.provider.capitalize()}'s git tree API but is unable to fetch the 'trees' and 'tree_node[path]' of the json.'")

    except errors.NoLockfile:
        await publish_redis_ln(f"Vire tried to fetch the lockfile from {common_line} but found no lockfile. Try setting 'dependencies=false' in vire.toml if installation of packages isn't needed for building the project.",)

    except errors.RepoFileFetchError as e:
        await publish_redis_ln(f"Vire tried to fetch the lockfile from {common_line} but was unsuccessful in doing so. Details: {e}")
