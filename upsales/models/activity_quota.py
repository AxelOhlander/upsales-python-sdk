"""
Activity quota models for Upsales API.

Activity quotas track quarterly storage and monthly API usage per user and activity type.

Generated from /api/v2/activityQuota endpoint.
Analysis based on 12 samples.
"""

from typing import TypedDict, Unpack

from pydantic import Field, field_validator

from upsales.models.activity_types import PartialActivityType
from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser


class ActivityQuotaUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an ActivityQuota.

    All fields are optional. Only administrator or team leader can update.
    """

    year: int
    month: int
    performed: int
    created: int


class ActivityQuota(BaseModel):
    """
    Activity quota model from /api/v2/activityQuota.

    Tracks quarterly storage and monthly API usage metrics per user and activity type.

    Attributes:
        id: Unique activity quota ID (read-only)
        year: Year for quota tracking
        month: Month for quota tracking (1-12)
        date: Date of the quota record (read-only, computed from year/month)
        performed: Number of activities performed
        created: Number of activities created
        user: User associated with this quota
        activityType: Activity type associated with this quota

    Permissions:
        Create/Update: Administrator or team leader only
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique activity quota ID")
    date: str | None = Field(None, frozen=True, description="Date of quota record (YYYY-MM-DD)")

    # Required fields
    year: int = Field(description="Year for quota tracking")
    month: int = Field(description="Month for quota tracking (1-12)")
    user: PartialUser = Field(description="User associated with this quota")
    activityType: PartialActivityType = Field(
        description="Activity type associated with this quota"
    )

    # Optional fields (default to 0)
    performed: int = Field(default=0, description="Number of activities performed")
    created: int = Field(default=0, description="Number of activities created")

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        """Validate month is between 1-12."""
        if not 1 <= v <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {v}")
        return v

    async def edit(self, **kwargs: Unpack[ActivityQuotaUpdateFields]) -> "ActivityQuota":
        """
        Edit this activity quota.

        Only year, month, performed, and created can be updated.
        Requires administrator or team leader permissions.

        Args:
            **kwargs: Fields to update. Available fields:
                - year: Year for quota tracking
                - month: Month for quota tracking (1-12)
                - performed: Number of activities performed
                - created: Number of activities created

        Returns:
            Updated activity quota.

        Raises:
            RuntimeError: If no client available.
            ValidationError: If month not between 1-12.
            PermissionError: If user lacks administrator/team leader permissions.

        Example:
            ```python
            quota = await upsales.activity_quota.get(1)
            updated = await quota.edit(performed=15, created=10)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_quota.update(self.id, **self.to_api_dict(**kwargs))


class PartialActivityQuota(PartialModel):
    """
    Partial ActivityQuota for nested responses.

    Contains minimal identifying information for activity quotas referenced
    in other resources.

    Attributes:
        id: Unique activity quota ID
    """

    id: int = Field(description="Unique activity quota ID")

    async def fetch_full(self) -> ActivityQuota:
        """
        Fetch full activity quota data.

        Returns:
            Complete ActivityQuota object with all fields.

        Raises:
            RuntimeError: If no client available.
            NotFoundError: If activity quota doesn't exist.

        Example:
            ```python
            partial_quota = some_object.quota  # PartialActivityQuota
            full_quota = await partial_quota.fetch_full()
            print(full_quota.performed, full_quota.created)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_quota.get(self.id)

    async def edit(self, **kwargs: Unpack[ActivityQuotaUpdateFields]) -> ActivityQuota:
        """
        Edit this activity quota.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated activity quota.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_quota.update(self.id, **kwargs)
