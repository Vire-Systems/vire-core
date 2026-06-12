"""
This module (parse_toml) is the master script that handles toml validation.

Functions-
1. parse_toml
"""

import tomllib
from Vire.project_manifest.toml.schema_check import check_toml_schema
from Vire.project_manifest.toml.errors.config_errors import InvalidVireToml

async def parse_toml(toml_string: str)-> tuple[tuple[str, ...], bool]:
    """
    Parses vire.toml from toml string.
    
    Args -
        toml_string - string returned from reading the repo's vire.toml.

    Returns:
        tup[tup[8 strings ]]
        if pkg install needed:
        (framework, package_manager, framework_ver, output_dir), True

        if pkg install not needed:
        (framework, package_manager, framework_ver, output_dir), False

    Raises:
        'InvalidVireToml' if 'check_toml_schema' raises InvalidVireToml
    
    Catches:
        InvalidVireToml and reraises it.
    """
    try:
        toml_dict = tomllib.loads(toml_string)
        return await check_toml_schema(toml_dict)
    except InvalidVireToml as e:
        raise e
