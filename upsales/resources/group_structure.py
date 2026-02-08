"""GroupStructure resource for Upsales API.

Prospecting group structure data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class GroupStructureResource:
    """Prospecting group structure data.

    Read-only endpoint at /prospectinggroupstructure.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/prospectinggroupstructure"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List group structure data.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
