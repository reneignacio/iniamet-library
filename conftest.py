"""
Pytest configuration file.
"""
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_api_key():
    """Set a test API key for all tests if not already set."""
    if "INIA_API_KEY" not in os.environ:
        # Set a dummy API key for testing
        os.environ["INIA_API_KEY"] = "test-api-key-for-ci"
    yield
    # Cleanup is optional since it's session scoped
