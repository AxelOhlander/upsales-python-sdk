"""Tests for SoliditetClientsResource.

Ensures complete CRUD coverage for soliditet clients endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.soliditet_clients import SoliditetClient
from upsales.resources.soliditet_clients import SoliditetClientsResource


class TestSoliditetClientsResourceCRUD:
    """Test CRUD operations for SoliditetClientsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample soliditet client data for testing."""
        return {
            "dunsNo": "123456789",
            "name": "ACME Corporation AB",
            "turnover": 1500000.0,
            "headquarters": "Stockholm",
            "city": "Stockholm",
            "country": "Sweden",
            "orgNo": "556677-8899",
            "sniCode": "62010",
            "noOfEmployeesExact": 150,
        }

    @pytest.mark.asyncio
    async def test_create_purchase(self, httpx_mock: HTTPXMock, sample_data):
        """Test purchasing company data (create)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/soliditet/clients",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SoliditetClientsResource(http)
            result = await resource.create(
                duns="123456789", options={}, properties=["name", "turnover", "employees"]
            )

            assert isinstance(result, SoliditetClient)
            assert result.dunsNo == "123456789"
            assert result.name == "ACME Corporation AB"
            assert result.turnover == 1500000.0

    @pytest.mark.asyncio
    async def test_purchase_method(self, httpx_mock: HTTPXMock, sample_data):
        """Test purchase convenience method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/soliditet/clients",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SoliditetClientsResource(http)
            result = await resource.purchase(
                duns="123456789",
                options={"refresh": False},
                properties=["name", "turnover"],
            )

            assert isinstance(result, SoliditetClient)
            assert result.dunsNo == "123456789"
            assert result.noOfEmployeesExact == 150

    @pytest.mark.asyncio
    async def test_refresh_method(self, httpx_mock: HTTPXMock, sample_data):
        """Test refresh convenience method (PUT)."""
        updated_data = {**sample_data, "turnover": 2000000.0, "noOfEmployeesExact": 200}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/soliditet/clients/123456789",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SoliditetClientsResource(http)
            result = await resource.refresh(
                duns="123456789",
                options={"refresh": True},
                properties=["turnover", "employees"],
            )

            assert isinstance(result, SoliditetClient)
            assert result.dunsNo == "123456789"
            assert result.turnover == 2000000.0
            assert result.noOfEmployeesExact == 200

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting single soliditet client."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/soliditet/clients/123456789",
            method="GET",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SoliditetClientsResource(http)
            result = await resource.get("123456789")

            assert isinstance(result, SoliditetClient)
            assert result.dunsNo == "123456789"
            assert result.name == "ACME Corporation AB"
            assert result.sniCode == "62010"

    @pytest.mark.asyncio
    async def test_model_validation(self, sample_data):
        """Test model validation and field types."""
        client = SoliditetClient.model_validate(sample_data)

        assert client.dunsNo == "123456789"
        assert client.name == "ACME Corporation AB"
        assert client.turnover == 1500000.0
        assert client.noOfEmployeesExact == 150
        assert client.country == "Sweden"
        assert client.orgNo == "556677-8899"

    @pytest.mark.asyncio
    async def test_partial_model(self):
        """Test partial model with minimal data."""
        from upsales.models.soliditet_clients import PartialSoliditetClient

        partial = PartialSoliditetClient(dunsNo="123456789", name="ACME Corp")

        assert partial.dunsNo == "123456789"
        assert partial.name == "ACME Corp"

    @pytest.mark.asyncio
    async def test_optional_fields(self):
        """Test model with optional fields missing."""
        minimal_data = {"dunsNo": "123456789"}

        client = SoliditetClient.model_validate(minimal_data)

        assert client.dunsNo == "123456789"
        assert client.name is None
        assert client.turnover is None
        assert client.noOfEmployeesExact is None
