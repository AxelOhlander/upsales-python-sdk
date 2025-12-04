"""Ticket status models for Upsales API.

This module provides models for managing ticket status types.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr, PositiveInt  # noqa: TC001


class TicketStatusUpdateFields(TypedDict, total=False):
    """Available fields for updating a TicketStatus.

    Attributes:
        name: Status name (max 128 characters).
        closed: Whether this status indicates a closed ticket.
    """

    name: str
    closed: bool


class TicketStatus(BaseModel):
    """Represents a ticket status type in Upsales.

    Ticket statuses define the lifecycle states that tickets can be in,
    such as "Open", "In Progress", "Resolved", etc.

    Examples:
        Get a status:

        >>> upsales = Upsales(token="...")
        >>> status = await upsales.ticket_statuses.get(1)
        >>> print(f"{status.name}: {'Closed' if status.is_closed else 'Open'}")

        Update a status:

        >>> await status.edit(name="Resolved", closed=True)

        Create a new status:

        >>> status = await upsales.ticket_statuses.create(
        ...     name="Awaiting Customer",
        ...     closed=False
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(
        frozen=True, strict=True, description="Unique identifier for the status"
    )
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Last modification date")
    regBy: dict[str, Any] | int | None = Field(
        None, frozen=True, description="Created by user (dict or 0 if not set)"
    )
    modBy: dict[str, Any] | int | None = Field(
        None, frozen=True, description="Last modified by user (dict or 0 if not set)"
    )

    # Updatable fields
    name: NonEmptyStr = Field(description="Status name (max 128 characters)", max_length=128)
    closed: bool = Field(default=False, description="Whether this status indicates closure")

    @property
    def is_closed(self) -> bool:
        """Check if this status indicates a closed ticket.

        Returns:
            True if status marks tickets as closed, False otherwise.

        Examples:
            >>> if status.is_closed:
            ...     print("Ticket is closed")
        """
        return self.closed

    async def edit(self, **kwargs: Unpack[TicketStatusUpdateFields]) -> TicketStatus:
        """Edit this ticket status with the provided field updates.

        Args:
            **kwargs: Field updates (name, closed).

        Returns:
            Updated TicketStatus instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update status:

            >>> status = await upsales.ticket_statuses.get(1)
            >>> updated = await status.edit(name="Closed - Resolved", closed=True)
        """
        if not self._client:
            raise RuntimeError("No client available for this status")
        return await self._client.ticket_statuses.update(self.id, **self.to_api_dict(**kwargs))


class PartialTicketStatus(PartialModel):
    """Partial ticket status model for nested responses.

    This model is used when ticket statuses appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> ticket = await upsales.tickets.get(1)
        >>> if ticket.status:
        ...     print(ticket.status.name)

        Fetch full status:

        >>> full_status = await partial_status.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    name: NonEmptyStr = Field(description="Status name")

    async def fetch_full(self) -> TicketStatus:
        """Fetch the complete ticket status object.

        Returns:
            Full TicketStatus instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the status doesn't exist.

        Examples:
            >>> partial = PartialTicketStatus(id=1, name="Open")
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this status")
        return await self._client.ticket_statuses.get(self.id)

    async def edit(self, **kwargs: Unpack[TicketStatusUpdateFields]) -> TicketStatus:
        """Edit this ticket status with the provided field updates.

        Args:
            **kwargs: Field updates (name, closed).

        Returns:
            Updated TicketStatus instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialTicketStatus(id=1, name="Open")
            >>> updated = await partial.edit(closed=False)
        """
        if not self._client:
            raise RuntimeError("No client available for this status")
        return await self._client.ticket_statuses.update(self.id, **kwargs)
