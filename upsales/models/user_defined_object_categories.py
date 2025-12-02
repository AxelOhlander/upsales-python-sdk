"""User Defined Object Categories models for the Upsales API.

This module provides Pydantic models for working with User Defined Object Categories,
which are used to organize and categorize UserDefinedObjects (1-4 variants).
"""

from __future__ import annotations

from typing import TypedDict, Unpack

from pydantic import Field, field_validator

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr, PositiveInt


class UserDefinedObjectCategoryUpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObjectCategory.

    All fields are optional for updates.

    Attributes:
        name: Category name (max 64 characters)
        categoryTypeId: Category type identifier
    """

    name: str
    categoryTypeId: int


class UserDefinedObjectCategory(BaseModel):
    """User Defined Object Category model.

    Represents a category for organizing UserDefinedObjects.

    Attributes:
        id: Unique category identifier (read-only)
        name: Category name
        categoryTypeId: Category type identifier

    Example:
        >>> # Get a category
        >>> category = await upsales.user_defined_object_categories.get(1, nr=1)
        >>> print(category.name)
        'Priority Customers'

        >>> # Update category
        >>> await category.edit(name="VIP Customers")

        >>> # Create new category
        >>> new_cat = await upsales.user_defined_object_categories.create(
        ...     nr=1,
        ...     name="Premium Accounts",
        ...     categoryTypeId=5
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique category identifier")

    # Updatable fields
    name: NonEmptyStr = Field(description="Category name (max 64 characters)")
    categoryTypeId: PositiveInt = Field(description="Category type identifier")

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        """Validate that name does not exceed 64 characters.

        Args:
            v: Name value to validate

        Returns:
            Validated name

        Raises:
            ValueError: If name exceeds 64 characters
        """
        if len(v) > 64:
            raise ValueError("name must not exceed 64 characters")
        return v

    async def edit(
        self, **kwargs: Unpack[UserDefinedObjectCategoryUpdateFields]
    ) -> UserDefinedObjectCategory:
        """Edit this category with partial updates.

        Args:
            **kwargs: Fields to update (name, categoryTypeId)

        Returns:
            Updated UserDefinedObjectCategory instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> category = await upsales.user_defined_object_categories.get(1, nr=1)
            >>> updated = await category.edit(name="New Category Name")
            >>> print(updated.name)
            'New Category Name'
        """
        if not self._client:
            raise RuntimeError("No client available for edit operation")
        # Note: We need to determine which 'nr' this category belongs to
        # This might require storing nr as an instance variable
        # For now, this will need to be called via the resource manager
        raise NotImplementedError(
            "Direct edit not supported. Use resource manager update() with nr parameter."
        )


class PartialUserDefinedObjectCategory(PartialModel):
    """Partial User Defined Object Category model for nested references.

    Used when categories appear as nested objects in other API responses.

    Attributes:
        id: Unique category identifier
        name: Category name

    Example:
        >>> # In a nested response
        >>> user_defined_obj.category.name  # Access partial data
        'Priority'

        >>> # Fetch full details
        >>> full_category = await user_defined_obj.category.fetch_full(nr=1)
        >>> print(full_category.categoryTypeId)
        5
    """

    id: PositiveInt = Field(description="Unique category identifier")
    name: NonEmptyStr = Field(description="Category name")

    async def fetch_full(self, nr: int) -> UserDefinedObjectCategory:
        """Fetch the complete category data.

        Args:
            nr: UserDefinedObject variant number (1-4)

        Returns:
            Complete UserDefinedObjectCategory instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialUserDefinedObjectCategory(id=1, name="Test")
            >>> full = await partial.fetch_full(nr=1)
            >>> print(full.categoryTypeId)
            5
        """
        if not self._client:
            raise RuntimeError("No client available for fetch operation")
        return await self._client.user_defined_object_categories.get(self.id, nr=nr)

    async def edit(
        self, nr: int, **kwargs: Unpack[UserDefinedObjectCategoryUpdateFields]
    ) -> UserDefinedObjectCategory:
        """Edit this category.

        Args:
            nr: UserDefinedObject variant number (1-4)
            **kwargs: Fields to update

        Returns:
            Updated UserDefinedObjectCategory instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialUserDefinedObjectCategory(id=1, name="Test")
            >>> updated = await partial.edit(nr=1, name="Updated Name")
        """
        if not self._client:
            raise RuntimeError("No client available for edit operation")
        # Merge kwargs with current data
        update_data = self.model_dump(by_alias=True, exclude_unset=True)
        update_data.update(kwargs)
        return await self._client.user_defined_object_categories.update(
            self.id, nr=nr, **update_data
        )


__all__ = [
    "UserDefinedObjectCategory",
    "PartialUserDefinedObjectCategory",
    "UserDefinedObjectCategoryUpdateFields",
]
