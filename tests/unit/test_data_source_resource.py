"""Unit tests for DataSourceResource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.data_source import DataSourceResponse
from upsales.resources.data_source import DataSourceResource


@pytest.mark.asyncio
async def test_get(httpx_mock: HTTPXMock):
    """Test GET request to data source endpoint."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/config?integrationId=123",
        json={
            "error": None,
            "data": {"success": True, "data": {"setting": "value"}},
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.get(path="config", integration_id=123)

        assert isinstance(result, DataSourceResponse)
        assert result.success is True
        assert result.data == {"setting": "value"}


@pytest.mark.asyncio
async def test_typeahead(httpx_mock: HTTPXMock):
    """Test typeahead operation."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/typeahead",
        json={
            "error": None,
            "data": {"success": True, "data": {"results": [{"name": "John"}]}},
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.typeahead(integration_id=123, type_="contact", query="john")

        assert isinstance(result, DataSourceResponse)
        assert result.success is True
        assert "results" in result.data


@pytest.mark.asyncio
async def test_buy(httpx_mock: HTTPXMock):
    """Test buy operation."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/buy",
        json={
            "error": None,
            "data": {"success": True, "data": {"id": "ext_123", "imported": True}},
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.buy(
            integration_id=123,
            type_="contact",
            external_id="ext_123",
            name="John Smith",
        )

        assert isinstance(result, DataSourceResponse)
        assert result.success is True
        assert result.data.get("imported") is True


@pytest.mark.asyncio
async def test_settings(httpx_mock: HTTPXMock):
    """Test settings operation."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/settings",
        json={
            "error": None,
            "data": {"success": True, "data": {"configured": True}},
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.settings(
            integration_id=123, type_="sync", enabled=True, interval=3600
        )

        assert isinstance(result, DataSourceResponse)
        assert result.success is True
        assert result.data.get("configured") is True


@pytest.mark.asyncio
async def test_monitor(httpx_mock: HTTPXMock):
    """Test monitor operation."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/monitor",
        json={
            "error": None,
            "data": {"success": True, "data": {"status": "healthy", "uptime": 99.9}},
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.monitor(integration_id=123, type_="health")

        assert isinstance(result, DataSourceResponse)
        assert result.success is True
        assert result.data.get("status") == "healthy"


@pytest.mark.asyncio
async def test_error_response(httpx_mock: HTTPXMock):
    """Test handling of error responses."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/datasource/typeahead",
        json={
            "error": None,
            "data": {
                "success": False,
                "data": None,
                "error": "Integration not found",
            },
        },
    )

    async with HTTPClient(token="test-token", auth_manager=None) as http:
        resource = DataSourceResource(http)
        result = await resource.typeahead(integration_id=999, type_="contact")

        assert isinstance(result, DataSourceResponse)
        assert result.success is False
        assert result.error == "Integration not found"
        assert result.data is None
