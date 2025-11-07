"""
Campaign models for Upsales API.

Simple PartialCampaign for nested objects (e.g., Company.projects).
Provides type-safe access to campaign data in company responses.

Note:
    API endpoint is /projects but we use "Campaign" to match the Upsales UI
    where users see "Campaigns". A campaign is a list/collection of companies,
    orders, contacts, and activities. See docs/terminology.md for rationale.

Example:
    >>> company = await upsales.companies.get(1)
    >>> if company.projects:
    ...     campaign = company.projects[0]
    ...     print(f"Campaign: {campaign.name}")  # ✅ Type-safe!
"""

from typing import TYPE_CHECKING, Any

from pydantic import Field, computed_field

from upsales.models.base import PartialModel
from upsales.validators import NonEmptyStr

if TYPE_CHECKING:
    from upsales.models.base import BaseModel


class PartialCampaign(PartialModel):
    """
    Partial Campaign model for nested responses.

    Minimal campaign information included when campaign appears nested
    in company responses (e.g., in projects list).

    Example:
        >>> company = await upsales.companies.get(1)
        >>> if company.projects:
        ...     for campaign in company.projects:
        ...         print(f"Campaign: {campaign.name}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique campaign ID")
    name: NonEmptyStr = Field(description="Campaign name")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the campaign.

        Returns:
            Campaign name formatted for display.

        Example:
            >>> campaign.display_name
            'Q4 Sales Campaign'
        """
        return self.name

    async def fetch_full(self) -> "BaseModel":
        """
        Fetch complete campaign data.

        Note:
            Full Campaign model not yet implemented. This returns self.
            Implement full Campaign model and CampaignsResource for full CRUD.

        Returns:
            Self (partial campaign).
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Full Campaign model not yet implemented. "
            "Add CampaignsResource to enable full CRUD operations. "
            "Reference implementation available in ai_temp_files/campaign_enhanced.py"
        )

    async def edit(self, **kwargs: Any) -> "BaseModel":
        """
        Edit this campaign.

        Note:
            Full Campaign model not yet implemented.

        Raises:
            NotImplementedError: Until CampaignsResource is implemented.
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError("Full Campaign model not yet implemented.")
