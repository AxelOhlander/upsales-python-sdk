"""AdCampaigns resource manager for Upsales API.

Provides methods to interact with the advertising campaigns endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     campaign = await upsales.ad_campaigns.get(1)
    ...     campaigns = await upsales.ad_campaigns.list(limit=10)
    ...     active = await upsales.ad_campaigns.get_active()
"""

from upsales.http import HTTPClient
from upsales.models.ad_campaigns import AdCampaign, PartialAdCampaign
from upsales.resources.base import BaseResource


class AdCampaignsResource(BaseResource[AdCampaign, PartialAdCampaign]):
    """Resource manager for advertising campaigns endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new campaign
    - get(id) - Get single campaign
    - list(limit, offset, **params) - List campaigns with pagination
    - list_all(**params) - Auto-paginated list of all campaigns
    - update(id, **data) - Update campaign
    - delete(id) - Delete campaign
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = AdCampaignsResource(http_client)
        >>> campaign = await resource.get(1)
        >>> active = await resource.get_active()
    """

    def __init__(self, http: HTTPClient):
        """Initialize advertising campaigns resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/engage/campaign",
            model_class=AdCampaign,
            partial_class=PartialAdCampaign,
        )

    async def get_active(self) -> list[AdCampaign]:
        """Get all active campaigns.

        Returns:
            List of active AdCampaign objects.

        Example:
            >>> active_campaigns = await upsales.ad_campaigns.get_active()
            >>> for campaign in active_campaigns:
            ...     print(f"{campaign.name}: {campaign.status}")
        """
        return await self.list_all(status="active")
