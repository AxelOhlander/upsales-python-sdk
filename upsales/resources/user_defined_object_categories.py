"""User Defined Object Categories resource for Upsales API.

This resource handles CRUD operations for categories that organize UserDefinedObjects.
Note that all operations require a 'nr' parameter (1-4) to specify which UserDefinedObject
variant the categories belong to.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from upsales.models.user_defined_object_categories import (
    PartialUserDefinedObjectCategory,
    UserDefinedObjectCategory,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class UserDefinedObjectCategoriesResource(
    BaseResource[UserDefinedObjectCategory, PartialUserDefinedObjectCategory]
):
    """Resource manager for User Defined Object Categories.

    This resource requires a 'nr' parameter (1-4) for all operations to specify
    which UserDefinedObject variant the categories belong to.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create category for UserDefinedObject variant 1
            category = await upsales.user_defined_object_categories.create(
                nr=1,
                name="Priority Customers",
                categoryTypeId=5
            )

            # Get category
            category = await upsales.user_defined_object_categories.get(1, nr=1)

            # List categories for variant 1
            categories = await upsales.user_defined_object_categories.list(nr=1)

            # Update category
            updated = await upsales.user_defined_object_categories.update(
                1,
                nr=1,
                name="VIP Customers"
            )

            # Delete category
            await upsales.user_defined_object_categories.delete(1, nr=1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize User Defined Object Categories resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/userDefinedObjectCategories",
            model_class=UserDefinedObjectCategory,
            partial_class=PartialUserDefinedObjectCategory,
        )
        # Provide easy access to protected attributes for custom methods
        self.http = self._http
        self.endpoint = self._endpoint
        self.model_class = self._model_class
        self.partial_class = self._partial_class

    async def get(self, id: int, nr: int) -> UserDefinedObjectCategory:  # type: ignore[override]
        """Get a single category by ID.

        Args:
            id: Category ID
            nr: UserDefinedObject variant number (1-4)

        Returns:
            UserDefinedObjectCategory instance

        Raises:
            NotFoundError: If category doesn't exist
            ValidationError: If nr is not 1-4

        Example:
            >>> category = await upsales.user_defined_object_categories.get(1, nr=1)
            >>> print(category.name)
            'Priority Customers'
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        response = await self._http.get(f"{self._endpoint}/{nr}/{id}")
        return self._model_class.model_validate(
            response["data"], context={"client": self._http._upsales_client}
        )

    async def list(  # type: ignore[override]
        self,
        nr: int,
        limit: int = 100,
        offset: int = 0,
        **params: Any,
    ) -> list[UserDefinedObjectCategory]:
        """List categories with pagination.

        Args:
            nr: UserDefinedObject variant number (1-4)
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)
            **params: Additional query parameters

        Returns:
            List of UserDefinedObjectCategory instances

        Raises:
            ValidationError: If nr is not 1-4

        Example:
            >>> categories = await upsales.user_defined_object_categories.list(
            ...     nr=1,
            ...     limit=50
            ... )
            >>> for cat in categories:
            ...     print(cat.name)
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        response = await self._http.get(
            f"{self._endpoint}/{nr}",
            limit=limit,
            offset=offset,
            **params,
        )
        return [
            self._model_class.model_validate(item, context={"client": self._http._upsales_client})
            for item in response["data"]
        ]

    async def list_all(self, nr: int, **params: Any) -> list[UserDefinedObjectCategory]:  # type: ignore[override,valid-type]
        """Fetch all categories using automatic pagination.

        Args:
            nr: UserDefinedObject variant number (1-4)
            **params: Additional query parameters

        Returns:
            Complete list of all UserDefinedObjectCategory instances

        Raises:
            ValidationError: If nr is not 1-4

        Example:
            >>> all_categories = await upsales.user_defined_object_categories.list_all(nr=1)
            >>> print(f"Total categories: {len(all_categories)}")
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        all_items: list[UserDefinedObjectCategory] = []
        offset = 0
        limit = 100

        while True:
            batch = await self.list(nr=nr, limit=limit, offset=offset, **params)
            if not batch:
                break
            all_items.extend(batch)
            if len(batch) < limit:
                break
            offset += limit

        return all_items

    async def create(self, nr: int, **data: Any) -> UserDefinedObjectCategory:  # type: ignore[override]
        """Create a new category.

        Args:
            nr: UserDefinedObject variant number (1-4)
            **data: Category data (name, categoryTypeId)

        Returns:
            Created UserDefinedObjectCategory instance

        Raises:
            ValidationError: If data is invalid or nr is not 1-4

        Example:
            >>> category = await upsales.user_defined_object_categories.create(
            ...     nr=1,
            ...     name="Premium Accounts",
            ...     categoryTypeId=5
            ... )
            >>> print(category.id)
            42
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        response = await self._http.post(f"{self._endpoint}/{nr}", **data)
        return self._model_class.model_validate(
            response["data"], context={"client": self._http._upsales_client}
        )

    async def update(self, id: int, nr: int, **data: Any) -> UserDefinedObjectCategory:  # type: ignore[override]
        """Update an existing category.

        Args:
            id: Category ID
            nr: UserDefinedObject variant number (1-4)
            **data: Fields to update (name, categoryTypeId)

        Returns:
            Updated UserDefinedObjectCategory instance

        Raises:
            NotFoundError: If category doesn't exist
            ValidationError: If data is invalid or nr is not 1-4

        Example:
            >>> updated = await upsales.user_defined_object_categories.update(
            ...     1,
            ...     nr=1,
            ...     name="VIP Customers"
            ... )
            >>> print(updated.name)
            'VIP Customers'
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        response = await self._http.put(f"{self._endpoint}/{nr}/{id}", **data)
        return self._model_class.model_validate(
            response["data"], context={"client": self._http._upsales_client}
        )

    async def delete(self, id: int, nr: int) -> None:  # type: ignore[override]
        """Delete a category.

        Args:
            id: Category ID
            nr: UserDefinedObject variant number (1-4)

        Raises:
            NotFoundError: If category doesn't exist
            ValidationError: If nr is not 1-4

        Example:
            >>> await upsales.user_defined_object_categories.delete(1, nr=1)
        """
        if nr not in (1, 2, 3, 4):
            raise ValueError("nr must be 1, 2, 3, or 4")
        await self._http.delete(f"{self._endpoint}/{nr}/{id}")


__all__ = ["UserDefinedObjectCategoriesResource"]
