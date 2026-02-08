"""StandardIntegrationUser resource for Upsales API.

Standard integration user info.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class StandardIntegrationUserResource:
    """Standard integration user info.

    Read-only endpoint at /standardIntegrationUser.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/standardIntegrationUser"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List standard integration users.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
