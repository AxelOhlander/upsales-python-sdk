"""
Pages resource manager for Upsales API.

Provides methods to interact with the /pages endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     page = await upsales.pages.get(1)
    ...     pages_list = await upsales.pages.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.pages import Page, PartialPage
from upsales.resources.base import BaseResource


class PagesResource(BaseResource[Page, PartialPage]):
    """
    Resource manager for Page endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single page
    - list(limit, offset, **params) - List pages with pagination
    - list_all(**params) - Auto-paginated list of all pages
    - update(id, **data) - Update page
    - delete(id) - Delete page
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = PagesResource(http_client)
        >>> page = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize pages resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/pages",
            model_class=Page,
            partial_class=PartialPage,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Page]:
    #     """Get all active pages."""
    #     return await self.list_all(active=1)
