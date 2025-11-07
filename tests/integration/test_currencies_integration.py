"""
Integration tests for Currency model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_currencies_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_currencies_integration/*.yaml
    uv run pytest tests/integration/test_currencies_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.currency import Currency

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_list_currencies_real_response.yaml")
async def test_list_currencies_real_response():
    """
    Test listing currencies with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Currency
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_currencies_integration/test_list_currencies_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all currencies (or replay from cassette)
        currencies = await upsales.currencies.list()

        assert len(currencies) > 0, "Should have at least one currency"

        for currency in currencies:
            # Validate Currency model
            assert isinstance(currency, Currency)
            assert isinstance(currency.iso, str)
            assert len(currency.iso) == 3, "ISO code should be 3 characters"
            assert isinstance(currency.rate, float)
            assert currency.rate > 0, "Exchange rate should be positive"
            assert isinstance(currency.masterCurrency, bool)
            assert isinstance(currency.active, bool)

            # Validate computed fields
            assert isinstance(currency.is_master, bool)
            assert isinstance(currency.is_active, bool)

        print(f"[OK] {len(currencies)} currencies parsed successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_get_master_currency.yaml")
async def test_get_master_currency():
    """
    Test getting the master currency.

    The master currency should have:
    - masterCurrency = True
    - rate = 1.0
    - active = True

    Cassette: tests/cassettes/integration/test_currencies_integration/test_get_master_currency.yaml
    """
    async with Upsales.from_env() as upsales:
        master = await upsales.currencies.get_master_currency()

        assert master is not None, "Should have a master currency"
        assert isinstance(master, Currency)
        assert master.is_master is True
        assert master.rate == 1.0
        assert master.active is True

        print(f"[OK] Master currency: {master.iso}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_get_by_iso.yaml")
async def test_get_by_iso():
    """
    Test getting a specific currency by ISO code.

    Cassette: tests/cassettes/integration/test_currencies_integration/test_get_by_iso.yaml
    """
    async with Upsales.from_env() as upsales:
        # First get list to see what's available
        all_currencies = await upsales.currencies.list()
        assert len(all_currencies) > 0

        # Get first currency by ISO
        first_iso = all_currencies[0].iso
        currency = await upsales.currencies.get_by_iso(first_iso)

        assert currency is not None
        assert isinstance(currency, Currency)
        assert currency.iso == first_iso

        print(f"[OK] Retrieved currency: {currency.iso} (rate: {currency.rate})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_get_active_currencies.yaml")
async def test_get_active_currencies():
    """
    Test getting only active currencies.

    Cassette: tests/cassettes/integration/test_currencies_integration/test_get_active_currencies.yaml
    """
    async with Upsales.from_env() as upsales:
        active = await upsales.currencies.get_active_currencies()

        assert len(active) > 0, "Should have at least one active currency"

        for currency in active:
            assert isinstance(currency, Currency)
            assert currency.is_active is True

        print(f"[OK] {len(active)} active currencies found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_currency_conversion.yaml")
async def test_currency_conversion():
    """
    Test currency conversion with real exchange rates.

    Cassette: tests/cassettes/integration/test_currencies_integration/test_currency_conversion.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get master currency and one other
        master = await upsales.currencies.get_master_currency()
        all_currencies = await upsales.currencies.list()

        # Find a non-master active currency
        other = next((c for c in all_currencies if not c.is_master and c.is_active), None)

        if other:
            # Convert 100 units from master to other currency
            result = await upsales.currencies.convert(100, master.iso, other.iso)

            # Result should be positive
            assert result > 0
            # Converting from master (rate=1) to other should multiply by inverse of rate
            # 100 * (1 / other.rate) = result
            expected = 100 / other.rate
            assert abs(result - expected) < 0.01  # Allow small floating point difference

            print(
                f"[OK] Converted 100 {master.iso} to {result:.2f} {other.iso} (rate: {other.rate})"
            )
        else:
            print("[SKIP] No non-master active currency found for conversion test")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_currencies_integration/test_model_validation.yaml")
async def test_model_validation():
    """
    Test that Currency model validates all fields correctly.

    Cassette: tests/cassettes/integration/test_currencies_integration/test_model_validation.yaml
    """
    async with Upsales.from_env() as upsales:
        currencies = await upsales.currencies.list()

        assert len(currencies) > 0

        for currency in currencies:
            # ISO code validation
            assert currency.iso.isupper(), "ISO code should be uppercase"
            assert currency.iso.isalpha(), "ISO code should be alphabetic"

            # Rate validation
            assert currency.rate > 0, "Rate must be positive"

            # Master currency should have rate = 1
            if currency.is_master:
                assert currency.rate == 1.0, "Master currency should have rate = 1.0"

            # Computed properties should match raw fields
            assert currency.is_master == currency.masterCurrency
            assert currency.is_active == currency.active

        print(f"[OK] All {len(currencies)} currencies validated successfully")
