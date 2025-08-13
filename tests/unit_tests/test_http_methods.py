"""Tests for KoboClient HTTP methods."""

from unittest.mock import Mock, patch

import pytest
import requests

from kobo_api import KoboClient


class TestHttpMethods:
    """Test HTTP method implementations."""

    def test_get_method_success(self, mock_response):
        """Test successful GET request."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client._get("api/v2/assets")

            # Verify URL construction and response handling
            expected_url = "https://test.com/api/v2/assets"
            mock_session.get.assert_called_once_with(expected_url)
            mock_response.raise_for_status.assert_called_once()
            assert result == mock_response.json.return_value

    def test_get_method_url_construction(self):
        """Test URL construction in _get method."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {"test": "data"}
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            # Test various path formats
            test_cases = [
                ("api/v2/assets", "https://test.com/api/v2/assets"),
                ("/api/v2/assets", "https://test.com/api/v2/assets"),
                ("api/v2/assets/", "https://test.com/api/v2/assets/"),
            ]

            for path, expected_url in test_cases:
                mock_session.reset_mock()
                client._get(path)
                mock_session.get.assert_called_once_with(expected_url)

    def test_get_method_http_error(self):
        """Test _get method handles HTTP errors properly."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "404 Not Found"
            )
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            with pytest.raises(requests.HTTPError):
                client._get("api/v2/nonexistent")

    def test_get_method_with_kwargs(self):
        """Test _get method passes through additional kwargs."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            # Test with additional parameters
            params = {"limit": 100, "offset": 0}
            timeout = 30

            client._get("api/v2/assets", params=params, timeout=timeout)

            mock_session.get.assert_called_once_with(
                "https://test.com/api/v2/assets", params=params, timeout=timeout
            )
