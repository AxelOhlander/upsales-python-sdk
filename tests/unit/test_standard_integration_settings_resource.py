"""
Unit tests for StandardIntegrationSettingsResource.

Tests CRUD operations and custom methods for standardIntegrationSettings endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.standard_integration_settings import StandardIntegrationSettings
from upsales.resources.standard_integration_settings import StandardIntegrationSettingsResource


class TestStandardIntegrationSettingsResourceCRUD:
    """Test CRUD operations for StandardIntegrationSettingsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample standard integration settings data for testing."""
        return {
            "id": 1,
            "integrationId": 10,
            "version": "1.0.0",
            "regDate": "2024-01-01T00:00:00Z",
            "modDate": "2024-01-15T00:00:00Z",
            "active": 1,
            "configJson": '{"key": "value", "enabled": true}',
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
                    "integrationId": 20,
                    "version": "2.0.0",
                    "active": 0,
                    "configJson": '{"key": "value2"}',
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating standard integration settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            result = await resource.create(
                integrationId=10,
                version="1.0.0",
                active=1,
                configJson='{"key": "value", "enabled": true}',
            )

            assert isinstance(result, StandardIntegrationSettings)
            assert result.id == 1
            assert result.integrationId == 10
            assert result.version == "1.0.0"
            assert result.is_active
            assert result.configJson == '{"key": "value", "enabled": true}'

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single standard integration settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            result = await resource.get(1)

            assert isinstance(result, StandardIntegrationSettings)
            assert result.id == 1
            assert result.integrationId == 10
            assert result.version == "1.0.0"
            assert result.is_active
            assert result.regDate == "2024-01-01T00:00:00Z"
            assert result.modDate == "2024-01-15T00:00:00Z"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing standard integration settings with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegrationSettings) for r in results)
            assert results[0].integrationId == 10
            assert results[1].integrationId == 20

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegrationSettings) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating standard integration settings."""
        updated_data = {
            **sample_data,
            "version": "1.1.0",
            "active": 0,
            "configJson": '{"key": "updated"}',
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            result = await resource.update(
                1,
                version="1.1.0",
                active=0,
                configJson='{"key": "updated"}',
            )

            assert isinstance(result, StandardIntegrationSettings)
            assert result.id == 1
            assert result.version == "1.1.0"
            assert not result.is_active
            assert result.configJson == '{"key": "updated"}'

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting standard integration settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationSettings/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegrationSettings/{i}",
                method="PUT",
                json={
                    "error": None,
                    "data": {**sample_data, "id": i, "active": 0},
                },
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"active": 0},
            )

            assert len(results) == 3
            assert all(isinstance(item, StandardIntegrationSettings) for item in results)
            assert all(not r.is_active for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegrationSettings/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationSettingsResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestStandardIntegrationSettingsModel:
    """Test StandardIntegrationSettings model properties and methods."""

    @pytest.mark.asyncio
    async def test_is_active_property(self):
        """Test is_active property."""
        settings_active = StandardIntegrationSettings(
            id=1,
            integrationId=10,
            version="1.0.0",
            active=1,
        )
        assert settings_active.is_active

        settings_inactive = StandardIntegrationSettings(
            id=2,
            integrationId=10,
            version="1.0.0",
            active=0,
        )
        assert not settings_inactive.is_active

    @pytest.mark.asyncio
    async def test_frozen_fields(self):
        """Test that frozen fields cannot be modified."""
        settings = StandardIntegrationSettings(
            id=1,
            integrationId=10,
            version="1.0.0",
            active=1,
        )

        # Attempt to modify frozen field
        with pytest.raises(Exception):  # Pydantic raises validation error
            settings.id = 999

        with pytest.raises(Exception):
            settings.integrationId = 999
