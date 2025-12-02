"""
Unit tests for AgreementsResource.

Tests all CRUD operations for agreements resource.
Uses pytest-httpx for mocking HTTP requests without real API calls.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.agreements import Agreement
from upsales.resources.agreements import AgreementsResource


class TestAgreementsResourceCRUD:
    """Test CRUD operations for AgreementsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample agreement data for testing."""
        return {
            "id": 1,
            "description": "Annual Software License",
            "date": "2025-01-01",
            "agreementGroupId": None,
            "notes": "Enterprise subscription",
            "user": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "client": {"id": 100, "name": "ACME Corp"},
            "contact": {"id": 50, "name": "John Doe"},
            "project": None,
            "children": [],
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "stage": {"id": 1, "name": "Active"},
            "clientConnection": None,
            "currencyRate": 1,
            "currency": "USD",
            "custom": [],
            "orderRow": [
                {
                    "product": {"id": 10, "name": "Enterprise Plan"},
                    "price": 1200,
                    "quantity": 1,
                }
            ],
            "orderValue": 1200,
            "value": 1200,
            "isParent": False,
            "parentId": None,
            "contributionMargin": 800,
            "contributionMarginInAgreementCurrency": 800,
            "purchaseCost": 400,
            "yearlyContributionMargin": 800,
            "yearlyContributionMarginInAgreementCurrency": 800,
            "yearlyValue": 1200,
            "yearlyValueInMasterCurrency": 1200,
            "valueInMasterCurrency": 1200,
            "metadata": {
                "agreementStartdate": "2025-01-01",
                "agreementIntervalPeriod": 12,
                "agreementOrderCreationTime": 1,
                "periodLength": 12,
            },
            "userRemovable": True,
            "userEditable": True,
            "regBy": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "priceListId": 1,
            "invoiceRelatedClient": False,
            "indexIncreaseId": None,
            "latestIndexIncreaseId": None,
            "latestIndexIncreaseDate": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {
                    **sample_data,
                    "id": 2,
                    "description": "Quarterly Support Package",
                    "value": 3000,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an agreement."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            result = await resource.create(
                description="Annual Software License",
                user={"id": 3},
                client={"id": 100},
                stage={"id": 1},
                orderRow=[{"product": {"id": 10}, "price": 1200, "quantity": 1}],
                metadata={
                    "agreementStartdate": "2025-01-01",
                    "agreementIntervalPeriod": 12,
                    "agreementOrderCreationTime": 1,
                    "periodLength": 12,
                },
            )

            assert isinstance(result, Agreement)
            assert result.id == 1
            assert result.description == "Annual Software License"
            assert result.value == 1200

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single agreement."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Agreement)
            assert result.id == 1
            assert result.description == "Annual Software License"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing agreements with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Agreement) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements?limit=100&offset=0&currency=USD",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            results = await resource.search(currency="USD")

            assert len(results) == 1
            assert results[0].currency == "USD"

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an agreement."""
        updated_data = {**sample_data, "description": "Updated License Agreement"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            result = await resource.update(1, description="Updated License Agreement")

            assert result.description == "Updated License Agreement"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an agreement."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/agreements/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AgreementsResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestAgreementModel:
    """Test Agreement model features."""

    @pytest.mark.asyncio
    async def test_custom_fields_access(self):
        """Test custom fields access."""
        agreement_data = {
            "id": 1,
            "description": "Test Agreement",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "user": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "client": {"id": 100, "name": "ACME Corp"},
            "stage": {"id": 1, "name": "Active"},
            "currencyRate": 1,
            "currency": "USD",
            "custom": [{"fieldId": 20, "value": "Priority Customer"}],
            "orderRow": [],
            "metadata": {},
            "priceListId": 1,
            "invoiceRelatedClient": False,
            "value": 1000,
            "contributionMargin": 600,
            "contributionMarginInAgreementCurrency": 600,
            "valueInMasterCurrency": 1000,
            "yearlyValue": 1000,
            "yearlyValueInMasterCurrency": 1000,
            "yearlyContributionMargin": 600,
            "yearlyContributionMarginInAgreementCurrency": 600,
            "purchaseCost": 400,
            "isParent": False,
            "children": [],
            "userRemovable": True,
            "userEditable": True,
        }

        agreement = Agreement(**agreement_data)
        assert agreement.custom_fields[20] == "Priority Customer"

    @pytest.mark.asyncio
    async def test_frozen_fields_protection(self):
        """Test that frozen fields cannot be modified."""
        agreement_data = {
            "id": 1,
            "description": "Test Agreement",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "user": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "client": {"id": 100, "name": "ACME Corp"},
            "stage": {"id": 1, "name": "Active"},
            "currencyRate": 1,
            "currency": "USD",
            "custom": [],
            "orderRow": [],
            "metadata": {},
            "priceListId": 1,
            "invoiceRelatedClient": False,
            "value": 1000,
            "contributionMargin": 600,
            "contributionMarginInAgreementCurrency": 600,
            "valueInMasterCurrency": 1000,
            "yearlyValue": 1000,
            "yearlyValueInMasterCurrency": 1000,
            "yearlyContributionMargin": 600,
            "yearlyContributionMarginInAgreementCurrency": 600,
            "purchaseCost": 400,
            "isParent": False,
            "children": [],
            "userRemovable": True,
            "userEditable": True,
        }

        agreement = Agreement(**agreement_data)

        # Attempt to modify frozen field should raise error
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            agreement.id = 999

    @pytest.mark.asyncio
    async def test_to_api_dict_excludes_frozen(self):
        """Test that to_api_dict excludes frozen fields."""
        agreement_data = {
            "id": 1,
            "description": "Test Agreement",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "user": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "client": {"id": 100, "name": "ACME Corp"},
            "stage": {"id": 1, "name": "Active"},
            "currencyRate": 1,
            "currency": "USD",
            "custom": [],
            "orderRow": [],
            "metadata": {},
            "priceListId": 1,
            "invoiceRelatedClient": False,
            "value": 1000,
            "contributionMargin": 600,
            "contributionMarginInAgreementCurrency": 600,
            "valueInMasterCurrency": 1000,
            "yearlyValue": 1000,
            "yearlyValueInMasterCurrency": 1000,
            "yearlyContributionMargin": 600,
            "yearlyContributionMarginInAgreementCurrency": 600,
            "purchaseCost": 400,
            "isParent": False,
            "children": [],
            "userRemovable": True,
            "userEditable": True,
        }

        agreement = Agreement(**agreement_data)
        api_dict = agreement.to_api_dict()

        # Frozen fields should not be in the dict
        assert "id" not in api_dict
        assert "regDate" not in api_dict
        assert "modDate" not in api_dict
        assert "value" not in api_dict
        assert "contributionMargin" not in api_dict

        # Updatable fields should be present
        assert "description" in api_dict
        assert "currency" in api_dict
