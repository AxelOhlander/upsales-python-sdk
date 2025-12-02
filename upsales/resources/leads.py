"""
Leads resource manager for Upsales API.

Provides methods to interact with the /leads endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     lead = await upsales.leads.get(1)
    ...     leads_list = await upsales.leads.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.leads import Lead, PartialLead
from upsales.resources.base import BaseResource


class LeadsResource(BaseResource[Lead, PartialLead]):
    """
    Resource manager for Lead endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single lead
    - list(limit, offset, **params) - List leads with pagination
    - list_all(**params) - Auto-paginated list of all leads
    - update(id, **data) - Update lead
    - delete(id) - Delete lead
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = LeadsResource(http_client)
        >>> lead = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize leads resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/leads",
            model_class=Lead,
            partial_class=PartialLead,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Lead]:
    #     """Get all active leads."""
    #     return await self.list_all(active=1)
