"""
Lead Source models for Upsales API.

Lead sources track where leads/contacts originated from (e.g., website,
referral, campaign). Used for marketing attribution.
"""

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class LeadSource(BaseModel):
    """
    Lead Source model from /api/v2/leadsources.

    Represents a lead source definition in Upsales. Lead sources are
    typically read-only and managed through the Upsales UI.

    Example:
        >>> sources = await upsales.lead_sources.list_all()
        >>> for source in sources:
        ...     print(f"{source.id}: {source.name}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique lead source ID")
    name: str = Field(description="Lead source name")


class PartialLeadSource(PartialModel):
    """
    Partial Lead Source for nested responses.

    Contains minimal fields when lead source appears in other API responses.
    """

    id: int = Field(frozen=True, strict=True, description="Unique lead source ID")
    name: str | None = Field(None, description="Lead source name")

    async def fetch_full(self) -> LeadSource:
        """
        Fetch complete lead source data.

        Returns:
            Full LeadSource object.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.lead_sources.get(self.id)
