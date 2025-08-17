# pyright: reportAny=false
# pyright: reportExplicitAny=false
from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

import requests
import requests_cache
from dotenv import dotenv_values
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class KoboClient:
    def __init__(
        self,
        server_url: str | None = None,
        token: str | None = None,
        cache_enabled: bool = True,
        cache_ttl: int = 36000,
    ) -> None:
        config = dotenv_values(".env")
        server_url = server_url or config.get("URL")
        if server_url is None:
            raise ValueError(
                "Server URL must be provided either in .env file or as an argument."
            )
        token = token or config.get("TOKEN")
        if token is None:
            raise ValueError(
                "Token must be provided either in .env file or as an argument."
            )

        self.server_url: str = server_url.rstrip("/")  # Normalize URL
        self.token: str = token
        self.cache_enabled: bool = cache_enabled
        self.headers: Mapping[str, str] = {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json",
            "User-Agent": "KoboClient/1.0",
        }
        self.session: requests.Session = self._make_session(cache_ttl=cache_ttl)

    def _make_session(self, cache_ttl: int = 3600) -> requests.Session:
        """Create a requests session with the necessary headers."""
        if self.cache_enabled:
            session = requests_cache.CachedSession(
                "kobo_cache",
                expire_after=cache_ttl,
                allowable_codes=(
                    200,
                    404,
                ),
            )
        else:
            session = requests.Session()

        retry = Retry(
            total=3,
            connect=2,
            read=2,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "HEAD", "OPTIONS"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry)

        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(self.headers)
        return session

    def _get(self, path: str, **kwargs) -> dict[str, Any]:
        """Helper method to perform a GET request."""
        url = urljoin(f"{self.server_url}/", path.lstrip("/"))
        logger.debug(f"GET request to {url}")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def clear_cache(self) -> None:
        """Clear the entire cache."""
        if self.cache_enabled and hasattr(self.session, "cache"):
            assert isinstance(self.session, requests_cache.CachedSession)
            self.session.cache.clear()
            logger.info("Cache cleared")

    def ping(self) -> bool:
        """Check if the Kobo server is reachable."""
        try:
            response = self.session.get(
                urljoin(f"{self.server_url}/", "api/v2/assets/hash"),
                headers=self.headers,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_assets(self) -> list[dict[str, Any]]:
        """Get a list of assets from the Kobo server."""
        response = self._get("api/v2/assets")
        return response.get("results", [])

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        """Get a single asset by its ID."""
        return self._get(f"api/v2/assets/{asset_id}")

    def get_asset_data(self, asset_id: str, **kwargs) -> dict[str, Any]:
        """Get asset data (submissions)."""
        return self._get(f"api/v2/assets/{asset_id}/data", **kwargs)

    def get_assets_hash(self) -> str:
        """Get the hash of all assets."""
        response = self._get("api/v2/assets/hash")
        return response.get("hash", "")
