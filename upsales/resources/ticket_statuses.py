"""Ticket statuses resource manager for Upsales API.

This module provides the resource manager for ticket status operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.ticket_statuses import PartialTicketStatus, TicketStatus
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class TicketStatusesResource(BaseResource[TicketStatus, PartialTicketStatus]):
    """Resource manager for ticket status operations.

    Handles all ticket status-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Status queries

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create status
        >>> status = await upsales.ticket_statuses.create(
        ...     name="In Progress",
        ...     closed=False
        ... )
        >>>
        >>> # Get status
        >>> status = await upsales.ticket_statuses.get(1)
        >>>
        >>> # List all statuses
        >>> statuses = await upsales.ticket_statuses.list_all()
        >>>
        >>> # Update status
        >>> updated = await upsales.ticket_statuses.update(
        ...     1, name="Resolved", closed=True
        ... )
        >>>
        >>> # Delete status
        >>> await upsales.ticket_statuses.delete(1)

        Query operations:

        >>> # Get all open statuses
        >>> open_statuses = await upsales.ticket_statuses.get_open_statuses()
        >>>
        >>> # Get all closed statuses
        >>> closed_statuses = await upsales.ticket_statuses.get_closed_statuses()
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the ticket statuses resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/ticketStatus",
            model_class=TicketStatus,
            partial_class=PartialTicketStatus,
        )

    async def get_by_name(self, name: str) -> TicketStatus | None:
        """Get ticket status by name.

        Args:
            name: Status name to search for (case-insensitive).

        Returns:
            TicketStatus object if found, None otherwise.

        Examples:
            >>> status = await upsales.ticket_statuses.get_by_name("Open")
            >>> if status:
            ...     print(status.id)
        """
        all_statuses: list[TicketStatus] = await self.list_all()
        for status in all_statuses:
            if status.name.lower() == name.lower():
                return status
        return None

    async def get_open_statuses(self) -> list[TicketStatus]:
        """Get all statuses that indicate open tickets.

        Returns:
            List of TicketStatus objects where closed=False.

        Examples:
            >>> open_statuses = await upsales.ticket_statuses.get_open_statuses()
            >>> for status in open_statuses:
            ...     print(status.name)
        """
        all_statuses: list[TicketStatus] = await self.list_all()
        return [status for status in all_statuses if not status.closed]

    async def get_closed_statuses(self) -> list[TicketStatus]:
        """Get all statuses that indicate closed tickets.

        Returns:
            List of TicketStatus objects where closed=True.

        Examples:
            >>> closed_statuses = await upsales.ticket_statuses.get_closed_statuses()
            >>> for status in closed_statuses:
            ...     print(status.name)
        """
        all_statuses: list[TicketStatus] = await self.list_all()
        return [status for status in all_statuses if status.closed]
