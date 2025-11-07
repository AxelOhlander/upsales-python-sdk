"""
Currency configuration models for product multi-currency pricing.

Uses Python 3.13 native type hints and Pydantic v2 patterns.

Currency configurations represent product pricing in different currencies.
Typically nested in Product.currencies list.

Example:
    >>> from upsales.models import CurrencyConfiguration
    >>>
    >>> config = CurrencyConfiguration(
    ...     currency="USD",
    ...     price=100.00,
    ...     listPrice=120.00,
    ... )
    >>> config.currency
    'USD'
    >>> config.discount_amount
    20.0
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

from upsales.validators import NonEmptyStr

if TYPE_CHECKING:
    from upsales.client import Upsales


class CurrencyConfiguration(PydanticBase):
    """
    Currency configuration for product pricing.

    Represents a product's price in a specific currency. Nested in Product.currencies.
    This model has no independent endpoints - it only appears as part of product data.

    Attributes:
        currency: ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')
        price: Price in the specified currency
        listPrice: List/suggested price (optional, for calculating discounts)

    Example:
        >>> config = CurrencyConfiguration(
        ...     currency="USD",
        ...     price=100.00,
        ...     listPrice=120.00,
        ... )
        >>> config.is_discounted
        True
        >>> config.discount_percentage
        16.67
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    currency: NonEmptyStr = Field(description="ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')")
    price: float = Field(description="Price in the specified currency")
    listPrice: float | None = Field(
        default=None, description="List/suggested price for calculating discount (optional)"
    )
    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize currency configuration with optional client reference.

        Args:
            **data: Currency configuration field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        # Use object.__setattr__ to bypass frozen check
        object.__setattr__(self, "_client", client)

    @computed_field
    @property
    def discount_amount(self) -> float | None:
        """
        Calculate discount amount if listPrice exists.

        Returns:
            Discount amount (listPrice - price), or None if no listPrice.

        Example:
            >>> config = CurrencyConfiguration(
            ...     currency="USD",
            ...     price=100.00,
            ...     listPrice=120.00,
            ... )
            >>> config.discount_amount
            20.0
        """
        if self.listPrice is None:
            return None
        return self.listPrice - self.price

    @computed_field
    @property
    def discount_percentage(self) -> float | None:
        """
        Calculate discount percentage if listPrice exists.

        Returns:
            Discount percentage (0-100), or None if no listPrice.

        Example:
            >>> config = CurrencyConfiguration(
            ...     currency="USD",
            ...     price=100.00,
            ...     listPrice=120.00,
            ... )
            >>> config.discount_percentage
            16.67
        """
        if self.listPrice is None or self.listPrice == 0:
            return None
        # discount_amount is guaranteed to be not None here due to listPrice check
        discount = self.discount_amount
        if discount is None:
            return None
        return round((discount / self.listPrice) * 100, 2)

    @computed_field
    @property
    def is_discounted(self) -> bool:
        """
        Check if price is discounted from list price.

        Returns:
            True if listPrice is set and price is less than listPrice.

        Example:
            >>> config = CurrencyConfiguration(
            ...     currency="USD",
            ...     price=100.00,
            ...     listPrice=120.00,
            ... )
            >>> config.is_discounted
            True
        """
        if self.listPrice is None:
            return False
        return self.price < self.listPrice

    async def edit(self, **kwargs: Any) -> "CurrencyConfiguration":
        """
        Edit is not supported for nested CurrencyConfiguration.

        Currency configurations are nested within products and should be
        edited through the parent product's edit() method.

        Args:
            **kwargs: (Unused) Fields to update.

        Returns:
            This method always raises NotImplementedError.

        Raises:
            NotImplementedError: Always - use Product.edit() instead.

        Example:
            >>> config = await product.currencies[0]
            >>> config.edit(price=150)  # Raises NotImplementedError
        """
        raise NotImplementedError(
            "CurrencyConfiguration is nested and read-only. "
            "Edit the parent Product instead using product.edit(currencies=[...])"
        )


class PartialCurrencyConfiguration(PydanticBase):
    """
    Partial currency configuration for nested responses.

    Represents minimal currency configuration information when embedded in
    other API responses. Contains only essential fields: currency and price.

    Use fetch_full() or edit() on parent object to get/modify complete data.

    Attributes:
        currency: ISO 4217 currency code
        price: Price in the specified currency

    Example:
        >>> product = await upsales.products.get(1)
        >>> partial_config = product.currencies[0]  # PartialCurrencyConfiguration
        >>> partial_config.currency
        'USD'
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    currency: NonEmptyStr = Field(description="ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')")
    price: float = Field(description="Price in the specified currency")
    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize partial currency configuration with optional client reference.

        Args:
            **data: Currency configuration field data.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        object.__setattr__(self, "_client", client)

    @computed_field
    @property
    def display_currency(self) -> str:
        """
        Get display string for currency configuration.

        Returns:
            Formatted string like "USD 100.00".

        Example:
            >>> partial_config.display_currency
            'USD 100.00'
        """
        return f"{self.currency} {self.price:.2f}"

    async def fetch_full(self) -> CurrencyConfiguration:
        """
        Convert to full CurrencyConfiguration.

        Since PartialCurrencyConfiguration only has essential fields,
        this returns a full CurrencyConfiguration with the same data.

        Returns:
            Full CurrencyConfiguration object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = product.currencies[0]
            >>> full = await partial.fetch_full()
            >>> full.discount_percentage  # Now computed fields available
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Convert partial to full by creating a CurrencyConfiguration with same data
        return CurrencyConfiguration(
            currency=self.currency,
            price=self.price,
            _client=self._client,
        )

    async def edit(self, **kwargs: Any) -> CurrencyConfiguration:
        """
        Edit is not supported for nested CurrencyConfiguration.

        Currency configurations are nested within products and should be
        edited through the parent product's edit() method.

        Args:
            **kwargs: (Unused) Fields to update.

        Returns:
            This method always raises NotImplementedError.

        Raises:
            NotImplementedError: Always - use Product.edit() instead.

        Example:
            >>> partial = product.currencies[0]
            >>> partial.edit(price=150)  # Raises NotImplementedError
        """
        raise NotImplementedError(
            "CurrencyConfiguration is nested and read-only. "
            "Edit the parent Product instead using product.edit(currencies=[...])"
        )
