"""
This module is responsible for validating the vire.toml file fetched from the user's repository.

Functions -
    1. validate_vire_toml
"""

from Vire.project_manifest.toml.errors import config_errors
from Vire.objects.dataclass_objects.validation_models import TOMLValidationParams, ValidatorContext, ParsedTOMLObject
from Vire.project_manifest.toml.validator import validate_toml
from Vire.utils.pub_redis import publish_log_redis

async def validate_vire_toml(TVP: TOMLValidationParams, VC: ValidatorContext, PTO: ParsedTOMLObject)-> None:
    """
    Validates vire.toml fetched from the user's repo.

    Args -
        1. TVP - TOMLValidationParams, abbrev. Data needed to validate the validation process.
        2. VC - ValidatorContext, abbrev. The full context given to validate_request.
        3. PTO - ParsedTomlObject, abbrev. The data returned after the said vire.toml is parsed.
    """

    # Helper inside fn for reducing reused lines
    async def publish_redis_ln(line, job_uuid=VC.job_uuid, user_uuid=VC.user_uuid, ts=TVP.ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )

    # Main logic
    try:
        await validate_toml(
            lockfile_name=TVP.lockfile_name,
            package_manager=PTO.package_manager,
            output_dir=PTO.output_dir
        )

    # Error handling
    except config_errors.PackageManagerException as e:
        await publish_redis_ln(f"Vire attempted to parse vire.toml from {TVP.common_line} and encountered the following issue: {e}")

    except config_errors.InvalidOutDir as e:
        await publish_redis_ln(f"The output_dir ('{PTO.output_dir}') fetched from {TVP.common_line} is invalid. Details : {e}")
