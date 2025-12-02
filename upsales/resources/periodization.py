"""
Periodizations resource manager for Upsales API.

Provides methods to interact with the /periodization endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     periodization = await upsales.periodization.get(1)
    ...     periodization_list = await upsales.periodization.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.periodization import PartialPeriodization, Periodization
from upsales.resources.base import BaseResource


class PeriodizationsResource(BaseResource[Periodization, PartialPeriodization]):
    """
    Resource manager for Periodization endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single periodization
    - list(limit, offset, **params) - List periodization with pagination
    - list_all(**params) - Auto-paginated list of all periodization
    - update(id, **data) - Update periodization
    - delete(id) - Delete periodization
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = PeriodizationsResource(http_client)
        >>> periodization = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize periodization resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/periodization",
            model_class=Periodization,
            partial_class=PartialPeriodization,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Periodization]:
    #     """Get all active periodization."""
    #     return await self.list_all(active=1)
