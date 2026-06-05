"""
This module (validator) Validates the package.json.

Functions-

1. validate_pakage_json (async, helper)
2. validate_toml (async)
"""

from Vire.utils.logger import vire_logger
from BuildScheduler.Scheduler.project_manifest.toml.errors import config_errors
import re, json
from BuildScheduler.shared.shared_state import package_managers, lockfile_matrix
# frameworks vite, astro, vue, react, sveltekit, nextjs, nuxtjs, 11ty
# pms: npm, pnpm, yarn, bun

# Helper, validates package.json. Called in 'validate.toml'
async def validate_package_json(package_json_str: str)-> bool:
    """
    Validates package.json and returns bool (True/False). Is a Helper called by 'validate_toml'.
    
    Args:
        package.json - str

    Behavior:
        Returns False if "{"preinstall", "postinstall", "install", "prepare", "prepublish"}" is present in pacakge.json[scripts].
    
    Raises:
        config_errors.InvalidPackageJson
    """
    try:
        package_json = json.loads(package_json_str)
        blocked_keys = {"preinstall", "postinstall", "install", "prepare", "prepublish"}
        scripts = package_json.get("scripts", {})
        found_keys = [key for key in blocked_keys if key in scripts]

        if found_keys:
            raise config_errors.InvalidPackageJson(
                f"The following keys cannot be present in package.json. The invalid keys: {tuple(key for key in found_keys)}"
            )
        return True
    except config_errors.InvalidPackageJson as e:
        raise e
    except Exception as e:
        await vire_logger(
            "critical", "[Core validate_package_json] Unable to validate package.json. Details: %s. package.json : %s",
            e, package_json
        )
        return False

async def validate_toml(lockfile_name: str, package_manager: str, output_dir: str)-> bool:
    """
    Validates the vire.toml file.

    Behavior:
        Returns False if "{"preinstall", "postinstall", "install", "prepare", "prepublish"}" is present in pacakge.json[scripts].

    Raises
        
    'PackageManagerException' -
        1. if the given package_manager (arg) is invalid (unsupported).
        2. if lockfile given does not match the lockfile of the provided package manager.

    'InvalidPackageJson'
        1. if package.json contains blocked methods (preinstall, postinstall, install, prepare, prepublish).

    'InvalidOutDir' -
        1. If output_dir provided fails regex check (r[a-zA-Z0-9_]+).

    Error class locations -

    1. 'InvalidPackageJson' - BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors.InvalidPackageJson
    2. 'PackageManagerException' - BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors.PackageManagerException
    3. 'InvalidOutDir' - BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors.InvalidOutDir
    """
    #TODO: Fix the error messages
    if package_manager not in package_managers:
        raise config_errors.PackageManagerException("Invalid Package manager")

    if lockfile_matrix.get(lockfile_name) != package_manager:
        raise config_errors.PackageManagerException("Invalid lockfile")

    allowed = re.fullmatch(r"[a-zA-Z0-9_]+", output_dir)
    if not allowed:
        raise config_errors.InvalidOutDir(
            f"The output directory ({output_dir}) is not allowed. Only alphanumeric and underscore characters are allowed."
        )

    return True
