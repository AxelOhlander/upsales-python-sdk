"""
Tickets resource manager for Upsales API.

Provides methods to interact with the /tickets endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     ticket = await upsales.tickets.get(1)
    ...     tickets_list = await upsales.tickets.list(limit=10)
"""

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

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Ticket]:
    #     """Get all active tickets."""
    #     return await self.list_all(active=1)
