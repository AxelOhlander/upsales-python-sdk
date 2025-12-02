"""Ad Creatives resource manager for Upsales API.

Provides methods to interact with ad creatives (banners, images, HTML5 ads)
used in marketing campaigns.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     creative = await upsales.ad_creatives.get(1)
    ...     all_creatives = await upsales.ad_creatives.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.ad_creatives import AdCreative, PartialAdCreative
from upsales.resources.base import BaseResource


class AdCreativesResource(BaseResource[AdCreative, PartialAdCreative]):
    """Resource manager for AdCreative endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new ad creative
    - get(id) - Get single ad creative
    - list(limit, offset, **params) - List ad creatives with pagination
    - list_all(**params) - Auto-paginated list of all ad creatives
    - update(id, **data) - Update ad creative
    - delete(id) - Delete ad creative
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Note:
        The ad creatives endpoint uses a custom path structure:
        /api/v2/:customerId/engage/creative

    Example:
        >>> resource = AdCreativesResource(http_client)
        >>> creative = await resource.create(
        ...     name="Banner",
        ...     type="image",
        ...     width=300,
        ...     height=250,
        ...     url="https://example.com/banner.jpg"
        ... )
        >>> all_images = await resource.list_all()
    """

    def __init__(self, http: HTTPClient):
        """Initialize ad creatives resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/adCreatives",
            model_class=AdCreative,
            partial_class=PartialAdCreative,
        )

    async def get_by_type(self, creative_type: str) -> list[AdCreative]:
        """Get ad creatives filtered by type.

        Args:
            creative_type: Type to filter by (image, html5, third_party_tag, zip).

        Returns:
            List of ad creatives matching the type.

        Example:
            >>> images = await resource.get_by_type("image")
            >>> html5_ads = await resource.get_by_type("html5")
        """
        return await self.list_all(type=creative_type)
