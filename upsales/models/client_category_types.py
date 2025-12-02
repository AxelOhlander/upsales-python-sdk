"""Client category types models for Upsales API.

This module provides models for managing client category types,
which are used to group and organize client categories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from upsales.validators import NonEmptyStr, PositiveInt


class ClientCategoryTypeUpdateFields(TypedDict, total=False):
    """Available fields for updating a ClientCategoryType.

    Attributes:
        name: Type name (max 255 characters).
    """

    name: str


class ClientCategoryType(BaseModel):
    """Represents a client category type in Upsales.

    Client category types are used to group and organize client categories
    into logical groupings.

    Examples:
        Get a type:

        >>> upsales = Upsales(token="...")
        >>> cat_type = await upsales.client_category_types.get(1)
        >>> print(cat_type.name)
        'Industry Classification'

        Update a type:

        >>> await cat_type.edit(name="Market Segments")

        Create a new type:

        >>> new_type = await upsales.client_category_types.create(
        ...     name="Regional Groups"
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique identifier for the type")

    # Updatable fields
    name: NonEmptyStr = Field(description="Type name (max 255 characters)", max_length=255)

    async def edit(self, **kwargs: Unpack[ClientCategoryTypeUpdateFields]) -> ClientCategoryType:
        """Edit this client category type with the provided field updates.

        Args:
            **kwargs: Field updates (name).

        Returns:
            Updated ClientCategoryType instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update type name:

            >>> cat_type = await upsales.client_category_types.get(1)
            >>> updated = await cat_type.edit(name="New Classification")
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.client_category_types.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialClientCategoryType(PartialModel):
    """Partial client category type model for nested responses.

    This model is used when client category types appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> category = await upsales.client_categories.get(1)
        >>> if category.categoryType:
        ...     print(category.categoryType.name)

        Fetch full type:

        >>> full_type = await partial_type.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    name: NonEmptyStr = Field(description="Type name")

    async def fetch_full(self) -> ClientCategoryType:
        """Fetch the complete client category type object.

        Returns:
            Full ClientCategoryType instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the type doesn't exist.

        Examples:
            >>> partial = PartialClientCategoryType(id=1, name="Industry")
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.client_category_types.get(self.id)

    async def edit(self, **kwargs: Unpack[ClientCategoryTypeUpdateFields]) -> ClientCategoryType:
        """Edit this client category type with the provided field updates.

        Args:
            **kwargs: Field updates (name).

        Returns:
            Updated ClientCategoryType instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialClientCategoryType(id=1, name="Industry")
            >>> updated = await partial.edit(name="Industry Sectors")
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.client_category_types.update(self.id, **kwargs)
