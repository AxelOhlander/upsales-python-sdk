"""
Unit tests for MetadataResource.

Note: Metadata endpoint is different from standard CRUD resources:
- Returns single dict (not a list)
- Read-only (no create/update/delete)
- Contains system configuration, user info, currencies, and field definitions

Tests cover:
- get() - Get system metadata
- get_currencies() - Get currency list
- get_default_currency() - Get default currency
- get_entity_fields() - Get field definitions for entity type
- get_required_fields() - Get required fields for entity type
- is_field_required() - Check if field is required
- get_user_info() - Get current user info
- get_system_version() - Get system version
- get_license_count() - Get license count
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.metadata import Currency, FieldDefinition, Metadata, MetadataUser
from upsales.resources.metadata import MetadataResource


class TestMetadataResource:
    """Test MetadataResource operations."""

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata data for testing."""
        return {
            "customerCurrencies": [
                {
                    "iso": "SEK",
                    "rate": 1.0,
                    "masterCurrency": True,
                    "active": True,
                },
                {
                    "iso": "USD",
                    "rate": 0.106791513,
                    "masterCurrency": False,
                    "active": True,
                },
                {
                    "iso": "EUR",
                    "rate": 0.091776799,
                    "masterCurrency": False,
                    "active": True,
                },
            ],
            "defaultCurrency": {
                "iso": "SEK",
                "rate": 1.0,
                "masterCurrency": True,
                "active": True,
            },
            "params": {
                "teamAccountManager": False,
                "MultiCurrency": True,
                "sessionTime": 600,
                "UseDiscount": True,
                "HasSamlLogin": False,
            },
            "user": {
                "id": 18,
                "name": "Test User",
                "administrator": True,
                "roleId": 5,
                "teamLeader": False,
                "active": True,
                "ghost": False,
                "free": False,
                "userTitle": "Sales Manager",
                "userAddress": None,
                "userZipCode": None,
                "userState": None,
                "userPhone": None,
                "userCellPhone": None,
                "export": True,
                "billingAdmin": False,
                "regDate": "2025-11-03T04:12:11.000Z",
                "crm": True,
                "support": False,
                "service": False,
                "supportAdmin": False,
                "projectAdmin": False,
                "custom": [],
            },
            "role": None,
            "version": "Enterprise",
            "licenses": 10,
            "supportLicenses": 2,
            "soliditetCredits": 100,
            "metaChannel": "private-meta_PRODUCTION_1000908",
            "notificationChannel": "private-PRODUCTION_1000908",
            "notificationUserChannel": "private-18_PRODUCTION_1000908",
            "publicChannel": "public-PRODUCTION",
            "iOSInterest": "18_PRODUCTION_1000908",
            "requiredFields": {
                "Client": {
                    "Name": False,
                    "Phone": False,
                    "Email": True,
                },
                "Contact": {
                    "Name": True,
                    "Email": False,
                },
            },
            "standardFields": {
                "Client": {
                    "Name": {
                        "id": 1,
                        "field": "name",
                        "name": "Name",
                        "type": "String",
                        "required": False,
                        "disabled": False,
                        "editable": False,
                        "active": True,
                        "canHide": False,
                        "canMakeRequired": True,
                        "sortOrder": 1,
                        "group": "standard",
                        "size": 100,
                        "selectOptions": [],
                    },
                    "Phone": {
                        "id": 5,
                        "field": "phone",
                        "name": "Phone",
                        "type": "String",
                        "required": False,
                        "disabled": False,
                        "editable": False,
                        "active": True,
                        "canHide": False,
                        "canMakeRequired": True,
                        "sortOrder": 23,
                        "group": "contactInfo",
                        "size": 30,
                        "selectOptions": [],
                    },
                },
                "Contact": {
                    "Name": {
                        "id": 31,
                        "field": "name",
                        "name": "Name",
                        "type": "String",
                        "required": True,
                        "disabled": False,
                        "editable": False,
                        "active": True,
                        "canHide": False,
                        "canMakeRequired": True,
                        "sortOrder": 1,
                        "group": "standard",
                        "size": 50,
                        "selectOptions": [],
                    },
                },
            },
        }

    @pytest.fixture
    def sample_api_response(self, sample_metadata):
        """Sample API response for metadata."""
        # Metadata returns data dict directly (not wrapped in {"error": null, "data": {...}})
        return {"error": None, "data": sample_metadata}

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting system metadata."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            result = await resource.get()

            assert isinstance(result, Metadata)
            assert result.version == "Enterprise"
            assert result.licenses == 10
            assert result.supportLicenses == 2
            assert result.user.name == "Test User"
            assert len(result.customerCurrencies) == 3
            assert result.defaultCurrency.iso == "SEK"

    @pytest.mark.asyncio
    async def test_get_currencies(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting currencies from metadata."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            results = await resource.get_currencies()

            assert isinstance(results, list)
            assert len(results) == 3
            assert all(isinstance(c, Currency) for c in results)
            assert results[0].iso == "SEK"
            assert results[1].iso == "USD"

    @pytest.mark.asyncio
    async def test_get_default_currency(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting default currency."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            result = await resource.get_default_currency()

            assert isinstance(result, Currency)
            assert result.iso == "SEK"
            assert result.is_master is True

    @pytest.mark.asyncio
    async def test_get_entity_fields(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting field definitions for entity type."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            results = await resource.get_entity_fields("Client")

            assert isinstance(results, dict)
            assert len(results) == 2
            assert "Name" in results
            assert "Phone" in results
            assert isinstance(results["Name"], FieldDefinition)
            assert results["Name"].type == "String"
            assert results["Name"].id == 1

    @pytest.mark.asyncio
    async def test_get_required_fields(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting required fields for entity type."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            results = await resource.get_required_fields("Client")

            assert isinstance(results, dict)
            assert results["Name"] is False
            assert results["Phone"] is False
            assert results["Email"] is True

    @pytest.mark.asyncio
    async def test_is_field_required(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test checking if field is required."""
        # Mock two responses since we call is_field_required twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)

            # Email is required
            result = await resource.is_field_required("Client", "Email")
            assert result is True

            # Name is not required
            result = await resource.is_field_required("Client", "Name")
            assert result is False

    @pytest.mark.asyncio
    async def test_get_user_info(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting current user info."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            result = await resource.get_user_info()

            assert isinstance(result, MetadataUser)
            assert result.name == "Test User"
            assert result.id == 18
            assert result.is_admin is True
            assert result.roleId == 5

    @pytest.mark.asyncio
    async def test_get_system_version(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting system version."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            result = await resource.get_system_version()

            assert result == "Enterprise"

    @pytest.mark.asyncio
    async def test_get_license_count(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting license count."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            result = await resource.get_license_count()

            assert result == 10

    @pytest.mark.asyncio
    async def test_metadata_computed_fields(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test Metadata model computed fields."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            metadata = await resource.get()

            # Test computed fields
            assert metadata.currency_count == 3
            assert metadata.has_multi_currency is True
            assert metadata.is_enterprise is True

            master = metadata.master_currency
            assert master is not None
            assert master.iso == "SEK"

            active = metadata.active_currencies
            assert len(active) == 3

    @pytest.mark.asyncio
    async def test_metadata_helper_methods(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test Metadata model helper methods."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/metadata",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MetadataResource(http)
            metadata = await resource.get()

            # Test get_currency_by_iso
            usd = metadata.get_currency_by_iso("USD")
            assert usd is not None
            assert usd.iso == "USD"

            unknown = metadata.get_currency_by_iso("ZZZ")
            assert unknown is None

            # Test is_field_required
            assert metadata.is_field_required("Client", "Email") is True
            assert metadata.is_field_required("Client", "Name") is False
