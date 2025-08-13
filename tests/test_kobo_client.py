from unittest.mock import patch

import pytest
import requests
import requests_mock

from kobo_api import KoboClient


class TestKoboClientInit:
    """Test KoboClient initialization."""

    def test_init_with_explicit_params(self):
        """Test initialization with explicit parameters."""
        client = KoboClient(
            server_url="https://kobo.example.com", token="test_token_123", cache=False
        )
        assert client.server_url == "https://kobo.example.com"
        assert client.token == "test_token_123"
        assert not client.cache_enabled

    def test_init_normalizes_url(self):
        """Test that trailing slashes are removed from server URL."""
        client = KoboClient(
            server_url="https://kobo.example.com/", token="test_token", cache=False
        )
        assert client.server_url == "https://kobo.example.com"

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_init_from_env_file(self, mock_dotenv):
        """Test initialization from .env file."""
        mock_dotenv.return_value = {
            "URL": "https://env.kobo.com",
            "TOKEN": "env_token_456",
        }

        client = KoboClient(cache=False)
        assert client.server_url == "https://env.kobo.com"
        assert client.token == "env_token_456"

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_init_missing_url_raises_error(self, mock_dotenv):
        """Test that missing URL raises ValueError."""
        mock_dotenv.return_value = {"TOKEN": "test_token"}

        with pytest.raises(ValueError, match="Server URL must be provided"):
            KoboClient()

    @patch("kobo_api.kobo_client.dotenv_values")
    def test_init_missing_token_raises_error(self, mock_dotenv):
        """Test that missing token raises ValueError."""
        mock_dotenv.return_value = {"URL": "https://test.com"}

        with pytest.raises(ValueError, match="Token must be provided"):
            KoboClient()

    def test_headers_set_correctly(self):
        """Test that headers are set correctly."""
        client = KoboClient(
            server_url="https://test.com", token="test_token", cache=False
        )

        expected_headers = {
            "Authorization": "Token test_token",
            "Accept": "application/json",
            "User-Agent": "KoboClient/1.0",
        }

        for key, value in expected_headers.items():
            assert client.session.headers[key] == value


class TestKoboClientRequests:
    """Test KoboClient HTTP requests."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return KoboClient(
            server_url="https://kobo.test.com", token="test_token", cache=False
        )

    def test_ping_success(self, client):
        """Test successful ping."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/hash", status_code=200)
            assert client.ping() is True

    def test_ping_failure(self, client):
        """Test ping failure."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/hash", status_code=404)
            assert client.ping() is False

    def test_ping_connection_error(self, client):
        """Test ping with connection error."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://kobo.test.com/api/v2/assets/hash", exc=requests.ConnectionError
            )
            assert client.ping() is False

    def test_get_assets_success(self, client):
        """Test successful assets retrieval."""
        mock_response = {
            "results": [
                {"uid": "asset1", "name": "Form 1"},
                {"uid": "asset2", "name": "Form 2"},
            ]
        }

        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets", json=mock_response)
            assets = client.get_assets()

            assert len(assets) == 2
            assert assets[0]["uid"] == "asset1"
            assert assets[1]["name"] == "Form 2"

    def test_get_assets_empty_results(self, client):
        """Test assets retrieval with empty results."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets", json={})
            assets = client.get_assets()
            assert assets == []

    def test_get_asset_success(self, client):
        """Test successful single asset retrieval."""
        mock_asset = {"uid": "asset123", "name": "Test Form", "asset_type": "survey"}

        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/asset123", json=mock_asset)
            asset = client.get_asset("asset123")

            assert asset["uid"] == "asset123"
            assert asset["name"] == "Test Form"

    def test_get_asset_data_success(self, client):
        """Test successful asset data retrieval."""
        mock_data = {
            "results": [
                {"_id": 1, "question1": "answer1"},
                {"_id": 2, "question1": "answer2"},
            ]
        }

        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/asset123/data", json=mock_data)
            data = client.get_asset_data("asset123")

            assert len(data["results"]) == 2
            assert data["results"][0]["_id"] == 1

    def test_get_assets_hash_success(self, client):
        """Test successful assets hash retrieval."""
        mock_response = {"hash": "abc123def456"}

        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/hash", json=mock_response)
            hash_value = client.get_assets_hash()

            assert hash_value == "abc123def456"

    def test_get_assets_hash_empty(self, client):
        """Test assets hash retrieval with empty response."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/hash", json={})
            hash_value = client.get_assets_hash()
            assert hash_value == ""

    def test_http_error_handling(self, client):
        """Test HTTP error handling."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets/nonexistent", status_code=404)

            with pytest.raises(requests.HTTPError):
                client.get_asset("nonexistent")


class TestKoboClientCaching:
    """Test caching functionality."""

    def test_cache_enabled_by_default(self):
        """Test that caching is enabled by default."""
        client = KoboClient(server_url="https://test.com", token="test_token")
        assert client.cache_enabled is True
        assert hasattr(client.session, "cache")

    def test_cache_disabled(self):
        """Test that caching can be disabled."""
        client = KoboClient(
            server_url="https://test.com", token="test_token", cache=False
        )
        assert client.cache_enabled is False
        assert not hasattr(client.session, "cache")


class TestUrlBuilding:
    """Test URL building functionality."""

    @pytest.fixture
    def client(self):
        return KoboClient(
            server_url="https://kobo.test.com", token="test_token", cache=False
        )

    def test_url_building_with_leading_slash(self, client):
        """Test URL building with leading slash in path."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets", json={"results": []})
            client._get("/api/v2/assets")

            # Should have made request to correct URL
            assert m.last_request.url == "https://kobo.test.com/api/v2/assets"

    def test_url_building_without_leading_slash(self, client):
        """Test URL building without leading slash in path."""
        with requests_mock.Mocker() as m:
            m.get("https://kobo.test.com/api/v2/assets", json={"results": []})
            client._get("api/v2/assets")

            # Should have made request to correct URL
            assert m.last_request.url == "https://kobo.test.com/api/v2/assets"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
