"""
Pricelist models for Upsales API.

Generated from /api/v2/pricelists endpoint.
Analysis based on 11 samples.

Enhanced with Pydantic v2 features:
- Frozen fields for read-only data
- Computed properties for boolean helpers
- Field descriptions
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class PricelistUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Pricelist.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    code: str
    active: bool
    isDefault: bool
    showDiscount: bool


class Pricelist(BaseModel):
    """
    Pricelist model from /api/v2/pricelists.

    Represents a price list in the Upsales system with full data.
    Price lists are used to manage product pricing for different customers or scenarios.

    Generated from 11 samples with field analysis.

    Example:
        >>> pricelist = await upsales.pricelists.get(1)
        >>> pricelist.name
        'Standard Pricing'
        >>> pricelist.is_active  # Computed property
        True
        >>> await pricelist.edit(active=False)  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique pricelist ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date (ISO 8601)")
    regBy: int = Field(frozen=True, description="User ID who registered this pricelist")
    modDate: str | None = Field(None, frozen=True, description="Last modification date (ISO 8601)")
    modBy: int = Field(frozen=True, description="User ID who last modified this pricelist")

    # Required fields
    name: NonEmptyStr = Field(description="Pricelist name")
    active: bool = Field(description="Active status (true=active, false=inactive)")
    isDefault: bool = Field(description="Default pricelist flag (true=default, false=not default)")
    showDiscount: bool = Field(
        description="Show discount flag (true=show discounts, false=hide discounts)"
    )

    # Optional fields
    code: str | None = Field(None, description="Pricelist code/identifier")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if pricelist is active.

        Returns:
            True if active, False otherwise.

        Example:
            >>> pricelist.is_active
            True
        """
        return self.active

    @computed_field
    @property
    def is_default(self) -> bool:
        """
        Check if this is the default pricelist.

        Returns:
            True if default, False otherwise.

        Example:
            >>> pricelist.is_default
            True
        """
        return self.isDefault

    async def edit(self, **kwargs: Unpack[PricelistUpdateFields]) -> "Pricelist":
        """
        Edit this pricelist.

        Uses Pydantic v2's optimized serialization via to_update_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated pricelist with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> pricelist = await upsales.pricelists.get(1)
            >>> updated = await pricelist.edit(
            ...     name="Premium Pricing",
            ...     active=True
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pricelists.update(self.id, **self.to_update_dict(**kwargs))


class PartialPricelist(PartialModel):
    """
    Partial Pricelist for nested responses.

    Contains minimal fields for when Pricelist appears nested in other
    API responses (e.g., in order items, product pricing, etc.).

    Use fetch_full() to get complete Pricelist object with all fields.

    Example:
        >>> product = await upsales.products.get(1)
        >>> pricelist = product.pricelist  # PartialPricelist
        >>> full_pricelist = await pricelist.fetch_full()  # Now Pricelist
    """

    id: int = Field(frozen=True, strict=True, description="Unique pricelist ID")
    name: NonEmptyStr = Field(description="Pricelist name")
    active: bool = Field(description="Active status")

    async def fetch_full(self) -> Pricelist:
        """
        Fetch complete pricelist data.

        Returns:
            Full Pricelist object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = product.pricelist  # PartialPricelist
            >>> full = await partial.fetch_full()  # Pricelist
            >>> full.isDefault  # Now available
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pricelists.get(self.id)

    async def edit(self, **kwargs: Unpack[PricelistUpdateFields]) -> Pricelist:
        """
        Edit this pricelist.

        Returns full Pricelist object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Pricelist object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = product.pricelist  # PartialPricelist
            >>> updated = await partial.edit(name="New Name")  # Returns Pricelist
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pricelists.update(self.id, **kwargs)
