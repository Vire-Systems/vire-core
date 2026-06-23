"""
This module (parse_toml) is the master script that handles toml validation.

Functions-
1. parse_toml
"""

import tomllib
from Vire.project_manifest.schema_check import check_toml_schema
from Vire.project_manifest.errors.config_errors import InvalidVireToml
from Vire.objects.dataclass_objects.validation_models import ParsedTOMLObject

async def parse_toml(toml_string: str)-> ParsedTOMLObject:
    """
    Parses vire.toml from toml string.
    
    Args -
        toml_string - string returned from reading the repo's vire.toml.

    Returns:
        ParsedTOMLObject

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
