"""
Product models for Upsales API.

Generated from /api/v2/products endpoint.
Analysis based on 17 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.bundled_product import BundledProduct
from upsales.models.category import PartialCategory
from upsales.models.currency_configuration import (
    CurrencyConfiguration,
)
from upsales.models.custom_fields import CustomFields
from upsales.models.price_tier import PriceTier
from upsales.validators import BinaryFlag, CustomFieldsList, NonEmptyStr


class ProductUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Product.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Excludes read-only field: id
        Total: 24 updatable fields
    """

    # Core fields
    name: str
    active: int
    articleNo: str
    description: Any

    # Pricing fields
    listPrice: int
    purchaseCost: int
    sortId: int

    # Recurring fields
    isRecurring: int
    isMultiCurrency: int
    recurringInterval: int

    # Bundle fields
    bundle: list[Any]
    bundleEditable: bool
    bundleFixedPrice: bool
    bundlePriceAdjustment: int
    bundlePriceAdjustmentType: Any

    # List fields
    custom: list[Any]
    tiers: list[Any]
    roles: list[Any]
    currencies: list[Any]

    # Object fields
    category: dict[str, Any]
    projectPlanTemplate: dict[str, Any]

    # Metadata
    importId: Any
    userEditable: bool
    userRemovable: bool


class Product(BaseModel):
    """
    Product model from /api/v2/products.

    Represents a product in the Upsales system. Generated from 17
    real product records with comprehensive field analysis.

    Example:
        >>> product = await upsales.products.get(1)
        >>> product.name
        'Premium Plan'
        >>> product.is_active
        True
        >>> product.is_recurring
        True
        >>> product.profit_margin
        45.5
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique product ID")

    # Required core fields with validators
    name: NonEmptyStr = Field(description="Product name")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

    # Required pricing fields
    listPrice: int = Field(default=0, description="List price")
    purchaseCost: int = Field(default=0, description="Purchase cost")
    sortId: int = Field(default=0, description="Sort order ID")

    # Binary flags
    isRecurring: BinaryFlag = Field(
        default=0, description="Recurring product flag (0=one-time, 1=recurring)"
    )
    isMultiCurrency: BinaryFlag = Field(
        default=0, description="Multi-currency support (0=no, 1=yes)"
    )

    # Boolean flags
    bundleEditable: bool = Field(default=False, description="Bundle is editable")
    bundleFixedPrice: bool = Field(default=False, description="Bundle has fixed price")
    userEditable: bool = Field(default=True, description="User can edit")
    userRemovable: bool = Field(default=True, description="User can remove")

    # Optional fields
    articleNo: str | None = Field(None, description="Article number/SKU")
    description: Any | None = Field(None, description="Product description")
    recurringInterval: int | None = Field(
        None, description="Recurring interval in months (if isRecurring=1)"
    )
    bundlePriceAdjustment: int | None = Field(None, description="Bundle price adjustment amount")
    bundlePriceAdjustmentType: Any | None = Field(None, description="Bundle price adjustment type")
    importId: Any | None = Field(None, description="Import ID")

    # List fields
    custom: CustomFieldsList = Field(default=[], description="Custom fields")
    bundle: list[BundledProduct] = Field(default=[], description="Bundled products")
    tiers: list[PriceTier] = Field(default=[], description="Price tiers")
    roles: list[Any] = Field(default=[], description="Roles with access")
    currencies: list[CurrencyConfiguration] = Field(
        default=[], description="Currency configurations"
    )

    # Object fields
    category: PartialCategory | None = Field(None, description="Product category")
    projectPlanTemplate: dict[str, Any] | None = Field(
        None, description="Project plan template (complex structure, kept as dict)"
    )

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> product.custom_fields[11]  # By field ID
            'value'
            >>> product.custom_fields["SKU"] = "PROD-001"  # By alias
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if product is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> product.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def is_recurring(self) -> bool:
        """
        Check if product is recurring.

        Returns:
            True if isRecurring flag is 1, False otherwise.

        Example:
            >>> product.is_recurring
            True
        """
        return self.isRecurring == 1

    @computed_field
    @property
    def profit_margin(self) -> float:
        """
        Calculate profit margin percentage.

        Returns:
            Profit margin as percentage. Returns 0 if listPrice is 0.

        Example:
            >>> product.profit_margin
            45.5
        """
        if self.listPrice == 0:
            return 0.0
        return ((self.listPrice - self.purchaseCost) / self.listPrice) * 100

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes fields without values to keep payloads clean.

        Args:
            custom: List of custom field dicts.

        Returns:
            Cleaned list with only fields that have values.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[ProductUpdateFields]) -> "Product":
        """
        Edit this product.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated product with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> product = await upsales.products.get(1)
            >>> updated = await product.edit(
            ...     name="Premium Plan v2",
            ...     listPrice=9999,
            ...     active=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.update(self.id, **self.to_api_dict(**kwargs))


class PartialProduct(PartialModel):
    """
    Partial Product for nested responses.

    Contains minimal fields for when Product appears nested in other
    API responses (e.g., in order line items).

    Use fetch_full() to get complete Product object with all fields.

    Example:
        >>> order = await upsales.orders.get(1)
        >>> product = order.products[0]  # PartialProduct
        >>> full_product = await product.fetch_full()  # Product
    """

    id: int = Field(frozen=True, strict=True, description="Unique product ID")
    name: NonEmptyStr = Field(description="Product name")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the product.

        Returns:
            Product name formatted for display.

        Example:
            >>> partial_product.display_name
            'Premium Plan'
        """
        return self.name

    async def fetch_full(self) -> Product:
        """
        Fetch complete product data.

        Returns:
            Full Product object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = order.products[0]  # PartialProduct
            >>> full = await partial.fetch_full()  # Product
            >>> full.listPrice  # Now available
            9999
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.get(self.id)

    async def edit(self, **kwargs: Unpack[ProductUpdateFields]) -> Product:
        """
        Edit this product.

        Returns full Product object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Product object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = order.products[0]  # PartialProduct
            >>> updated = await partial.edit(listPrice=10999)  # Returns Product
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.update(self.id, **kwargs)
