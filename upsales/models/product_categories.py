"""Product categories models for Upsales API.

This module provides models for managing product categories with hierarchical structure.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, PositiveInt


class ProductCategoryUpdateFields(TypedDict, total=False):
    """Available fields for updating a ProductCategory.

    Attributes:
        name: Category name (max 128 characters).
        parentId: Parent category ID for hierarchy.
        sortId: Sort order.
        inheritRoles: Whether to inherit roles from parent.
        roles: List of role IDs with access.
        orderRowFields: List of custom field IDs for order rows.
        calculatingField: Calculating field configuration.
    """

    name: str
    parentId: int
    sortId: int
    inheritRoles: bool
    roles: list[int]
    orderRowFields: list[int]
    calculatingField: dict[str, Any]


class ProductCategory(BaseModel):
    """Represents a product category in Upsales.

    Product categories support hierarchical organization with parent/child relationships.

    Examples:
        Get a category:

        >>> upsales = Upsales(token="...")
        >>> category = await upsales.product_categories.get(1)
        >>> print(category.name)

        Update a category:

        >>> await category.edit(name="New Category", parentId=5)

        Check if category is root:

        >>> if category.is_root:
        ...     print("Top-level category")
    """

    # Read-only fields
    id: PositiveInt = Field(
        frozen=True, strict=True, description="Unique identifier for the category"
    )
    accessRoles: list[dict[str, Any]] = Field(
        default_factory=list, frozen=True, description="Computed access roles"
    )
    userUsable: BinaryFlag = Field(
        default=1, frozen=True, description="Whether category is usable (0=no, 1=yes)"
    )

    # Updatable fields
    name: str = Field(description="Category name (max 128 characters)", max_length=128)
    parentId: int | None = Field(
        default=None, description="Parent category ID (0 or null for root)"
    )
    sortId: int = Field(default=0, description="Sort order")
    inheritRoles: bool = Field(
        default=False, description="Whether to inherit roles from parent category"
    )
    roles: list[int] = Field(default_factory=list, description="List of role IDs with access")
    orderRowFields: list[int] = Field(
        default_factory=list, description="Custom field IDs for order rows"
    )
    calculatingField: dict[str, Any] | None = Field(
        default=None, description="Calculating field configuration"
    )

    @property
    def is_root(self) -> bool:
        """Check if this is a root category (no parent).

        Returns:
            True if category has no parent, False otherwise.

        Examples:
            >>> if category.is_root:
            ...     print("Top-level category")
        """
        return self.parentId is None or self.parentId == 0

    @property
    def has_roles(self) -> bool:
        """Check if category has assigned roles.

        Returns:
            True if category has roles assigned, False otherwise.

        Examples:
            >>> if category.has_roles:
            ...     print(f"Category has {len(category.roles)} roles")
        """
        return len(self.roles) > 0

    async def edit(self, **kwargs: Unpack[ProductCategoryUpdateFields]) -> ProductCategory:
        """Edit this product category with the provided field updates.

        Args:
            **kwargs: Field updates (name, parentId, sortId, etc.).

        Returns:
            Updated ProductCategory instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update category:

            >>> category = await upsales.product_categories.get(1)
            >>> updated = await category.edit(name="Premium Products", parentId=0)
        """
        if not self._client:
            raise RuntimeError("No client available for this category")
        return await self._client.product_categories.update(self.id, **self.to_api_dict(**kwargs))


class PartialProductCategory(PartialModel):
    """Partial product category model for nested responses.

    This model is used when product categories appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> product = await upsales.products.get(1)
        >>> if product.category:
        ...     print(product.category.name)

        Fetch full category:

        >>> full_category = await partial_category.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    name: str = Field(description="Category name")

    async def fetch_full(self) -> ProductCategory:
        """Fetch the complete product category object.

        Returns:
            Full ProductCategory instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the category doesn't exist.

        Examples:
            >>> partial = PartialProductCategory(id=1, name="Electronics")
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this category")
        return await self._client.product_categories.get(self.id)

    async def edit(self, **kwargs: Unpack[ProductCategoryUpdateFields]) -> ProductCategory:
        """Edit this product category with the provided field updates.

        Args:
            **kwargs: Field updates (name, parentId, sortId, etc.).

        Returns:
            Updated ProductCategory instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialProductCategory(id=1, name="Electronics")
            >>> updated = await partial.edit(name="Consumer Electronics")
        """
        if not self._client:
            raise RuntimeError("No client available for this category")
        return await self._client.product_categories.update(self.id, **kwargs)
