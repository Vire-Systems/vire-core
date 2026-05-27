import tomllib
from schema_check import check_toml_schema #TODO: add full paths
from Vire.project_manifest.toml.errors.config_errors import InvalidPackageJson, InvalidVireToml

def parse_toml(toml_string: str):
    try:
        toml_dict = tomllib.loads(toml_string)
        check_toml_schema(toml_dict)
    except (InvalidVireToml, InvalidPackageJson) as e:
        print(e)


t_str = """
[details]
framework = "node"
package_manager = "npm"

[project]
framework_version = "20"
output_dir = "/dist"
dependencies="present"
"""

parse_toml(t_str)