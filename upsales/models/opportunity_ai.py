"""
OpportunityAI models for Upsales API.

This endpoint provides AI-analyzed data for opportunities, including:
- Activity tracking (appointments, calls, todos)
- Risk assessments
- Decision maker involvement
- Complete opportunity details

This is a READ-ONLY resource - no create/update/delete operations supported.

The endpoint structure:
- GET /opportunityAI: Returns dict mapping opportunity IDs to AI analysis
- GET /opportunityAI/:id: Returns AI analysis for single opportunity

Enhanced with Pydantic v2 features:
- Strict type checking
- Computed fields (@computed_field)
- Field descriptions (100% coverage)
- Frozen fields (all fields read-only)
"""

from typing import Any

from pydantic import Field, computed_field, model_validator

from upsales.models.base import BaseModel, PartialModel


class OpportunityAI(BaseModel):
    """
    AI-analyzed opportunity data from /api/v2/opportunityAI/:id.

    This model contains AI-derived insights about an opportunity including
    activity tracking, decision maker involvement, and risk factors.

    All fields are read-only (frozen=True) as this endpoint does not support updates.

    Note:
        The 'id' field is extracted from the nested opportunity object during
        validation, as the OpportunityAI endpoint doesn't return a top-level ID.

    Example:
        >>> async with Upsales.from_env() as client:
        ...     ai_data = await client.opportunity_ai.get(45)
        ...     print(ai_data.is_decision_maker_involved)
        ...     print(ai_data.opportunity["description"])
    """

    # ID from nested opportunity (required by BaseModel)
    id: int = Field(frozen=True, description="Opportunity ID (extracted from opportunity object)")

    # AI Analysis Fields
    appointment: dict[str, Any] = Field(
        default_factory=dict,
        frozen=True,
        alias="meeting",
        description="Appointment/meeting data for this opportunity",
    )
    activity: dict[str, Any] = Field(
        default_factory=dict, frozen=True, description="Activity data for this opportunity"
    )
    allActivity: dict[str, Any] = Field(
        default_factory=dict,
        frozen=True,
        alias="allActivity",
        description="All activity data combined",
    )
    isDecisionMakerInvolved: bool = Field(
        False, frozen=True, description="Whether decision maker is involved"
    )
    decisionMakerId: int | None = Field(
        None, frozen=True, description="ID of decision maker if involved"
    )
    avg: float | None = Field(
        None, frozen=True, description="Average metric (usage context-dependent)"
    )
    checklist: list[dict[str, Any]] = Field(
        default_factory=list, frozen=True, description="Checklist items for opportunity"
    )

    # Complete Opportunity Object
    opportunity: dict[str, Any] | None = Field(
        None,
        frozen=True,
        description="Complete opportunity object with all standard fields (returned by get() but not get_all())",
    )

    @model_validator(mode="before")
    @classmethod
    def extract_id_from_opportunity(cls, data: Any) -> Any:
        """
        Extract ID from nested opportunity object before validation.

        The API response doesn't include a top-level 'id' field, so we extract
        it from the nested opportunity object.

        Args:
            data: Raw data from API.

        Returns:
            Data with 'id' field added.
        """
        if isinstance(data, dict) and "opportunity" in data and "id" not in data:
            opportunity = data.get("opportunity", {})
            if isinstance(opportunity, dict):
                data["id"] = opportunity.get("id", 0)
        return data

    @computed_field
    @property
    def opportunity_description(self) -> str:
        """
        Extract opportunity description from nested opportunity object.

        Returns:
            Opportunity description or empty string if not available.
        """
        if not self.opportunity:
            return ""
        value = self.opportunity.get("description", "")
        return str(value) if value is not None else ""

    @computed_field
    @property
    def opportunity_value(self) -> int:
        """
        Extract opportunity value from nested opportunity object.

        Returns:
            Opportunity value or 0 if not available.
        """
        if not self.opportunity:
            return 0
        value = self.opportunity.get("value", 0)
        return int(value) if value is not None else 0

    @computed_field
    @property
    def opportunity_stage(self) -> dict[str, Any]:
        """
        Extract opportunity stage from nested opportunity object.

        Returns:
            Stage dict with 'id' and 'name', or empty dict if not available.
        """
        if not self.opportunity:
            return {}
        stage = self.opportunity.get("stage", {})
        return dict(stage) if isinstance(stage, dict) else {}

    @computed_field
    @property
    def has_appointment(self) -> bool:
        """
        Check if opportunity has appointment data.

        Returns:
            True if appointment data exists and is not empty.
        """
        return bool(self.appointment)

    @computed_field
    @property
    def has_activity(self) -> bool:
        """
        Check if opportunity has any activity.

        Returns:
            True if activity data exists and is not empty.
        """
        return bool(self.activity) or bool(self.allActivity)

    async def edit(self, **kwargs: Any) -> "OpportunityAI":
        """
        Not supported for read-only OpportunityAI resource.

        The OpportunityAI endpoint only supports GET operations. Use the
        underlying Opportunity resource to modify opportunity data.

        Raises:
            RuntimeError: This endpoint is read-only.
        """
        raise RuntimeError(
            "OpportunityAI is a read-only resource. "
            "To edit opportunities, use client.opportunities.update() instead."
        )


class PartialOpportunityAI(PartialModel):
    """
    Partial OpportunityAI for nested responses.

    Note: This endpoint does not typically return nested OpportunityAI objects,
    but this class is provided for API consistency.

    Example:
        >>> # Fetch full AI data from partial
        >>> full_ai = await partial_ai.fetch_full()
    """

    id: int = Field(..., description="Opportunity ID")

    async def fetch_full(self) -> OpportunityAI:
        """
        Fetch full OpportunityAI data.

        Returns:
            Complete OpportunityAI object with all AI analysis.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.opportunity_ai.get(self.id)
