"""
This module (fetch_toml) fetches the toml file from a remote.
"""
import requests
from Vire.objects.git_provider_adapter import PROVIDER_REGISTRY
from Vire.errors.errors import InvalidBranchError

#TODO: Requests is blocking, use an async version.

async def fetch_toml_remote(
        provider: str,
        remote_user: str, remote_reponame: str,
        branch = "main"
    )-> str:
    """
    Fetches vire.toml from the provided provider's File content fetching APIs.
    
    Args -
        1. provider - The name of the git provider (ex: 'github', 'gitlab', etc)
        2. remote_user - The username of the build requester. (ex: Vire-Systems in "https://github.com/Vire-Systems/...")
        3. remote_reponame - The repository name (ex: vire in "https://github.com/Vire-Systems/vire/...")
        4. path - The path to the req file.
        5. branch - Latest branch which was pushed
    """
    try:
        adapter = PROVIDER_REGISTRY[provider]
        if not branch:
            branch = adapter.return_default_branch()

        toml_raw_url = adapter.get_raw_url(remote_user, remote_reponame, branch, "vire.toml")
        body = requests.get(toml_raw_url, timeout=2)
        toml_b:bytes = body.content
        toml_str = toml_b.decode(encoding="utf-8")
        return toml_str
    except Exception as e:
        print(e) #TODO: Change this later.

async def fetch_packagejson_remote(
        provider: str,
        remote_user: str, remote_reponame: str,
        branch: str | None
    )-> str:
    """b"""
    adapter = PROVIDER_REGISTRY[provider]
    if not branch:
        raise InvalidBranchError("Branch provided is 'None'")
    packagejson_raw_url = adapter.get_raw_url(user=remote_user, repo_name=remote_reponame, branch=branch, path_name="package.json")
    body = requests.get(packagejson_raw_url, timeout=2)
    packagejson_bytes = body.content
    packagejson_str = packagejson_bytes.decode(encoding="utf-8")
    return packagejson_str
 