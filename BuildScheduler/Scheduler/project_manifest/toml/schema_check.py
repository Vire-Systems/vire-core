"""
This module (schema_chech.py) checks the vire.toml schema.

Functions -

1. check_toml_schema
"""

from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors import InvalidVireToml

async def check_toml_schema(toml_dict: dict)-> tuple[tuple[str, ...], bool]:
    """
    Validates the schema of the toml file. Also returns whether package install is required.
    
    Args:
        toml_dict: The dictionary format of toml using tomllib.load.

    Returns:

        if pkg install needed:
        (framework, package_manager, framework_ver, output_dir), True

        if pkg install not needed:
        (framework, package_manager, framework_ver, output_dir), False

    Raises "BuildScheduler.Scheduler.project_manifest.toml.errors.config_errors.InvalidVireToml" if toml is malformed.                         
    Raise returns a string with all missing toml_dict keys.
    Catches broad Exceptions.
    """
    try:
        output_str = ""
        details: dict[str, str]|None = toml_dict.get("details")
        if not details:
            raise InvalidVireToml("[details] table not found.")

        framework = details.get("framework")
        package_manager = details.get("package_manager")

        project: dict[str,str]|None = toml_dict.get("project")
        if not project:
            raise InvalidVireToml("[project] table not found")

        output_dir = project.get("output_dir")
        framework_version = project.get("framework_version")
        dependencies_req = project.get("dependencies")

        if not framework:
            output_str += "'framework' cannot be null. "
        if not package_manager:
            output_str += "'package_manager' cannot be none. "
        if not output_dir:
            output_str += "output_dir cannot be none. "
        if not framework_version:
            output_str += "framework_version cannot be none. "
        if not dependencies_req:
            output_str += "'dependencies' cannot be none"

        if output_str:
            raise InvalidVireToml(output_str)
        if dependencies_req:
            return (framework, package_manager, framework_version, output_dir), True
        elif not dependencies_req:
            return (framework, package_manager, framework_version, output_dir), False
        else:
            raise InvalidVireToml(f"'dependencies_req' under the table [projects] can only be bool. Not {dependencies_req}")
    except Exception as e:
        await vire_logger("critical", "[Core check_toml_template] unable to parse toml. Details: %s. toml_dict: %s", e, toml_dict)
        raise InvalidVireToml(
            "Unexpected errors occoured during parsing vire.toml. It appears to be misconfigured. See the docs for more information."
        )
