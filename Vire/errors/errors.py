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
