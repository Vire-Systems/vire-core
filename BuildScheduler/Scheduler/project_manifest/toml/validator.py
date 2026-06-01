"""
This module (validator) Validates the package.json.

Functions-

1. validate_pakage_json (async, helper)
2. validate_toml (async)
"""

from Vire.utils.logger import vire_logger
from BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors import InvalidPackageJson, PackageManagerException, InvalidOutDir
import re

# frameworks vite, astro, vue, react, sveltekit, nextjs, nuxtjs, 11ty
# pms: npm, pnpm, yarn, bun


package_managers = ["npm", "pnpm", "yarn", "bun"]

lockfile_matrix = {
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "bun.lock": "bun",
    "bun.lockb": "bun"
}

# Helper, validates package.json. Called in 'validate.toml'
async def validate_package_json(package_json: dict)-> bool:
    """
    Validates package.json and returns bool (True/False). Is a Helper called by 'validate_toml'.
    
    Args:
        package.json - Dict of package.json after json.load / json.loads.

    Behavior:
        Returns False if "{"preinstall", "postinstall", "install", "prepare", "prepublish"}" is present in pacakge.json[scripts].
    """
    try:
        blocked_keys = {"preinstall", "postinstall", "install", "prepare", "prepublish"}
        scripts = package_json.get("scripts", {})
        found_keys = [key for key in blocked_keys if key in scripts]

        if found_keys:
            return False
        return True
    except Exception as e:
        await vire_logger(
            "critical", "[Core validate_package_json] Unable to validate package.json. Details: %s. package.json : %s",
            e, package_json
        )
        return False

async def validate_toml(package_manager: str, package_json: dict, lockfile_name: str, output_dir: str)-> bool:
    """
    Validates the vire.toml file using validate_package_json for validating package.json.

    Behavior:
        Returns False if "{"preinstall", "postinstall", "install", "prepare", "prepublish"}" is present in pacakge.json[scripts].

    Raises -
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

    packagejson_valid = await validate_package_json(package_json)
    if not packagejson_valid:
        raise InvalidPackageJson("package.json contains blocked methods (preinstall, postinstall, install, prepare, prepublish)")

    if package_manager not in package_managers:
        raise PackageManagerException("Invalid Package manager")

    if lockfile_matrix.get(lockfile_name) != package_manager:
        raise PackageManagerException("Invalid log file")

    allowed = re.fullmatch(r"[a-zA-Z0-9_]+", output_dir)
    if not allowed:
        raise InvalidOutDir(f"The output directory ({output_dir}) is not allowed. Only alphanumeric and underscore characters are allowed.")

    return True
