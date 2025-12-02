"""
Tests for QuotasResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.quota import Quota
from upsales.resources.quota import QuotasResource


class TestQuotasResourceCustomMethods:
    """Test custom methods specific to QuotasResource."""

    @pytest.fixture
    def sample_quota(self):
        """Sample quota data."""
        return {
            "id": 1,
            "year": 2025,
            "month": 11,
            "value": 100000,
            "currencyRate": 1,
            "currency": "USD",
            "date": "2025-11-01",
            "valueInMasterCurrency": 100000,
            "user": {
                "id": 123,
                "name": "John Doe",
                "email": "john@example.com",
            },
        }

    @pytest.mark.asyncio
    async def test_get_by_user(self, httpx_mock: HTTPXMock, sample_quota):
        """Test get_by_user() returns quotas for specific user."""
        quotas = [
            sample_quota,
            {**sample_quota, "id": 2, "month": 12},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/quota?user.id=123&limit=100&offset=0",
            json={"error": None, "data": quotas},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)
            results = await resource.get_by_user(123)

            assert len(results) == 2
            assert all(isinstance(q, Quota) for q in results)
            assert all(q.user.id == 123 for q in results)

    @pytest.mark.asyncio
    async def test_get_by_year(self, httpx_mock: HTTPXMock, sample_quota):
        """Test get_by_year() returns quotas for specific year."""
        quotas = [
            sample_quota,
            {**sample_quota, "id": 2, "month": 10},
            {**sample_quota, "id": 3, "month": 12},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/quota?year=2025&limit=100&offset=0",
            json={"error": None, "data": quotas},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)
            results = await resource.get_by_year(2025)

            assert len(results) == 3
            assert all(q.year == 2025 for q in results)

    @pytest.mark.asyncio
    async def test_get_by_quarter(self, httpx_mock: HTTPXMock, sample_quota):
        """Test get_by_quarter() returns quotas for specific quarter."""
        # Q4 = Oct, Nov, Dec (months 10, 11, 12)
        quotas = [
            {**sample_quota, "id": 1, "month": 10},
            {**sample_quota, "id": 2, "month": 11},
            {**sample_quota, "id": 3, "month": 12},
            {**sample_quota, "id": 4, "month": 9},  # Q3, should be filtered
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/quota?year=2025&limit=100&offset=0",
            json={"error": None, "data": quotas},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)
            results = await resource.get_by_quarter(2025, 4)

            assert len(results) == 3
            assert all(10 <= q.month <= 12 for q in results)
            assert all(q.quarter == 4 for q in results)

    @pytest.mark.asyncio
    async def test_get_by_quarter_invalid(self, httpx_mock: HTTPXMock):
        """Test get_by_quarter() raises ValueError for invalid quarter."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)

            with pytest.raises(ValueError, match="Quarter must be 1-4"):
                await resource.get_by_quarter(2025, 5)

            with pytest.raises(ValueError, match="Quarter must be 1-4"):
                await resource.get_by_quarter(2025, 0)

    @pytest.mark.asyncio
    async def test_get_by_user_and_period_with_month(self, httpx_mock: HTTPXMock, sample_quota):
        """Test get_by_user_and_period() with specific month."""
        quotas = [sample_quota]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/quota?user.id=123&year=2025&month=11&limit=100&offset=0",
            json={"error": None, "data": quotas},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)
            results = await resource.get_by_user_and_period(123, 2025, 11)

            assert len(results) == 1
            assert results[0].user.id == 123
            assert results[0].year == 2025
            assert results[0].month == 11

    @pytest.mark.asyncio
    async def test_get_by_user_and_period_without_month(self, httpx_mock: HTTPXMock, sample_quota):
        """Test get_by_user_and_period() without month (all year)."""
        quotas = [
            sample_quota,
            {**sample_quota, "id": 2, "month": 10},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/quota?user.id=123&year=2025&limit=100&offset=0",
            json={"error": None, "data": quotas},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)
            results = await resource.get_by_user_and_period(123, 2025)

            assert len(results) == 2
            assert all(q.user.id == 123 for q in results)
            assert all(q.year == 2025 for q in results)

    @pytest.mark.asyncio
    async def test_get_by_user_and_period_invalid_month(self, httpx_mock: HTTPXMock):
        """Test get_by_user_and_period() raises ValueError for invalid month."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = QuotasResource(http)

            with pytest.raises(ValueError, match="Month must be 1-12"):
                await resource.get_by_user_and_period(123, 2025, 13)

            with pytest.raises(ValueError, match="Month must be 1-12"):
                await resource.get_by_user_and_period(123, 2025, 0)


# Coverage check
# Run: uv run pytest tests/unit/test_quota_resource.py -v --cov=upsales/resources/quota.py --cov-report=term-missing
