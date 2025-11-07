"""
Unit tests for OrdersResource.

Tests CRUD operations and custom methods for orders endpoint.
Achieves 100% coverage of OrdersResource methods.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.orders import Order
from upsales.resources.orders import OrdersResource


class TestOrdersResourceCRUD:
    """Test CRUD operations for OrdersResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample order data for testing."""
        return {
            "id": 1,
            "description": "Enterprise Deal",
            "date": "2025-01-15",
            "regDate": "2025-01-01",
            "modDate": "2025-01-15",
            "probability": 50,
            "value": 100000,
            "currency": "USD",
            "currencyRate": 1,
            "oneOffValue": 0,
            "monthlyValue": 5000,
            "annualValue": 60000,
            "purchaseCost": 30000,
            "contributionMargin": 70000,
            "contributionMarginLocalCurrency": 70000,
            "valueInMasterCurrency": 100000,
            "oneOffValueInMasterCurrency": 0,
            "monthlyValueInMasterCurrency": 5000,
            "annualValueInMasterCurrency": 60000,
            "weightedValue": 50000,
            "weightedOneOffValue": 0,
            "weightedMonthlyValue": 2500,
            "weightedAnnualValue": 30000,
            "weightedContributionMargin": 35000,
            "weightedContributionMarginLocalCurrency": 35000,
            "weightedValueInMasterCurrency": 50000,
            "weightedOneOffValueInMasterCurrency": 0,
            "weightedMonthlyValueInMasterCurrency": 2500,
            "weightedAnnualValueInMasterCurrency": 30000,
            "client": {"id": 10, "name": "ACME Corp"},
            "user": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "stage": {"id": 3, "name": "Qualified"},
            "regBy": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "contact": None,
            "priceListId": 1,
            "recurringInterval": 1,
            "locked": 0,
            "invoiceRelatedClient": False,
            "confirmedSolution": False,
            "userEditable": True,
            "userRemovable": True,
            "closeDate": "2025-12-31",
            "notes": "Important client",
            "confirmedDate": None,
            "confirmedBudget": None,
            "agreement": None,
            "project": None,
            "competitorId": None,
            "lostReason": None,
            "marketingContribution": None,
            "clientConnection": None,
            "userSalesStatistics": None,
            "orderRow": [],
            "checklist": [],
            "stakeholders": [],
            "titleCategories": [],
            "projectPlanOptions": [],
            "salesCoach": [],
            "lastIntegrationStatus": [],
            "noCompletedAppointments": 5,
            "noPostponedAppointments": 2,
            "noTimesCallsNotAnswered": 1,
            "noTimesClosingDateChanged": 3,
            "noTimesOrderValueChanged": 2,
            "risks": {},
            "custom": [],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "description": "SMB Deal", "value": 20000},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an order."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            result = await resource.create(
                description="Enterprise Deal",
                date="2025-01-15",
                probability=50,
                value=100000,
            )

            assert isinstance(result, Order)
            assert result.id == 1
            assert result.description == "Enterprise Deal"
            assert result.value == 100000
            assert result.probability == 50

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single order."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            result = await resource.get(1)

            assert isinstance(result, Order)
            assert result.id == 1
            assert result.description == "Enterprise Deal"
            assert result.expected_value == 50000.0  # 100000 * 50%

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing orders with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, Order) for r in results)
            assert results[0].description == "Enterprise Deal"
            assert results[1].description == "SMB Deal"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, Order) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an order."""
        updated_data = {**sample_data, "probability": 75, "value": 150000}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            result = await resource.update(1, probability=75, value=150000)

            assert isinstance(result, Order)
            assert result.id == 1
            assert result.probability == 75
            assert result.value == 150000

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an order."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?probability=gte%3A75&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.search(probability=">=75")

            assert len(results) == 1
            assert results[0].id == 1


class TestOrdersResourceCustomMethods:
    """Test custom methods for OrdersResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample order data for testing."""
        return {
            "id": 1,
            "description": "Test Order",
            "date": "2025-01-15",
            "regDate": "2025-01-01",
            "modDate": "2025-01-15",
            "probability": 50,
            "value": 100000,
            "currency": "USD",
            "currencyRate": 1,
            "oneOffValue": 0,
            "monthlyValue": 5000,
            "annualValue": 60000,
            "purchaseCost": 30000,
            "contributionMargin": 70000,
            "contributionMarginLocalCurrency": 70000,
            "valueInMasterCurrency": 100000,
            "oneOffValueInMasterCurrency": 0,
            "monthlyValueInMasterCurrency": 5000,
            "annualValueInMasterCurrency": 60000,
            "weightedValue": 50000,
            "weightedOneOffValue": 0,
            "weightedMonthlyValue": 2500,
            "weightedAnnualValue": 30000,
            "weightedContributionMargin": 35000,
            "weightedContributionMarginLocalCurrency": 35000,
            "weightedValueInMasterCurrency": 50000,
            "weightedOneOffValueInMasterCurrency": 0,
            "weightedMonthlyValueInMasterCurrency": 2500,
            "weightedAnnualValueInMasterCurrency": 30000,
            "client": {"id": 10, "name": "ACME Corp"},
            "user": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "stage": {"id": 3, "name": "Qualified"},
            "regBy": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "contact": None,
            "priceListId": 1,
            "recurringInterval": 1,
            "locked": 0,
            "invoiceRelatedClient": False,
            "confirmedSolution": False,
            "userEditable": True,
            "userRemovable": True,
            "closeDate": "2025-12-31",
            "notes": None,
            "confirmedDate": None,
            "confirmedBudget": None,
            "agreement": None,
            "project": None,
            "competitorId": None,
            "lostReason": None,
            "marketingContribution": None,
            "clientConnection": None,
            "userSalesStatistics": None,
            "orderRow": [],
            "checklist": [],
            "stakeholders": [],
            "titleCategories": [],
            "projectPlanOptions": [],
            "salesCoach": [],
            "lastIntegrationStatus": [],
            "noCompletedAppointments": 0,
            "noPostponedAppointments": 0,
            "noTimesCallsNotAnswered": 0,
            "noTimesClosingDateChanged": 0,
            "noTimesOrderValueChanged": 0,
            "risks": {},
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_by_company(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders by company."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?client.id=10&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_by_company(10)

            assert len(results) == 1
            assert results[0].client.id == 10

    @pytest.mark.asyncio
    async def test_get_by_user(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders by user."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?user.id=5&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_by_user(5)

            assert len(results) == 1
            assert results[0].user.id == 5

    @pytest.mark.asyncio
    async def test_get_by_stage(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders by stage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?stage.id=3&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_by_stage(3)

            assert len(results) == 1
            assert results[0].stage.id == 3

    @pytest.mark.asyncio
    async def test_get_high_value(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting high value orders."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?value=gte%3A100000&sort=-value&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_high_value(100000)

            assert len(results) == 1
            assert results[0].value >= 100000

    @pytest.mark.asyncio
    async def test_get_by_probability_range(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders by probability range."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?probability=gte%3A75&probability_max=lte%3A100&sort=-probability&limit=100&offset=0",
            json={"error": None, "data": [{**sample_data, "probability": 80}]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_by_probability_range(75, 100)

            assert len(results) == 1
            assert 75 <= results[0].probability <= 100

    @pytest.mark.asyncio
    async def test_get_closing_soon(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders closing soon."""
        from datetime import datetime, timedelta

        today = datetime.now().date()
        target_date = today + timedelta(days=30)

        # Match specific URL with date parameters (operators are transformed to gte: and lte:)
        httpx_mock.add_response(
            url=f"https://power.upsales.com/api/v2/orders?closeDate=gte%3A{today.isoformat()}&closeDate_max=lte%3A{target_date.isoformat()}&sort=closeDate&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_closing_soon(30)

            assert len(results) == 1
            assert results[0].closeDate is not None

    @pytest.mark.asyncio
    async def test_get_recurring(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting orders with recurring revenue."""
        # Add non-recurring order
        non_recurring = {**sample_data, "id": 2, "monthlyValue": 0, "annualValue": 0}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/orders?limit=100&offset=0",
            json={"error": None, "data": [sample_data, non_recurring]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OrdersResource(http)
            results = await resource.get_recurring()

            # Only the order with monthlyValue > 0 should be returned
            assert len(results) == 1
            assert results[0].is_recurring


class TestOrderModel:
    """Test Order model computed fields."""

    def test_computed_fields(self):
        """Test all computed fields."""
        order_data = {
            "id": 1,
            "description": "Test",
            "date": "2025-01-01",
            "regDate": "2025-01-01",
            "modDate": "2025-01-01",
            "probability": 50,
            "value": 100000,
            "monthlyValue": 5000,
            "annualValue": 60000,
            "contributionMargin": 30000,
            "locked": 0,
            "currency": "USD",
            "currencyRate": 1,
            "oneOffValue": 0,
            "purchaseCost": 0,
            "contributionMarginLocalCurrency": 0,
            "valueInMasterCurrency": 0,
            "oneOffValueInMasterCurrency": 0,
            "monthlyValueInMasterCurrency": 0,
            "annualValueInMasterCurrency": 0,
            "weightedValue": 0,
            "weightedOneOffValue": 0,
            "weightedMonthlyValue": 0,
            "weightedAnnualValue": 0,
            "weightedContributionMargin": 0,
            "weightedContributionMarginLocalCurrency": 0,
            "weightedValueInMasterCurrency": 0,
            "weightedOneOffValueInMasterCurrency": 0,
            "weightedMonthlyValueInMasterCurrency": 0,
            "weightedAnnualValueInMasterCurrency": 0,
            "client": {"id": 1, "name": "Test Co"},
            "user": {"id": 1, "name": "Test User", "email": "test@example.com"},
            "stage": {"id": 1, "name": "Qualified"},
            "regBy": {"id": 1, "name": "Test User", "email": "test@example.com"},
            "priceListId": 0,
            "recurringInterval": 0,
            "invoiceRelatedClient": False,
            "confirmedSolution": False,
            "userEditable": True,
            "userRemovable": True,
            "orderRow": [],
            "checklist": [],
            "stakeholders": [],
            "titleCategories": [],
            "projectPlanOptions": [],
            "salesCoach": [],
            "lastIntegrationStatus": [],
            "noCompletedAppointments": 0,
            "noPostponedAppointments": 0,
            "noTimesCallsNotAnswered": 0,
            "noTimesClosingDateChanged": 0,
            "noTimesOrderValueChanged": 0,
            "risks": {},
            "custom": [],
        }

        order = Order(**order_data)

        # Test computed fields
        assert order.is_locked is False
        assert order.expected_value == 50000.0  # 100000 * 50%
        assert order.is_recurring is True  # monthlyValue > 0
        assert order.margin_percentage == 30.0  # (30000/100000) * 100

    def test_locked_order(self):
        """Test is_locked computed field."""
        order = Order(
            id=1,
            description="Test",
            date="2025-01-01",
            regDate="2025-01-01",
            modDate="2025-01-01",
            probability=50,
            locked=1,  # Locked
            client={"id": 1, "name": "Test Co"},
            user={"id": 1, "name": "Test User", "email": "test@example.com"},
        )

        assert order.is_locked is True

    def test_non_recurring_order(self):
        """Test is_recurring for non-recurring orders."""
        order = Order(
            id=1,
            description="Test",
            date="2025-01-01",
            regDate="2025-01-01",
            modDate="2025-01-01",
            probability=50,
            monthlyValue=0,
            annualValue=0,
            client={"id": 1, "name": "Test Co"},
            user={"id": 1, "name": "Test User", "email": "test@example.com"},
        )

        assert order.is_recurring is False
