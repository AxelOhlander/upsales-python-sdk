"""
HTTP client with rate limiting and retry logic.

Leverages Python 3.13 features:
- Native type hints (no typing imports needed)
- Pattern matching for clean error handling
- Free-threaded mode benefits for parallel requests

Example:
    >>> async with HTTPClient("YOUR_TOKEN") as client:
    ...     data = await client.get("/users/1")
    ...     print(data)

Note:
    With Python 3.13 free-threaded mode, concurrent requests can truly
    run in parallel without GIL contention, maximizing throughput within
    the API rate limits (200 requests per 10 seconds).
"""

from typing import TYPE_CHECKING, Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from upsales.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from upsales.auth import AuthenticationManager


class HTTPClient:
    """
    Async HTTP client with rate limiting and automatic retries.

    Handles authentication, response parsing, and error handling for the
    Upsales API. Automatically retries on rate limit errors (HTTP 429) with
    exponential backoff.

    Args:
        token: Upsales API token for authentication.
        base_url: Base API URL (default: https://power.upsales.com/api/v2).
        max_concurrent: Maximum concurrent requests (default: 50).

    Attributes:
        token: API authentication token.
        base_url: Base URL for all API requests.
        max_concurrent: Maximum number of concurrent requests allowed.

    Example:
        >>> async with HTTPClient("token") as client:
        ...     # Single request
        ...     user = await client.get("/users/1")
        ...
        ...     # Update request
        ...     updated = await client.put("/users/1", name="New Name")
        ...
        ...     # Delete request
        ...     await client.delete("/users/1")

    Note:
        With Python 3.13 free-threaded mode, concurrent requests made through
        this client can achieve true parallelism without GIL contention, allowing
        you to maximize throughput within the 200 req/10 sec rate limit.
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://power.upsales.com/api/v2",
        max_concurrent: int = 50,
        auth_manager: "AuthenticationManager | None" = None,
        upsales_client: Any = None,  # Reference to parent Upsales instance
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            token: Upsales API token.
            base_url: Base API URL.
            max_concurrent: Max concurrent requests.
            auth_manager: Optional authentication manager for token refresh.
            upsales_client: Parent Upsales instance (for model._client reference).
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.max_concurrent = max_concurrent
        self.auth_manager = auth_manager
        self._upsales_client = upsales_client  # Parent Upsales instance
        self._client: httpx.AsyncClient | None = None
        self._auth_refresh_attempted = False
        # Marker used by resources to know when temporary sessions are allowed.
        self._auto_allow_uninitialized = True

    async def __aenter__(self) -> "HTTPClient":
        """
        Initialize httpx client when entering async context.

        Returns:
            Self for context manager usage.
        """
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Cookie": f"token={self.token}"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Close httpx client when exiting async context."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def close(self) -> None:
        """Close the HTTP client explicitly."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _update_token(self, new_token: str) -> None:
        """
        Update token and recreate httpx client.

        Args:
            new_token: New API token to use.
        """
        self.token = new_token
        if self._client:
            await self._client.aclose()
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Cookie": f"token={new_token}"},
                timeout=30.0,
            )

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=60),
    )
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Make HTTP request with automatic retry on rate limits and token refresh.

        Uses pattern matching (Python 3.10+) for clean error handling based
        on HTTP status codes. Automatically retries on rate limit errors
        with exponential backoff.

        If authentication fails (401/403) and fallback authentication is enabled,
        automatically refreshes the token using username/password and retries once.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (without base URL).
            **kwargs: Additional arguments passed to httpx.

        Returns:
            Parsed response data from the API.

        Raises:
            RateLimitError: When rate limit exceeded (retries automatically).
            AuthenticationError: When authentication fails (HTTP 401/403).
            NotFoundError: When resource not found (HTTP 404).
            ValidationError: When request validation fails (HTTP 400).
            ServerError: When server error occurs (HTTP 500+).
            RuntimeError: If client not initialized with async context.

        Example:
            >>> data = await client.request("GET", "/users/1")
            >>> updated = await client.request(
            ...     "PUT",
            ...     "/users/1",
            ...     json={"name": "New Name"}
            ... )

        Note:
            Automatic token refresh is only attempted once per request to avoid
            infinite loops. If the refreshed token also fails, AuthenticationError
            is raised.
        """
        created_temp_client = False
        allow_temp = kwargs.pop("_allow_uninitialized", False)
        if not self._client:
            if not allow_temp:
                raise RuntimeError("HTTP client not initialized. Use 'async with' context.")
            await self.__aenter__()
            created_temp_client = True

        try:
            path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
            response = await self._client.request(method, path, **kwargs)

            # Pattern matching for clean error handling (Python 3.10+)
            match response.status_code:
                case 200 | 201:
                    pass  # Success - continue to parse response
                case 400:
                    raise ValidationError(f"Validation failed: {response.text}")
                case 401 | 403:
                    # Attempt token refresh if enabled and not already attempted
                    if (
                        self.auth_manager
                        and self.auth_manager.should_retry_with_refresh()
                        and not self._auth_refresh_attempted
                    ):
                        # Mark that we're attempting refresh to avoid infinite loops
                        self._auth_refresh_attempted = True

                        try:
                            # Refresh token
                            new_token = await self.auth_manager.refresh_token()

                            # Update client with new token
                            await self._update_token(new_token)

                            # Retry the request with new token
                            response = await self._client.request(method, endpoint, **kwargs)

                            # Reset flag on success
                            self._auth_refresh_attempted = False

                            # Check if retry succeeded
                            if response.status_code not in (200, 201):
                                raise AuthenticationError(
                                    f"Authentication failed even after token refresh: {response.text}"
                                )

                        except Exception as e:
                            # Reset flag
                            self._auth_refresh_attempted = False

                            # Re-raise if it's already an AuthenticationError
                            if isinstance(e, AuthenticationError):
                                raise

                            # Wrap other errors
                            raise AuthenticationError(f"Token refresh failed: {e}") from e
                    else:
                        raise AuthenticationError(f"Authentication failed: {response.text}")
                case 404:
                    raise NotFoundError(f"Resource not found: {endpoint}")
                case 429:
                    raise RateLimitError("Rate limit exceeded (200 req/10 sec)")
                case code if code >= 500:
                    raise ServerError(f"Server error {code}: {response.text}")
                case _:
                    # Fallback for any other status codes
                    response.raise_for_status()

            # Parse Upsales API response wrapper
            data: dict[str, Any] = response.json()
            if data.get("error"):
                raise ValidationError(f"API error: {data['error']}")

            return data
        finally:
            if created_temp_client:
                await self.__aexit__(None, None, None)

    async def get(
        self,
        endpoint: str,
        _allow_uninitialized: bool = False,
        **params: Any,
    ) -> dict[str, Any]:
        """
        Make GET request.

        Args:
            endpoint: API endpoint path.
            **params: Query parameters.

        Returns:
            Response data.

        Example:
            >>> users = await client.get("/users", limit=100, offset=0)
        """
        return await self.request(
            "GET",
            endpoint,
            _allow_uninitialized=_allow_uninitialized,
            params=params,
        )

    async def post(
        self,
        endpoint: str,
        _allow_uninitialized: bool = False,
        **data: Any,
    ) -> dict[str, Any]:
        """
        Make POST request.

        Args:
            endpoint: API endpoint path.
            **data: Request body data.

        Returns:
            Response data.

        Example:
            >>> user = await client.post("/users", name="John", email="john@example.com")
        """
        return await self.request(
            "POST",
            endpoint,
            _allow_uninitialized=_allow_uninitialized,
            json=data,
        )

    async def put(
        self,
        endpoint: str,
        _allow_uninitialized: bool = False,
        **data: Any,
    ) -> dict[str, Any]:
        """
        Make PUT request.

        Args:
            endpoint: API endpoint path.
            **data: Request body data.

        Returns:
            Response data.

        Example:
            >>> user = await client.put("/users/1", name="Jane")
        """
        return await self.request(
            "PUT",
            endpoint,
            _allow_uninitialized=_allow_uninitialized,
            json=data,
        )

    async def delete(
        self,
        endpoint: str,
        _allow_uninitialized: bool = False,
    ) -> dict[str, Any]:
        """
        Make DELETE request.

        Args:
            endpoint: API endpoint path.

        Returns:
            Response data.

        Example:
            >>> await client.delete("/users/1")
        """
        return await self.request(
            "DELETE",
            endpoint,
            _allow_uninitialized=_allow_uninitialized,
        )
