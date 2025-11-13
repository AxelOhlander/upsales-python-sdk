"""
Quotas resource manager for Upsales API.

Provides methods to interact with the /quota endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     quota = await upsales.quota.get(1)
    ...     quota = await upsales.quota.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.quota import PartialQuota, Quota
from upsales.resources.base import BaseResource


class QuotasResource(BaseResource[Quota, PartialQuota]):
    """
    Resource manager for Quota endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single quota
    - list(limit, offset, **params) - List quota with pagination
    - list_all(**params) - Auto-paginated list of all quota
    - update(id, **data) - Update quota
    - delete(id) - Delete quota
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> quota = QuotasResource(http_client)
        >>> quota = await quota.get(1)
        >>> all_active = await quota.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize quota resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/quota",
            model_class=Quota,
            partial_class=PartialQuota,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Quota]:
    #     """Get all active quota."""
    #     return await self.list_all(active=1)
