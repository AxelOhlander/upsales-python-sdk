"""AdLocations resource for Upsales API.

Engage ad locations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class AdLocationsResource:
    """Engage ad locations.

    Read-only endpoint at /engage/location.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/engage/location"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List ad locations.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
