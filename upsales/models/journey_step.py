"""
Journey step models for Upsales API.

Journey steps represent stages in the customer lifecycle (e.g., Lead, MQL, Customer).
This is a read-only system configuration endpoint.

Generated from /api/v2/journeySteps endpoint.
Analysis based on 9 samples.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for derived properties
- Strict type checking on immutable fields
- Optimized serialization via to_api_dict()
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

from upsales.models.base import PartialModel

if TYPE_CHECKING:
    from upsales.client import Upsales


class JourneyStepUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Journey Step.

    Note: JourneySteps is typically read-only in most Upsales installations.
    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    color: str
    colorName: str
    priority: int
    value: str


class JourneyStep(PydanticBase):
    """
    Journey step model representing a stage in the customer lifecycle.

    Journey steps are system-defined stages like Lead, MQL (Marketing Qualified Lead),
    SQL (Sales Qualified Lead), Customer, etc. Each step has a unique value identifier,
    display name, priority order, and color coding for visual representation.

    This is typically a read-only configuration endpoint in most Upsales installations.

    Note: Unlike most models, JourneyStep uses 'value' as the identifier instead of 'id'.

    Attributes:
        value: Unique identifier for the journey step (e.g., "lead", "mql", "customer")
        name: Display name of the journey step
        priority: Sort order/position in the journey (1-based)
        color: Hex color code for visual representation
        colorName: Named color identifier for the journey step

    Example:
        >>> # Get all journey steps
        >>> steps = await upsales.journey_steps.list_all()
        >>> for step in steps:
        ...     print(f"{step.name} ({step.value}) - Priority {step.priority}")
        Lead (lead) - Priority 1
        Marketing Qualified Lead (MQL) (mql) - Priority 2

        >>> # Find a specific journey step
        >>> customer_step = next(s for s in steps if s.value == "customer")
        >>> print(f"Customer step: {customer_step.name} ({customer_step.color})")
        Customer step: Kund (#5CB85C)
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    # All fields are effectively read-only (system configuration)
    # But not marked as frozen since the endpoint might support updates in some installations
    value: str = Field(
        description="Unique identifier for the journey step (e.g., 'lead', 'mql', 'customer')"
    )
    name: str = Field(description="Display name of the journey step")
    priority: int = Field(description="Sort order/position in the journey sequence (1-based)")
    color: str = Field(description="Hex color code for visual representation (e.g., '#5CB85C')")
    colorName: str = Field(description="Named color identifier (e.g., 'bright-green', 'purple')")

    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize model with optional client reference.

        Args:
            **data: Model field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        # Use object.__setattr__ to bypass frozen check
        object.__setattr__(self, "_client", client)

    def to_api_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize model for API requests with Pydantic v2 optimized serialization.

        This method uses Pydantic v2's Rust-based serialization (5-50x faster than v1).
        Automatically excludes frozen fields and uses field aliases.

        Args:
            **overrides: Additional fields to override in the output.

        Returns:
            Dictionary suitable for API requests.

        Example:
            >>> step = await upsales.journey_steps.get_by_value("lead")
            >>> api_data = step.to_api_dict()
            >>> # Or with overrides
            >>> api_data = step.to_api_dict(name="New Lead Name")
        """
        # Get model dump with aliases and exclude unset
        data = self.model_dump(by_alias=True, exclude_unset=True, exclude={"_client"})
        # Apply overrides
        data.update(overrides)
        return data

    @computed_field
    @property
    def is_lead_stage(self) -> bool:
        """
        Check if this is a lead-related stage.

        Returns:
            True if the journey step represents a lead stage (lead, mql, sql, assigned).

        Example:
            >>> step = await upsales.journey_steps.get_by_value("mql")
            >>> if step.is_lead_stage:
            ...     print("This is a lead stage")
        """
        lead_values = {"lead", "mql", "sql", "assigned"}
        return self.value.lower() in lead_values

    @computed_field
    @property
    def is_customer_stage(self) -> bool:
        """
        Check if this represents a customer stage.

        Returns:
            True if the journey step represents customer status.

        Example:
            >>> step = await upsales.journey_steps.get_by_value("customer")
            >>> if step.is_customer_stage:
            ...     print("This is a customer stage")
        """
        return self.value.lower() in {"customer", "lost_customer"}

    @computed_field
    @property
    def is_opportunity_stage(self) -> bool:
        """
        Check if this represents an opportunity/pipeline stage.

        Returns:
            True if the journey step represents pipeline/opportunity status.

        Example:
            >>> step = await upsales.journey_steps.get_by_value("pipeline")
            >>> if step.is_opportunity_stage:
            ...     print("This is an opportunity stage")
        """
        return self.value.lower() == "pipeline"

    @computed_field
    @property
    def is_negative_outcome(self) -> bool:
        """
        Check if this represents a negative outcome.

        Returns:
            True if the journey step represents lost/disqualified status.

        Example:
            >>> step = await upsales.journey_steps.get_by_value("disqualified")
            >>> if step.is_negative_outcome:
            ...     print("This represents a lost opportunity")
        """
        negative_values = {"lost_opportunity", "disqualified", "lost_customer"}
        return self.value.lower() in negative_values

    async def edit(self, **kwargs: Unpack[JourneyStepUpdateFields]) -> "JourneyStep":
        """
        Edit this journey step.

        Note: JourneySteps is typically read-only in most Upsales installations.
        This method is not supported as the endpoint doesn't allow updates.

        Args:
            **kwargs: Fields to update (name, color, colorName, priority, value).

        Returns:
            Updated journey step instance.

        Raises:
            NotImplementedError: Journey steps are read-only and cannot be updated.

        Example:
            >>> step = await upsales.journey_steps.get_by_value("lead")
            >>> try:
            ...     updated = await step.edit(name="New Lead")
            ... except NotImplementedError:
            ...     print("Journey steps are read-only in this installation")
        """
        raise NotImplementedError(
            "Journey steps are read-only and cannot be updated. "
            "This is a system configuration endpoint."
        )


class PartialJourneyStep(PartialModel):
    """
    Partial Journey Step for nested responses.

    Used when journey step data appears nested in other API responses
    (e.g., in company or contact objects).

    Attributes:
        value: Unique identifier for the journey step
        name: Display name of the journey step

    Example:
        >>> company = await upsales.companies.get(123)
        >>> if company.journey_step:
        ...     print(f"Company is at: {company.journey_step.name}")
        ...     # Fetch full details if needed
        ...     full_step = await company.journey_step.fetch_full()
    """

    value: str = Field(description="Unique identifier for the journey step")
    name: str = Field(description="Display name of the journey step")

    async def fetch_full(self) -> "JourneyStep":
        """
        Fetch full journey step data.

        Returns:
            Complete JourneyStep instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = company.journey_step
            >>> full = await partial.fetch_full()
            >>> print(f"Color: {full.color}, Priority: {full.priority}")
        """
        if not self._client:
            raise RuntimeError("No client available")
        result = await self._client.journey_steps.get_by_value(self.value)
        if result is None:
            raise RuntimeError(f"Journey step with value '{self.value}' not found")
        return result

    async def edit(self, **kwargs: Unpack[JourneyStepUpdateFields]) -> "JourneyStep":
        """
        Edit this journey step.

        Note: JourneySteps is typically read-only. This method is not supported.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated journey step.

        Raises:
            NotImplementedError: Journey steps are read-only and cannot be updated.
        """
        raise NotImplementedError(
            "Journey steps are read-only and cannot be updated. "
            "This is a system configuration endpoint."
        )
