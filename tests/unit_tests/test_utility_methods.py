"""Tests for KoboClient utility methods."""

from unittest.mock import Mock, patch

import requests
import requests_cache

from kobo_api import KoboClient


class TestUtilityMethods:
    """Test utility methods."""

    def test_ping_success(self):
        """Test successful ping."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.ping()

            assert result is True
            expected_url = "https://test.com/api/v2/assets/hash"
            mock_session.get.assert_called_once_with(
                expected_url, headers=client.headers
            )

    def test_ping_failure_http_error(self):
        """Test ping with HTTP error response."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 404
            mock_session.get.return_value = mock_response
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.ping()

            assert result is False

    def test_ping_failure_request_exception(self):
        """Test ping with network exception."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock()
            mock_session.get.side_effect = requests.RequestException("Network error")
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.ping()

            assert result is False

    def test_clear_cache_with_cache_enabled(self):
        """Test cache clearing when cache is enabled."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            # Create a proper mock that will pass the isinstance check
            mock_session = Mock(spec=requests_cache.CachedSession)
            mock_cache = Mock()
            mock_session.cache = mock_cache
            mock_make_session.return_value = mock_session

            client = KoboClient(server_url="https://test.com", token="test", cache=True)
            client.clear_cache()

            # Verify cache.clear was called
            mock_cache.clear.assert_called_once()

    def test_clear_cache_with_cache_disabled(self):
        """Test cache clearing when cache is disabled - should do nothing."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock(spec=requests.Session)
            # Regular session doesn't have cache attribute
            mock_make_session.return_value = mock_session

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            # Should not raise error when cache is disabled
            client.clear_cache()  # Should do nothing gracefully

    def test_clear_cache_cache_enabled_but_no_cache_attr(self):
        """Test cache clearing when cache_enabled=True but session has no cache attribute."""
        with patch.object(KoboClient, "_make_session") as mock_make_session:
            mock_session = Mock(spec=requests.Session)
            # Remove cache attribute to simulate regular session
            mock_make_session.return_value = mock_session

            client = KoboClient(server_url="https://test.com", token="test", cache=True)
            client.cache_enabled = True

            # Should not do anything when hasattr(session, 'cache') is False
            client.clear_cache()  # Should handle gracefully

    def test_get_assets(self, mock_response):
        """Test get_assets method."""
        with patch.object(KoboClient, "_get") as mock_get:
            mock_get.return_value = {"results": [{"uid": "test1"}, {"uid": "test2"}]}

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.get_assets()

            mock_get.assert_called_once_with("api/v2/assets")
            assert result == [{"uid": "test1"}, {"uid": "test2"}]

    def test_get_asset(self):
        """Test get_asset method."""
        with patch.object(KoboClient, "_get") as mock_get:
            expected_asset = {"uid": "test123", "name": "Test Asset"}
            mock_get.return_value = expected_asset

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.get_asset("test123")

            mock_get.assert_called_once_with("api/v2/assets/test123")
            assert result == expected_asset

    def test_get_assets_empty_results(self):
        """Test get_assets when no results returned."""
        with patch.object(KoboClient, "_get") as mock_get:
            mock_get.return_value = {}  # No 'results' key

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.get_assets()

            assert result == []  # Should return empty list when no results

    def test_get_assets_with_results(self):
        """Test get_assets with actual results."""
        with patch.object(KoboClient, "_get") as mock_get:
            expected_assets = [
                {"uid": "asset1", "name": "Asset 1"},
                {"uid": "asset2", "name": "Asset 2"},
            ]
            mock_get.return_value = {"results": expected_assets}

            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )
            result = client.get_assets()

            assert result == expected_assets
