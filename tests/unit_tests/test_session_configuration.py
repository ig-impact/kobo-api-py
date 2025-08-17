from types import SimpleNamespace
from unittest.mock import Mock, patch

from kobo_api import KoboClient


class TestSessionConfiguration:
    def test_cached_session_creation_with_default_ttl(self):
        # Default cache_ttl in __init__ is 36000
        with patch("kobo_api.kobo_client.requests_cache.CachedSession") as mock_cached:
            mock_cached.return_value = Mock()
            _ = KoboClient(server_url="https://test.com", token="t", cache_enabled=True)
            mock_cached.assert_called_once_with(
                "kobo_cache",
                expire_after=36000,
                allowable_codes=(200, 404),
            )

    def test_cached_session_creation_with_custom_ttl(self):
        with patch("kobo_api.kobo_client.requests_cache.CachedSession") as mock_cached:
            mock_cached.return_value = Mock()
            _ = KoboClient(
                server_url="https://test.com",
                token="t",
                cache_enabled=True,
                cache_ttl=600,
            )
            mock_cached.assert_called_once_with(
                "kobo_cache",
                expire_after=600,
                allowable_codes=(200, 404),
            )

    def test_regular_session_creation_when_cache_disabled(self):
        with patch("kobo_api.kobo_client.requests.Session") as mock_session_cls:
            mock_session_cls.return_value = Mock()
            _ = KoboClient(
                server_url="https://test.com", token="t", cache_enabled=False
            )
            mock_session_cls.assert_called_once()

    def test_retry_and_adapter_configuration(self):
        # Build a lightweight dummy session object that supports headers and mount
        dummy_session = SimpleNamespace(headers={}, mount=Mock())

        with (
            patch("kobo_api.kobo_client.requests.Session") as mock_session_cls,
            patch("kobo_api.kobo_client.Retry") as mock_retry_cls,
            patch("kobo_api.kobo_client.HTTPAdapter") as mock_adapter_cls,
        ):
            mock_session_cls.return_value = dummy_session

            mock_retry = Mock()
            mock_retry_cls.return_value = mock_retry

            mock_adapter = Mock()
            mock_adapter_cls.return_value = mock_adapter

            _ = KoboClient(
                server_url="https://test.com", token="t", cache_enabled=False
            )

            # Retry configuration matches implementation
            mock_retry_cls.assert_called_once_with(
                total=3,
                connect=2,
                read=2,
                backoff_factor=0.3,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET", "HEAD", "OPTIONS"),
                raise_on_status=False,
            )

            # Adapter created with pool and retry config
            mock_adapter_cls.assert_called_once_with(
                pool_connections=100, pool_maxsize=100, max_retries=mock_retry
            )

            # Adapters mounted for both protocols
            assert dummy_session.mount.call_count == 2
            dummy_session.mount.assert_any_call("https://", mock_adapter)
            dummy_session.mount.assert_any_call("http://", mock_adapter)

    def test_session_headers_are_applied(self):
        dummy_session = SimpleNamespace(headers={}, mount=Mock())
        with patch("kobo_api.kobo_client.requests.Session") as mock_session_cls:
            mock_session_cls.return_value = dummy_session

            token = "token_123"
            _ = KoboClient(
                server_url="https://test.com", token=token, cache_enabled=False
            )

            expected_headers = {
                "Authorization": f"Token {token}",
                "Accept": "application/json",
                "User-Agent": "KoboClient/1.0",
            }
            for k, v in expected_headers.items():
                assert dummy_session.headers.get(k) == v
