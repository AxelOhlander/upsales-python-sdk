"""LookerExplores resource for Upsales API.

Looker explores listing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LookerExploresResource:
    """Looker explores listing.

    Read-only endpoint at /looker/explores.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/looker/explores"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List available Looker explores.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
