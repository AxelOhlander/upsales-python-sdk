"""Product categories resource manager for Upsales API.

This module provides the resource manager for product category operations with
hierarchical support.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.product_categories import (
    PartialProductCategory,
    ProductCategory,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ProductCategoriesResource(BaseResource[ProductCategory, PartialProductCategory]):
    """Resource manager for product category operations.

    Handles all product category-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Hierarchical operations

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create category
        >>> category = await upsales.product_categories.create(
        ...     name="Electronics",
        ...     parentId=0
        ... )
        >>>
        >>> # Create subcategory
        >>> subcategory = await upsales.product_categories.create(
        ...     name="Smartphones",
        ...     parentId=category.id
        ... )
        >>>
        >>> # Get category
        >>> category = await upsales.product_categories.get(1)
        >>>
        >>> # List all categories
        >>> categories = await upsales.product_categories.list_all()
        >>>
        >>> # Get root categories
        >>> roots = await upsales.product_categories.get_root_categories()

        Hierarchy operations:

        >>> # Get children of a category
        >>> children = await upsales.product_categories.get_children(category_id=1)
        >>> for child in children:
        ...     print(f"  - {child.name}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the product categories resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/productCategories",
            model_class=ProductCategory,
            partial_class=PartialProductCategory,
        )

    async def get_root_categories(self) -> list[ProductCategory]:
        """Get all root categories (categories with no parent).

        Returns:
            List of root ProductCategory objects.

        Examples:
            >>> roots = await upsales.product_categories.get_root_categories()
            >>> for root in roots:
            ...     print(root.name)
        """
        all_categories: list[ProductCategory] = await self.list_all()
        return [cat for cat in all_categories if cat.is_root]

    async def get_children(self, category_id: int) -> list[ProductCategory]:
        """Get all child categories of a given category.

        Args:
            category_id: ID of the parent category.

        Returns:
            List of child ProductCategory objects.

        Examples:
            >>> children = await upsales.product_categories.get_children(5)
            >>> print(f"Found {len(children)} subcategories")
        """
        all_categories: list[ProductCategory] = await self.list_all()
        return [cat for cat in all_categories if cat.parentId == category_id]

    async def get_by_name(self, name: str) -> ProductCategory | None:
        """Get product category by name.

        Args:
            name: Category name to search for (case-insensitive).

        Returns:
            ProductCategory object if found, None otherwise.

        Examples:
            >>> category = await upsales.product_categories.get_by_name("Electronics")
            >>> if category:
            ...     print(category.id)
        """
        all_categories: list[ProductCategory] = await self.list_all()
        for cat in all_categories:
            if cat.name.lower() == name.lower():
                return cat
        return None
