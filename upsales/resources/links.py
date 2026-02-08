"""Links resource for Upsales API.

Link tracking data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LinksResource:
    """Link tracking data.

    Read-only endpoint at /links.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/links"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List tracked links.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
