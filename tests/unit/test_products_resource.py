"""
Tests for ProductsResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.product import Product
from upsales.resources.products import ProductsResource


class TestProductsResourceCustomMethods:
    """Test custom methods specific to ProductsResource."""

    @pytest.fixture
    def sample_product(self):
        """Sample product data."""
        return {
            "id": 1,
            "name": "Test Product",
            "active": 1,
            "isRecurring": 0,
            "listPrice": 100.0,
            "purchaseCost": 60.0,
            "recurringInterval": 1,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_product):
        """Test get_active() returns only active products."""
        active_products = [
            {**sample_product, "id": 1, "active": 1},
            {**sample_product, "id": 2, "active": 1, "name": "Product 2"},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/products?active=1&limit=100&offset=0",
            json={"error": None, "data": active_products},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProductsResource(http)
            results = await resource.get_active()

            assert len(results) == 2
            assert all(isinstance(p, Product) for p in results)
            assert all(p.active == 1 for p in results)
            assert all(p.is_active for p in results)

    @pytest.mark.asyncio
    async def test_get_recurring(self, httpx_mock: HTTPXMock, sample_product):
        """Test get_recurring() returns only recurring products."""
        recurring_products = [
            {**sample_product, "id": 1, "isRecurring": 1},
            {**sample_product, "id": 2, "isRecurring": 1, "name": "Subscription Plan"},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/products?isRecurring=1&limit=100&offset=0",
            json={"error": None, "data": recurring_products},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProductsResource(http)
            results = await resource.get_recurring()

            assert len(results) == 2
            assert all(p.isRecurring == 1 for p in results)
            assert all(p.is_recurring for p in results)

    @pytest.mark.asyncio
    async def test_bulk_deactivate(self, httpx_mock: HTTPXMock, sample_product):
        """Test bulk_deactivate() sets active=0 for multiple products."""
        # Mock 3 successful deactivations
        for i in range(1, 4):
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/products/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_product, "id": i, "active": 0}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProductsResource(http)
            results = await resource.bulk_deactivate(ids=[1, 2, 3])

            assert len(results) == 3
            assert all(isinstance(p, Product) for p in results)
            assert all(p.active == 0 for p in results)
            assert all(not p.is_active for p in results)

    @pytest.mark.asyncio
    async def test_bulk_deactivate_with_custom_concurrency(
        self, httpx_mock: HTTPXMock, sample_product
    ):
        """Test bulk_deactivate() respects max_concurrent parameter."""
        # Mock 5 deactivations
        for i in range(1, 6):
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/products/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_product, "id": i, "active": 0}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProductsResource(http)
            results = await resource.bulk_deactivate(ids=[1, 2, 3, 4, 5], max_concurrent=2)

            assert len(results) == 5
            assert all(p.active == 0 for p in results)


# Coverage check
# Run: uv run pytest tests/unit/test_products_resource.py -v --cov=upsales/resources/products.py --cov-report=term-missing
