"""
AdCampaign models for company advertising campaigns.

This module provides models for the ad campaign data structure that appears
nested in company responses. AdCampaign objects do not have a dedicated API
endpoint and are only accessible as nested data within companies.

Example:
    >>> company = await upsales.companies.get(1)
    >>> if company.ad_campaign:
    ...     print(f"Campaign {company.ad_campaign.id} has {company.ad_campaign.clicks} clicks")
    ...     print(f"Active: {company.ad_campaign.is_active}")
"""

from typing import Any

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, PositiveInt


class AdCampaign(BaseModel):
    """
    Full ad campaign data for a company.

    AdCampaign represents advertising campaign metrics and configuration
    nested within company data. This includes performance metrics (clicks,
    impressions), campaign settings, and status information.

    Attributes:
        id: Unique campaign identifier.
        active: Campaign active status (0=inactive, 1=active).
        brandId: Associated brand ID for the campaign.
        clicks: Total number of clicks on campaign ads.
        impressions: Total number of ad impressions shown.
        grade: Campaign performance grade (e.g., "A", "B", "C").
        hasIp: Whether campaign has IP tracking enabled.
        lastTimestamp: ISO 8601 timestamp of last campaign activity.

    Example:
        >>> campaign = AdCampaign(
        ...     id=1,
        ...     active=1,
        ...     brandId=1,
        ...     clicks=150,
        ...     impressions=5000,
        ...     grade="A",
        ...     hasIp=True,
        ...     lastTimestamp="2025-10-01T12:00:00.000Z"
        ... )
        >>> campaign.is_active
        True
        >>> campaign.clicks
        150

    Note:
        AdCampaign objects are read-only nested data. They cannot be directly
        edited or updated via the API. All fields are frozen as they represent
        historical campaign data.
    """

    # Read-only fields (all fields are frozen for nested data)
    id: int = Field(
        frozen=True,
        strict=True,
        description="Unique campaign identifier",
    )
    active: bool = Field(
        frozen=True,
        description="Campaign active status (true/false)",
    )
    brandId: int = Field(
        frozen=True,
        description="Associated brand ID for the campaign",
    )
    clicks: PositiveInt = Field(
        frozen=True,
        description="Total number of clicks on campaign ads",
    )
    impressions: PositiveInt = Field(
        frozen=True,
        description="Total number of ad impressions shown",
    )
    grade: str | None = Field(
        default=None,
        frozen=True,
        description="Campaign performance grade (e.g., 'A', 'B', 'C', optional)",
    )
    hasIp: bool = Field(
        frozen=True,
        description="Whether campaign has IP tracking enabled",
    )
    lastTimestamp: int | str | None = Field(
        default=None,
        frozen=True,
        description="Last campaign activity timestamp (Unix int or ISO string, optional)",
    )

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if campaign is currently active.

        Returns:
            True if campaign is active, False otherwise.

        Example:
            >>> campaign = AdCampaign(id=1, active=True, brandId=1, clicks=100, impressions=1000, grade="A", hasIp=True)
            >>> campaign.is_active
            True
            >>> inactive = AdCampaign(id=2, active=False, brandId=1, clicks=0, impressions=0, grade="F", hasIp=False)
            >>> inactive.is_active
            False
        """
        return self.active

    async def edit(self, **kwargs: Any) -> "AdCampaign":
        """
        Edit operation not supported for nested ad campaign data.

        AdCampaign objects are read-only nested data within companies and
        cannot be directly edited via the API.

        Args:
            **kwargs: Ignored (operation not supported).

        Raises:
            NotImplementedError: AdCampaign objects cannot be directly edited.

        Example:
            >>> campaign = company.ad_campaign
            >>> await campaign.edit(active=0)  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            NotImplementedError: AdCampaign objects are read-only nested data
        """
        raise NotImplementedError(
            "AdCampaign objects are read-only nested data and cannot be directly edited"
        )


class PartialAdCampaign(PartialModel):
    """
    Minimal ad campaign data for nested references.

    PartialAdCampaign contains only the most essential campaign information
    for use in nested contexts where full campaign details are not needed.

    Attributes:
        id: Unique campaign identifier.
        active: Campaign active status (0=inactive, 1=active).
        clicks: Total number of clicks on campaign ads.
        impressions: Total number of ad impressions shown.

    Example:
        >>> partial = PartialAdCampaign(id=1, active=1, clicks=150, impressions=5000)
        >>> partial.is_active
        True
        >>> partial.clicks
        150

    Note:
        Since ad campaigns don't have a dedicated endpoint, fetch_full()
        is not supported. To get the full ad campaign, fetch the parent
        company object.
    """

    id: int = Field(description="Unique campaign identifier")
    active: BinaryFlag = Field(description="Campaign active status (0=inactive, 1=active)")
    clicks: PositiveInt = Field(description="Total number of clicks on campaign ads")
    impressions: PositiveInt = Field(description="Total number of ad impressions shown")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if campaign is currently active.

        Returns:
            True if campaign is active, False otherwise.

        Example:
            >>> partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
            >>> partial.is_active
            True
        """
        return self.active == 1

    async def fetch_full(self) -> AdCampaign:
        """
        Fetch full campaign data not supported.

        AdCampaign objects don't have a dedicated API endpoint. To get the
        full ad campaign data, fetch the parent company object instead.

        Raises:
            NotImplementedError: AdCampaign has no dedicated endpoint.

        Example:
            >>> partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
            >>> await partial.fetch_full()  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            NotImplementedError: AdCampaign has no dedicated endpoint
        """
        raise NotImplementedError(
            "AdCampaign has no dedicated endpoint. Fetch the parent company instead."
        )

    async def edit(self, **kwargs: Any) -> AdCampaign:
        """
        Edit operation not supported for ad campaign data.

        AdCampaign objects are read-only nested data and cannot be directly
        edited via the API.

        Args:
            **kwargs: Ignored (operation not supported).

        Raises:
            NotImplementedError: AdCampaign objects cannot be directly edited.

        Example:
            >>> partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
            >>> await partial.edit(active=0)  # doctest: +SKIP
            Traceback (most recent call last):
            ...
            NotImplementedError: AdCampaign objects are read-only nested data
        """
        raise NotImplementedError(
            "AdCampaign objects are read-only nested data and cannot be directly edited"
        )
