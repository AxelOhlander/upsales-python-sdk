"""
Unit tests for StandardIntegrationUserSettingsResource.

Tests CRUD operations and custom methods for standardIntegrationUserSettings endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.standard_integration_user_settings import StandardIntegrationUserSettings
from upsales.resources.standard_integration_user_settings import (
    StandardIntegrationUserSettingsResource,
)


class TestStandardIntegrationUserSettingsResourceCRUD:
    """Test CRUD operations for StandardIntegrationUserSettingsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample standard integration user settings data for testing."""
        return {
            "id": 1,
            "userId": 100,
            "integrationId": 10,
            "version": 1,
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
                    "userId": 200,
                    "integrationId": 20,
                    "active": 0,
                    "configJson": '{"key": "value2"}',
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating standard integration user settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            result = await resource.create(
                integrationId=10,
                active=1,
                configJson='{"key": "value", "enabled": true}',
            )

            assert isinstance(result, StandardIntegrationUserSettings)
            assert result.id == 1
            assert result.userId == 100
            assert result.integrationId == 10
            assert result.is_active
            assert result.configJson == '{"key": "value", "enabled": true}'

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single standard integration user settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            result = await resource.get(1)

            assert isinstance(result, StandardIntegrationUserSettings)
            assert result.id == 1
            assert result.userId == 100
            assert result.integrationId == 10
            assert result.is_active
            assert result.regDate == "2024-01-01T00:00:00Z"
            assert result.modDate == "2024-01-15T00:00:00Z"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing standard integration user settings with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegrationUserSettings) for r in results)
            assert results[0].userId == 100
            assert results[1].userId == 200

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegrationUserSettings) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating standard integration user settings."""
        updated_data = {
            **sample_data,
            "active": 0,
            "configJson": '{"key": "updated"}',
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            result = await resource.update(
                1,
                active=0,
                configJson='{"key": "updated"}',
            )

            assert isinstance(result, StandardIntegrationUserSettings)
            assert result.id == 1
            assert not result.is_active
            assert result.configJson == '{"key": "updated"}'

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting standard integration user settings."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegrationUserSettings/{i}",
                method="PUT",
                json={
                    "error": None,
                    "data": {**sample_data, "id": i, "active": 0},
                },
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"active": 0},
            )

            assert len(results) == 3
            assert all(isinstance(item, StandardIntegrationUserSettings) for item in results)
            assert all(not r.is_active for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/standardIntegrationUserSettings/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestStandardIntegrationUserSettingsResourceCustomMethods:
    """Test custom methods specific to StandardIntegrationUserSettingsResource."""

    @pytest.fixture
    def sample_settings(self):
        """Sample settings for custom method testing."""
        return [
            {
                "id": 1,
                "userId": 100,
                "integrationId": 10,
                "version": 1,
                "regDate": "2024-01-01T00:00:00Z",
                "modDate": "2024-01-15T00:00:00Z",
                "active": 1,
                "configJson": '{"enabled": true}',
            },
            {
                "id": 2,
                "userId": 100,
                "integrationId": 20,
                "version": 1,
                "regDate": "2024-02-01T00:00:00Z",
                "modDate": "2024-02-15T00:00:00Z",
                "active": 0,
                "configJson": '{"enabled": false}',
            },
            {
                "id": 3,
                "userId": 200,
                "integrationId": 10,
                "version": 1,
                "regDate": "2024-03-01T00:00:00Z",
                "modDate": "2024-03-15T00:00:00Z",
                "active": 1,
                "configJson": '{"key": "value"}',
            },
        ]

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_settings):
        """Test get_active() custom method."""
        active_settings = [s for s in sample_settings if s["active"] == 1]
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardIntegrationUserSettings?limit=100&offset=0&active=1",
            json={"error": None, "data": active_settings},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardIntegrationUserSettingsResource(http)
            results = await resource.get_active()

            assert len(results) == 2
            assert all(isinstance(r, StandardIntegrationUserSettings) for r in results)
            assert all(r.is_active for r in results)


class TestStandardIntegrationUserSettingsModel:
    """Test StandardIntegrationUserSettings model properties and methods."""

    @pytest.mark.asyncio
    async def test_is_active_property(self):
        """Test is_active property."""
        settings_active = StandardIntegrationUserSettings(
            id=1,
            userId=100,
            integrationId=10,
            active=1,
        )
        assert settings_active.is_active

        settings_inactive = StandardIntegrationUserSettings(
            id=2,
            userId=100,
            integrationId=10,
            active=0,
        )
        assert not settings_inactive.is_active

    @pytest.mark.asyncio
    async def test_frozen_fields(self):
        """Test that frozen fields cannot be modified."""
        settings = StandardIntegrationUserSettings(
            id=1,
            userId=100,
            integrationId=10,
            active=1,
        )

        # Attempt to modify frozen field
        with pytest.raises(Exception):  # Pydantic raises validation error
            settings.id = 999

        with pytest.raises(Exception):
            settings.userId = 999

        with pytest.raises(Exception):
            settings.integrationId = 999
