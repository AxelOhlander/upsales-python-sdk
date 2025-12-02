"""AdCampaign model for Upsales API.

This module defines the AdCampaign model representing advertising campaigns
in the Upsales CRM system, including budget, targeting, creatives, and status lifecycle.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList  # noqa: TC001


class AdCampaignUpdateFields(TypedDict, total=False):
    """Available fields for updating an AdCampaign.

    All fields are optional for partial updates.
    """

    name: str
    budget: float
    startDate: str
    endDate: str
    status: str
    creative: list[dict[str, Any]]
    target: list[dict[str, Any]]
    siteTemplate: list[dict[str, Any]]
    useRange: bool
    targetAbm: int
    custom: list[dict[str, Any]]


class AdCampaign(BaseModel):
    """Represents an advertising campaign in Upsales.

    AdCampaigns manage advertising campaigns including budget tracking,
    targeting configuration, creative assets, and performance metrics.

    Attributes:
        id: Unique campaign identifier (read-only)
        name: Campaign name
        type: Campaign type (read-only)
        budget: Campaign budget amount
        spent: Amount spent (read-only)
        startDate: Campaign start date
        endDate: Campaign end date
        status: Current campaign status
        impressions: Number of impressions (read-only)
        clicks: Number of clicks (read-only)
        conversions: Number of conversions (read-only)
        cpm: Cost per thousand impressions (read-only)
        externalId: External campaign identifier (read-only)
        useRange: Whether to use date range
        targetAbm: Target ABM value
        creative: Array of creative assets
        target: Array of targeting criteria
        siteTemplate: Array of site templates
        custom: Custom fields list

    Example:
        >>> campaign = AdCampaign(
        ...     id=1,
        ...     name="Q4 Campaign",
        ...     budget=10000,
        ...     startDate="2024-10-01",
        ...     endDate="2024-12-31",
        ...     status="active"
        ... )
        >>> campaign.name
        'Q4 Campaign'
        >>> await campaign.edit(budget=15000)
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique campaign identifier")
    type: str | None = Field(None, frozen=True, description="Campaign type")
    spent: float | None = Field(None, frozen=True, description="Amount spent")
    impressions: int | None = Field(None, frozen=True, description="Number of impressions")
    clicks: int | None = Field(None, frozen=True, description="Number of clicks")
    conversions: int | None = Field(None, frozen=True, description="Number of conversions")
    cpm: float | None = Field(None, frozen=True, description="Cost per thousand impressions")
    externalId: str | None = Field(None, frozen=True, description="External campaign identifier")

    # Updatable fields
    name: str = Field(max_length=100, description="Campaign name")
    budget: float = Field(default=0, description="Campaign budget amount")
    startDate: str = Field(description="Campaign start date (YYYY-MM-DD)")
    endDate: str = Field(description="Campaign end date (YYYY-MM-DD)")
    status: str | None = Field(None, description="Current campaign status")
    useRange: bool = Field(default=True, description="Whether to use date range")
    targetAbm: int = Field(default=0, description="Target ABM value")
    creative: list[dict[str, Any]] = Field(default=[], description="Array of creative assets")
    target: list[dict[str, Any]] = Field(default=[], description="Array of targeting criteria")
    siteTemplate: list[dict[str, Any]] = Field(default=[], description="Array of site templates")
    custom: CustomFieldsList = Field(default=[], description="Custom fields list")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for accessing custom field values.

        Example:
            >>> campaign.custom_fields[11]  # By ID
            'value'
            >>> campaign.custom_fields["CAMPAIGN_TYPE"]  # By alias
            'email'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active.

        Returns:
            True if status is 'active', False otherwise.

        Example:
            >>> campaign.status = "active"
            >>> campaign.is_active
            True
        """
        return self.status == "active" if self.status else False

    @computed_field
    @property
    def ctr(self) -> float:
        """Calculate click-through rate.

        Returns:
            Click-through rate as a percentage (0-100).
            Returns 0 if no impressions.

        Example:
            >>> campaign.impressions = 1000
            >>> campaign.clicks = 25
            >>> campaign.ctr
            2.5
        """
        if not self.impressions or self.impressions == 0:
            return 0.0
        return (self.clicks or 0) / self.impressions * 100

    @computed_field
    @property
    def budget_remaining(self) -> float:
        """Calculate remaining budget.

        Returns:
            Amount of budget remaining (budget - spent).

        Example:
            >>> campaign.budget = 10000
            >>> campaign.spent = 3500
            >>> campaign.budget_remaining
            6500.0
        """
        return self.budget - (self.spent or 0)

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Clean custom fields for API requests.

        Args:
            custom: List of custom field dictionaries.

        Returns:
            Cleaned list with only fieldId and value.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[AdCampaignUpdateFields]) -> AdCampaign:
        """Edit this campaign with the provided field updates.

        Args:
            **kwargs: Field values to update (see AdCampaignUpdateFields).

        Returns:
            Updated AdCampaign instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> campaign = await upsales.ad_campaigns.get(1)
            >>> updated = await campaign.edit(
            ...     name="Updated Campaign",
            ...     budget=15000
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available for edit operation")
        return await self._client.ad_campaigns.update(self.id, **self.to_api_dict(**kwargs))


class PartialAdCampaign(PartialModel):
    """Minimal AdCampaign representation for nested responses.

    Used when AdCampaign data appears nested in other API responses,
    containing only essential identifying information.

    Attributes:
        id: Unique campaign identifier
        name: Campaign name

    Example:
        >>> partial = PartialAdCampaign(id=1, name="Q4 Campaign")
        >>> full = await partial.fetch_full()
        >>> full.budget
        10000
    """

    id: int = Field(description="Unique campaign identifier")
    name: str = Field(description="Campaign name")

    async def fetch_full(self) -> AdCampaign:
        """Fetch the complete AdCampaign object.

        Returns:
            Full AdCampaign instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialAdCampaign(id=1, name="Q4 Campaign")
            >>> full = await partial.fetch_full()
            >>> full.budget
            10000
        """
        if not self._client:
            raise RuntimeError("No client available for fetch_full operation")
        return await self._client.ad_campaigns.get(self.id)

    async def edit(self, **kwargs: Any) -> AdCampaign:
        """Edit this campaign with the provided field updates.

        Args:
            **kwargs: Field values to update.

        Returns:
            Updated full AdCampaign instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialAdCampaign(id=1, name="Q4 Campaign")
            >>> updated = await partial.edit(budget=15000)
        """
        if not self._client:
            raise RuntimeError("No client available for edit operation")
        return await self._client.ad_campaigns.update(self.id, **kwargs)
