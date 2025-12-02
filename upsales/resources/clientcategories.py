"""
Client Categories resource manager for Upsales API.

Provides methods to interact with the /client_categories endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     category = await upsales.client_categories.get(1)
    ...     categories = await upsales.client_categories.list(limit=10)
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.client_categories import ClientCategory, PartialClientCategory
from upsales.resources.base import BaseResource


class ClientCategoriesResource(BaseResource[ClientCategory, PartialClientCategory]):
    """
    Resource manager for ClientCategory endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single client category
    - list(limit, offset, **params) - List categories with pagination
    - list_all(**params) - Auto-paginated list of all categories
    - create(**data) - Create new client category
    - update(id, **data) - Update client category
    - delete(id) - Delete client category
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> categories = ClientCategoriesResource(http_client)
        >>> category = await categories.get(1)
        >>> all_with_roles = await categories.get_with_roles()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize client categories resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/clientcategories",
            model_class=ClientCategory,
            partial_class=PartialClientCategory,
        )

    async def get_by_name(self, name: str) -> ClientCategory | None:
        """
        Get client category by name.

        Args:
            name: Category name to search for.

        Returns:
            ClientCategory object if found, None otherwise.

        Example:
            >>> category = await upsales.client_categories.get_by_name("Övrigt")
            >>> if category:
            ...     print(category.id)
        """
        all_categories: list[ClientCategory] = await self.list_all()
        for category in all_categories:
            if category.name.lower() == name.lower():
                return category
        return None

    async def get_with_roles(self) -> list[ClientCategory]:
        """
        Get all categories that have associated roles.

        Returns:
            List of categories with roles assigned.

        Example:
            >>> categories_with_roles = await upsales.client_categories.get_with_roles()
            >>> for category in categories_with_roles:
            ...     print(f"{category.name} has {category.role_count} roles")
        """
        all_categories: list[ClientCategory] = await self.list_all()
        return [category for category in all_categories if category.has_roles]

    async def get_by_type(self, category_type: int) -> list[ClientCategory]:
        """
        Get all categories with specified type.

        Args:
            category_type: Category type identifier to filter by.

        Returns:
            List of categories with matching categoryType.

        Example:
            >>> type_zero = await upsales.client_categories.get_by_type(0)
            >>> for category in type_zero:
            ...     print(f"{category.name} is type 0")
        """
        all_categories: list[ClientCategory] = await self.list_all()
        return [category for category in all_categories if category.categoryType == category_type]

    async def merge(
        self, from_id: int, to_id: int, category_type: int, name: str | None = None
    ) -> dict[str, Any]:
        """
        Merge one category into another.

        This operation combines two categories, moving all associations
        from the source category to the target category.

        Args:
            from_id: ID of the category to merge from (will be removed).
            to_id: ID of the category to merge into (will remain).
            category_type: Category type ID for the merged category.
            name: Optional new name for the merged category.

        Returns:
            API response with merge result.

        Raises:
            NotFoundError: If either category doesn't exist.
            ValidationError: If merge operation is invalid.

        Example:
            >>> result = await upsales.client_categories.merge(
            ...     from_id=5,
            ...     to_id=3,
            ...     category_type=1,
            ...     name="Merged Enterprise Category"
            ... )
        """
        data: dict[str, Any] = {
            "from": from_id,
            "to": to_id,
            "categoryType": category_type,
        }
        if name:
            data["name"] = name

        response = await self._http.post(f"{self._endpoint}/merge", json=data)
        return response
