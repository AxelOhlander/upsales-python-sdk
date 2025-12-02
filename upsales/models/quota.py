"""
Quota models for Upsales API.

Sales quotas track monthly/quarterly sales targets for users. The API stores
them quarterly but provides monthly access. Enhanced with Pydantic v2 features.

Generated from /api/v2/quota endpoint.
Analysis based on 1299 samples.

Enhanced with Pydantic v2 features:
- Read-only field protection (frozen=True)
- Field descriptions for documentation
- Computed fields for convenience
- Type-safe updates with IDE autocomplete
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser
from upsales.validators import PositiveInt


class QuotaUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Quota.

    All fields are optional. Only year, month, value, currency, and currencyRate
    can be updated according to API specification.
    """

    year: int
    month: int
    value: int
    currency: str
    currencyRate: int


class Quota(BaseModel):
    """
    Quota model from /api/v2/quota.

    Represents a sales quota for a user in a specific month/year. Quotas are
    stored quarterly in the system but can be accessed and managed monthly.

    Generated from 1299 samples with Pydantic v2 enhancements.

    Example:
        >>> quota = await upsales.quota.get(1)
        >>> quota.year
        2025
        >>> quota.month
        11
        >>> quota.value
        100000
        >>> quota.is_current_quarter
        True
        >>> await quota.edit(value=150000)
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique quota ID")
    date: str = Field(frozen=True, description="Date string (computed from year/month)")
    valueInMasterCurrency: int = Field(
        frozen=True, description="Quota value in account's master currency"
    )

    # Required fields
    year: PositiveInt = Field(description="Year of the quota (e.g., 2025)")
    month: int = Field(ge=1, le=12, description="Month of the quota (1-12)")
    value: PositiveInt = Field(description="Quota value in specified currency")
    currencyRate: int = Field(description="Currency exchange rate")
    user: PartialUser = Field(description="User this quota belongs to")

    # Optional fields
    currency: str | None = Field(None, max_length=3, description="Currency code (3 letters)")

    @computed_field
    @property
    def is_current_quarter(self) -> bool:
        """
        Check if this quota is for the current quarter.

        Returns:
            True if quota is in current quarter, False otherwise.

        Example:
            >>> quota.is_current_quarter
            True
        """
        from datetime import datetime

        now = datetime.now()
        current_quarter = (now.month - 1) // 3 + 1
        quota_quarter = (self.month - 1) // 3 + 1
        return self.year == now.year and quota_quarter == current_quarter

    @computed_field
    @property
    def quarter(self) -> int:
        """
        Get the quarter (1-4) this quota belongs to.

        Returns:
            Quarter number (1, 2, 3, or 4).

        Example:
            >>> quota.month = 3
            >>> quota.quarter
            1
            >>> quota.month = 11
            >>> quota.quarter
            4
        """
        return (self.month - 1) // 3 + 1

    @computed_field
    @property
    def formatted_period(self) -> str:
        """
        Get formatted period string.

        Returns:
            Human-readable period string.

        Example:
            >>> quota.formatted_period
            '2025-Q4 (Nov)'
        """
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        month_name = month_names[self.month - 1]
        return f"{self.year}-Q{self.quarter} ({month_name})"

    async def edit(self, **kwargs: Unpack[QuotaUpdateFields]) -> "Quota":
        """
        Edit this quota.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated quota with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> quota = await upsales.quota.get(1)
            >>> updated = await quota.edit(value=150000, currency="USD")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.update(self.id, **self.to_api_dict(**kwargs))


class PartialQuota(PartialModel):
    """
    Partial Quota for nested responses.

    Contains minimal fields for when Quota appears nested in other
    API responses. Use fetch_full() to get complete Quota object.

    Example:
        >>> # When quota appears nested
        >>> partial_quota = some_object.quota  # PartialQuota
        >>> full_quota = await partial_quota.fetch_full()  # Now Quota
    """

    id: int = Field(frozen=True, strict=True, description="Unique quota ID")
    year: PositiveInt = Field(description="Year of the quota")
    month: int = Field(ge=1, le=12, description="Month of the quota (1-12)")
    value: PositiveInt = Field(description="Quota value")

    async def fetch_full(self) -> Quota:
        """
        Fetch complete quota data.

        Returns:
            Full Quota object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.quota  # PartialQuota
            >>> full = await partial.fetch_full()  # Quota
            >>> full.valueInMasterCurrency  # Now available
            150000
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.get(self.id)

    async def edit(self, **kwargs: Unpack[QuotaUpdateFields]) -> Quota:
        """
        Edit this quota.

        Returns full Quota object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Quota object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.quota  # PartialQuota
            >>> updated = await partial.edit(value=150000)  # Returns Quota
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.update(self.id, **kwargs)
