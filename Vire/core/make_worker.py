"""
This module (make_worker) is repsonsible with providing an abstracted function called scheduler_create_worker.
This is made so that the API layer does not mess with fetching raw data, parsing, etc.
"""


# um, idk what to call this.. custom imports ?
from BuildScheduler.Scheduler.core.create_worker import create_worker_process
from Vire.core.core_utilities.fetch_buildreq import fetch_vire_toml, fetch_package_json
from BuildScheduler.Scheduler.project_manifest.toml.parse_toml import parse_toml
from BuildScheduler.Scheduler.project_manifest.toml.validator import validate_package_json, validate_toml
from BuildScheduler.Scheduler.project_manifest.toml.errors import config_errors
from Vire.utils.pub_redis import publish_log_redis
from Vire.core.core_utilities.fetch_lockfile import fetch_lockfile_name


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

    Arg - data_tuple
        1. provider - str, name of the git provider (github, gitlab, codeberg, etc).
        2. remote_user - str, username for the git provider.
        3. remote_username
    Errors raised by the functions used.
    """
    try:

        vire_toml_str = await fetch_vire_toml(
            provider=provider, remote_user=remote_user, remote_reponame=remote_reponame, branch=branch
        )
        toml_data, install_req = await parse_toml(vire_toml_str)
        framework, pm, _, output_dir = toml_data
        lockfile_name = await fetch_lockfile_name(
            username=remote_user, reponame=remote_reponame, provider=provider, commit_id=commit_id, pm=pm
        )

        valid_toml = await validate_toml(lockfile_name=lockfile_name, package_manager=pm, output_dir=output_dir)
        if not valid_toml:
            publish_log_redis("Invalid vire.toml.", user_uuid, job_uuid)
            return

        package_json_str = await fetch_package_json(
            provider=provider, remote_user=remote_user, remote_reponame=remote_reponame, branch=branch
        )

        try:
            valid_packagejson = await validate_package_json(package_json_str)
        except config_errors.InvalidPackageJson as e:
            publish_log_redis(f"Invalid package.json. Details: {e}", user_uuid, job_uuid)
            return

        if not valid_packagejson:
            publish_log_redis("invalid package.json.", user_uuid, job_uuid)
            return

        json_struct: tuple = (
            job_uuid, user_uuid, remote_link, remote_reponame,
            framework, pm, install_req, output_dir, commit_id
        )

        await create_worker_process(json_struct)
    except Exception as e:
        print(e)
