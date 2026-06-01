"""
This module (config_errors) provides custom errors for config related errors.

Errors -
1. InvalidPackageJson
2. InvalidVireToml
3. PackageManagerException
4. InvalidOutDir 
"""

class InvalidPackageJson(Exception):
    """Exception for Invalid package.json."""

class InvalidVireToml(Exception):
    """Exception for invalid vire.toml."""

class PackageManagerException(Exception):
    """Exception for package manager exception."""

class InvalidOutDir(Exception):
    """Exception for invalid/malicious output dir."""
