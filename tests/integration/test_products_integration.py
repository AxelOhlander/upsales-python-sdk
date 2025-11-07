"""
Integration tests for Product model with real API responses.

Uses VCR.py to record API responses from /products endpoint.
Validates that our Pydantic v2 Product model correctly parses real data.

To record cassettes:
    uv run pytest tests/integration/test_products_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.product import Product

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_products_integration/test_get_product_real_response.yaml")
async def test_get_product_real_response():
    """
    Test getting a product with real API response structure.

    Records actual /products response and validates Product model
    correctly parses all 25 fields.

    Cassette: tests/cassettes/integration/test_products_integration/test_get_product_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get products list to find a valid ID
        products = await upsales.products.list(limit=1)

        assert len(products) > 0, "Should have at least one product"
        product = products[0]

        # Validate Product model with Pydantic v2 features
        assert isinstance(product, Product)
        assert isinstance(product.id, int)
        assert isinstance(product.name, str)
        assert len(product.name) > 0  # NonEmptyStr validator

        # Validate BinaryFlag fields (0 or 1)
        assert product.active in (0, 1)
        assert product.isRecurring in (0, 1)
        assert product.isMultiCurrency in (0, 1)

        # Validate pricing fields
        assert isinstance(product.listPrice, int)
        assert isinstance(product.purchaseCost, int)
        assert product.listPrice >= 0
        assert product.purchaseCost >= 0

        # Validate computed fields
        assert isinstance(product.is_active, bool)
        assert isinstance(product.is_recurring, bool)
        assert isinstance(product.profit_margin, float)

        print(
            f"[OK] Product parsed: {product.name} (ID: {product.id}, Margin: {product.profit_margin:.1f}%)"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_products_integration/test_list_products_real_response.yaml")
async def test_list_products_real_response():
    """
    Test listing products with real API response structure.

    Validates multiple product objects and pagination.

    Cassette: tests/cassettes/integration/test_products_integration/test_list_products_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get products with limit
        products = await upsales.products.list(limit=5)

        assert isinstance(products, list)
        assert len(products) <= 5

        for product in products:
            assert isinstance(product, Product)
            assert product.id > 0
            assert len(product.name) > 0

        print(f"[OK] Listed {len(products)} products successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_products_integration/test_product_profit_margin_calculation.yaml")
async def test_product_profit_margin_calculation():
    """
    Test profit_margin computed field with real pricing data.

    Validates the calculation works correctly with actual API values.

    Cassette: tests/cassettes/integration/test_products_integration/test_product_profit_margin_calculation.yaml
    """
    async with Upsales.from_env() as upsales:
        products = await upsales.products.list(limit=10)

        for product in products:
            # Validate profit margin calculation
            if product.listPrice > 0:
                expected_margin = (
                    (product.listPrice - product.purchaseCost) / product.listPrice
                ) * 100
                assert abs(product.profit_margin - expected_margin) < 0.01
            else:
                assert product.profit_margin == 0.0

        print(f"[OK] Profit margins validated for {len(products)} products")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_products_integration/test_product_resource_custom_methods.yaml")
async def test_product_resource_custom_methods():
    """
    Test ProductsResource custom methods with real data.

    Validates get_active() and get_recurring() methods.

    Cassette: tests/cassettes/integration/test_products_integration/test_product_resource_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active_products = await upsales.products.get_active()
        assert isinstance(active_products, list)
        for product in active_products:
            assert product.active == 1
            assert product.is_active is True

        print(f"[OK] get_active() returned {len(active_products)} active products")

        # Test get_recurring()
        recurring_products = await upsales.products.get_recurring()
        assert isinstance(recurring_products, list)
        for product in recurring_products:
            assert product.isRecurring == 1
            assert product.is_recurring is True

        print(f"[OK] get_recurring() returned {len(recurring_products)} recurring products")
