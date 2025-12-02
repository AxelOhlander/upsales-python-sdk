"""Ticket types resource manager for Upsales API.

This module provides the resource manager for ticket type operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.ticket_types import PartialTicketType, TicketType
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class TicketTypesResource(BaseResource[TicketType, PartialTicketType]):
    """Resource manager for ticket type operations.

    Handles all ticket type-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Default type management

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create type
        >>> ticket_type = await upsales.ticket_types.create(
        ...     name="Bug",
        ...     isDefault=False
        ... )
        >>>
        >>> # Get type
        >>> ticket_type = await upsales.ticket_types.get(1)
        >>>
        >>> # List all types
        >>> types = await upsales.ticket_types.list_all()
        >>>
        >>> # Update type
        >>> updated = await upsales.ticket_types.update(
        ...     1, name="Critical Bug", isDefault=True
        ... )
        >>>
        >>> # Delete type
        >>> await upsales.ticket_types.delete(1)

        Query operations:

        >>> # Get default type
        >>> default_type = await upsales.ticket_types.get_default_type()
        >>> if default_type:
        ...     print(f"Default: {default_type.name}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the ticket types resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/ticketType",
            model_class=TicketType,
            partial_class=PartialTicketType,
        )

    async def get_by_name(self, name: str) -> TicketType | None:
        """Get ticket type by name.

        Args:
            name: Type name to search for (case-insensitive).

        Returns:
            TicketType object if found, None otherwise.

        Examples:
            >>> ticket_type = await upsales.ticket_types.get_by_name("Bug")
            >>> if ticket_type:
            ...     print(ticket_type.id)
        """
        all_types: list[TicketType] = await self.list_all()
        for ticket_type in all_types:
            if ticket_type.name.lower() == name.lower():
                return ticket_type
        return None

    async def get_default_type(self) -> TicketType | None:
        """Get the default ticket type.

        Returns:
            TicketType object marked as default, or None if no default is set.

        Examples:
            >>> default_type = await upsales.ticket_types.get_default_type()
            >>> if default_type:
            ...     print(f"Default type: {default_type.name}")
        """
        all_types: list[TicketType] = await self.list_all()
        for ticket_type in all_types:
            if ticket_type.isDefault:
                return ticket_type
        return None
