"""Shared fixtures and utilities for unit tests."""

from unittest.mock import Mock

import pytest
import requests
import requests_cache


@pytest.fixture
def valid_config():
    """Valid configuration for creating KoboClient instances."""
    return {
        "server_url": "https://kobo.test.com",
        "token": "test_token_123",
        "cache": False,
    }


@pytest.fixture
def valid_env_values():
    """Valid environment values for dotenv mocking."""
    return {"URL": "https://env.kobo.com", "TOKEN": "env_token_456"}


@pytest.fixture
def mock_session():
    """Mock requests.Session object."""
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get = Mock()
    return session


@pytest.fixture
def mock_cached_session():
    """Mock requests_cache.CachedSession object."""
    session = Mock(spec=requests_cache.CachedSession)
    session.headers = {}
    session.get = Mock()
    session.cache = Mock()
    session.cache.clear = Mock()
    return session


@pytest.fixture
def mock_response():
    """Mock HTTP response object."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"data": "test_data"}
    response.raise_for_status = Mock()
    return response


@pytest.fixture
def mock_error_response():
    """Mock HTTP error response."""
    response = Mock()
    response.status_code = 404
    response.json.return_value = {"error": "Not found"}
    response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    return response
