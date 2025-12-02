"""
Unit tests for PeriodizationsResource.

Tests CRUD operations for the periodization endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.periodization import Periodization
from upsales.resources.periodization import PeriodizationsResource


class TestPeriodizationsResourceCRUD:
    """Test CRUD operations for PeriodizationsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample periodization data for testing."""
        return {
            "id": 1,
            "orderId": 123,
            "startDate": "2025-01-01",
            "endDate": "2025-12-31",
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "orderId": 456},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a periodization."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            result = await resource.create(
                orderId=123, startDate="2025-01-01", endDate="2025-12-31"
            )

            assert isinstance(result, Periodization)
            assert result.id == 1
            assert result.orderId == 123
            assert result.startDate == "2025-01-01"
            assert result.endDate == "2025-12-31"
            assert result.is_valid_date_range

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single periodization."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Periodization)
            assert result.id == 1
            assert result.orderId == 123
            assert result.is_valid_date_range

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing periodizations with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Periodization) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a periodization."""
        updated_data = {**sample_data, "startDate": "2025-02-01"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            result = await resource.update(1, startDate="2025-02-01")

            assert isinstance(result, Periodization)
            assert result.startDate == "2025-02-01"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a periodization."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/periodization/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PeriodizationsResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestPeriodizationModel:
    """Test Periodization model methods and properties."""

    @pytest.mark.asyncio
    async def test_is_valid_date_range_true(self):
        """Test is_valid_date_range property when valid."""
        p = Periodization(id=1, orderId=123, startDate="2025-01-01", endDate="2025-12-31")
        assert p.is_valid_date_range is True

    @pytest.mark.asyncio
    async def test_is_valid_date_range_false(self):
        """Test is_valid_date_range property when invalid."""
        p = Periodization(id=1, orderId=123, startDate="2025-12-31", endDate="2025-01-01")
        assert p.is_valid_date_range is False

    @pytest.mark.asyncio
    async def test_is_valid_date_range_same(self):
        """Test is_valid_date_range property when dates are same."""
        p = Periodization(id=1, orderId=123, startDate="2025-01-01", endDate="2025-01-01")
        assert p.is_valid_date_range is False
