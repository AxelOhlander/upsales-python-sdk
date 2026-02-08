"""FindProspect resource for Upsales API.

Prospect finder for sales prospecting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FindProspectResource:
    """Prospect finder for sales prospecting.

    Read-only endpoint at /findProspect.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/findProspect"

    async def find(self, **params: Any) -> dict[str, Any]:
        """Find prospects matching criteria.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
