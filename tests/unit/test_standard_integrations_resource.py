"""
Unit tests for StandardIntegrationsResource.

Tests CRUD operations and custom methods for standardIntegration endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.standard_integration import StandardIntegration
from upsales.resources.standard_integrations import StandardIntegrationsResource


class TestStandardIntegrationsResourceCRUD:
    """Test CRUD operations for StandardIntegrationsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample standard integration data for testing."""
        return {
            "id": 1,
            "name": "Salesforce Integration",
            "description": "Connect with Salesforce CRM",
            "descriptionLong": "Full integration with Salesforce CRM platform",
            "alias": "salesforce-crm",
            "category": "CRM",
            "url": "https://www.salesforce.com",
            "imageLink": "https://example.com/salesforce.png",
            "color": "#1798C1",
            "version": "2.1.0",
            "active": True,
            "visible": True,
            "public": True,
            "userOnly": False,
            "userConfigurable": True,
            "externalConfig": False,
            "apiKey": True,
            "hideForNew": False,
            "endpoint": "https://api.salesforce.com",
            "authenticationKey": None,
            "supportEmail": "support@salesforce.com",
            "hostingProvider": "AWS",
            "hostingLocation": "US-EAST-1",
            "region": "US",
            "langTagPrefix": "integration.salesforce",
            "configJson": "{}",
            "price": None,
            "pricePerUser": 25,
            "env": 1,
            "publisherClientId": 100,
            "publisherName": "Salesforce Inc",
            "termsAccepted": "2024-01-01T00:00:00Z",
            "termsAcceptedUser": "admin@example.com",
            "inputDebounceInMs": None,
            "contract": {},
            "userContract": None,
            "standardIntegrationInit": [],
            "standardIntegrationTag": ["crm", "sales"],
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
                    "name": "HubSpot Integration",
                    "alias": "hubspot-crm",
                    "category": "Marketing",
                    "active": False,
                    "apiKey": False,
                    "publisherName": "HubSpot Inc",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a standard integration."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.create(
                name="Salesforce Integration",
                description="Connect with Salesforce CRM",
                category="CRM",
                active=True,
            )

            assert isinstance(result, StandardIntegration)
            assert result.id == 1
            assert result.name == "Salesforce Integration"
            assert result.category == "CRM"
            assert result.is_active
            assert result.requires_api_key

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single standard integration."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.get(1)

            assert isinstance(result, StandardIntegration)
            assert result.id == 1
            assert result.name == "Salesforce Integration"
            assert result.is_active
            assert result.is_visible
            assert result.is_public
            assert result.requires_api_key
            assert result.has_pricing
            assert result.display_name == "Salesforce Integration v2.1.0"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing standard integrations with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert results[0].name == "Salesforce Integration"
            assert results[1].name == "HubSpot Integration"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a standard integration."""
        updated_data = {**sample_data, "name": "Salesforce Pro", "active": False}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.update(1, name="Salesforce Pro", active=False)

            assert isinstance(result, StandardIntegration)
            assert result.id == 1
            assert result.name == "Salesforce Pro"
            assert not result.is_active

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a standard integration."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        # Mock responses for each update
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegration/{i}",
                method="PUT",
                json={
                    "error": None,
                    "data": {**sample_data, "id": i, "active": False},
                },
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"active": False},
            )

            assert len(results) == 3
            assert all(isinstance(item, StandardIntegration) for item in results)
            assert all(not r.is_active for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        # Mock responses for each delete
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegration/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestStandardIntegrationsResourceCustomMethods:
    """Test custom methods specific to StandardIntegrationsResource."""

    @pytest.fixture
    def sample_integrations(self):
        """Sample integrations for custom method testing."""
        return [
            {
                "id": 1,
                "name": "Salesforce Integration",
                "description": "CRM Integration",
                "descriptionLong": "Full Salesforce integration",
                "alias": "salesforce-crm",
                "category": "CRM",
                "url": "https://www.salesforce.com",
                "imageLink": None,
                "color": "#1798C1",
                "version": "2.1.0",
                "active": True,
                "visible": True,
                "public": True,
                "userOnly": False,
                "userConfigurable": True,
                "externalConfig": False,
                "apiKey": True,
                "hideForNew": False,
                "endpoint": None,
                "authenticationKey": None,
                "supportEmail": "support@salesforce.com",
                "hostingProvider": "AWS",
                "hostingLocation": "US-EAST-1",
                "region": "US",
                "langTagPrefix": "integration.salesforce",
                "configJson": "{}",
                "price": None,
                "pricePerUser": 25,
                "env": 1,
                "publisherClientId": 100,
                "publisherName": "Salesforce Inc",
                "termsAccepted": None,
                "termsAcceptedUser": None,
                "inputDebounceInMs": None,
                "contract": {},
                "userContract": None,
                "standardIntegrationInit": [],
                "standardIntegrationTag": [],
            },
            {
                "id": 2,
                "name": "HubSpot Integration",
                "description": "Marketing Integration",
                "descriptionLong": "Full HubSpot integration",
                "alias": "hubspot-marketing",
                "category": "Marketing",
                "url": "https://www.hubspot.com",
                "imageLink": None,
                "color": "#FF7A59",
                "version": "1.5.0",
                "active": False,
                "visible": True,
                "public": True,
                "userOnly": False,
                "userConfigurable": True,
                "externalConfig": False,
                "apiKey": False,
                "hideForNew": False,
                "endpoint": None,
                "authenticationKey": None,
                "supportEmail": "support@hubspot.com",
                "hostingProvider": "GCP",
                "hostingLocation": "EU-WEST-1",
                "region": "EU",
                "langTagPrefix": "integration.hubspot",
                "configJson": "{}",
                "price": 100,
                "pricePerUser": None,
                "env": 1,
                "publisherClientId": 101,
                "publisherName": "HubSpot Inc",
                "termsAccepted": None,
                "termsAcceptedUser": None,
                "inputDebounceInMs": None,
                "contract": {},
                "userContract": None,
                "standardIntegrationInit": [],
                "standardIntegrationTag": [],
            },
            {
                "id": 3,
                "name": "Slack Integration",
                "description": "Communication tool",
                "descriptionLong": "Slack messaging integration",
                "alias": "slack-messaging",
                "category": "Communication",
                "url": "https://www.slack.com",
                "imageLink": None,
                "color": "#36C5F0",
                "version": "3.0.0",
                "active": True,
                "visible": False,
                "public": False,
                "userOnly": True,
                "userConfigurable": False,
                "externalConfig": True,
                "apiKey": True,
                "hideForNew": True,
                "endpoint": None,
                "authenticationKey": None,
                "supportEmail": "support@slack.com",
                "hostingProvider": "AWS",
                "hostingLocation": "US-WEST-2",
                "region": "US",
                "langTagPrefix": "integration.slack",
                "configJson": "{}",
                "price": None,
                "pricePerUser": None,
                "env": 1,
                "publisherClientId": 100,
                "publisherName": "Salesforce Inc",
                "termsAccepted": None,
                "termsAcceptedUser": None,
                "inputDebounceInMs": None,
                "contract": {},
                "userContract": None,
                "standardIntegrationInit": [],
                "standardIntegrationTag": [],
            },
        ]

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_name() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.get_by_name("Salesforce Integration")

            assert result is not None
            assert isinstance(result, StandardIntegration)
            assert result.id == 1
            assert result.name == "Salesforce Integration"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_name() when integration not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.get_by_name("Nonexistent Integration")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_alias(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_alias() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            result = await resource.get_by_alias("hubspot-marketing")

            assert result is not None
            assert isinstance(result, StandardIntegration)
            assert result.id == 2
            assert result.alias == "hubspot-marketing"

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_active() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_active()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.is_active for r in results)
            assert results[0].name == "Salesforce Integration"
            assert results[1].name == "Slack Integration"

    @pytest.mark.asyncio
    async def test_get_visible(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_visible() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_visible()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.is_visible for r in results)

    @pytest.mark.asyncio
    async def test_get_public(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_public() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_public()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.is_public for r in results)

    @pytest.mark.asyncio
    async def test_get_by_category(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_category() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_by_category("CRM")

            assert len(results) == 1
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert results[0].category == "CRM"
            assert results[0].name == "Salesforce Integration"

    @pytest.mark.asyncio
    async def test_get_by_publisher(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_publisher() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_by_publisher("Salesforce Inc")

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.publisherName == "Salesforce Inc" for r in results)

    @pytest.mark.asyncio
    async def test_get_with_api_key(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_with_api_key() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_with_api_key()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.requires_api_key for r in results)

    @pytest.mark.asyncio
    async def test_get_user_configurable(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_user_configurable() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_user_configurable()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.userConfigurable for r in results)

    @pytest.mark.asyncio
    async def test_get_with_pricing(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_with_pricing() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_with_pricing()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.has_pricing for r in results)

    @pytest.mark.asyncio
    async def test_get_by_region(self, httpx_mock: HTTPXMock, sample_integrations):
        """Test get_by_region() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegration?limit=100&offset=0",
            json={"error": None, "data": sample_integrations},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationsResource(http)
            results = await resource.get_by_region("US")

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegration) for r in results)
            assert all(r.region == "US" for r in results)
