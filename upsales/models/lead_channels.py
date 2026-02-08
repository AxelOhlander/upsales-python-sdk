"""
Lead Channel models for Upsales API.

Lead channels represent the marketing channels through which leads arrive
(e.g., organic search, paid ads, social media, email).
"""

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class LeadChannel(BaseModel):
    """
    Lead Channel model from /api/v2/leadchannels.

    Represents a lead channel definition in Upsales. Lead channels are
    typically read-only and managed through the Upsales UI.

    Example:
        >>> channels = await upsales.lead_channels.list_all()
        >>> for channel in channels:
        ...     print(f"{channel.id}: {channel.name}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique lead channel ID")
    name: str = Field(description="Lead channel name")


class PartialLeadChannel(PartialModel):
    """
    Partial Lead Channel for nested responses.

    Contains minimal fields when lead channel appears in other API responses.
    """

    id: int = Field(frozen=True, strict=True, description="Unique lead channel ID")
    name: str | None = Field(None, description="Lead channel name")

    async def fetch_full(self) -> LeadChannel:
        """
        Fetch complete lead channel data.

        Returns:
            Full LeadChannel object.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.lead_channels.get(self.id)
