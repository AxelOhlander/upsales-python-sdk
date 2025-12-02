"""Market rejectlist resource manager for Upsales API.

Provides methods to interact with the /marketRejectlist endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     entry = await upsales.market_rejectlist.get(1)
    ...     entries = await upsales.market_rejectlist.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.market_rejectlist import MarketRejectlist, PartialMarketRejectlist
from upsales.resources.base import BaseResource


class MarketRejectlistsResource(BaseResource[MarketRejectlist, PartialMarketRejectlist]):
    """Resource manager for MarketRejectlist endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new rejectlist entry
    - get(id) - Get single rejectlist entry
    - list(limit, offset, **params) - List entries with pagination
    - list_all(**params) - Auto-paginated list of all entries
    - update(id, **data) - Update rejectlist entry
    - delete(id) - Delete rejectlist entry
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = MarketRejectlistsResource(http_client)
        >>> entry = await resource.get(1)
        >>> all_entries = await resource.list_all()
    """

    def __init__(self, http: HTTPClient):
        """Initialize market rejectlist resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/marketRejectlist",
            model_class=MarketRejectlist,
            partial_class=PartialMarketRejectlist,
        )
