"""Client category types resource manager for Upsales API.

This module provides the resource manager for client category type operations,
including CRUD operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.client_category_types import (
    ClientCategoryType,
    PartialClientCategoryType,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ClientCategoryTypesResource(BaseResource[ClientCategoryType, PartialClientCategoryType]):
    """Resource manager for client category type operations.

    Handles all client category type-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Bulk operations

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create type
        >>> cat_type = await upsales.client_category_types.create(
        ...     name="Industry Classification"
        ... )
        >>>
        >>> # Get type
        >>> cat_type = await upsales.client_category_types.get(1)
        >>>
        >>> # List all types
        >>> types = await upsales.client_category_types.list_all()
        >>>
        >>> # Update type
        >>> updated = await upsales.client_category_types.update(
        ...     1, name="Market Segments"
        ... )
        >>>
        >>> # Delete type
        >>> await upsales.client_category_types.delete(1)

        Search by name:

        >>> industry_type = await upsales.client_category_types.get_by_name(
        ...     "Industry Classification"
        ... )
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the client category types resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/clientCategoryTypes",
            model_class=ClientCategoryType,
            partial_class=PartialClientCategoryType,
        )

    async def get_by_name(self, name: str) -> ClientCategoryType | None:
        """Get client category type by name.

        Args:
            name: Type name to search for (case-insensitive).

        Returns:
            ClientCategoryType object if found, None otherwise.

        Examples:
            >>> cat_type = await upsales.client_category_types.get_by_name(
            ...     "Industry Classification"
            ... )
            >>> if cat_type:
            ...     print(cat_type.id)
        """
        all_types: list[ClientCategoryType] = await self.list_all()
        for cat_type in all_types:
            if cat_type.name.lower() == name.lower():
                return cat_type
        return None
