"""
Tests for CurrencyConfiguration and PartialCurrencyConfiguration models.

Uses Python 3.13 native type hints.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from upsales.models.currency_configuration import (
    CurrencyConfiguration,
    PartialCurrencyConfiguration,
)


@pytest.fixture
def sample_currency_config_data() -> dict[str, Any]:
    """
    Sample currency configuration data from API.

    Returns:
        Dict with complete currency configuration data.
    """
    return {
        "currency": "USD",
        "price": 100.00,
        "listPrice": 120.00,
    }


@pytest.fixture
def sample_usd_config_data() -> dict[str, Any]:
    """Sample USD currency configuration."""
    return {
        "currency": "USD",
        "price": 100.00,
        "listPrice": 120.00,
    }


@pytest.fixture
def sample_eur_config_data() -> dict[str, Any]:
    """Sample EUR currency configuration."""
    return {
        "currency": "EUR",
        "price": 95.00,
        "listPrice": 110.00,
    }


@pytest.fixture
def sample_sek_config_no_list_price() -> dict[str, Any]:
    """Sample SEK configuration without list price."""
    return {
        "currency": "SEK",
        "price": 950.00,
        "listPrice": None,
    }


# ============================================================================
# CurrencyConfiguration Model Tests
# ============================================================================


def test_currency_configuration_creation(sample_currency_config_data):
    """Test creating CurrencyConfiguration with complete data."""
    config = CurrencyConfiguration(**sample_currency_config_data)

    assert config.currency == "USD"
    assert config.price == 100.00
    assert config.listPrice == 120.00


def test_currency_configuration_minimal_creation():
    """Test creating CurrencyConfiguration with minimal data."""
    config = CurrencyConfiguration(currency="USD", price=100.00)

    assert config.currency == "USD"
    assert config.price == 100.00
    assert config.listPrice is None


def test_currency_configuration_validates_required_fields():
    """Test that CurrencyConfiguration validates required fields."""
    # Missing currency
    with pytest.raises(ValidationError, match="currency"):
        CurrencyConfiguration(price=100.00)

    # Missing price
    with pytest.raises(ValidationError, match="price"):
        CurrencyConfiguration(currency="USD")


def test_currency_configuration_validates_non_empty_currency():
    """Test that CurrencyConfiguration validates non-empty currency."""
    # Empty currency
    with pytest.raises(ValidationError):
        CurrencyConfiguration(currency="", price=100.00)

    # Whitespace-only currency
    with pytest.raises(ValidationError):
        CurrencyConfiguration(currency="   ", price=100.00)


def test_currency_configuration_discount_amount(sample_currency_config_data):
    """Test discount_amount computed field."""
    config = CurrencyConfiguration(**sample_currency_config_data)

    assert config.discount_amount == 20.00


def test_currency_configuration_discount_amount_none():
    """Test discount_amount is None when listPrice is not set."""
    config = CurrencyConfiguration(currency="USD", price=100.00)

    assert config.discount_amount is None


def test_currency_configuration_discount_amount_zero():
    """Test discount_amount when price equals listPrice."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=100.00,
    )

    assert config.discount_amount == 0.00


def test_currency_configuration_discount_percentage(sample_currency_config_data):
    """Test discount_percentage computed field."""
    config = CurrencyConfiguration(**sample_currency_config_data)

    # (120 - 100) / 120 * 100 = 16.67%
    assert config.discount_percentage == 16.67


def test_currency_configuration_discount_percentage_precision():
    """Test discount_percentage rounding to 2 decimal places."""
    config = CurrencyConfiguration(
        currency="USD",
        price=99.99,
        listPrice=100.00,
    )

    # (100 - 99.99) / 100 * 100 = 0.01%
    assert config.discount_percentage == 0.01


def test_currency_configuration_discount_percentage_none():
    """Test discount_percentage is None when listPrice is not set."""
    config = CurrencyConfiguration(currency="USD", price=100.00)

    assert config.discount_percentage is None


def test_currency_configuration_discount_percentage_zero_list_price():
    """Test discount_percentage is None when listPrice is zero."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=0.0,
    )

    assert config.discount_percentage is None


def test_currency_configuration_is_discounted_true(sample_currency_config_data):
    """Test is_discounted computed field when price < listPrice."""
    config = CurrencyConfiguration(**sample_currency_config_data)

    assert config.is_discounted is True


def test_currency_configuration_is_discounted_false():
    """Test is_discounted is False when price >= listPrice."""
    config = CurrencyConfiguration(
        currency="USD",
        price=120.00,
        listPrice=100.00,
    )

    assert config.is_discounted is False


def test_currency_configuration_is_discounted_equal():
    """Test is_discounted is False when price == listPrice."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=100.00,
    )

    assert config.is_discounted is False


def test_currency_configuration_is_discounted_no_list_price():
    """Test is_discounted is False when listPrice is not set."""
    config = CurrencyConfiguration(currency="USD", price=100.00)

    assert config.is_discounted is False


def test_currency_configuration_edit_raises_not_implemented():
    """Test that edit() raises NotImplementedError."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=120.00,
    )

    with pytest.raises(NotImplementedError, match="nested"):
        import asyncio

        asyncio.run(config.edit(price=150.00))


def test_currency_configuration_str_representation(sample_currency_config_data):
    """Test string representation."""
    config = CurrencyConfiguration(**sample_currency_config_data)
    repr_str = repr(config)

    assert "CurrencyConfiguration" in repr_str


def test_currency_configuration_mutability(sample_currency_config_data):
    """Test that CurrencyConfiguration is mutable."""
    config = CurrencyConfiguration(**sample_currency_config_data)

    # Should allow assignment
    config.price = 110.00
    assert config.price == 110.00

    # Should validate on assignment
    with pytest.raises(ValidationError):
        config.currency = ""


def test_currency_configuration_different_currencies():
    """Test CurrencyConfiguration with different currency codes."""
    currencies = ["USD", "EUR", "GBP", "JPY", "SEK", "CHF"]

    for currency in currencies:
        config = CurrencyConfiguration(currency=currency, price=100.00)
        assert config.currency == currency


def test_currency_configuration_price_types():
    """Test CurrencyConfiguration with various price values."""
    # Integer price
    config = CurrencyConfiguration(currency="USD", price=100)
    assert config.price == 100

    # Float price
    config = CurrencyConfiguration(currency="USD", price=100.50)
    assert config.price == 100.50

    # Small price
    config = CurrencyConfiguration(currency="USD", price=0.01)
    assert config.price == 0.01

    # Large price
    config = CurrencyConfiguration(currency="USD", price=999999.99)
    assert config.price == 999999.99


def test_currency_configuration_large_discounts():
    """Test discount calculation with large discounts."""
    config = CurrencyConfiguration(
        currency="USD",
        price=50.00,
        listPrice=100.00,
    )

    assert config.discount_amount == 50.00
    assert config.discount_percentage == 50.0
    assert config.is_discounted is True


def test_currency_configuration_small_discounts():
    """Test discount calculation with very small discounts."""
    import pytest

    config = CurrencyConfiguration(
        currency="USD",
        price=99.99,
        listPrice=100.00,
    )

    # Use pytest.approx for floating-point precision
    assert config.discount_amount == pytest.approx(0.01)
    assert config.discount_percentage == 0.01
    assert config.is_discounted is True


# ============================================================================
# PartialCurrencyConfiguration Model Tests
# ============================================================================


def test_partial_currency_configuration_creation(sample_currency_config_data):
    """Test creating PartialCurrencyConfiguration with complete data."""
    partial = PartialCurrencyConfiguration(**sample_currency_config_data)

    assert partial.currency == "USD"
    assert partial.price == 100.00


def test_partial_currency_configuration_minimal_creation():
    """Test creating PartialCurrencyConfiguration with minimal data."""
    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    assert partial.currency == "USD"
    assert partial.price == 100.00


def test_partial_currency_configuration_validates_required_fields():
    """Test that PartialCurrencyConfiguration validates required fields."""
    # Missing currency
    with pytest.raises(ValidationError, match="currency"):
        PartialCurrencyConfiguration(price=100.00)

    # Missing price
    with pytest.raises(ValidationError, match="price"):
        PartialCurrencyConfiguration(currency="USD")


def test_partial_currency_configuration_validates_non_empty_currency():
    """Test that PartialCurrencyConfiguration validates non-empty currency."""
    # Empty currency
    with pytest.raises(ValidationError):
        PartialCurrencyConfiguration(currency="", price=100.00)

    # Whitespace-only currency
    with pytest.raises(ValidationError):
        PartialCurrencyConfiguration(currency="   ", price=100.00)


def test_partial_currency_configuration_display_currency():
    """Test display_currency computed field."""
    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    assert partial.display_currency == "USD 100.00"


def test_partial_currency_configuration_display_currency_formatting():
    """Test display_currency formats price to 2 decimal places."""
    partial = PartialCurrencyConfiguration(currency="EUR", price=99.5)

    assert partial.display_currency == "EUR 99.50"


def test_partial_currency_configuration_display_currency_large_price():
    """Test display_currency with large prices."""
    partial = PartialCurrencyConfiguration(currency="JPY", price=12345.6789)

    assert partial.display_currency == "JPY 12345.68"


def test_partial_currency_configuration_fetch_full():
    """Test fetch_full() raises when no client available."""
    import asyncio

    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    async def test():
        # fetch_full will raise because no client is available
        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    asyncio.run(test())


def test_partial_currency_configuration_fetch_full_no_client():
    """Test fetch_full() raises RuntimeError when no client."""
    import asyncio

    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    async def test():
        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    asyncio.run(test())


def test_partial_currency_configuration_edit_raises_not_implemented():
    """Test that edit() raises NotImplementedError."""
    import asyncio

    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    async def test():
        with pytest.raises(NotImplementedError, match="nested"):
            await partial.edit(price=150.00)

    asyncio.run(test())


def test_partial_currency_configuration_str_representation():
    """Test string representation."""
    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)
    repr_str = repr(partial)

    assert "PartialCurrencyConfiguration" in repr_str


def test_partial_currency_configuration_mutability():
    """Test that PartialCurrencyConfiguration is mutable."""
    partial = PartialCurrencyConfiguration(currency="USD", price=100.00)

    # Should allow assignment
    partial.price = 110.00
    assert partial.price == 110.00

    # Should validate on assignment
    with pytest.raises(ValidationError):
        partial.currency = ""


# ============================================================================
# Integration Tests
# ============================================================================


def test_currency_configuration_in_list():
    """Test using CurrencyConfiguration in a list (like Product.currencies)."""
    configs = [
        CurrencyConfiguration(currency="USD", price=100.00, listPrice=120.00),
        CurrencyConfiguration(currency="EUR", price=95.00, listPrice=110.00),
        CurrencyConfiguration(currency="SEK", price=950.00),
    ]

    discounted = [c for c in configs if c.is_discounted]
    assert len(discounted) == 2

    with_list_price = [c for c in configs if c.listPrice is not None]
    assert len(with_list_price) == 2


def test_currency_configuration_extra_fields():
    """Test that CurrencyConfiguration allows extra fields from API."""
    data = {
        "currency": "USD",
        "price": 100.00,
        "listPrice": 120.00,
        "unknown_field": "some_value",
    }

    # Should not raise error (extra="allow" in config)
    config = CurrencyConfiguration(**data)
    assert config.currency == "USD"


def test_partial_currency_configuration_extra_fields():
    """Test that PartialCurrencyConfiguration allows extra fields."""
    data = {
        "currency": "USD",
        "price": 100.00,
        "future_field": 123,
    }

    # Should not raise error (extra="allow" in config)
    partial = PartialCurrencyConfiguration(**data)
    assert partial.currency == "USD"


def test_currency_configuration_zero_price():
    """Test CurrencyConfiguration with zero price."""
    config = CurrencyConfiguration(currency="USD", price=0.0)

    assert config.price == 0.0
    assert config.discount_amount is None


def test_currency_configuration_zero_list_price():
    """Test CurrencyConfiguration with zero listPrice."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=0.0,
    )

    assert config.listPrice == 0.0
    assert config.discount_amount == -100.00
    assert config.is_discounted is False


def test_currency_configuration_negative_discount():
    """Test CurrencyConfiguration where price > listPrice (negative discount)."""
    config = CurrencyConfiguration(
        currency="USD",
        price=150.00,
        listPrice=100.00,
    )

    assert config.discount_amount == -50.00
    assert config.discount_percentage == -50.0
    assert config.is_discounted is False


def test_multiple_currency_configurations():
    """Test working with multiple currency configurations."""
    configs_data = [
        {"currency": "USD", "price": 100.00, "listPrice": 120.00},
        {"currency": "EUR", "price": 95.00, "listPrice": 110.00},
        {"currency": "GBP", "price": 85.00, "listPrice": 100.00},
        {"currency": "JPY", "price": 11000.00},
    ]

    configs = [CurrencyConfiguration(**data) for data in configs_data]

    assert len(configs) == 4
    assert all(c.currency in ["USD", "EUR", "GBP", "JPY"] for c in configs)
    assert sum(1 for c in configs if c.is_discounted) == 3
    assert sum(1 for c in configs if c.listPrice is None) == 1


def test_currency_configuration_serialization():
    """Test CurrencyConfiguration serialization."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=120.00,
    )

    # Should be able to convert to dict
    data = config.model_dump()
    assert data["currency"] == "USD"
    assert data["price"] == 100.00
    assert data["listPrice"] == 120.00


def test_currency_configuration_model_dump():
    """Test model_dump() method for API serialization."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=120.00,
    )

    api_data = config.model_dump()
    assert api_data["currency"] == "USD"
    assert api_data["price"] == 100.00
    assert api_data["listPrice"] == 120.00


def test_currency_configuration_json_serialization():
    """Test CurrencyConfiguration JSON serialization."""
    config = CurrencyConfiguration(
        currency="USD",
        price=100.00,
        listPrice=120.00,
    )

    json_str = config.model_dump_json()
    assert "USD" in json_str
    assert "100.0" in json_str or "100" in json_str
