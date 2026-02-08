"""LookerLooks resource for Upsales API.

Looker looks listing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LookerLooksResource:
    """Looker looks listing.

    Read-only endpoint at /looker/looks.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/looker/looks"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List available Looker looks.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
