"""
Unit tests for ContractAcceptedResource.

Tests CRUD operations for the contract accepted endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.contract_accepted import ContractAccepted
from upsales.resources.contract_accepted import ContractAcceptedResource


class TestContractAcceptedResourceCRUD:
    """Test CRUD operations for ContractAcceptedResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample contract accepted data for testing."""
        return {
            "id": 1,
            "contractId": 123,
            "customerId": 456,
            "userId": 789,
            "body": "Contract terms and conditions...",
            "version": "1.0",
            "date": "2024-01-15 10:30:45",
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 3, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "contractId": 124, "date": "2024-01-16 11:00:00"},
                {**sample_data, "id": 3, "contractId": 125, "date": "2024-01-17 09:15:30"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a contract acceptance record."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            result = await resource.create(contractId=123)

            assert isinstance(result, ContractAccepted)
            assert result.id == 1
            assert result.contractId == 123
            assert result.has_date

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single contract acceptance record."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            result = await resource.get(1)

            assert isinstance(result, ContractAccepted)
            assert result.id == 1
            assert result.contractId == 123
            assert result.customerId == 456
            assert result.userId == 789
            assert result.body == "Contract terms and conditions..."
            assert result.version == "1.0"
            assert result.date == "2024-01-15 10:30:45"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing contract acceptance records with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 3
            assert all(isinstance(item, ContractAccepted) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a contract acceptance record."""
        updated_data = {**sample_data, "version": "2.0"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            result = await resource.update(1, version="2.0")

            assert isinstance(result, ContractAccepted)
            assert result.version == "2.0"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a contract acceptance record."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contractAccepted/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContractAcceptedResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestContractAcceptedModelFeatures:
    """Test model-specific features."""

    @pytest.mark.asyncio
    async def test_has_date_computed_field(self):
        """Test has_date computed field."""
        # With date
        contract = ContractAccepted(id=1, contractId=123, date="2024-01-15 10:30:45")
        assert contract.has_date is True

        # Without date
        contract_no_date = ContractAccepted(id=2, contractId=124, date=None)
        assert contract_no_date.has_date is False

        # Empty date
        contract_empty = ContractAccepted(id=3, contractId=125, date="")
        assert contract_empty.has_date is False

    @pytest.mark.asyncio
    async def test_frozen_id_field(self):
        """Test that id field is frozen and cannot be modified."""
        contract = ContractAccepted(id=1, contractId=123)

        # Attempting to modify frozen field should raise validation error
        with pytest.raises(Exception):  # Pydantic raises validation error
            contract.id = 999

    @pytest.mark.asyncio
    async def test_optional_fields(self):
        """Test that optional fields can be None."""
        # Minimal required fields
        contract = ContractAccepted(id=1, contractId=123)

        assert contract.id == 1
        assert contract.contractId == 123
        assert contract.customerId is None
        assert contract.userId is None
        assert contract.body is None
        assert contract.version is None
        assert contract.date is None
