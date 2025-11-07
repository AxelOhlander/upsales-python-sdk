"""
OrderStage models for Upsales API.

Generated from /api/v2/orderStages endpoint.
Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, NonEmptyStr, Percentage


class OrderStageUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an OrderStage.

    All fields are optional (total=False).
    """

    name: str
    probability: int
    exclude: int
    roles: list[Any]


class OrderStage(BaseModel):
    """
    OrderStage model from /api/v2/orderStages.

    Represents a stage in the order/opportunity pipeline with probability
    and role assignments. Enhanced with Pydantic v2 validators, computed
    fields, and optimized serialization.

    Example:
        >>> # Get order stage
        >>> stage = await upsales.order_stages.get(1)
        >>> stage.name
        'Qualified'
        >>>
        >>> # Use computed fields
        >>> stage.is_excluded
        False
        >>> stage.probability_decimal
        0.45
        >>>
        >>> # Edit stage (IDE autocomplete!)
        >>> await stage.edit(
        ...     name="Highly Qualified",
        ...     probability=75
        ... )
    """

    # Read-only fields - set by API, never send in updates
    id: int = Field(frozen=True, strict=True, description="Unique order stage ID")

    # Updatable fields
    name: NonEmptyStr = Field(description="Order stage name")
    probability: Percentage = Field(
        description="Win probability percentage (0-100) for orders at this stage"
    )
    exclude: BinaryFlag = Field(
        description="Exclude from pipeline calculations (0=include, 1=exclude)"
    )
    roles: list[Any] = Field(
        default=[],
        description="List of role IDs that can access this stage",
    )

    # Required fields for updates (Pattern 11 - minimal updates)
    _required_update_fields = {"probability"}

    @computed_field
    @property
    def is_excluded(self) -> bool:
        """
        Check if stage is excluded from pipeline calculations.

        Returns:
            True if exclude flag is 1, False otherwise.

        Example:
            >>> stage.is_excluded
            False
        """
        return self.exclude == 1

    @computed_field
    @property
    def probability_decimal(self) -> float:
        """
        Get probability as decimal (0.0-1.0) for calculations.

        Returns:
            Probability as decimal value between 0 and 1.

        Example:
            >>> stage.probability  # 45
            >>> stage.probability_decimal
            0.45
        """
        return self.probability / 100.0

    async def edit(self, **kwargs: Unpack[OrderStageUpdateFields]) -> "OrderStage":
        """
        Edit this order stage via the API.

        Uses to_update_dict_minimal() to send only changed fields plus
        required fields (probability). This reduces edit conflicts in
        concurrent scenarios.

        Args:
            **kwargs: Fields to update (from OrderStageUpdateFields TypedDict).

        Returns:
            Updated OrderStage object with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> stage = await upsales.order_stages.get(1)
            >>> updated = await stage.edit(
            ...     name="New Stage Name",
            ...     probability=80
            ... )
            >>> print(updated.name)
            'New Stage Name'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.order_stages.update(
            self.id, **self.to_update_dict_minimal(**kwargs)
        )


class PartialOrderStage(PartialModel):
    """
    Partial OrderStage for nested responses.

    Contains minimal fields for when OrderStage appears nested in other
    API responses (e.g., as opportunity stage, order stage reference, etc.).

    Use fetch_full() to get complete OrderStage object with all fields.

    Example:
        >>> opportunity = await upsales.opportunities.get(1)
        >>> stage = opportunity.stage  # PartialOrderStage
        >>> full = await stage.fetch_full()  # Now OrderStage
    """

    # Minimum fields (id + name)
    id: int = Field(frozen=True, strict=True, description="Unique order stage ID")
    name: NonEmptyStr = Field(description="Order stage name")

    async def fetch_full(self) -> OrderStage:
        """
        Fetch complete order stage data from API.

        Returns:
            Full OrderStage object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.stage  # PartialOrderStage
            >>> full = await partial.fetch_full()  # OrderStage
            >>> full.probability
            45
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.order_stages.get(self.id)

    async def edit(self, **kwargs: Any) -> OrderStage:
        """
        Edit order stage via partial reference.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full OrderStage object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.stage  # PartialOrderStage
            >>> updated = await partial.edit(name="New Name")  # Returns OrderStage
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.order_stages.update(self.id, **kwargs)
