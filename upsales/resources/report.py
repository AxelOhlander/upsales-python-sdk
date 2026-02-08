"""Report resource for Upsales API.

Report data for various entity types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ReportResource:
    """Report data for various entity types.

    Read-only endpoint at /report/api.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/report/api"

    async def get(self, entity: str, **params: Any) -> dict[str, Any]:
        """Get report data for an entity type.

        Args:
            entity: Entity type (Client, Contact, Order, etc.).
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(f"{self._endpoint}/{entity}", **params)
