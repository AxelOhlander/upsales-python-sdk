"""Flow models for Upsales API.

This module provides models for managing marketing automation flows.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class FlowUpdateFields(TypedDict, total=False):
    """Available fields for updating a Flow.

    Attributes:
        name: Flow name (max 45 characters).
        segmentId: Segment ID for flow targeting.
        status: Flow status (draft, active, paused).
        hasBeenActive: Whether flow has ever been active.
        statusChangedDate: Date when status was changed.
        startTime: Start time in HH:mm format.
        endTime: End time in HH:mm format.
        timezone: Timezone string (max 35 characters).
        skipWeekends: Whether to skip weekends.
        loop: Whether flow should loop.
        loopTime: Loop interval time.
        loopUnit: Loop interval unit (month, day, etc).
        path: Flow path structure (complex object).
        endCriterias: End criteria rules.
    """

    name: str
    segmentId: int
    status: str
    hasBeenActive: bool
    statusChangedDate: str
    startTime: str
    endTime: str
    timezone: str
    skipWeekends: bool
    loop: bool
    loopTime: int
    loopUnit: str
    path: dict[str, Any]
    endCriterias: list[dict[str, Any]]


class Flow(BaseModel):
    """Represents a marketing automation flow in Upsales.

    Flows are automated marketing workflows that execute actions based on
    customer segments and triggers.

    Examples:
        Get a flow:

        >>> upsales = Upsales(token="...")
        >>> flow = await upsales.flows.get(1)
        >>> print(f"{flow.name} - Status: {flow.status}")

        Update a flow:

        >>> await flow.edit(status="active", skipWeekends=True)

        Create a new flow:

        >>> flow = await upsales.flows.create(
        ...     name="Welcome Campaign",
        ...     segmentId=5,
        ...     status="draft"
        ... )
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, ge=1, description="Unique identifier for the flow")
    regBy: dict[str, Any] | int | None = Field(None, frozen=True, description="Created by user")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modBy: dict[str, Any] | int | None = Field(
        None, frozen=True, description="Last modified by user"
    )
    sourceTemplate: str | None = Field(
        None, frozen=True, description="Source template (create-only)"
    )
    brandId: int = Field(default=1, frozen=True, description="Brand ID")
    completedContactCount: int | None = Field(
        None, frozen=True, description="Number of completed contacts"
    )

    # Updatable fields
    name: str | None = Field(None, description="Flow name (max 45 characters)", max_length=45)
    segmentId: int | None = Field(None, description="Segment ID for targeting")
    segment: dict[str, Any] | None = Field(None, description="Segment details")
    status: str = Field(default="draft", description="Flow status (draft, active, paused)")
    hasBeenActive: bool | None = Field(None, description="Whether flow has ever been active")
    statusChangedDate: str | None = Field(None, description="Status change date")
    startTime: str | None = Field(None, description="Start time in HH:mm format")
    endTime: str | None = Field(None, description="End time in HH:mm format")
    timezone: str | None = Field(
        None, description="Timezone string (max 35 characters)", max_length=35
    )
    skipWeekends: bool | None = Field(None, description="Skip weekends flag")
    loop: bool = Field(default=False, description="Whether flow loops")
    loopTime: int | None = Field(None, description="Loop interval time")
    loopUnit: str = Field(default="month", description="Loop interval unit")
    path: dict[str, Any] | None = Field(None, description="Flow path structure")
    endCriterias: list[dict[str, Any]] = Field(
        default_factory=list, description="End criteria rules"
    )

    @property
    def is_active(self) -> bool:
        """Check if flow is currently active.

        Returns:
            True if status is 'active', False otherwise.

        Examples:
            >>> if flow.is_active:
            ...     print("Flow is running")
        """
        return self.status == "active"

    @property
    def is_draft(self) -> bool:
        """Check if flow is in draft state.

        Returns:
            True if status is 'draft', False otherwise.

        Examples:
            >>> if flow.is_draft:
            ...     print("Flow is still being configured")
        """
        return self.status == "draft"

    @property
    def is_paused(self) -> bool:
        """Check if flow is paused.

        Returns:
            True if status is 'paused', False otherwise.

        Examples:
            >>> if flow.is_paused:
            ...     print("Flow is temporarily stopped")
        """
        return self.status == "paused"

    async def edit(self, **kwargs: Unpack[FlowUpdateFields]) -> Flow:
        """Edit this flow with the provided field updates.

        Args:
            **kwargs: Field updates (name, status, segmentId, etc.).

        Returns:
            Updated Flow instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update flow status:

            >>> flow = await upsales.flows.get(1)
            >>> updated = await flow.edit(status="active", skipWeekends=True)
        """
        if not self._client:
            raise RuntimeError("No client available for this flow")
        return await self._client.flows.update(self.id, **self.to_api_dict(**kwargs))


class PartialFlow(PartialModel):
    """Partial flow model for nested responses.

    This model is used when flows appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> segment = await upsales.segments.get(1)
        >>> if segment.flow:
        ...     print(segment.flow.name)

        Fetch full flow:

        >>> full_flow = await partial_flow.fetch_full()
    """

    id: int = Field(ge=1, description="Unique identifier")
    name: str | None = Field(None, description="Flow name")
    status: str = Field(default="draft", description="Flow status")

    async def fetch_full(self) -> Flow:
        """Fetch the complete flow object.

        Returns:
            Full Flow instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the flow doesn't exist.

        Examples:
            >>> partial = PartialFlow(id=1, name="Welcome Campaign", status="active")
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this flow")
        return await self._client.flows.get(self.id)

    async def edit(self, **kwargs: Unpack[FlowUpdateFields]) -> Flow:
        """Edit this flow with the provided field updates.

        Args:
            **kwargs: Field updates (name, status, segmentId, etc.).

        Returns:
            Updated Flow instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialFlow(id=1, name="Welcome Campaign")
            >>> updated = await partial.edit(status="paused")
        """
        if not self._client:
            raise RuntimeError("No client available for this flow")
        return await self._client.flows.update(self.id, **kwargs)
