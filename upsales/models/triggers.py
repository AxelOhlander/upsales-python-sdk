"""
Trigger models for Upsales API.

Generated from /api/v2/triggers endpoint.
Analysis based on 4 samples.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for boolean helpers
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, NonEmptyStr


class TriggerUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Trigger.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    description: str | None
    active: int
    events: list[str]
    actions: list[dict[str, Any]]
    criterias: list[dict[str, Any]]


class Trigger(BaseModel):
    """
    Trigger model from /api/v2/triggers.

    Represents an automation trigger in Upsales that executes actions when
    specific events occur and criteria are met. Triggers are used to automate
    workflows such as creating activities, sending emails, or updating records.

    Generated from 4 samples with field analysis.

    Example:
        >>> trigger = await upsales.triggers.get(1001003)
        >>> trigger.name
        'Trigger that creates meeting on order'
        >>> trigger.is_active
        True
        >>> await trigger.edit(name="Updated Trigger")
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique trigger ID")

    # Required updatable fields
    name: NonEmptyStr = Field(description="Trigger name")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    events: list[str] = Field(
        default=[],
        description="List of events that activate this trigger (e.g., 'after_order_insert')",
    )
    actions: list[dict[str, Any]] = Field(
        default=[], description="List of actions to execute when trigger fires"
    )
    criterias: list[dict[str, Any]] = Field(
        default=[], description="List of criteria that must be met for trigger to fire"
    )

    # Optional fields
    description: str | None = Field(default=None, description="Trigger description")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if trigger is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> trigger.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def has_events(self) -> bool:
        """
        Check if trigger has any events configured.

        Returns:
            True if events list is not empty, False otherwise.

        Example:
            >>> trigger.has_events
            True
        """
        return len(self.events) > 0

    @computed_field
    @property
    def has_actions(self) -> bool:
        """
        Check if trigger has any actions configured.

        Returns:
            True if actions list is not empty, False otherwise.

        Example:
            >>> trigger.has_actions
            True
        """
        return len(self.actions) > 0

    @computed_field
    @property
    def has_criterias(self) -> bool:
        """
        Check if trigger has any criteria configured.

        Returns:
            True if criterias list is not empty, False otherwise.

        Example:
            >>> trigger.has_criterias
            True
        """
        return len(self.criterias) > 0

    async def edit(self, **kwargs: Unpack[TriggerUpdateFields]) -> "Trigger":
        """
        Edit this trigger.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated trigger with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> trigger = await upsales.triggers.get(1001003)
            >>> updated = await trigger.edit(
            ...     name="Updated Trigger",
            ...     description="New description",
            ...     active=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.update(self.id, **self.to_update_dict(**kwargs))


class PartialTrigger(PartialModel):
    """
    Partial Trigger for nested responses.

    Contains minimal fields for when Trigger appears nested in other
    API responses. Use fetch_full() to get complete Trigger object with all fields.

    Example:
        >>> # If trigger appeared nested somewhere
        >>> partial_trigger = some_object.trigger  # PartialTrigger
        >>> full_trigger = await partial_trigger.fetch_full()  # Now Trigger
    """

    id: int = Field(frozen=True, strict=True, description="Unique trigger ID")
    name: NonEmptyStr = Field(description="Trigger name")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

    async def fetch_full(self) -> Trigger:
        """
        Fetch complete trigger data.

        Returns:
            Full Trigger object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.trigger  # PartialTrigger
            >>> full = await partial.fetch_full()  # Trigger
            >>> full.events  # Now available
            ['after_order_insert', 'after_order_update']
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.get(self.id)

    async def edit(self, **kwargs: Unpack[TriggerUpdateFields]) -> Trigger:
        """
        Edit this trigger.

        Returns full Trigger object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Trigger object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.trigger  # PartialTrigger
            >>> updated = await partial.edit(name="New Name")  # Returns Trigger
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.update(self.id, **kwargs)
