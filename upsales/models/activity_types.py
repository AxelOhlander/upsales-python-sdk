"""
Activity Type models for Upsales API.

Generated from /api/v2/activitytypes/activity endpoint.

Enhanced with Pydantic v2 features:
- Reusable validators
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class ActivityTypeUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an ActivityType.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Excludes read-only fields: id
    """

    name: str
    roles: list[Any]
    hasOutcome: bool


class ActivityType(BaseModel):
    """
    Activity Type model from /api/v2/activitytypes/activity.

    Represents an activity type configuration in the Upsales system.

    Example:
        >>> activity_type = await upsales.activity_types.get(1)
        >>> activity_type.name
        'Phone Call'
        >>> activity_type.has_outcome
        True
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique activity type ID")

    # Required core fields
    name: NonEmptyStr = Field(description="Activity type name")

    # Optional fields
    roles: list[Any] = Field(default=[], description="Associated roles")
    hasOutcome: bool = Field(default=False, description="Whether activity has outcome tracking")

    @computed_field
    @property
    def has_outcome(self) -> bool:
        """
        Check if activity type has outcome tracking.

        Returns:
            True if outcome tracking is enabled, False otherwise.

        Example:
            >>> activity_type.has_outcome
            True
        """
        return self.hasOutcome

    async def edit(self, **kwargs: Unpack[ActivityTypeUpdateFields]) -> "ActivityType":
        """
        Edit this activity type.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated activity type with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> activity_type = await upsales.activity_types.get(1)
            >>> updated = await activity_type.edit(
            ...     name="Updated Name",
            ...     hasOutcome=True
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_types.update(self.id, **self.to_api_dict(**kwargs))


class PartialActivityType(PartialModel):
    """
    Partial ActivityType for nested responses.

    Contains minimal fields for when ActivityType appears nested in other
    API responses.

    Use fetch_full() to get complete ActivityType object with all fields.

    Example:
        >>> # If activity type appears nested somewhere
        >>> partial_type = some_object.activity_type  # PartialActivityType
        >>> full_type = await partial_type.fetch_full()  # ActivityType
    """

    id: int = Field(frozen=True, strict=True, description="Unique activity type ID")
    name: NonEmptyStr = Field(description="Activity type name")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the activity type.

        Returns:
            Activity type name formatted for display.

        Example:
            >>> partial_type.display_name
            'Phone Call'
        """
        return self.name

    async def fetch_full(self) -> ActivityType:
        """
        Fetch complete activity type data.

        Returns:
            Full ActivityType object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.activity_type  # PartialActivityType
            >>> full = await partial.fetch_full()  # ActivityType
            >>> full.hasOutcome  # Now available
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_types.get(self.id)

    async def edit(self, **kwargs: Unpack[ActivityTypeUpdateFields]) -> ActivityType:
        """
        Edit this activity type.

        Returns full ActivityType object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full ActivityType object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.activity_type  # PartialActivityType
            >>> updated = await partial.edit(name="New Name")  # Returns ActivityType
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activity_types.update(self.id, **kwargs)
