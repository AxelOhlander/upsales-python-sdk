"""
Price Tier models for quantity-based pricing tiers.

Represents tiered pricing structure used in products. Each tier specifies
a minimum quantity with an associated price and optional discount percentage.

API Structure:
    {
        "quantity": 10,
        "price": 95.00,
        "discount": 5
    }

Example:
    >>> tier = PriceTier(quantity=10, price=95.00, discount=5)
    >>> tier.quantity
    10
    >>> tier.price
    95.0
    >>> tier.discount
    5
    >>> tier.effective_price
    90.25

Note:
    PriceTier is a simple data model without an ID field, as price tiers
    are always nested within products and never accessed as standalone resources.
    No edit() or fetch_full() methods are needed.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from upsales.validators import PositiveInt


class PriceTier(BaseModel):
    """
    Quantity-based pricing tier.

    Represents a single tier in a product's tiered pricing structure.
    Specifies a minimum quantity with an associated price and optional discount.

    Price tiers are always nested within products and never accessed as standalone
    resources, so this model does not inherit from BaseModel's full interface.

    Attributes:
        quantity: Minimum quantity for this tier.
        price: Price at this tier.
        discount: Optional discount percentage (0-100).

    Example:
        >>> tier = PriceTier(quantity=10, price=95.00, discount=5)
        >>> tier.effective_price  # Price after discount
        90.25
        >>> tier.quantity
        10
    """

    model_config = ConfigDict(
        validate_assignment=False,  # Disable assignment validation for simple data model
        extra="allow",  # Allow extra fields from API (future compatibility)
    )

    quantity: PositiveInt = Field(description="Minimum quantity for this tier")
    price: float = Field(description="Price at this tier")
    discount: PositiveInt | None = Field(None, description="Discount percentage (0-100)")

    @computed_field
    @property
    def effective_price(self) -> float:
        """
        Calculate effective price after discount.

        Returns:
            Price after applying discount percentage, or original price if no discount.

        Example:
            >>> tier = PriceTier(quantity=10, price=100.00, discount=10)
            >>> tier.effective_price
            90.0
            >>> tier_no_discount = PriceTier(quantity=10, price=100.00)
            >>> tier_no_discount.effective_price
            100.0
        """
        if self.discount is None or self.discount == 0:
            return self.price
        return self.price * (1 - self.discount / 100)

    def __repr__(self) -> str:
        """
        Return string representation of the price tier.

        Returns:
            String like "<PriceTier qty=10 price=95.00 discount=5%>".

        Example:
            >>> tier = PriceTier(quantity=10, price=95.00, discount=5)
            >>> repr(tier)
            '<PriceTier qty=10 price=95.0 discount=5%>'
        """
        if self.discount is not None and self.discount > 0:
            return f"<PriceTier qty={self.quantity} price={self.price} discount={self.discount}%>"
        return f"<PriceTier qty={self.quantity} price={self.price}>"


class PartialPriceTier(BaseModel):
    """
    Partial pricing tier with minimal fields.

    Contains only quantity and price - the essential tier information.
    Useful when discount information is not available or not needed.

    Attributes:
        quantity: Minimum quantity for this tier.
        price: Price at this tier.

    Example:
        >>> tier = PartialPriceTier(quantity=10, price=95.00)
        >>> tier.quantity
        10
        >>> tier.price
        95.0
    """

    model_config = ConfigDict(
        validate_assignment=False,  # Disable assignment validation for simple data model
        extra="allow",  # Allow extra fields from API (future compatibility)
    )

    quantity: PositiveInt = Field(description="Minimum quantity for this tier")
    price: float = Field(description="Price at this tier")

    def __repr__(self) -> str:
        """
        Return string representation of the partial price tier.

        Returns:
            String like "<PartialPriceTier qty=10 price=95.00>".

        Example:
            >>> tier = PartialPriceTier(quantity=10, price=95.00)
            >>> repr(tier)
            '<PartialPriceTier qty=10 price=95.0>'
        """
        return f"<PartialPriceTier qty={self.quantity} price={self.price}>"
