"""
Sales Coach models for Upsales API.

Sales Coaches are part of the Upsales BANT (Budget, Authority, Need, Timing) methodology
for qualifying opportunities. They define the stages and criteria for evaluating sales
opportunities across different dimensions.

This module provides:
- SalesCoach: Full sales coach configuration with all BANT stages
- PartialSalesCoach: Minimal sales coach for nested responses

Example:
    >>> async with Upsales.from_env() as upsales:
    ...     # Get a sales coach
    ...     coach = await upsales.sales_coaches.get(1)
    ...     print(f"Coach: {coach.name}")
    ...     print(f"Budget tracking: {coach.budgetActive}")
    ...
    ...     # Update coach settings
    ...     await coach.edit(budgetActive=True, timeframeActive=True)
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class SalesCoachUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a SalesCoach.

    All fields are optional for partial updates.
    """

    name: str
    active: bool
    budgetActive: bool
    budgetStages: list[Any]
    decisionMakersActive: bool
    decisionMakersStages: list[Any]
    decisionMakersTitles: list[dict[str, Any]]
    decisionMakersType: Any
    solutionActive: bool
    solutionStages: list[Any]
    timeframeActive: bool
    timeframeStages: list[Any]
    nextStepActive: bool
    nextStepOnlyAppointments: bool
    checklist: list[Any]
    users: list[Any]
    roles: list[Any]
    decisionMakers: list[Any]


class SalesCoach(BaseModel):
    """
    Sales Coach configuration for BANT methodology.

    Sales Coaches help sales teams qualify opportunities using the BANT framework:
    - Budget: Does the prospect have budget allocated?
    - Authority: Are we talking to decision makers?
    - Need/Solution: Does our solution match their needs?
    - Timing/Timeframe: When will they make a decision?

    Each dimension can have custom stages and be enabled/disabled independently.

    Attributes:
        id: Unique sales coach ID (read-only)
        name: Sales coach name
        active: Whether this coach is active
        budgetActive: Enable budget qualification
        budgetStages: Custom budget stages
        decisionMakersActive: Enable decision maker tracking
        decisionMakersStages: Custom decision maker stages
        decisionMakersTitles: Required decision maker titles/roles
        decisionMakersType: Type of decision maker tracking
        solutionActive: Enable solution/need tracking
        solutionStages: Custom solution stages
        timeframeActive: Enable timeframe/timing tracking
        timeframeStages: Custom timeframe stages
        nextStepActive: Enable next step tracking
        nextStepOnlyAppointments: Restrict next steps to appointments only
        checklist: Custom checklist items
        users: Users assigned to this coach
        roles: Roles assigned to this coach
        decisionMakers: Decision makers tracked
        regBy: User ID who created this coach (read-only)
        regDate: Registration timestamp (read-only)
        modBy: User ID who last modified this coach (read-only)
        modDate: Last modification timestamp (read-only)

    Example:
        >>> # Get and update a sales coach
        >>> coach = await upsales.sales_coaches.get(1)
        >>> await coach.edit(
        ...     budgetActive=True,
        ...     timeframeActive=True,
        ...     nextStepActive=True
        ... )
        >>>
        >>> # Check which BANT dimensions are enabled
        >>> if coach.budgetActive:
        ...     print("Budget tracking enabled")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique sales coach ID")
    regBy: int = Field(frozen=True, description="User ID who created this coach")
    regDate: str = Field(frozen=True, description="Registration timestamp (ISO 8601)")
    modBy: int = Field(frozen=True, description="User ID who last modified this coach")
    modDate: str | None = Field(
        None, frozen=True, description="Last modification timestamp (ISO 8601)"
    )

    # Basic configuration
    name: NonEmptyStr = Field(description="Sales coach name")
    active: bool = Field(description="Whether this coach is active")

    # Budget (BANT - B)
    budgetActive: bool = Field(description="Enable budget qualification tracking")
    budgetStages: list[Any] = Field(
        default_factory=list, description="Custom budget qualification stages"
    )

    # Authority/Decision Makers (BANT - A)
    decisionMakersActive: bool = Field(description="Enable decision maker tracking")
    decisionMakersStages: list[Any] = Field(
        default_factory=list, description="Custom decision maker stages"
    )
    decisionMakersTitles: list[dict[str, Any]] = Field(
        default_factory=list, description="Required decision maker titles/roles"
    )
    decisionMakersType: Any | None = Field(None, description="Type of decision maker tracking")
    decisionMakers: list[Any] = Field(default_factory=list, description="Tracked decision makers")

    # Need/Solution (BANT - N)
    solutionActive: bool = Field(description="Enable solution/need tracking")
    solutionStages: list[Any] = Field(
        default_factory=list, description="Custom solution qualification stages"
    )

    # Timing/Timeframe (BANT - T)
    timeframeActive: bool = Field(description="Enable timeframe/timing tracking")
    timeframeStages: list[Any] = Field(default_factory=list, description="Custom timeframe stages")

    # Next steps
    nextStepActive: bool = Field(description="Enable next step tracking")
    nextStepOnlyAppointments: bool = Field(
        description="Restrict next steps to appointments only (vs any activity)"
    )

    # Additional configuration
    checklist: list[Any] = Field(default_factory=list, description="Custom checklist items")
    users: list[Any] = Field(default_factory=list, description="Users assigned to this coach")
    roles: list[Any] = Field(default_factory=list, description="Roles assigned to this coach")

    async def edit(self, **kwargs: Unpack[SalesCoachUpdateFields]) -> "SalesCoach":
        """
        Edit this sales coach.

        Updates coach configuration with specified fields. All fields are optional.
        Uses Pydantic v2 optimized serialization (5-50x faster than v1).

        Args:
            **kwargs: Fields to update (see SalesCoachUpdateFields for available options).

        Returns:
            Updated sales coach with refreshed data from API.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> coach = await upsales.sales_coaches.get(1)
            >>> # Enable all BANT dimensions
            >>> updated = await coach.edit(
            ...     budgetActive=True,
            ...     decisionMakersActive=True,
            ...     solutionActive=True,
            ...     timeframeActive=True
            ... )
            >>> print(f"Updated: {updated.name}")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.sales_coaches.update(self.id, **self.to_api_dict(**kwargs))


class PartialSalesCoach(PartialModel):
    """
    Partial SalesCoach for nested responses.

    Minimal sales coach information included when sales coach appears nested
    in other API responses (e.g., opportunity.salesCoach).

    Typically includes just id and name from the API.

    Example:
        >>> opportunity = await upsales.opportunities.get(123)
        >>> if opportunity.salesCoach:
        ...     print(f"Using coach: {opportunity.salesCoach.name}")
        ...     # Fetch full coach if needed
        ...     full_coach = await opportunity.salesCoach.fetch_full()
    """

    id: int = Field(frozen=True, strict=True, description="Unique sales coach ID")
    name: NonEmptyStr = Field(description="Sales coach name")

    async def fetch_full(self) -> SalesCoach:
        """
        Fetch full sales coach data.

        Returns:
            Full SalesCoach object with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial_coach = opportunity.salesCoach  # PartialSalesCoach
            >>> full_coach = await partial_coach.fetch_full()  # SalesCoach
            >>> print(f"Budget tracking: {full_coach.budgetActive}")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.sales_coaches.get(self.id)

    async def edit(self, **kwargs: Unpack[SalesCoachUpdateFields]) -> SalesCoach:
        """
        Edit this sales coach.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full SalesCoach object.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> await partial_coach.edit(active=True)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.sales_coaches.update(self.id, **kwargs)
