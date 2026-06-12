from Vire.core.core_utils.fetch_buildreq import fetch_vire_toml
from Vire.project_manifest.toml.parse_toml import parse_toml
from Vire.project_manifest.toml.errors import config_errors
from Vire.errors import errors
from Vire.utils.pub_redis import publish_log_redis

async def fetch_and_parse_toml(
    job_uuid: str,user_uuid: str,
    provider: str, remote_user: str, remote_reponame: str, branch: str, ts: str
)-> tuple[str,str,bool] | None:
    """
    This function fetches and parses vire.toml.

    returns -
        tuple - (pm, output_dir, install_req)
    """

    #Helper inside the fn for publishing log lines to redis.
    async def publish_redis_ln(line, job_uuid=job_uuid, user_uuid=user_uuid, ts=ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )
        
    try:
        vire_toml_str = await fetch_vire_toml(
            provider=provider, remote_user=remote_user, remote_reponame=remote_reponame, branch=branch
        )
        toml_data, install_req = await parse_toml(vire_toml_str)
        _, pm, _, output_dir = toml_data

    except errors.InvalidBranchError:
        await publish_redis_ln(f"The branch provided ({branch}) does not contain vire.toml. Vire tried to fetch vire.toml from in Repo's root but found nothing.)")
        return
    
    except config_errors.InvalidVireToml as e:
        await publish_redis_ln(f"Parsing error for vire.toml fetched from  failed. Details for the error: {e}")
        return
    
    except errors.RepoFileFetchError as e:
        await publish_redis_ln(e)
        return

    except errors.UnsupportedGitProvider as e:
        await publish_redis_ln(e)
        return
        
    return pm, output_dir, install_req
