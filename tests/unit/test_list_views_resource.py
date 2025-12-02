"""Unit tests for list views resource."""

from unittest.mock import AsyncMock

import pytest

from upsales.models.list_views import ListView, PartialListView
from upsales.resources.list_views import ListViewsResource


@pytest.fixture
def list_view_data():
    """Sample list view data."""
    return {
        "id": 1,
        "title": "Active Accounts",
        "description": "Shows all active accounts",
        "listType": "account",
        "type": "custom",
        "grouping": "category",
        "columns": [{"field": "name", "width": 200}],
        "sorting": [{"field": "name", "order": "asc"}],
        "filters": [{"field": "active", "value": 1}],
        "limit": 100,
        "users": [{"id": 1}],
        "roles": [{"id": 2}],
        "default": True,
        "regDate": "2024-01-01",
        "modDate": "2024-01-02",
        "regBy": {"id": 1, "name": "Admin"},
    }


@pytest.fixture
def http_client():
    """Mock HTTP client."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.client = None
    return client


@pytest.fixture
def resource(http_client):
    """List views resource instance."""
    return ListViewsResource(http_client)


@pytest.mark.asyncio
async def test_get(resource, http_client, list_view_data):
    """Test getting a single list view."""
    http_client.get.return_value = list_view_data

    result = await resource.get("account", 1)

    assert isinstance(result, ListView)
    assert result.id == 1
    assert result.title == "Active Accounts"
    assert result.listType == "account"
    assert result.is_default is True
    http_client.get.assert_awaited_once_with("/listViews/account/1")


@pytest.mark.asyncio
async def test_list(resource, http_client, list_view_data):
    """Test listing list views."""
    http_client.get.return_value = [list_view_data]

    result = await resource.list("account", limit=10, offset=0)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], ListView)
    assert result[0].title == "Active Accounts"
    http_client.get.assert_awaited_once_with(
        "/listViews/account", params={"limit": 10, "offset": 0}
    )


@pytest.mark.asyncio
async def test_list_all(resource, http_client, list_view_data):
    """Test listing all list views with pagination."""
    # First batch
    first_batch = [list_view_data]
    # Second batch (empty to stop pagination)
    second_batch = []

    http_client.get.side_effect = [first_batch, second_batch]

    result = await resource.list_all("account")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].title == "Active Accounts"


@pytest.mark.asyncio
async def test_create(resource, http_client, list_view_data):
    """Test creating a list view."""
    http_client.post.return_value = list_view_data

    result = await resource.create("account", title="New View", listType="account", type="custom")

    assert isinstance(result, ListView)
    assert result.id == 1
    http_client.post.assert_awaited_once_with(
        "/listViews/account", json={"title": "New View", "listType": "account", "type": "custom"}
    )


@pytest.mark.asyncio
async def test_update(resource, http_client, list_view_data):
    """Test updating a list view."""
    updated_data = list_view_data.copy()
    updated_data["title"] = "Updated Title"
    http_client.put.return_value = updated_data

    result = await resource.update("account", 1, title="Updated Title")

    assert isinstance(result, ListView)
    assert result.title == "Updated Title"
    http_client.put.assert_awaited_once_with(
        "/listViews/account/1", json={"title": "Updated Title"}
    )


@pytest.mark.asyncio
async def test_delete(resource, http_client):
    """Test deleting a list view."""
    http_client.delete.return_value = None

    await resource.delete("account", 1)

    http_client.delete.assert_awaited_once_with("/listViews/account/1")


@pytest.mark.asyncio
async def test_partial_list_view_fetch_full(list_view_data):
    """Test partial list view fetch_full method."""
    # Create a mock Upsales client with list_views resource
    mock_client = AsyncMock()
    mock_client.list_views = AsyncMock()
    mock_client.list_views.get = AsyncMock(return_value=ListView(**list_view_data))

    # Pass client through model initialization
    partial = PartialListView(id=1, title="Test", listType="account", _client=mock_client)

    result = await partial.fetch_full()

    assert isinstance(result, ListView)
    assert result.id == 1
    mock_client.list_views.get.assert_awaited_once_with("account", 1)


def test_list_view_is_default_property(list_view_data):
    """Test is_default computed property."""
    view = ListView(**list_view_data)
    assert view.is_default is True

    view_not_default = ListView(**{**list_view_data, "default": False})
    assert view_not_default.is_default is False

    view_none_default = ListView(**{**list_view_data, "default": None})
    assert view_none_default.is_default is False
