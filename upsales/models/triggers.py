"""
Trigger models for Upsales API.

Workflow automation triggers that execute actions based on events and criteria.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag


class TriggerUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Trigger.

    All fields are optional for updates.
    """

    name: str
    description: str
    active: int
    events: list[str]
    actions: list[dict[str, Any]]
    criterias: list[dict[str, Any]]


class Trigger(BaseModel):
    """
    Trigger model from /api/v2/triggers.

    Represents a workflow automation trigger that executes actions
    based on events and criteria.

    Attributes:
        id: Unique trigger identifier (read-only).
        name: Name of the trigger.
        description: Detailed description of the trigger's purpose.
        active: Active status (0=inactive, 1=active).
        events: List of events that activate this trigger.
        triggers: List of trigger conditions (returned by GET, name variant).
        criterias: List of criteria for trigger evaluation.
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique trigger identifier")
    client_id: int | None = Field(None, frozen=True, description="Client ID (read-only)")

    # Updatable fields
    name: str | None = Field(None, description="Trigger name")
    description: str | None = Field(None, description="Trigger description")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    events: list[str] = Field(default=[], description="Events that activate this trigger")
    triggers: list[dict[str, Any]] = Field(
        default=[], description="Trigger conditions (GET response)"
    )
    actions: list[dict[str, Any]] = Field(default=[], description="Actions to execute")
    criterias: list[dict[str, Any]] = Field(default=[], description="Criteria for evaluation")

    @property
    def is_active(self) -> bool:
        """
        Check if trigger is active.

        Returns:
            True if trigger is active (active == 1), False otherwise.

        Example:
            >>> trigger = Trigger(id=1, active=1)
            >>> trigger.is_active
            True
        """
        return self.active == 1

    @property
    def has_events(self) -> bool:
        """
        Check if trigger has any events configured.

        Returns:
            True if trigger has at least one event.

        Example:
            >>> trigger = Trigger(id=1, events=["after_order_insert"])
            >>> trigger.has_events
            True
        """
        return len(self.events) > 0

    @property
    def has_actions(self) -> bool:
        """
        Check if trigger has any actions configured.

        Returns:
            True if trigger has at least one action.

        Example:
            >>> trigger = Trigger(id=1, actions=[{"alias": "CreateAppointment"}])
            >>> trigger.has_actions
            True
        """
        return len(self.actions) > 0

    @property
    def has_criterias(self) -> bool:
        """
        Check if trigger has any criterias configured.

        Returns:
            True if trigger has at least one criteria.

        Example:
            >>> trigger = Trigger(id=1, criterias=[{"attribute": "Order.Stage"}])
            >>> trigger.has_criterias
            True
        """
        return len(self.criterias) > 0

    async def edit(self, **kwargs: Unpack[TriggerUpdateFields]) -> "Trigger":
        """
        Edit this trigger with full IDE autocomplete.

        Args:
            **kwargs: Fields to update (name, description, active, events, actions, criterias).

        Returns:
            Updated trigger instance with new values.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> trigger = await upsales.triggers.get(1)
            >>> updated = await trigger.edit(
            ...     name="New Trigger Name",
            ...     active=0
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.update(self.id, **self.to_api_dict(**kwargs))


class PartialTrigger(PartialModel):
    """
    Partial Trigger for nested responses.

    Minimal representation when triggers appear in nested contexts.

    Attributes:
        id: Unique trigger identifier.
        name: Trigger name.
    """

    id: int = Field(description="Unique trigger identifier")
    name: str | None = Field(None, description="Trigger name")

    async def fetch_full(self) -> Trigger:
        """
        Fetch complete trigger data from API.

        Returns:
            Full Trigger instance with all fields populated.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialTrigger(id=1, name="My Trigger")
            >>> full = await partial.fetch_full()
            >>> print(full.description)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.get(self.id)

    async def edit(self, **kwargs: Unpack[TriggerUpdateFields]) -> Trigger:
        """
        Edit this trigger.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Trigger instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialTrigger(id=1, name="My Trigger")
            >>> updated = await partial.edit(active=0)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.triggers.update(self.id, **kwargs)
