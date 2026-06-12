"""
This module (validate_request) is responsible for providing an abstracted interface for validation.

Handles fetching, validation, etc.
"""

import traceback
from datetime import datetime

from Vire.core.validate.fetch_parse_toml import fetch_and_parse_toml

from Vire.core.core_utils.fetch_buildreq import fetch_package_json

from Vire.project_manifest.toml.validator import validate_package_json, validate_toml
from Vire.project_manifest.toml.errors import config_errors
from Vire.errors import errors
from Vire.utils.pub_redis import publish_log_redis
from Vire.core.core_utils.fetch_lockfile import fetch_lockfile_name

def ts():
    """Returns the current datetime in the format '%d-%m-%Y, %H:%M:%S'"""
    return datetime.now().strftime('%d-%m-%Y, %H:%M:%S')


# Validate
async def validate_details(
    job_uuid: str, user_uuid: str, commit_id: str,
    provider: str, remote_user: str, remote_reponame: str, branch: str,
)-> bool | None:
    """
    The abstracted function for validating build data (vire.toml, package.json, lockfile verification) provided by the user.

    Handles all intermediary processes like -
    
        1. fetching vire.toml, package.json from the git provider.
        2. parsing the provided vire.toml and checking its schema.
        3. Validating the package.json (see validate_package_json docstring) and vire.toml.
        4. Creating a worker when it passes all checks.

    Args -
    
        1. job_uuid - UUID4 of the job.
        2. user_uuid - UUID4 of the user.
        3. commit_id - SHA for the commit that is to be built.
        4. provider - Name of the git provider (github, gitlab, codeberg, etc).
        5. remote_user - Username under the git provider.
        6. remote_reponame - The remote repository's name.
        7. branch - The branch which the commit was pushed to.
    
    Errors raised by the functions used -
    
        1. InvalidBranchError (fetch_vire_toml)
        2. InvalidVireToml (parse_toml)
        3. EmptyLockfile, KeyErrror, NoLockfile (fetch_lockfile)
        4. InvalidPackageJson, PackageManagerException, InvalidOutDir (validate_toml)
        5. InvalidBranchError (fetch_package_json)
        6. InvalidPackageJson (validate_package_json)
    """
    try:
        common_line = f"the branch {branch} from {remote_user}'s repository named {remote_reponame} from {provider.capitalize()}"

        # Fetch toml, parse toml.
        # Fetch lockfile name
        try:
            toml_data: tuple[str,str,bool]|None = await fetch_and_parse_toml(
                job_uuid=job_uuid,
                user_uuid=user_uuid,
                provider=provider,
                remote_user = remote_user,
                remote_reponame=remote_reponame,
                branch=branch,
                ts=datetime.now().strftime('%d-%m-%Y, %H:%M:%S')
            )
            if not toml_data:
                return
            pm, output_dir, install_req = toml_data
            if install_req:
                lockfile_name = await fetch_lockfile_name(
                    username=remote_user, reponame=remote_reponame, provider=provider, commit_id=commit_id, pm=pm
                )
            else:
                lockfile_name = None

        except errors.EmptyLockfile as e:
            await publish_log_redis(
                line =f"{ts()} : Vire fetched a lockfile ({e}) from {common_line} but found it empty.",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except KeyError:
            await publish_log_redis(
                line=f"{ts()} : Vire tried to fetch the contents from {common_line} using {provider.capitalize()}'s git tree API but is unable to fetch the 'trees' and 'tree_node[path]' of the json.'",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except errors.NoLockfile:
            await publish_log_redis(
                line=f"{ts()} : Vire tried to fetch the lockfile from {common_line} but found no lockfile. Try setting 'dependencies=false' in vire.toml if installation of packages isn't needed for building the project.",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except errors.RepoFileFetchError as e:
            await publish_log_redis(
                line = f"{ts()} : ",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        # Validate toml
        try:
            valid_toml = await validate_toml(lockfile_name=lockfile_name, package_manager=pm, output_dir=output_dir)
            if not valid_toml:
                await publish_log_redis(
                    f"{ts()} : While attempting to parse vire.toml, Vire encountered unexpected errors. The toml appears to be misconfigured.",
                    user_uuid, job_uuid
                )
                return

        except config_errors.PackageManagerException as e:
            await publish_log_redis(
                line=f"{ts()} : Vire attempted to parse vire.toml from {common_line} and encountered the following issue: {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except config_errors.InvalidOutDir as e:
            await publish_log_redis(
                line = f"{ts()} : The output_dir ('{output_dir}') fetched from {common_line} is invalid. Details : {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        # fetch package json and validate package json
        try:
            package_json_str = await fetch_package_json(
                provider=provider, remote_user=remote_user, remote_reponame=remote_reponame, branch=branch
            )
            valid_packagejson = await validate_package_json(package_json_str)

        except config_errors.InvalidPackageJson as e:
            await publish_log_redis(
                f"{ts()} : The package.json in {common_line} is invalid. Vire cannot run the build command with this package.json. Details : {e}",
                user_uuid, job_uuid
            )
            return

        except errors.InvalidBranchError:
            await publish_log_redis(
                line=f"{ts()} : The branch provided ({branch}) does not contain a package.json. Vire tried to fetch package.json from {common_line} but found nothing.)",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except errors.RepoFileFetchError as e:
            await publish_log_redis(
                line = f"{ts()} : Vire failed in fetching package.json from {common_line}. Details: {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        except errors.UnsupportedGitProvider as e:
            await publish_log_redis(
                line = f"{ts()} : {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            )

        # Check for errors (since valid becomes false when validate_package_json catches 'Exception'.)
        if not valid_packagejson:
            await publish_log_redis(
                f"{ts()} : While attempting to parse package.json, Vire encountered unexpected errors. Details unavailable (Internal Error).",
                user_uuid=user_uuid, job_uuid=job_uuid
            )
            return

        return True
    except Exception:
        traceback.print_exc()
        

