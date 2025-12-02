"""
Mail campaigns resource manager for Upsales API.

Provides methods to interact with the /api/v2/mailCampaigns endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     campaign = await upsales.mail_campaigns.get(1)
    ...     campaigns_list = await upsales.mail_campaigns.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.mail_campaigns import MailCampaign, PartialMailCampaign
from upsales.resources.base import BaseResource


class MailCampaignsResource(BaseResource[MailCampaign, PartialMailCampaign]):
    """
    Resource manager for MailCampaign endpoint.

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
        >>> resource = MailCampaignsResource(http_client)
        >>> campaign = await resource.get(1)
        >>> all_drafts = await resource.list_all(status="DRAFT")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize mail campaigns resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/mailCampaigns",
            model_class=MailCampaign,
            partial_class=PartialMailCampaign,
        )

    async def get_drafts(self) -> list[MailCampaign]:
        """
        Get all draft campaigns.

        Returns:
            List of campaigns with DRAFT status.

        Example:
            >>> drafts = await upsales.mail_campaigns.get_drafts()
            >>> for draft in drafts:
            ...     print(f"Draft: {draft.name}")
        """
        return await self.list_all(status="DRAFT")

    async def get_sent(self) -> list[MailCampaign]:
        """
        Get all sent campaigns.

        Returns:
            List of campaigns with SENT status.

        Example:
            >>> sent = await upsales.mail_campaigns.get_sent()
            >>> for campaign in sent:
            ...     print(f"Open rate: {campaign.open_rate:.2f}%")
        """
        return await self.list_all(status="SENT")

    async def get_archived(self) -> list[MailCampaign]:
        """
        Get all archived campaigns.

        Returns:
            List of archived campaigns.

        Example:
            >>> archived = await upsales.mail_campaigns.get_archived()
        """
        return await self.list_all(isArchived=1)
