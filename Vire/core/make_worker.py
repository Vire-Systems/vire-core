"""
This module (make_worker) is repsonsible with providing an abstracted function called scheduler_create_worker.
This is made so that the API layer does not mess with fetching raw data, parsing, etc.
"""

from datetime import datetime

# um, idk what to call this.. custom imports ?
from BuildScheduler.Scheduler.core.create_worker import create_worker_process
from Vire.core.core_utilities.fetch_buildreq import fetch_vire_toml, fetch_package_json
from BuildScheduler.Scheduler.project_manifest.toml.parse_toml import parse_toml
from BuildScheduler.Scheduler.project_manifest.toml.validator import validate_package_json, validate_toml
from BuildScheduler.Scheduler.project_manifest.toml.errors import config_errors
from Vire.errors import errors
from Vire.utils.pub_redis import publish_log_redis
from Vire.core.core_utilities.fetch_lockfile import fetch_lockfile_name

def ts():
    """Returns the current datetime in the format '%d-%m-%Y, %H:%M:%S'"""
    return datetime.now().strftime('%d-%m-%Y, %H:%M:%S')

def return_common_line(provider: str, remote_user: str, remote_reponame: str, branch: str, commit_id: str):
    """Returns the string "{provider}'s, {remote_user}/{remote_reponame}, {branch}, sha: {commit_id}"."""
    return f"{provider}'s, {remote_user}/{remote_reponame}, {branch}, sha: {commit_id}"

async def scheduler_create_worker(
        job_uuid: str, user_uuid: str, remote_link: str, commit_id: str,
        provider: str, remote_user: str, remote_reponame: str, branch: str,
    ):
    """
    The abstracted function for creating a worker.

    Handles all intermediary processes like -
        1. fetching vire.toml, package.json from the git provider.
        2. parsing the provided vire.toml and checking its schema.
        3. Validating the package.json (see validate_package_json docstring) and vire.toml.
        4. Creating a worker when it passes all checks.

    Args -
        1. job_uuid - UUID4 of the job.
        2. user_uuid - UUID4 of the user.
        3. remote_link - git clone link for the remote repository.
        4. commit_id - SHA for the commit that is to be built.
        5. provider - Name of the git provider (github, gitlab, codeberg, etc).
        6. remote_user - Username under the git provider.
        7. remote_reponame - The remote repository's name.
        8. branch - The branch which the commit was pushed to.
    
    Errors raised by the functions used -
        1. InvalidBranchError (fetch_vire_toml)
        2. InvalidVireToml (parse_toml)
        3. EmptyLockfile, KeyErrror, NoLockfile (fetch_lockfile)
        4. InvalidPackageJson, PackageManagerException, InvalidOutDir (validate_toml)
        5. InvalidBranchError (fetch_package_json)
        6. InvalidPackageJson (validate_package_json)
    """
    #pylint: disable=line-too-long
    try:
        common_line = return_common_line(provider, remote_user, remote_reponame, branch, commit_id)

        # Fetch toml, parse toml.
        try:
            vire_toml_str = await fetch_vire_toml(
                provider=provider, remote_user=remote_user, remote_reponame=remote_reponame, branch=branch
            )
            toml_data, install_req = await parse_toml(vire_toml_str)
            framework, pm, _, output_dir = toml_data

        except errors.InvalidBranchError:
            await publish_log_redis(
                line = f"{ts()} : The branch provided ({branch}) does not contain vire.toml. Vire tried to fetch vire.toml from {common_line} in Repo's root but found nothing.)",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        except config_errors.InvalidVireToml as e:
            await publish_log_redis(
                line = f"{ts()} : Parsing error for vire.toml fetched from  failed. Details for the error: {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        # Fetch lockfile name
        try:
            if install_req:
                lockfile_name = await fetch_lockfile_name(
                    username=remote_user, reponame=remote_reponame, provider=provider, commit_id=commit_id, pm=pm
                )
            else: lockfile_name = None

        except errors.EmptyLockfile as e:
            await publish_log_redis(
                line =f"{ts()} : Vire fetched a lockfile ({e}) from {common_line} but found it empty.",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        except KeyError:
            await publish_log_redis(
                line=f"{ts()} : Vire tried to fetch the contents of {common_line} using {provider}'s git tree API but is unable to fetch the 'trees' and 'tree_node[path]' of the json.'",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        except errors.NoLockfile:
            await publish_log_redis(
                line=f"{ts()} : Vire tried to fetch the lockfile from {common_line} but found no lockfile. Try setting 'dependencies=false' in vire.toml if installation of packages isn't needed for building the project.",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

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
                line=f"{ts()} : Vire attempted to parse vire.toml from {common_line}, The repository {remote_reponame}'s root directory and encountered the following issue: {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return
        except config_errors.InvalidOutDir as e:
            await publish_log_redis(
                line = f"{ts()} : The output_dir ('{output_dir}') fetched from {common_line} is invalid. Details : {e}",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

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
            ) ; return

        except errors.InvalidBranchError:
            await publish_log_redis(
                line=f"{ts()} : The branch provided ({branch}) does not contain a package.json. Vire tried to fetch package.json from {common_line} in '{remote_reponame}'s root but found nothing.)",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        # Check for errors (since valid becomes false when validate_package_json catches 'Exception'.)
        if not valid_packagejson:
            await publish_log_redis(
                f"{ts()} : While attempting to parse package.json, Vire encountered unexpected errors.",
                user_uuid=user_uuid, job_uuid=job_uuid
            ) ; return

        json_struct: tuple = (
            job_uuid, user_uuid, remote_link, remote_reponame,
            framework, pm, install_req, output_dir, commit_id
        )

        await create_worker_process(json_struct)
    except Exception as e:
        print(e)
    #pylint: enable=line-too-long
