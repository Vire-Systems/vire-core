#from Vire.utils.logger import vire_logger
from Vire.project_manifest.toml.errors.config_errors import InvalidPackageJson

# frameworks vite, astro, vue, react, sveltekit, nextjs, nuxtjs, 11ty
# pms: npm, pnpm, yarn, bun

pm_matrix = {
    "npm":"package-lock.json",
    "yarn":"yarn.lock",
    "pnpm":"pnpm-lock.yaml",
    "bun":"bun.lockb"
}

package_managers = ["npm", "pnpm", "yarn", "bun"]

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
        #await vire_logger("critical", "[Core validate_package_json] Unable to validate package.json. Details: %s. package.json : %s", e, package_json)
        print(e)
        return False

async def validate_toml(package_manager, framework, package_json):

    packagejson_valid = await validate_package_json(package_json)
    if not packagejson_valid:   #TODO: swap the thing below with a custom error like InvalidPackageJson
        raise InvalidPackageJson("package.json contains blocked methods (like preinstall, postinstall, install, prepare, prepublish)")