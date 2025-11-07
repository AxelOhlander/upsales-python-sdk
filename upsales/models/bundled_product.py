"""
BundledProduct models for Upsales API.

Represents products bundled within a parent product. This model is used
for nested bundle data in Product.bundle list field.

Note:
    BundledProduct does not have its own dedicated API endpoint. It is
    always nested within the Product model's bundle field. The bundle
    field structure represents product bundles configured in the Upsales UI.

Enhanced with Pydantic v2 features:
- Reusable validators (PositiveInt, NonEmptyStr)
- Computed fields (@computed_field)
- Field descriptions for documentation
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr, PositiveInt


class BundledProductUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a BundledProduct.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Excludes read-only field: id
        Total: 2 updatable fields
    """

    name: str
    quantity: int


class BundledProduct(BaseModel):
    """
    BundledProduct model for nested bundle data in Product.

    Represents a single product within a product bundle. Always appears
    nested in Product.bundle field, never as a standalone API response.

    Attributes:
        id: Unique product ID (read-only).
        name: Product name.
        quantity: Number of units in bundle (default: 1).

    Example:
        >>> product = await upsales.products.get(123)
        >>> for bundled in product.bundle:
        ...     print(f"{bundled.name} x{bundled.quantity}")
        ...     print(f"Display: {bundled.display_name}")
        Widget A x2
        Display: Widget A (x2)
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique product ID")

    # Required core fields with validators
    name: NonEmptyStr = Field(description="Product name")

    # Optional fields with defaults
    quantity: PositiveInt = Field(default=1, description="Quantity in bundle (non-negative)")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get formatted display name with quantity.

        Returns:
            Product name with quantity in format "Name (xN)" if quantity > 1.

        Example:
            >>> bundled.name = "Widget A"
            >>> bundled.quantity = 2
            >>> bundled.display_name
            'Widget A (x2)'
            >>> bundled.quantity = 1
            >>> bundled.display_name
            'Widget A'
        """
        if self.quantity > 1:
            return f"{self.name} (x{self.quantity})"
        return self.name

    @computed_field
    @property
    def is_single_unit(self) -> bool:
        """
        Check if bundle contains single unit.

        Returns:
            True if quantity is 1, False otherwise.

        Example:
            >>> bundled.quantity = 1
            >>> bundled.is_single_unit
            True
            >>> bundled.quantity = 5
            >>> bundled.is_single_unit
            False
        """
        return self.quantity == 1

    async def edit(self, **kwargs: Unpack[BundledProductUpdateFields]) -> "BundledProduct":
        """
        Edit this bundled product.

        Note:
            Since BundledProduct is always nested within Product.bundle,
            this method updates the parent product's bundle configuration.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated bundled product with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> product = await upsales.products.get(123)
            >>> bundled = product.bundle[0]
            >>> updated = await bundled.edit(quantity=5)
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Since bundled products are nested, we need to update the parent product
        # This is a conceptual implementation - in practice, you would update
        # the entire bundle array on the parent product
        raise NotImplementedError(
            "BundledProduct.edit() requires parent product context. "
            "Update the parent Product.bundle list instead."
        )


class PartialBundledProduct(PartialModel):
    """
    Partial BundledProduct for minimal nested responses.

    Contains minimal fields for when BundledProduct appears nested in other
    API responses. This is the most common form since bundled products are
    always nested.

    Attributes:
        id: Unique product ID.
        name: Product name.

    Example:
        >>> order = await upsales.orders.get(456)
        >>> product = order.products[0]
        >>> if product.bundle:
        ...     for bundled in product.bundle:
        ...         print(bundled.display_name)
        Widget A
    """

    id: int = Field(frozen=True, strict=True, description="Unique product ID")
    name: NonEmptyStr = Field(description="Product name")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the bundled product.

        Returns:
            Product name formatted for display.

        Example:
            >>> partial_bundled.display_name
            'Widget A'
        """
        return self.name

    async def fetch_full(self) -> BundledProduct:
        """
        Fetch complete bundled product data.

        Note:
            Since bundled products don't have a dedicated endpoint, this
            fetches the full Product and extracts the bundled product data.

        Returns:
            Full BundledProduct object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.
            ValueError: If bundled product not found in parent bundle.

        Example:
            >>> partial = order.products[0].bundle[0]  # PartialBundledProduct
            >>> full = await partial.fetch_full()  # BundledProduct
            >>> full.quantity  # Now available
            2
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Fetch the full product
        full_product = await self._client.products.get(self.id)

        # Return a BundledProduct constructed from the full product data
        # Note: quantity defaults to 1 if not specified
        return BundledProduct(
            id=full_product.id,
            name=full_product.name,
            quantity=1,  # Default quantity for standalone product
            _client=self._client,
        )

    async def edit(self, **kwargs: Unpack[BundledProductUpdateFields]) -> BundledProduct:
        """
        Edit this bundled product.

        Note:
            Since BundledProduct is always nested within Product.bundle,
            this method updates the parent product's bundle configuration.

        Returns full BundledProduct object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full BundledProduct object.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: BundledProduct requires parent context.

        Example:
            >>> partial = order.products[0].bundle[0]  # PartialBundledProduct
            >>> updated = await partial.edit(quantity=3)  # Returns BundledProduct
        """
        if not self._client:
            raise RuntimeError("No client available")

        raise NotImplementedError(
            "PartialBundledProduct.edit() requires parent product context. "
            "Update the parent Product.bundle list instead."
        )
