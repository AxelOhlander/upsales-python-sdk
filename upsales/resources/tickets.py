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
