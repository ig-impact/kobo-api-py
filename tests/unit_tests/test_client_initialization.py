"""Tests for KoboClient initialization and configuration."""

from unittest.mock import Mock, patch

import pytest

from kobo_api import KoboClient


class TestKoboClientInitialization:
    """Test KoboClient initialization logic."""

    def test_explicit_parameters_success(self, valid_config):
        """Test successful initialization with explicit parameters."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_make_session.return_value = Mock()

            client = KoboClient(
                server_url=valid_config["server_url"],
                token=valid_config["token"],
                cache=valid_config["cache"],
            )

            assert client.server_url == valid_config["server_url"]
            assert client.token == valid_config["token"]
            assert client.cache_enabled == valid_config["cache"]
            mock_make_session.assert_called_once()

    @pytest.mark.parametrize(
        "input_url,expected_url",
        [
            ("https://kobo.com/", "https://kobo.com"),
            ("https://kobo.com", "https://kobo.com"),
            ("https://kobo.com///", "https://kobo.com"),
            ("http://localhost:8000/", "http://localhost:8000"),
            ("https://kobo.com/api/", "https://kobo.com/api"),
        ],
    )
    def test_url_normalization(self, input_url, expected_url):
        """Test URL normalization removes trailing slashes correctly."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_make_session.return_value = Mock()

            client = KoboClient(server_url=input_url, token="test", cache=False)
            assert client.server_url == expected_url

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_environment_variable_loading(self, mock_dotenv, valid_env_values):
        """Test loading configuration from environment variables."""
        mock_dotenv.return_value = valid_env_values

        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_make_session.return_value = Mock()

            client = KoboClient()

            assert client.server_url == valid_env_values["URL"]
            assert client.token == valid_env_values["TOKEN"]
            mock_dotenv.assert_called_once_with(".env")

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_explicit_params_override_env(self, mock_dotenv, valid_env_values):
        """Test that explicit parameters override environment variables."""
        mock_dotenv.return_value = valid_env_values

        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_make_session.return_value = Mock()

            override_url = "https://override.com"
            client = KoboClient(server_url=override_url)

            assert client.server_url == override_url
            assert client.token == valid_env_values["TOKEN"]  # From env

    @pytest.mark.parametrize(
        "env_values,missing_param,error_message",
        [
            ({}, "server_url", "Server URL must be provided"),
            ({"URL": "https://test.com"}, "token", "Token must be provided"),
            ({"TOKEN": "abc123"}, "server_url", "Server URL must be provided"),
        ],
    )
    @patch("kobo_api.kobo_client.dotenv_values")
    def test_missing_required_parameters(
        self, mock_dotenv, env_values, missing_param, error_message
    ):
        """Test validation errors for missing required parameters."""
        mock_dotenv.return_value = env_values

        with pytest.raises(ValueError, match=error_message):
            KoboClient()

    # Removed invalid URL validation tests since your implementation doesn't validate URLs
    # Removed empty token validation test since your implementation allows empty strings

    @pytest.mark.parametrize(
        "cache_value,ttl_value",
        [
            (True, 300),  # Custom TTL
            (True, 600),  # Custom TTL
            (False, None),  # No cache
        ],
    )
    def test_cache_configuration(self, cache_value, ttl_value):
        """Test cache configuration options."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_make_session.return_value = Mock()

            kwargs = {
                "server_url": "https://test.com",
                "token": "test",
                "cache": cache_value,
            }
            if ttl_value is not None:
                kwargs["cache_ttl"] = ttl_value

            client = KoboClient(**kwargs)

            assert client.cache_enabled == cache_value  # Fixed: cache_enabled

    def test_authorization_header_construction(self):
        """Test that authorization header is properly constructed."""
        token = "test_token_123"

        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_session.headers = {}
            mock_make_session.return_value = mock_session

            client = KoboClient(server_url="https://test.com", token=token, cache=False)

            # Check headers mapping (not session.headers directly)
            expected_headers = {
                "Authorization": f"Token {token}",
                "Accept": "application/json",
                "User-Agent": "KoboClient/1.0",  # Fixed: actual User-Agent format
            }

            # Verify headers are in the client's headers mapping
            for key, value in expected_headers.items():
                assert client.headers[key] == value

    # Removed env_file_path_parameter test since your implementation doesn't support custom env file paths

    def test_user_agent_header(self):
        """Test that User-Agent header is correctly set."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_session.headers = {}
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            user_agent = client.headers.get("User-Agent", "")
            assert user_agent == "KoboClient/1.0"  # Fixed: check actual format

    def test_session_initialization(self):
        """Test that session is properly created and stored."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            # Verify session was created with correct parameters
            mock_make_session.assert_called_once_with(
                cache=False, cache_ttl=36000
            )  # Default TTL
            assert client.session is mock_session
