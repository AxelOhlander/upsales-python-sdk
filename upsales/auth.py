"""
Authentication module for Upsales API.

Handles token management and automatic refresh via username/password fallback.

Uses Python 3.13 features:
- Native type hints
- Pattern matching for response handling
"""

import asyncio
import time

import httpx


class AuthenticationManager:
    """
    Manages authentication tokens with automatic refresh fallback.

    Handles the scenario where API tokens expire (e.g., sandbox resets)
    and automatically refreshes them using username/password credentials.

    Args:
        token: Initial API token.
        email: Email for fallback authentication (optional).
        password: Password for fallback authentication (optional).
        enable_fallback: Whether to enable automatic token refresh (default: False).
        base_url: Base API URL.

    Attributes:
        token: Current active API token.
        email: Email for fallback authentication.
        password: Password for fallback authentication.
        enable_fallback: Whether fallback authentication is enabled.
        base_url: Base URL for API requests.

    Example:
        >>> auth = AuthenticationManager(
        ...     token="old_token",
        ...     email="user@email.com",
        ...     password="password",
        ...     enable_fallback=True
        ... )
        >>>
        >>> # When token expires, automatically refreshes
        >>> new_token = await auth.refresh_token()

    Note:
        Fallback authentication is primarily intended for sandbox environments
        that reset daily. Production environments should use permanent API tokens.
    """

    def __init__(
        self,
        token: str,
        email: str | None = None,
        password: str | None = None,
        enable_fallback: bool = False,
        base_url: str = "https://power.upsales.com/api/v2",
    ) -> None:
        """
        Initialize authentication manager.

        Args:
            token: Initial API token.
            email: Email for fallback auth.
            password: Password for fallback auth.
            enable_fallback: Enable automatic token refresh.
            base_url: Base API URL.
        """
        self.token = token
        self.email = email
        self.password = password
        self.enable_fallback = enable_fallback
        self.base_url = base_url.rstrip("/")
        self._refresh_lock = asyncio.Lock()
        self._last_refresh_time: float = 0
        self._refresh_debounce: float = 1.0  # 1 second

    async def refresh_token(self) -> str:
        """
        Refresh API token using username/password.

        Makes a POST request to /session/ endpoint to get a new token.
        Uses a lock to serialize concurrent refresh attempts and a debounce
        period to prevent multiple API calls when the token was recently refreshed.

        Returns:
            New API token.

        Raises:
            ValueError: If email or password not provided.
            RuntimeError: If login request fails.

        Example:
            >>> auth = AuthenticationManager(
            ...     token="old",
            ...     email="user@email.com",
            ...     password="pass",
            ...     enable_fallback=True
            ... )
            >>> new_token = await auth.refresh_token()

        Note:
            When multiple coroutines call this method concurrently, the lock
            ensures they are serialized. The second caller will check if the
            token was recently refreshed (within debounce period) and return
            the current token without making another API call.
        """
        if not self.email or not self.password:
            raise ValueError(
                "Email and password required for token refresh. "
                "Set UPSALES_EMAIL and UPSALES_PASSWORD in .env file."
            )

        # Use lock to prevent multiple simultaneous refresh attempts
        async with self._refresh_lock:
            # Check if we recently refreshed (within debounce period)
            # This prevents the second concurrent call from making another API request
            if time.time() - self._last_refresh_time < self._refresh_debounce:
                return self.token

            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                try:
                    response = await client.post(
                        "/session/",
                        json={
                            "email": self.email,
                            "password": self.password,
                            "samlBypass": None,
                        },
                    )

                    # Pattern matching for response handling
                    match response.status_code:
                        case 200:
                            data = response.json()
                            new_token: str = data["data"]["token"]
                            self.token = new_token
                            # Record the actual refresh completion time so
                            # concurrent callers skip issuing another request.
                            self._last_refresh_time = time.time()
                            return new_token
                        case 401:
                            raise RuntimeError(
                                "Invalid email or password. Check UPSALES_EMAIL and "
                                "UPSALES_PASSWORD in .env file."
                            )
                        case _:
                            raise RuntimeError(
                                f"Token refresh failed with status {response.status_code}: "
                                f"{response.text}"
                            )

                except httpx.RequestError as e:
                    raise RuntimeError(f"Token refresh request failed: {e}") from e

    def get_token(self) -> str:
        """
        Get current token.

        Returns:
            Current API token.
        """
        return self.token

    def should_retry_with_refresh(self) -> bool:
        """
        Check if token refresh should be attempted on auth failure.

        Returns:
            True if fallback authentication is enabled and credentials are available.
        """
        return self.enable_fallback and self.email is not None and self.password is not None

    def __repr__(self) -> str:
        """String representation."""
        status = "with fallback" if self.enable_fallback else "no fallback"
        return f"<AuthenticationManager {status}>"
