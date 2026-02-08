"""Contact categories resource for Upsales API.

Categories for organizing contacts. Same structure as client categories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ContactCategoriesResource:
    """Manage contact categories.

    Endpoint at /contactcategories. Mirrors the client categories structure.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/contactcategories"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List contact categories.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response with category data.
        """
        return await self._http.get(self._endpoint, **params)

    async def get(self, category_id: int) -> dict[str, Any]:
        """Get a specific contact category.

        Args:
            category_id: Category ID.

        Returns:
            Category data.
        """
        return await self._http.get(f"{self._endpoint}/{category_id}")
