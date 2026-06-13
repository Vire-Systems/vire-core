"""
This module is responsible for fetching and parsing the vire.toml.
Details provided by the user's requested repo, branch and commit SHA.

Functions -
    1. fetch_and_parse_toml
"""

from Vire.core.core_utils.fetch_buildreq import fetch_vire_toml
from Vire.project_manifest.toml.parse_toml import parse_toml
from Vire.project_manifest.toml.errors import config_errors
from Vire.errors import errors
from Vire.utils.pub_redis import publish_log_redis
from Vire.objects.dataclass_objects.validation_models import ValidatorContext, ParsedTOMLObject

async def fetch_and_parse_toml(VC: ValidatorContext, ts: str)-> ParsedTOMLObject:
    """
    This function fetches and parses vire.toml.
    
    Args -
        TO - ValidatorContext, Toml object with toml data.

    returns -
        ParsedTOMLObject
    """

    #Helper inside the fn for publishing log lines to redis.
    async def publish_redis_ln(line, job_uuid=VC.job_uuid, user_uuid=VC.user_uuid, ts=ts)-> None:
        await publish_log_redis(
            line = f"{ts} : {line}",
            user_uuid=user_uuid, job_uuid=job_uuid
        )

    try:
        vire_toml_str = await fetch_vire_toml(
            provider=VC.provider, remote_user=VC.remote_user, remote_reponame=VC.remote_reponame, branch=VC.branch
        )
        verified_toml: ParsedTOMLObject = await parse_toml(vire_toml_str)

        return verified_toml

    except errors.InvalidBranchError:
        await publish_redis_ln(f"The branch provided ({VC.branch}) does not contain vire.toml. Vire tried to fetch vire.toml from in Repo's root but found nothing.)")
    
    except config_errors.InvalidVireToml as e:
        await publish_redis_ln(f"Parsing error for vire.toml fetched from  failed. Details for the error: {e}")
    
    except errors.RepoFileFetchError as e:
        await publish_redis_ln(e)

    except errors.UnsupportedGitProvider as e:
        await publish_redis_ln(e)
