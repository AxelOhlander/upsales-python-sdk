"""
Tickets resource manager for Upsales API.

Provides methods to interact with the /tickets endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     ticket = await upsales.tickets.get(1)
    ...     tickets_list = await upsales.tickets.list(limit=10)
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.tickets import PartialTicket, Ticket
from upsales.resources.base import BaseResource


class TicketsResource(BaseResource[Ticket, PartialTicket]):
    """
    Resource manager for Ticket endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single ticket
    - list(limit, offset, **params) - List tickets with pagination
    - list_all(**params) - Auto-paginated list of all tickets
    - update(id, **data) - Update ticket
    - delete(id) - Delete ticket
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = TicketsResource(http_client)
        >>> ticket = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize tickets resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/tickets",
            model_class=Ticket,
            partial_class=PartialTicket,
        )

    async def update(self, resource_id: int, **data: Any) -> Ticket:
        """
        Update a ticket.

        Note:
            The Upsales tickets API requires the `id` field in the request body
            for updates. Without it, the API creates a new ticket instead of
            updating the existing one.

        Args:
            resource_id: Ticket ID to update.
            **data: Fields to update with new values.

        Returns:
            Updated Ticket object with fresh data from API.

        Raises:
            NotFoundError: If ticket with given ID does not exist.
            ValidationError: If field validation fails.
            AuthenticationError: If authentication fails.

        Example:
            >>> ticket = await upsales.tickets.update(
            ...     1,
            ...     title="Updated title",
            ...     statusId=2
            ... )
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.put(
            f"{self._endpoint}/{resource_id}",
            **request_kwargs,
            id=resource_id,  # Required by Upsales tickets API
            **data,
        )
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def add_comment(
        self,
        ticket_id: int,
        description: str,
        comment_type: str = "public",
        status_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Add a comment to a ticket.

        Comments can be public (sent to customer), internal (support team only),
        or external (sent via external contact).

        Args:
            ticket_id: ID of the ticket to comment on.
            description: The comment text/message.
            comment_type: Comment type - "public", "internal", or "external".
                         Default is "public" which sends email to customer.
            status_id: Optionally update ticket status with the comment.

        Returns:
            API response containing the created comment data.

        Example:
            >>> # Public reply to customer
            >>> await upsales.tickets.add_comment(
            ...     ticket_id=123,
            ...     description="Thank you for contacting us!",
            ...     comment_type="public"
            ... )
            >>>
            >>> # Internal note
            >>> await upsales.tickets.add_comment(
            ...     ticket_id=123,
            ...     description="Escalated to engineering",
            ...     comment_type="internal"
            ... )
            >>>
            >>> # Reply and close ticket
            >>> await upsales.tickets.add_comment(
            ...     ticket_id=123,
            ...     description="Issue resolved!",
            ...     comment_type="public",
            ...     status_id=2  # Closed status ID
            ... )
        """
        data: dict[str, Any] = {
            "description": description,
            "type": comment_type,
        }
        if status_id is not None:
            data["statusId"] = status_id

        request_kwargs = self._prepare_http_kwargs()
        return await self._http.post(
            f"{self._endpoint}/{ticket_id}/comment",
            **request_kwargs,
            **data,
        )

    async def add_internal_note(
        self,
        ticket_id: int,
        description: str,
    ) -> dict[str, Any]:
        """
        Add an internal note to a ticket (not visible to customer).

        Convenience method for adding internal-only comments.

        Args:
            ticket_id: ID of the ticket.
            description: The note text.

        Returns:
            API response containing the created comment data.

        Example:
            >>> await upsales.tickets.add_internal_note(
            ...     ticket_id=123,
            ...     description="Customer called - waiting for callback"
            ... )
        """
        return await self.add_comment(
            ticket_id=ticket_id,
            description=description,
            comment_type="internal",
        )

    async def get_open(self) -> list[Ticket]:
        """
        Get all open tickets.

        Returns:
            List of tickets with open status.

        Example:
            >>> open_tickets = await upsales.tickets.get_open()
        """
        # Status ID 1 is typically "Open" in Upsales
        return await self.list_all(**{"status.closed": 0})

    async def get_by_client(self, client_id: int) -> list[Ticket]:
        """
        Get all tickets for a specific client/company.

        Args:
            client_id: Client/company ID.

        Returns:
            List of tickets for the client.

        Example:
            >>> tickets = await upsales.tickets.get_by_client(456)
        """
        return await self.list_all(**{"client.id": client_id})

    async def get_by_contact(self, contact_id: int) -> list[Ticket]:
        """
        Get all tickets for a specific contact.

        Args:
            contact_id: Contact ID.

        Returns:
            List of tickets for the contact.

        Example:
            >>> tickets = await upsales.tickets.get_by_contact(789)
        """
        return await self.list_all(**{"contact.id": contact_id})
