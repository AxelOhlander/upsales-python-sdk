"""Contact category types resource for Upsales API.

Category type definitions for contact categories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ContactCategoryTypesResource:
    """Manage contact category types.

    Endpoint at /contactCategoryTypes.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/contactCategoryTypes"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List contact category types.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response with category type data.
        """
        return await self._http.get(self._endpoint, **params)

    async def get(self, type_id: int) -> dict[str, Any]:
        """Get a specific contact category type.

        Args:
            type_id: Category type ID.

        Returns:
            Category type data.
        """
        return await self._http.get(f"{self._endpoint}/{type_id}")
