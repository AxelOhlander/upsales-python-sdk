"""Salesboard card models for Upsales API.

This module defines models for salesboard cards (custom salesboard view configurations).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import SalesboardCardUpdateFields


class SalesboardCard(BaseModel):
    """Salesboard card model.

    Represents a salesboard card configuration for custom salesboard views.

    Attributes:
        id: Unique salesboard card ID (read-only).
        config: Card configuration (required for creation).
        custom: Custom fields list.

    Example:
        ```python
        # Create salesboard card (administrator only)
        card = await upsales.salesboard_cards.create(
            config={"type": "pipeline", "settings": {}}
        )

        # Update salesboard card
        card.config = {"type": "pipeline", "settings": {"view": "compact"}}
        updated = await card.edit()

        # Or use edit with parameters
        updated = await card.edit(config={"type": "pipeline", "settings": {}})
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique salesboard card ID")

    # Updatable fields
    config: dict[str, Any] = Field(description="Card configuration")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            card = await upsales.salesboard_cards.get(1)
            value = card.custom_fields.get(11)
            card.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    async def edit(self, **kwargs: Unpack[SalesboardCardUpdateFields]) -> SalesboardCard:
        """Edit this salesboard card with type-safe field updates.

        Args:
            **kwargs: Fields to update (config, custom).

        Returns:
            Updated SalesboardCard instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If salesboard card no longer exists.

        Example:
            ```python
            card = await upsales.salesboard_cards.get(1)

            # Update config
            updated = await card.edit(config={"type": "pipeline", "settings": {}})
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.salesboard_cards.update(self.id, **self.to_api_dict(**kwargs))


class PartialSalesboardCard(PartialModel):
    """Partial salesboard card model for nested responses.

    Used when salesboard cards appear as nested objects in API responses.

    Attributes:
        id: Unique salesboard card ID.
        config: Card configuration.

    Example:
        ```python
        # Fetch full salesboard card from partial
        partial: PartialSalesboardCard = some_object.salesboard_card
        full: SalesboardCard = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(config={})
        ```
    """

    id: int = Field(description="Unique salesboard card ID")
    config: dict[str, Any] | None = Field(None, description="Card configuration")

    async def fetch_full(self) -> SalesboardCard:
        """Fetch complete salesboard card data.

        Returns:
            Full SalesboardCard instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If salesboard card not found.

        Example:
            ```python
            partial = PartialSalesboardCard(id=1, config={})
            full = await partial.fetch_full()
            print(full.config)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.salesboard_cards.get(self.id)

    async def edit(self, **kwargs: Unpack[SalesboardCardUpdateFields]) -> SalesboardCard:
        """Edit this salesboard card.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated SalesboardCard instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If salesboard card not found.

        Example:
            ```python
            partial = PartialSalesboardCard(id=1, config={})
            updated = await partial.edit(config={"type": "pipeline"})
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.salesboard_cards.update(self.id, **kwargs)
