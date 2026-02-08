"""Leads2 resource for Upsales API.

Leads v2 endpoint with enhanced data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class Leads2Resource:
    """Leads v2 endpoint with enhanced data.

    Read-only endpoint at /leads2.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/leads2"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List leads (v2).

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
