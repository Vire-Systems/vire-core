"""This module (errors) houses errors used by worker."""

class ContainerCreationFail(Exception):
    """Exception for Container creation failure."""

class UnsupportedFramework(Exception):
    """Exception used when encountering an unsupported framework."""

class CredentialError(Exception):
    """Exception used for Credential errors by worker."""

class InstallReqMismatch(Exception):
    """Exception for the mismatch of 'install_req' flag."""
