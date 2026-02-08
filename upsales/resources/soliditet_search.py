"""SoliditetSearch resource for Upsales API.

Soliditet company database search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SoliditetSearchResource:
    """Soliditet company database search.

    Read-only endpoint at /soliditet/search.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/soliditet/search"

    async def search(self, **params: Any) -> dict[str, Any]:
        """Search the Soliditet company database.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
