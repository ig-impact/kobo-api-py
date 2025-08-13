"""Tests for KoboClient session management and configuration."""

from unittest.mock import Mock, patch

from kobo_api import KoboClient


class TestSessionManagement:
    """Test session creation and configuration."""

    @patch("kobo_api.kobo_client.requests_cache.CachedSession")
    def test_cached_session_creation(self, mock_cached_session_class):
        """Test creation of cached session when cache is enabled."""
        mock_session = Mock()
        mock_cached_session_class.return_value = mock_session

        client = KoboClient(
            server_url="https://test.com", token="test", cache=True, cache_ttl=600
        )

        # Verify CachedSession was called with correct parameters
        mock_cached_session_class.assert_called_once_with(
            "kobo_cache", expire_after=600, allowable_codes=(200, 404)
        )

    @patch("kobo_api.kobo_client.requests.Session")
    def test_regular_session_creation(self, mock_session_class):
        """Test creation of regular session when cache is disabled."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = KoboClient(server_url="https://test.com", token="test", cache=False)

        mock_session_class.assert_called_once()

    @patch("kobo_api.kobo_client.HTTPAdapter")
    @patch("kobo_api.kobo_client.Retry")
    def test_retry_configuration(self, mock_retry_class, mock_adapter_class):
        """Test retry policy configuration."""
        mock_retry = Mock()
        mock_retry_class.return_value = mock_retry
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter

        with patch("kobo_api.kobo_client.requests.Session"):
            client = KoboClient(
                server_url="https://test.com", token="test", cache=False
            )

            # Verify Retry configuration matches actual implementation
            mock_retry_class.assert_called_once_with(
                total=3,
                connect=2,
                read=2,
                backoff_factor=0.3,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET", "HEAD", "OPTIONS"),
                raise_on_status=False,
            )

    def test_session_headers_applied(self):
        """Test that headers are properly applied to session."""
        with patch("kobo_api.kobo_client.requests.Session") as mock_session_class:
            mock_session = Mock()
            # Create a proper mock for headers that supports update()
            mock_headers = Mock()
            mock_session.headers = mock_headers
            mock_session_class.return_value = mock_session

            token = "test_token_123"
            client = KoboClient(server_url="https://test.com", token=token, cache=False)

            # Verify headers were updated on session
            expected_headers = {
                "Authorization": f"Token {token}",
                "Accept": "application/json",
                "User-Agent": "KoboClient/1.0",
            }

            mock_headers.update.assert_called_once_with(expected_headers)

    def test_adapter_mounting(self):
        """Test HTTP adapter mounting on session."""
        with patch("kobo_api.kobo_client.requests.Session") as mock_session_class:
            with patch("kobo_api.kobo_client.HTTPAdapter") as mock_adapter_class:
                mock_session = Mock()
                mock_adapter = Mock()
                mock_session.headers = Mock()
                mock_session_class.return_value = mock_session
                mock_adapter_class.return_value = mock_adapter

                client = KoboClient(
                    server_url="https://test.com", token="test", cache=False
                )

                # Verify adapters were mounted
                assert mock_session.mount.call_count == 2
                mock_session.mount.assert_any_call("https://", mock_adapter)
                mock_session.mount.assert_any_call("http://", mock_adapter)
