"""
Quota models for Upsales API.

Generated from /api/v2/quota endpoint.
Analysis based on 1302 samples.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []

TODO: Review and customize the generated models:
1. Mark read-only fields with Field(frozen=True)
2. Update field types if needed
3. Add custom_fields property if 'custom' field exists
4. Update docstrings with detailed descriptions
5. Add any custom methods
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser


class QuotaUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Quota.

    All fields are optional. Read-only fields (id, date, valueInMasterCurrency, user)
    are excluded as they cannot be updated via API.

    Verified against API PUT /api/v2/quota/:id (2025-11-08).
    """

    currency: str
    currencyRate: int
    month: int
    value: int
    year: int


class Quota(BaseModel):
    """
    Quota model from /api/v2/quota.

    Generated from 1302 samples.

    TODO: Review and update field types and docstrings.
    TODO: Mark read-only fields with Field(frozen=True).
    TODO: Add custom_fields property if model has 'custom' field.
    # from upsales.models.user import PartialUser
    TODO: Add the above imports to use Partial models
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique quota ID")
    date: str = Field(frozen=True, description="Date of quota")
    valueInMasterCurrency: int = Field(frozen=True, description="Value in master currency")
    user: PartialUser = Field(frozen=True, description="User this quota belongs to")

    # Updatable fields
    currency: str | None = Field(None, description="Currency code (3 letters)")
    currencyRate: int = Field(description="Currency exchange rate")
    month: int = Field(description="Month (1-12)")
    value: int = Field(description="Quota value")
    year: int = Field(description="Year")

    async def edit(self, **kwargs: Unpack[QuotaUpdateFields]) -> "Quota":
        """
        Edit this quota.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated quota.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.update(self.id, **self.to_update_dict(**kwargs))


class PartialQuota(PartialModel):
    """
    Partial Quota for nested responses.

    TODO: Add fields that should be available in partial objects.
    """

    id: int  # Present in 100% (1302/1302)

    async def fetch_full(self) -> Quota:
        """Fetch full quota data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.get(self.id)

    async def edit(self, **kwargs: Unpack[QuotaUpdateFields]) -> Quota:
        """Edit this quota."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.quota.update(self.id, **kwargs)
