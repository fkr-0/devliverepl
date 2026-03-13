"""Pytest fixtures and configuration."""

import pytest


@pytest.fixture
def sample_locals():
    """Sample local variables for testing."""
    return {
        "user_id": 123,
        "username": "testuser",
        "items": [1, 2, 3],
        "active": True,
    }


@pytest.fixture
def sample_globals():
    """Sample global variables for testing."""
    return {
        "APP_NAME": "TestApp",
        "VERSION": "1.0.0",
    }
