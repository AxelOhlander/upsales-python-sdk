"""
Currency models for Upsales API.

Generated from /api/v2/currencies endpoint.
Analysis based on 6 samples.

IMPORTANT: Currencies do NOT have ID fields - they are identified by ISO code.
This endpoint is read-only and likely doesn't support standard CRUD operations.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.validators import NonEmptyStr


class CurrencyUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Currency.

    All fields are optional.
    Note: Currencies may be read-only in Upsales API.
    """

    active: bool
    iso: str
    masterCurrency: bool
    rate: float


class Currency(PydanticBase):
    """
    Currency model from /api/v2/currencies.

    Represents a currency configuration in Upsales. Note that currencies
    are identified by their ISO code, not by an ID field. This endpoint
    may be read-only.

    Generated from 6 samples.

    Attributes:
        iso: ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')
        rate: Exchange rate relative to master currency
        masterCurrency: Whether this is the master currency (rate = 1)
        active: Whether this currency is active in the system

    Example:
        >>> currencies = await upsales.currencies.list()
        >>> sek = next(c for c in currencies if c.is_master)
        >>> sek.iso
        'SEK'
        >>> sek.rate
        1.0
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    # All fields are required (present in 100% of samples)
    iso: NonEmptyStr = Field(description="ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')")
    rate: float = Field(description="Exchange rate relative to master currency")
    masterCurrency: bool = Field(description="Whether this is the master currency (rate = 1)")
    active: bool = Field(description="Whether this currency is active in the system")
    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize currency with optional client reference.

        Args:
            **data: Currency field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        # Use object.__setattr__ to bypass frozen check
        object.__setattr__(self, "_client", client)

    def to_api_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize currency for API requests.

        Args:
            **overrides: Field overrides to apply before serialization.

        Returns:
            Dictionary of currency data for API.

        Example:
            >>> currency.to_api_dict(active=False)
            {'iso': 'USD', 'rate': 0.106, 'masterCurrency': False, 'active': False}
        """
        # Apply overrides
        data = self.model_dump(exclude={"_client"})
        data.update(overrides)
        return data

    @computed_field
    @property
    def is_master(self) -> bool:
        """
        Check if this is the master currency.

        The master currency has a rate of 1.0 and all other currencies
        are calculated relative to it.

        Returns:
            True if this is the master currency, False otherwise.

        Example:
            >>> currency.is_master
            True
        """
        return self.masterCurrency

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if currency is active.

        Returns:
            True if currency is active, False otherwise.

        Example:
            >>> currency.is_active
            True
        """
        return self.active

    async def edit(self, **kwargs: Unpack[CurrencyUpdateFields]) -> "Currency":
        """
        Edit this currency.

        Note: The currencies endpoint is read-only. This method is provided
        for API consistency but will raise NotImplementedError.

        Args:
            **kwargs: Fields to update (from CurrencyUpdateFields).

        Returns:
            Updated currency.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: Currencies endpoint is read-only.

        Example:
            >>> currency = currencies[0]
            >>> updated = await currency.edit(active=False)  # Raises NotImplementedError
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Currencies endpoint is read-only
        raise NotImplementedError(
            "Currencies endpoint is read-only. Update operations are not supported."
        )


class PartialCurrency(PydanticBase):
    """
    Partial Currency for nested responses.

    Contains minimal currency information when embedded in other objects.

    Attributes:
        iso: ISO 4217 currency code

    Example:
        >>> order.currency.iso
        'USD'
        >>> full = await order.currency.fetch_full()
        >>> full.rate
        0.106791513
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True,
    )

    iso: str = Field(description="ISO 4217 currency code")
    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize partial currency with optional client reference.

        Args:
            **data: Currency field data.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        object.__setattr__(self, "_client", client)

    async def fetch_full(self) -> Currency:
        """
        Fetch full currency data.

        Returns:
            Complete Currency object with all fields.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = order.currency
            >>> full = await partial.fetch_full()
            >>> full.rate
            0.106791513
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Fetch by ISO code since there's no ID field
        currencies = await self._client.currencies.list()
        currency = next((c for c in currencies if c.iso == self.iso), None)
        if not currency:
            raise ValueError(f"Currency not found: {self.iso}")
        return currency

    async def edit(self, **kwargs: Unpack[CurrencyUpdateFields]) -> Currency:
        """
        Edit this currency.

        Note: The currencies endpoint is read-only. This method is provided
        for API consistency but will raise NotImplementedError.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated currency.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: Currencies endpoint is read-only.

        Example:
            >>> currency = order.currency
            >>> updated = await currency.edit(active=False)  # Raises NotImplementedError
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Currencies endpoint is read-only
        raise NotImplementedError(
            "Currencies endpoint is read-only. Update operations are not supported."
        )
