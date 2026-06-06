"""
All errors used in Vire Core (excludes Scheduler).

Contains -
    1. InvalidBranchError
"""

class InvalidBranchError(Exception):
    """Raise for Invalid / Unprovided branches."""

class UnsupportedPackageManager(Exception):
    """Raise for unsupported pms."""

class EmptyLockfile(Exception):
    """Raise when lockfile is empty."""

class NoLockfile(Exception):
    """Raise when unable to find a lockfile."""

class UnsupportedGitProvider(Exception):
    """Raise when the git provider isn't supported."""
