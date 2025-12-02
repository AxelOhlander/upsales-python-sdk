"""
Unit tests for bulk prospecting save resource.

Tests the BulkResource class which handles bulk saving of prospecting companies.
This is a specialized resource that only supports POST operations.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.bulk import BulkSaveResponse
from upsales.resources.bulk import BulkResource


@pytest.fixture
async def http_client():
    """Create HTTP client for testing."""
    client = HTTPClient(token="test_token", base_url="https://api.test.com")
    await client.__aenter__()
    yield client
    await client.__aexit__(None, None, None)


@pytest.fixture
def bulk_resource(http_client):
    """Create bulk resource for testing."""
    return BulkResource(http_client)


@pytest.mark.asyncio
async def test_save_success(bulk_resource: BulkResource, httpx_mock: HTTPXMock):
    """Test successful bulk save operation."""
    # Mock API response
    httpx_mock.add_response(
        method="POST",
        url="https://api.test.com/prospectingbulk",
        json={
            "error": None,
            "data": {"success": True, "count": 42, "message": "Successfully saved 42 companies"},
        },
    )

    # Execute save
    result = await bulk_resource.save(
        filters=[{"field": "country", "value": "US"}], userId=123, categoryId=456
    )

    # Verify result
    assert isinstance(result, BulkSaveResponse)
    assert result.success is True
    assert result.count == 42
    assert "42 companies" in result.message


@pytest.mark.asyncio
async def test_save_with_all_params(bulk_resource: BulkResource, httpx_mock: HTTPXMock):
    """Test bulk save with all optional parameters."""
    # Mock API response
    httpx_mock.add_response(
        method="POST",
        url="https://api.test.com/prospectingbulk",
        json={"error": None, "data": {"success": True, "count": 10, "message": "Saved"}},
    )

    # Execute save with all params
    result = await bulk_resource.save(
        filters=[
            {"field": "country", "value": "US"},
            {"field": "employees", "operator": "gte", "value": 50},
        ],
        operationalAccountId=999,
        userId=123,
        categoryId=456,
        stageId=789,
    )

    # Verify request was made correctly
    request = httpx_mock.get_request()
    assert request.method == "POST"
    import json

    body = json.loads(request.content)
    assert "filters" in body
    assert body["operationalAccountId"] == 999
    assert body["userId"] == 123
    assert body["categoryId"] == 456
    assert body["stageId"] == 789
    assert len(body["filters"]) == 2

    # Verify result
    assert result.success is True
    assert result.count == 10


@pytest.mark.asyncio
async def test_save_minimal_params(bulk_resource: BulkResource, httpx_mock: HTTPXMock):
    """Test bulk save with only required parameters."""
    # Mock API response
    httpx_mock.add_response(
        method="POST",
        url="https://api.test.com/prospectingbulk",
        json={"error": None, "data": {"success": True, "count": 5, "message": None}},
    )

    # Execute save with minimal params
    result = await bulk_resource.save(filters=[{"field": "industry", "value": "Technology"}])

    # Verify request
    request = httpx_mock.get_request()
    import json

    body = json.loads(request.content)
    assert "filters" in body
    assert len(body["filters"]) == 1
    # Optional params should not be in body
    assert "operationalAccountId" not in body
    assert "userId" not in body
    assert "categoryId" not in body
    assert "stageId" not in body

    # Verify result
    assert result.success is True
    assert result.count == 5
    assert result.message is None


@pytest.mark.asyncio
async def test_save_failure(bulk_resource: BulkResource, httpx_mock: HTTPXMock):
    """Test bulk save operation failure."""
    # Mock API error response
    httpx_mock.add_response(
        method="POST",
        url="https://api.test.com/prospectingbulk",
        json={
            "error": None,
            "data": {"success": False, "count": 0, "message": "Invalid filters"},
        },
    )

    # Execute save
    result = await bulk_resource.save(filters=[{"field": "invalid"}])

    # Verify error handling
    assert result.success is False
    assert result.count == 0
    assert "Invalid filters" in result.message


def test_endpoint_path(bulk_resource: BulkResource):
    """Test that the correct endpoint path is used."""
    assert bulk_resource.endpoint == "/prospectingbulk"


def test_resource_initialization():
    """Test resource can be initialized correctly."""
    http = HTTPClient(token="test")
    resource = BulkResource(http)
    assert resource.http is http
    assert resource.endpoint == "/prospectingbulk"
