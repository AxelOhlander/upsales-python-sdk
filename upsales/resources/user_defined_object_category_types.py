"""User-defined object category types resource for Upsales API.

Category types for UserDefinedObjectCategories. POST and PUT are disabled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class UserDefinedObjectCategoryTypesResource:
    """Manage UDO category types.

    Endpoint at /userDefinedObjectCategoryTypes. Supports GET by UDO number
    (1-4) and DELETE.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/userDefinedObjectCategoryTypes"

    async def list(self, nr: int, **params: Any) -> dict[str, Any]:
        """List category types for a UDO number.

        Args:
            nr: UDO number (1, 2, 3, or 4).
            **params: Query parameters for filtering.

        Returns:
            API response with category type data (id, name).
        """
        return await self._http.get(f"{self._endpoint}/{nr}", **params)

    async def delete(self, category_type_id: int) -> dict[str, Any]:
        """Delete a category type.

        Args:
            category_type_id: Category type ID to delete.

        Returns:
            API response data.
        """
        return await self._http.delete(f"{self._endpoint}/{category_type_id}")
