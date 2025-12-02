"""
Agreements resource manager for Upsales API.

Provides methods to interact with the /agreements endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     agreement = await upsales.agreements.get(1)
    ...     agreements_list = await upsales.agreements.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.agreements import Agreement, PartialAgreement
from upsales.resources.base import BaseResource


class AgreementsResource(BaseResource[Agreement, PartialAgreement]):
    """
    Resource manager for Agreement endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single agreement
    - list(limit, offset, **params) - List agreements with pagination
    - list_all(**params) - Auto-paginated list of all agreements
    - update(id, **data) - Update agreement
    - delete(id) - Delete agreement
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = AgreementsResource(http_client)
        >>> agreement = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize agreements resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/agreements",
            model_class=Agreement,
            partial_class=PartialAgreement,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[Agreement]:
    #     """Get all active agreements."""
    #     return await self.list_all(active=1)
