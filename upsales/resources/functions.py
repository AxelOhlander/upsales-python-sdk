"""
Functions resource for utility endpoints.

This module provides access to utility function endpoints in the Upsales API.
These are simple endpoints that return single values or perform utility operations.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FunctionsResource:
    """
    Resource manager for utility function endpoints.

    Provides access to utility functions like IP address lookup.

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     ip = await upsales.functions.whatismyip()
        ...     print(f"Your IP: {ip}")
    """

    def __init__(self, http: "HTTPClient") -> None:
        """
        Initialize functions resource.

        Args:
            http: HTTP client instance for API requests.
        """
        self.http = http

    async def whatismyip(self) -> str:
        """
        Get the IP address of the current API client.

        Returns the IP address from which the API request originates.
        Useful for debugging, logging, or IP-based access control.

        Returns:
            The IP address as a string (e.g., "83.249.76.75").

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> async with Upsales.from_env() as upsales:
            ...     ip = await upsales.functions.whatismyip()
            ...     print(f"API requests from: {ip}")
            API requests from: 83.249.76.75
        """
        response = await self.http.get("/function/whatismyip")
        # Response format: {"error": null, "data": "83.249.76.75"}
        ip: str = response["data"]
        return ip
