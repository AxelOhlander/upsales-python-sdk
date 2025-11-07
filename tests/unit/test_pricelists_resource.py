"""
Tests for PricelistsResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.pricelist import Pricelist
from upsales.resources.pricelists import PricelistsResource


class TestPricelistsResourceCustomMethods:
    """Test custom methods specific to PricelistsResource."""

    @pytest.fixture
    def sample_pricelist(self):
        """Sample pricelist data."""
        return {
            "id": 1,
            "name": "Standard Pricing",
            "code": "STD",
            "active": True,
            "isDefault": True,
            "showDiscount": True,
            "regDate": "2025-01-01",
            "regBy": 1,
            "modDate": "2025-01-15",
            "modBy": 1,
        }

    @pytest.mark.asyncio
    async def test_get_default_found(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_default() finds the default pricelist."""
        # get_default calls list_all() which fetches all pricelists then filters
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    sample_pricelist,
                    {**sample_pricelist, "id": 2, "name": "Premium", "isDefault": False},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_default()

            assert isinstance(result, Pricelist)
            assert result.isDefault is True
            assert result.is_default is True
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_default_not_found(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_default() returns None when no default pricelist exists."""
        # get_default calls list_all() which fetches all pricelists
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    {**sample_pricelist, "isDefault": False},
                    {**sample_pricelist, "id": 2, "isDefault": False},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_default()

            assert result is None

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_active() returns only active pricelists."""
        active_pricelists = [
            {**sample_pricelist, "id": 1, "active": True},
            {**sample_pricelist, "id": 2, "name": "Premium", "active": True},
            {**sample_pricelist, "id": 3, "name": "Enterprise", "active": True},
        ]

        # Match any request with active parameter (bool gets encoded as True/true)
        import re

        httpx_mock.add_response(
            url=re.compile(r"https://power.upsales.com/api/v2/pricelists\?.*active=.*"),
            json={"error": None, "data": active_pricelists},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            results = await resource.get_active()

            assert len(results) == 3
            assert all(isinstance(pl, Pricelist) for pl in results)
            assert all(pl.active is True for pl in results)
            assert all(pl.is_active for pl in results)

    @pytest.mark.asyncio
    async def test_get_by_code_found(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_by_code() finds pricelist by code."""
        # get_by_code calls list_all() which fetches all pricelists then filters
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    sample_pricelist,
                    {**sample_pricelist, "id": 2, "code": "PREM", "name": "Premium"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_by_code("STD")

            assert isinstance(result, Pricelist)
            assert result.code == "STD"
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_by_code_case_insensitive(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_by_code() is case-insensitive."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [sample_pricelist],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_by_code("std")  # lowercase

            assert isinstance(result, Pricelist)
            assert result.code == "STD"

    @pytest.mark.asyncio
    async def test_get_by_code_not_found(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_by_code() returns None when code not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [{**sample_pricelist, "code": "STD"}],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_by_code("NOTFOUND")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_code_with_null_codes(self, httpx_mock: HTTPXMock, sample_pricelist):
        """Test get_by_code() handles pricelists with null codes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pricelists?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    {**sample_pricelist, "id": 1, "code": None},  # null code
                    {**sample_pricelist, "id": 2, "code": "STD"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PricelistsResource(http)
            result = await resource.get_by_code("STD")

            assert isinstance(result, Pricelist)
            assert result.id == 2
            assert result.code == "STD"


# Coverage check
# Run: uv run pytest tests/unit/test_pricelists_resource.py -v --cov=upsales/resources/pricelists.py --cov-report=term-missing
