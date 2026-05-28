from Vire.utils.logger import vire_logger
from Vire.project_manifest.toml.errors.config_errors import InvalidPackageJson, PackageManagerException

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
    try:
        blocked_keys = {"preinstall", "postinstall", "install", "prepare", "prepublish"}
        scripts = package_json.get("scripts", {})
        found_keys = [key for key in blocked_keys if key in scripts]

        if found_keys:
            return False
        else:
            True
    except Exception as e:
        await vire_logger("critical", "[Core validate_package_json] Unable to validate package.json. Details: %s. package.json : %s", e, package_json)
        print(e)
        return False

async def validate_toml(package_manager,package_json, lockfile)-> bool:

    # TODO: Fix the error messages

    packagejson_valid = await validate_package_json(package_json)
    if not packagejson_valid:   #TODO: swap the thing below with a custom error like InvalidPackageJson
        raise InvalidPackageJson("package.json contains blocked methods (like preinstall, postinstall, install, prepare, prepublish)")
    
    install_req = packagejson_valid
    if package_manager not in package_managers:
        raise PackageManagerException("Invalid Package manager")
    if lockfile_matrix.get(lockfile) != package_manager:
        raise PackageManagerException("Invalid log file")
    return True