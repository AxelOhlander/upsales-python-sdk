"""
Unit tests for OrderStagesResource.

Tests CRUD operations and custom methods for order stages endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.orderStages import OrderStage
from upsales.resources.orderStages import OrderStagesResource


class TestOrderStagesResourceCRUD:
    """Test CRUD operations for OrderStagesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample order stage data for testing."""
        return {
            "id": 1,
            "name": "Qualified",
            "probability": 25,
            "exclude": 0,
            "roles": [],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Proposal", "probability": 50},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an order stage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            result = await resource.create(name="Qualified", probability=25, exclude=0, roles=[])

            assert isinstance(result, OrderStage)
            assert result.id == 1
            assert result.name == "Qualified"
            assert result.probability == 25

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single order stage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            result = await resource.get(1)

            assert isinstance(result, OrderStage)
            assert result.id == 1
            assert result.name == "Qualified"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing order stages with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, OrderStage) for r in results)
            assert results[0].name == "Qualified"
            assert results[1].name == "Proposal"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, OrderStage) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an order stage."""
        updated_data = {**sample_data, "name": "Highly Qualified", "probability": 30}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            result = await resource.update(1, name="Highly Qualified", probability=30)

            assert isinstance(result, OrderStage)
            assert result.id == 1
            assert result.name == "Highly Qualified"
            assert result.probability == 30

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an order stage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?exclude=0&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.search(exclude=0)

            assert len(results) == 1
            assert results[0].exclude == 0


class TestOrderStagesResourceCustomMethods:
    """Test custom methods specific to OrderStagesResource."""

    @pytest.fixture
    def sample_included_stage(self):
        """Sample included stage data."""
        return {
            "id": 1,
            "name": "Qualified",
            "probability": 25,
            "exclude": 0,
            "roles": [],
        }

    @pytest.fixture
    def sample_excluded_stage(self):
        """Sample excluded stage data."""
        return {
            "id": 2,
            "name": "Lost",
            "probability": 0,
            "exclude": 1,
            "roles": [],
        }

    @pytest.mark.asyncio
    async def test_get_included(self, httpx_mock: HTTPXMock, sample_included_stage):
        """Test get_included() returns stages with exclude=0."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?exclude=0&limit=100&offset=0",
            json={"error": None, "data": [sample_included_stage]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.get_included()

            assert len(results) == 1
            assert results[0].exclude == 0
            assert results[0].name == "Qualified"

    @pytest.mark.asyncio
    async def test_get_excluded(self, httpx_mock: HTTPXMock, sample_excluded_stage):
        """Test get_excluded() returns stages with exclude=1."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?exclude=1&limit=100&offset=0",
            json={"error": None, "data": [sample_excluded_stage]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.get_excluded()

            assert len(results) == 1
            assert results[0].exclude == 1
            assert results[0].name == "Lost"

    @pytest.mark.asyncio
    async def test_get_by_probability_range(self, httpx_mock: HTTPXMock):
        """Test get_by_probability_range() filters stages."""
        all_stages = [
            {"id": 1, "name": "Qualified", "probability": 10, "exclude": 0, "roles": []},
            {"id": 2, "name": "Discovery", "probability": 25, "exclude": 0, "roles": []},
            {"id": 3, "name": "Negotiation", "probability": 75, "exclude": 0, "roles": []},
            {"id": 4, "name": "Closed Won", "probability": 100, "exclude": 0, "roles": []},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?limit=100&offset=0&sort=probability",
            json={"error": None, "data": all_stages},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.get_by_probability_range(70, 100)

            assert len(results) == 2
            assert all(r.probability >= 70 for r in results)
            assert results[0].name == "Negotiation"
            assert results[1].name == "Closed Won"

    @pytest.mark.asyncio
    async def test_get_sorted_by_probability(self, httpx_mock: HTTPXMock):
        """Test get_sorted_by_probability() sorts stages."""
        stages = [
            {"id": 1, "name": "Qualified", "probability": 10, "exclude": 0, "roles": []},
            {"id": 2, "name": "Discovery", "probability": 25, "exclude": 0, "roles": []},
            {"id": 3, "name": "Closed Won", "probability": 100, "exclude": 0, "roles": []},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?limit=100&offset=0&sort=probability",
            json={"error": None, "data": stages},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.get_sorted_by_probability()

            assert len(results) == 3
            assert results[0].probability == 10
            assert results[1].probability == 25
            assert results[2].probability == 100

    @pytest.mark.asyncio
    async def test_get_sorted_by_probability_descending(self, httpx_mock: HTTPXMock):
        """Test get_sorted_by_probability() with descending order."""
        stages = [
            {"id": 3, "name": "Closed Won", "probability": 100, "exclude": 0, "roles": []},
            {"id": 2, "name": "Discovery", "probability": 25, "exclude": 0, "roles": []},
            {"id": 1, "name": "Qualified", "probability": 10, "exclude": 0, "roles": []},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orderStages?limit=100&offset=0&sort=-probability",
            json={"error": None, "data": stages},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrderStagesResource(http)
            results = await resource.get_sorted_by_probability(descending=True)

            assert len(results) == 3
            assert results[0].probability == 100
            assert results[1].probability == 25
            assert results[2].probability == 10
