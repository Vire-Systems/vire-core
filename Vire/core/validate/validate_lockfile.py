"""
This module handles fetching and validating the lockfile from data provided when requesting build.

Functions -
    1. fetch_and_validate_lockfile
"""

from textwrap import dedent

from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.shared.shared_state import package_managers
from Vire.errors import errors
from Vire.objects.dataclass_objects.validation_models import LockfileValidationParams, ValidatorContext
from Vire.project_manifest.toml.errors import config_errors
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
    async def publish_redis_ln(line, error_code: str, job_uuid=VC.job_uuid, user_uuid=VC.user_uuid, ts=ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )
        await vire_logger("info", f"Error code: '{error_code}' for job_uuid: '{job_uuid}'")

    # Main logic
    try:
        if LVP.install_req:

            if LVP.package_manager not in package_managers:
                raise config_errors.PackageManagerException(f"The package manager provided ({LVP.package_manager}) isn't supported by Vire yet.")

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
    except config_errors.PackageManagerException as e:
        await publish_redis_ln(dedent(
            f"""
            Error: VC-VD-015. Unsupported package manager.

            Details:
                Job UUID: {VC.job_uuid}
                Commit SHA: {VC.commit_id}
                Branch Name: {VC.branch}
                PM provided: {LVP.package_manager}
            """
        ), "VC-VD-015")

    except errors.EmptyLockfile as e:
        await publish_redis_ln(dedent(
            f"""
            Error: VC-VD-012. Empty lockfile.

            Details:
                Job UUID: {VC.job_uuid}
                Commit SHA: {VC.commit_id}
                Branch Name: {VC.branch}
                Fetched from: {common_line}
                Lockfile path: '{e}'
            """), "VC-VD-012")

    except KeyError:
        await publish_redis_ln(dedent(
            f"""
            Error: VC-VD-011. Check docs for details.

            Job Details:
                Job UUID: {VC.job_uuid}
                Commit SHA: {VC.commit_id}
                Branch Name: {VC.branch}
                Tried to fetch from: {common_line}

            Brief overview:
                {VC.provider.capitalize()}'s git tree api returned malformed JSON. 
            """), "VC-VD-011")

    except errors.NoLockfile:
        await publish_redis_ln(dedent(
            f"""
            Error: VC-VD-013. No lockfile.

            Job Details:
                Job UUID: {VC.job_uuid}
                Commit SHA: {VC.commit_id}
                Branch Name: {VC.branch}
                Fetched from: {common_line}

            Potential fixes:
                Try setting 'dependencies=false' in vire.toml if installation of packages isn't needed for building the project.
            """,), "VC-VD-013")

    except errors.RepoFileFetchError as e:
        await publish_redis_ln(dedent(
            f"""
            Error: VC-VD-014. Check docs for error definition.

            Details:
                Job UUID: {VC.job_uuid}
                Commit SHA: {VC.commit_id}
                Branch Name: {VC.branch}
                Tried to fetch from: {common_line}
                Issue: {e}
            """
        ), "VC-VD-014")
