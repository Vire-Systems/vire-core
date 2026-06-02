"""
This module (remote_adapter) is responsible for providing remote (github,gitlab, etc) details.

"""

class GitProviderAdapter:
    """
    Master class for all provider specific classes.
    
    Methods-
        1. get_raw_url
        2. return_clone_link

    """
    def get_raw_url(self, user: str, repo_name: str, branch: str, path_name: str):
        """Returns raw url for the path specified."""
        raise NotImplementedError

    def return_clone_link(self, user, repo_name):
        """Returns a repository clone link."""
        raise NotImplementedError

    def return_default_branch(self):
        """Returns default fallback branch, ie; 'main'."""
        return 'main'

# Adapters

class GithubAdapter(GitProviderAdapter):
    """
    Adapter for Github. Inherits 'GitProviderAdapter'.
    """
    def get_raw_url(self, user, repo_name, branch, path_name):
        return(
            f"https://raw.githubusercontent.com/{user}/{repo_name}/{branch}/{path_name}"
        )

    def return_clone_link(self, user, repo_name):
        return(
            f"https://github.com/{user}/{repo_name}.git"
        )

PROVIDER_REGISTRY = {
    "github":GithubAdapter(),
}