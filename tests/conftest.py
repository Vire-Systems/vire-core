"""Pytest configuration and fixtures.

This file contains shared fixtures and configuration for all tests.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_session():
    """Provide a mocked database session"""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_redis_client():
    """Provide a mocked Redis client"""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_build_request():
    """Provide a sample build request"""
    return {
        "repo_url": "https://github.com/test/repo",
        "branch": "main",
        "commit_sha": "abc123def456",
        "build_script": "python setup.py build"
    }


@pytest.fixture
def sample_worker_config():
    """Provide a sample worker configuration"""
    return {
        "container_id": "worker-001",
        "image": "python:3.9",
        "cpu": 2,
        "memory_mb": 2048,
        "timeout_seconds": 3600
    }
