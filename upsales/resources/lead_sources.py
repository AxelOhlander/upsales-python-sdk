"""
Lead Sources resource manager for Upsales API.

Provides methods to interact with the /leadsources endpoint.
"""

from upsales.http import HTTPClient
from upsales.models.lead_sources import LeadSource, PartialLeadSource
from upsales.resources.base import BaseResource


class LeadSourcesResource(BaseResource[LeadSource, PartialLeadSource]):
    """
    Resource manager for Lead Sources endpoint.

    Lead sources are typically read-only definitions managed through
    the Upsales UI. This resource provides list and get operations.

    Inherits from BaseResource:
    - get(id) - Get single lead source
    - list(limit, offset, **params) - List with pagination
    - list_all(**params) - Auto-paginated list of all sources
    - count(**params) - Count sources matching criteria

    Example:
        >>> sources = await upsales.lead_sources.list_all()
        >>> source = await upsales.lead_sources.get(1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize lead sources resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/leadsources",
            model_class=LeadSource,
            partial_class=PartialLeadSource,
        )

    async def get_by_name(self, name: str) -> LeadSource | None:
        """
        Get lead source by name.

        Args:
            name: Lead source name to search for.

        Returns:
            LeadSource if found, None otherwise.

        Example:
            >>> source = await upsales.lead_sources.get_by_name("Website")
        """
        sources: list[LeadSource] = await self.list_all(name=name)
        return sources[0] if sources else None
