"""
This module handles all the custom db exceptions used in crud.py.

Contains - 
    1. NoJobStateError
"""

class NoJobStateError(Exception):
    """Raised when Job state doesn't exist in the db."""