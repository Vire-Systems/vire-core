

from Vire.core.core_utils.fetch_buildreq import fetch_package_json
from Vire.project_manifest.toml.validator import validate_package_json
from Vire.utils.pub_redis import publish_log_redis

from Vire.errors import errors
from Vire.project_manifest.toml.errors import config_errors
from Vire.objects.dataclass_objects.validation_models import ValidatorContext, PkgJSONValidationParams


async def fetch_and_validate_pkgjson(
    VC: ValidatorContext,
    PJVP: PkgJSONValidationParams
)-> None:
    """
    Fetches and validates the package.json from user's repo,branch.

    Args:
        1. VC - Validator context, abbrev. Context provided to 'validate_request'.
        2. PJVP - Package JSON Validation Params, abbrev. Parameters for the function.
    """

    #helper to publish line to redis pubsub
    async def publish_redis_ln(line, job_uuid=VC.job_uuid, user_uuid=VC.user_uuid, ts=PJVP.ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )

    # Main logic
    try:
        package_json_str = await fetch_package_json(
            provider=VC.provider, remote_user=VC.remote_user, remote_reponame=VC.remote_reponame, branch=VC.branch
        )
        await validate_package_json(package_json_str)

    except config_errors.InvalidPackageJson as e:
        await publish_redis_ln(f"The package.json in {PJVP.common_line} is invalid. Vire cannot run the build command with this package.json. Details : {e}")

    except errors.InvalidBranchError:
        await publish_redis_ln(f"The branch provided ({VC.branch}) does not contain a package.json. Vire tried to fetch package.json from {PJVP.common_line} but found nothing.)")

    except errors.RepoFileFetchError as e:
        await publish_redis_ln(f"Vire failed in fetching package.json from {PJVP.common_line}. Details: {e}")

    except errors.UnsupportedGitProvider as e:
        await publish_redis_ln(f"Vire encountered an issue while fetching and validating package.json from {PJVP.common_line}. Details: {e}")
