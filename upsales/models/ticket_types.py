"""Ticket type models for Upsales API.

This module provides models for managing ticket type categories.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr, PositiveInt


class TicketTypeUpdateFields(TypedDict, total=False):
    """Available fields for updating a TicketType.

    Attributes:
        name: Type name (max 128 characters).
        isDefault: Whether this is the default ticket type.
    """

    name: str
    isDefault: bool


class TicketType(BaseModel):
    """Represents a ticket type category in Upsales.

    Ticket types define categories for classifying tickets,
    such as "Bug", "Feature Request", "Support", etc.

    Examples:
        Get a type:

        >>> upsales = Upsales(token="...")
        >>> ticket_type = await upsales.ticket_types.get(1)
        >>> print(f"{ticket_type.name} (Default: {ticket_type.is_default})")

        Update a type:

        >>> await ticket_type.edit(name="Critical Bug", isDefault=False)

        Create a new type:

        >>> ticket_type = await upsales.ticket_types.create(
        ...     name="Feature Request",
        ...     isDefault=False
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique identifier for the type")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Last modification date")
    regBy: dict[str, Any] | None = Field(None, frozen=True, description="Created by user")
    modBy: dict[str, Any] | None = Field(None, frozen=True, description="Last modified by user")

    # Updatable fields
    name: NonEmptyStr = Field(description="Type name (max 128 characters)", max_length=128)
    isDefault: bool = Field(default=False, description="Whether this is the default ticket type")

    @property
    def is_default(self) -> bool:
        """Check if this is the default ticket type.

        Returns:
            True if this is the default type, False otherwise.

        Examples:
            >>> if ticket_type.is_default:
            ...     print("This is the default type")
        """
        return self.isDefault

    async def edit(self, **kwargs: Unpack[TicketTypeUpdateFields]) -> TicketType:
        """Edit this ticket type with the provided field updates.

        Args:
            **kwargs: Field updates (name, isDefault).

        Returns:
            Updated TicketType instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update type:

            >>> ticket_type = await upsales.ticket_types.get(1)
            >>> updated = await ticket_type.edit(name="Urgent Issue", isDefault=True)
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.ticket_types.update(self.id, **self.to_api_dict(**kwargs))


class PartialTicketType(PartialModel):
    """Partial ticket type model for nested responses.

    This model is used when ticket types appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> ticket = await upsales.tickets.get(1)
        >>> if ticket.type:
        ...     print(ticket.type.name)

        Fetch full type:

        >>> full_type = await partial_type.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    name: NonEmptyStr = Field(description="Type name")

    async def fetch_full(self) -> TicketType:
        """Fetch the complete ticket type object.

        Returns:
            Full TicketType instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the type doesn't exist.

        Examples:
            >>> partial = PartialTicketType(id=1, name="Bug")
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.ticket_types.get(self.id)

    async def edit(self, **kwargs: Unpack[TicketTypeUpdateFields]) -> TicketType:
        """Edit this ticket type with the provided field updates.

        Args:
            **kwargs: Field updates (name, isDefault).

        Returns:
            Updated TicketType instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialTicketType(id=1, name="Bug")
            >>> updated = await partial.edit(name="Critical Bug")
        """
        if not self._client:
            raise RuntimeError("No client available for this type")
        return await self._client.ticket_types.update(self.id, **kwargs)
