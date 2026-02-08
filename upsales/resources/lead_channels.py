"""
Lead Channels resource manager for Upsales API.

Provides methods to interact with the /leadchannels endpoint.
"""

from upsales.http import HTTPClient
from upsales.models.lead_channels import LeadChannel, PartialLeadChannel
from upsales.resources.base import BaseResource


class LeadChannelsResource(BaseResource[LeadChannel, PartialLeadChannel]):
    """
    Resource manager for Lead Channels endpoint.

    Lead channels are typically read-only definitions managed through
    the Upsales UI. This resource provides list and get operations.

    Inherits from BaseResource:
    - get(id) - Get single lead channel
    - list(limit, offset, **params) - List with pagination
    - list_all(**params) - Auto-paginated list of all channels
    - count(**params) - Count channels matching criteria

    Example:
        >>> channels = await upsales.lead_channels.list_all()
        >>> channel = await upsales.lead_channels.get(1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize lead channels resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/leadchannels",
            model_class=LeadChannel,
            partial_class=PartialLeadChannel,
        )

    async def get_by_name(self, name: str) -> LeadChannel | None:
        """
        Get lead channel by name.

        Args:
            name: Lead channel name to search for.

        Returns:
            LeadChannel if found, None otherwise.

        Example:
            >>> channel = await upsales.lead_channels.get_by_name("Organic Search")
        """
        channels: list[LeadChannel] = await self.list_all(name=name)
        return channels[0] if channels else None
