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
    """A Python client for the KoBoToolbox API v2.
    
    This client provides methods to interact with KoBoToolbox forms and data
    through their REST API. It supports authentication, caching, and automatic
    retry logic for reliable API access.
    
    Attributes:
        server_url: The base URL of the KoBoToolbox server.
        token: The API token for authentication.
        cache_enabled: Whether response caching is enabled.
        headers: HTTP headers used for API requests.
        session: The requests session used for HTTP calls.
    
    Example:
        Basic usage with direct parameters:
        
        ```python
        client = KoboClient(
            server_url="https://kobo.example.com",
            token="your-api-token"
        )
        
        if client.ping():
            assets = client.get_assets()
            print(f"Found {len(assets)} forms")
        ```
        
        Using environment variables:
        
        ```python
        # With .env file or environment variables set
        client = KoboClient()
        ```
    """
    
    def __init__(
        self,
        server_url: str | None = None,
        token: str | None = None,
        cache: bool = True,
        cache_ttl: int = 36000,
    ) -> None:
        """Initialize the KoboClient with authentication and configuration.
        
        Args:
            server_url: The base URL of the KoBoToolbox server. If None, 
                will attempt to read from 'URL' environment variable or .env file.
            token: The API token for authentication. If None, will attempt 
                to read from 'TOKEN' environment variable or .env file.
            cache: Whether to enable response caching for GET requests. 
                Defaults to True.
            cache_ttl: Cache time-to-live in seconds. Defaults to 36000 (10 hours).
        
        Raises:
            ValueError: If server_url or token cannot be determined from 
                parameters or environment variables.
        
        Example:
            ```python
            # Direct initialization
            client = KoboClient(
                server_url="https://kobo.example.com",
                token="your-api-token",
                cache=True,
                cache_ttl=3600
            )
            
            # Using environment variables
            os.environ['URL'] = "https://kobo.example.com"
            os.environ['TOKEN'] = "your-api-token"
            client = KoboClient()
            ```
        """
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
        self.cache_enabled: bool = cache
        self.headers: Mapping[str, str] = {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json",
            "User-Agent": "KoboClient/1.0",
        }
        self.session: requests.Session = self._make_session(
            cache=cache, cache_ttl=cache_ttl
        )

    def _make_session(
        self, cache: bool = True, cache_ttl: int = 3600
    ) -> requests.Session:
        """Create a requests session with the necessary headers and configuration.
        
        Sets up a session with authentication headers, retry logic, and optional
        caching for improved performance and reliability.
        
        Args:
            cache: Whether to create a cached session. Defaults to True.
            cache_ttl: Cache time-to-live in seconds. Defaults to 3600.
        
        Returns:
            A configured requests.Session or requests_cache.CachedSession.
        """
        if cache:
            session = requests_cache.CachedSession(
                "kobo_cache",
                expire_after=cache_ttl,
                allowable_codes=(
                    200,
                    404,
                ),  # Cache 404s to avoid repeated failed requests
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

    def _get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Perform a GET request to the KoBoToolbox API.
        
        This is a helper method that constructs the full URL, performs the request,
        and handles error checking.
        
        Args:
            path: The API endpoint path (relative to server_url).
            **kwargs: Additional keyword arguments passed to requests.get().
        
        Returns:
            The JSON response as a dictionary.
        
        Raises:
            requests.HTTPError: If the HTTP request fails.
            requests.RequestException: If a network error occurs.
        """
        url = urljoin(f"{self.server_url}/", path.lstrip("/"))
        logger.debug(f"GET request to {url}")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def clear_cache(self) -> None:
        """Clear the entire request cache.
        
        This method clears all cached responses if caching is enabled.
        Has no effect if caching is disabled.
        
        Example:
            ```python
            client = KoboClient(cache=True)
            # ... make some requests ...
            client.clear_cache()  # Clear all cached responses
            ```
        """
        if self.cache_enabled and hasattr(self.session, "cache"):
            assert isinstance(self.session, requests_cache.CachedSession)
            self.session.cache.clear()
            logger.info("Cache cleared")

    def ping(self) -> bool:
        """Check if the KoBoToolbox server is reachable and accessible.
        
        This method attempts to connect to the server using the configured
        credentials to verify the connection is working.
        
        Returns:
            True if the server is reachable and authentication is valid,
            False otherwise.
        
        Example:
            ```python
            client = KoboClient(server_url="https://kobo.example.com", token="token")
            
            if client.ping():
                print("Successfully connected to KoBoToolbox")
            else:
                print("Failed to connect - check credentials and URL")
            ```
        """
        try:
            response = self.session.get(
                urljoin(f"{self.server_url}/", "api/v2/assets/hash"),
                headers=self.headers,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_assets(self) -> list[dict[str, Any]]:
        """Retrieve a list of all assets (forms) from the KoBoToolbox server.
        
        Assets represent forms, surveys, or other data collection instruments
        in KoBoToolbox.
        
        Returns:
            A list of dictionaries, each representing an asset. Each dictionary
            contains asset metadata such as 'uid', 'name', 'asset_type', 
            'date_created', 'owner__username', etc.
        
        Raises:
            requests.HTTPError: If the API request fails.
            requests.RequestException: If a network error occurs.
        
        Example:
            ```python
            assets = client.get_assets()
            
            for asset in assets:
                print(f"Form: {asset['name']} (ID: {asset['uid']})")
                print(f"Created: {asset['date_created']}")
                print(f"Owner: {asset['owner__username']}")
            ```
        """
        response = self._get("api/v2/assets")
        return response.get("results", [])

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        """Retrieve detailed information about a specific asset.
        
        Args:
            asset_id: The unique identifier (UID) of the asset to retrieve.
        
        Returns:
            A dictionary containing detailed asset information including
            metadata, settings, and form structure.
        
        Raises:
            requests.HTTPError: If the asset is not found or access is denied.
            requests.RequestException: If a network error occurs.
        
        Example:
            ```python
            asset = client.get_asset("a1b2c3d4e5f6g7h8i9j0")
            
            print(f"Asset name: {asset['name']}")
            print(f"Asset type: {asset['asset_type']}")
            print(f"Questions: {len(asset.get('content', {}).get('survey', []))}")
            ```
        """
        return self._get(f"api/v2/assets/{asset_id}")

    def get_asset_data(self, asset_id: str, **kwargs: Any) -> dict[str, Any]:
        """Retrieve submission data from a specific asset (form).
        
        This method fetches the actual survey responses/submissions for a given
        form. Supports various query parameters for filtering and pagination.
        
        Args:
            asset_id: The unique identifier (UID) of the asset.
            **kwargs: Additional query parameters such as:
                - limit: Maximum number of submissions to return
                - offset: Number of submissions to skip 
                - sort: Sort order (JSON string)
                - fields: List of specific fields to include (JSON string)
                - query: Filter submissions (JSON string)
        
        Returns:
            A dictionary containing submission data with keys:
            - 'count': Total number of submissions
            - 'results': List of submission dictionaries
            - 'next': URL for next page (if paginated)
            - 'previous': URL for previous page (if paginated)
        
        Raises:
            requests.HTTPError: If the asset is not found or access is denied.
            requests.RequestException: If a network error occurs.
        
        Example:
            ```python
            # Get all submissions
            data = client.get_asset_data("a1b2c3d4e5f6g7h8i9j0")
            print(f"Total submissions: {data['count']}")
            
            # Get limited submissions with specific fields
            data = client.get_asset_data(
                "a1b2c3d4e5f6g7h8i9j0",
                limit=50,
                fields='["name", "age", "_submission_time"]'
            )
            
            for submission in data['results']:
                print(f"Name: {submission.get('name')}")
                print(f"Submitted: {submission.get('_submission_time')}")
            ```
        """
        return self._get(f"api/v2/assets/{asset_id}/data", **kwargs)

    def get_assets_hash(self) -> str:
        """Retrieve a hash representing the current state of all assets.
        
        This hash can be used to detect changes in the asset collection
        without fetching the full asset list.
        
        Returns:
            A string hash value representing the current state of all assets.
        
        Raises:
            requests.HTTPError: If the API request fails.
            requests.RequestException: If a network error occurs.
        
        Example:
            ```python
            # Get current hash
            current_hash = client.get_assets_hash()
            
            # Later, check if assets have changed
            new_hash = client.get_assets_hash()
            if new_hash != current_hash:
                print("Assets have been modified")
                # Fetch updated asset list
                assets = client.get_assets()
            ```
        """
        response = self._get("api/v2/assets/hash")
        return response.get("hash", "")
