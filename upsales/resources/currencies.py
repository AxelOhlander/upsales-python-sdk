"""
Currencies resource manager for Upsales API.

Manages /api/v2/currencies endpoint operations.

IMPORTANT: Currencies endpoint is likely read-only and doesn't follow standard
CRUD patterns since currencies lack ID fields (identified by ISO code instead).

This resource manager provides limited operations:
- list(): Get all currencies
- get_by_iso(): Get specific currency by ISO code

Standard operations like create(), update(), delete() are likely not supported
by the API and are omitted from this resource manager.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.currency import Currency


class CurrenciesResource:
    """
    Resource manager for /api/v2/currencies endpoint.

    Note: Unlike most resources, currencies are identified by ISO code,
    not by numeric ID. This endpoint is likely read-only (no create/update/delete).

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/currencies).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # List all currencies
        ...     currencies = await upsales.currencies.list()
        ...     for currency in currencies:
        ...         print(f"{currency.iso}: {currency.rate}")
        ...
        ...     # Get specific currency
        ...     usd = await upsales.currencies.get_by_iso("USD")
        ...     print(f"USD rate: {usd.rate}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize currencies resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/currencies"

    async def list(self) -> list[Currency]:
        """
        Get all currencies.

        Returns all configured currencies with their exchange rates relative
        to the master currency.

        Returns:
            List of Currency objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> currencies = await upsales.currencies.list()
            >>> for currency in currencies:
            ...     print(f"{currency.iso}: {currency.rate}")
            USD: 0.106791513
            EUR: 0.091776799
            SEK: 1.0
        """
        response = await self._http.get(self._endpoint)
        # Extract the data list from the API response wrapper
        data = cast("list[dict[str, Any]]", response.get("data", []))
        currencies = []
        for item in data:
            currency_data: dict[str, Any] = {**item, "_client": None}
            currencies.append(Currency(**currency_data))
        return currencies

    async def get_by_iso(self, iso_code: str) -> Currency | None:
        """
        Get a specific currency by ISO code.

        Args:
            iso_code: ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK').

        Returns:
            Currency object if found, None otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> usd = await upsales.currencies.get_by_iso("USD")
            >>> if usd:
            ...     print(f"USD rate: {usd.rate}")
            USD rate: 0.106791513

            >>> unknown = await upsales.currencies.get_by_iso("ZZZ")
            >>> print(unknown)
            None
        """
        currencies = await self.list()
        currency = next((c for c in currencies if c.iso == iso_code), None)
        return currency

    async def get_master_currency(self) -> Currency | None:
        """
        Get the master currency.

        The master currency has masterCurrency=True and rate=1.0.
        All other currencies are calculated relative to it.

        Returns:
            Master Currency object if found, None otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> master = await upsales.currencies.get_master_currency()
            >>> print(f"Master: {master.iso} (rate: {master.rate})")
            Master: SEK (rate: 1.0)
        """
        currencies = await self.list()
        master = next((c for c in currencies if c.is_master), None)
        return master

    async def get_active_currencies(self) -> list[Currency]:  # type: ignore[valid-type]
        """
        Get all active currencies.

        Filters the currency list to only include active currencies.

        Returns:
            List of active Currency objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> active = await upsales.currencies.get_active_currencies()
            >>> for currency in active:
            ...     print(f"{currency.iso}: active")
            USD: active
            EUR: active
        """
        currencies = await self.list()
        active = [c for c in currencies if c.is_active]
        return active

    async def convert(self, amount: float, from_iso: str, to_iso: str) -> float:
        """
        Convert amount from one currency to another.

        Uses the exchange rates from the API to convert between currencies.
        Conversion goes through the master currency (from -> master -> to).

        Args:
            amount: Amount to convert.
            from_iso: Source currency ISO code.
            to_iso: Target currency ISO code.

        Returns:
            Converted amount in target currency.

        Raises:
            ValueError: If either currency is not found.
            UpsalesError: If API request fails.

        Example:
            >>> # Convert 100 USD to EUR
            >>> eur_amount = await upsales.currencies.convert(100, "USD", "EUR")
            >>> print(f"100 USD = {eur_amount:.2f} EUR")
            100 USD = 85.92 EUR
        """
        from_currency = await self.get_by_iso(from_iso)
        to_currency = await self.get_by_iso(to_iso)

        if not from_currency:
            raise ValueError(f"Currency not found: {from_iso}")
        if not to_currency:
            raise ValueError(f"Currency not found: {to_iso}")

        # Convert: amount -> master -> target
        # amount * from_rate = amount in master currency
        # (amount in master) / to_rate = amount in target currency
        master_amount = amount * from_currency.rate
        target_amount = master_amount / to_currency.rate

        return target_amount
