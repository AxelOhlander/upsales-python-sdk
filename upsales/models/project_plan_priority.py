"""
ProjectPlanPriority models for Upsales API.

Generated from /api/v2/projectPlanPriority endpoint.
Analysis based on 3 samples.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for boolean helpers
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class ProjectPlanPriorityUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ProjectPlanPriority.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    category: str
    isDefault: bool


class ProjectPlanPriority(BaseModel):
    """
    ProjectPlanPriority model from /api/v2/projectPlanPriority.

    Represents priority levels for project plans (LOW, MEDIUM, HIGH).
    Used to categorize and prioritize project plans in Upsales.

    Generated from 3 samples with field analysis.

    Example:
        >>> priority = await upsales.project_plan_priorities.get(1)
        >>> priority.name
        'Låg'
        >>> priority.category
        'LOW'
        >>> priority.is_default
        True
        >>> await priority.edit(name="Low Priority")
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique priority ID")

    # Required updatable fields
    name: NonEmptyStr = Field(description="Priority display name")
    category: NonEmptyStr = Field(description="Priority category (LOW, MEDIUM, HIGH)")
    isDefault: bool = Field(
        default=False,
        description="Whether this is a default system priority",
    )

    @computed_field
    @property
    def is_default(self) -> bool:
        """
        Check if this is a default priority.

        Returns:
            True if isDefault is True, False otherwise.

        Example:
            >>> priority.is_default
            True
        """
        return self.isDefault is True

    @computed_field
    @property
    def is_low(self) -> bool:
        """
        Check if this is a low priority.

        Returns:
            True if category is 'LOW', False otherwise.

        Example:
            >>> priority.is_low
            True
        """
        return self.category == "LOW"

    @computed_field
    @property
    def is_medium(self) -> bool:
        """
        Check if this is a medium priority.

        Returns:
            True if category is 'MEDIUM', False otherwise.

        Example:
            >>> priority.is_medium
            False
        """
        return self.category == "MEDIUM"

    @computed_field
    @property
    def is_high(self) -> bool:
        """
        Check if this is a high priority.

        Returns:
            True if category is 'HIGH', False otherwise.

        Example:
            >>> priority.is_high
            False
        """
        return self.category == "HIGH"

    async def edit(
        self, **kwargs: Unpack[ProjectPlanPriorityUpdateFields]
    ) -> "ProjectPlanPriority":
        """
        Edit this project plan priority.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated priority with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> priority = await upsales.project_plan_priorities.get(1)
            >>> updated = await priority.edit(
            ...     name="Low Priority",
            ...     category="LOW"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_priorities.update(
            self.id, **self.to_update_dict(**kwargs)
        )


class PartialProjectPlanPriority(PartialModel):
    """
    Partial ProjectPlanPriority for nested responses.

    Contains minimal fields for when ProjectPlanPriority appears nested in other
    API responses (e.g., in project plan objects).

    Use fetch_full() to get complete ProjectPlanPriority object with all fields.

    Example:
        >>> # When priority appears nested in a project plan
        >>> partial_priority = project_plan.priority  # PartialProjectPlanPriority
        >>> full_priority = await partial_priority.fetch_full()  # ProjectPlanPriority
    """

    id: int = Field(frozen=True, strict=True, description="Unique priority ID")
    name: NonEmptyStr = Field(description="Priority display name")
    category: NonEmptyStr = Field(description="Priority category (LOW, MEDIUM, HIGH)")

    async def fetch_full(self) -> ProjectPlanPriority:
        """
        Fetch complete priority data.

        Returns:
            Full ProjectPlanPriority object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = project_plan.priority  # PartialProjectPlanPriority
            >>> full = await partial.fetch_full()  # ProjectPlanPriority
            >>> full.is_default  # Now available
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_priorities.get(self.id)

    async def edit(self, **kwargs: Unpack[ProjectPlanPriorityUpdateFields]) -> ProjectPlanPriority:
        """
        Edit this priority.

        Returns full ProjectPlanPriority object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full ProjectPlanPriority object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = project_plan.priority  # PartialProjectPlanPriority
            >>> updated = await partial.edit(name="Low")  # Returns ProjectPlanPriority
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_priorities.update(self.id, **kwargs)
