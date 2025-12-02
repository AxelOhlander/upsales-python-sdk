"""Unit tests for ReportViewsResource.

Tests CRUD operations for report views endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.report_view import ReportView
from upsales.resources.report_view import ReportViewsResource


class TestReportViewsResourceCRUD:
    """Test CRUD operations for ReportViewsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample report view data for testing."""
        return {
            "id": "uuid-123",
            "description": "My custom view",
            "type": "own",
            "title": "Sales Report",
            "default": True,
            "editable": True,
            "private": False,
            "sorting": [{"field": "date", "order": "desc"}],
            "grouping": "stage",
            "tableGrouping": "user",
            "filters": [{"field": "status", "value": "active"}],
            "roleId": 1,
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
                {**sample_data, "id": "uuid-456", "title": "Pipeline Report"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a report view."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ReportViewsResource(http)
            result = await resource.create(
                title="Sales Report",
                type="own",
                default=True,
            )

            assert isinstance(result, ReportView)
            assert result.id == "uuid-123"
            assert result.title == "Sales Report"
            assert result.type == "own"
            assert result.default is True

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single report view."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView/uuid-123",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ReportViewsResource(http)
            result = await resource.get("uuid-123")

            assert isinstance(result, ReportView)
            assert result.id == "uuid-123"
            assert result.title == "Sales Report"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing report views with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ReportViewsResource(http)
            result = await resource.list(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, ReportView) for item in result)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a report view."""
        updated_data = {**sample_data, "title": "Updated Report"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView/uuid-123",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ReportViewsResource(http)
            result = await resource.update("uuid-123", title="Updated Report")

            assert isinstance(result, ReportView)
            assert result.id == "uuid-123"
            assert result.title == "Updated Report"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a report view."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView/uuid-123",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ReportViewsResource(http)
            await resource.delete("uuid-123")

            # No exception means success


class TestReportViewModel:
    """Test ReportView model features."""

    def test_is_default_property(self):
        """Test is_default computed property."""
        view = ReportView(
            id="uuid-123",
            title="Test",
            default=True,
        )
        assert view.is_default is True

        view_not_default = ReportView(
            id="uuid-456",
            title="Test Not Default",
            default=False,
        )
        assert view_not_default.is_default is False

    def test_is_private_property(self):
        """Test is_private computed property."""
        view = ReportView(
            id="uuid-123",
            title="Test",
            private=True,
        )
        assert view.is_private is True

        view_public = ReportView(
            id="uuid-456",
            title="Test Public",
            private=False,
        )
        assert view_public.is_private is False

    def test_custom_fields_property(self):
        """Test custom_fields computed property."""
        view = ReportView(
            id="uuid-123",
            title="Test",
            custom=[{"fieldId": 11, "value": "test_value"}],
        )
        assert view.custom_fields.get(11) == "test_value"

    @pytest.mark.asyncio
    async def test_edit_method(self, httpx_mock: HTTPXMock):
        """Test model edit method."""
        from upsales import Upsales

        updated_data = {
            "id": "uuid-123",
            "title": "Updated Title",
            "default": True,
            "custom": [],
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/reportView/uuid-123",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with Upsales(token="test_token") as upsales:
            view = ReportView(
                id="uuid-123",
                title="Old Title",
                default=False,
                _client=upsales,
            )

            updated = await view.edit(title="Updated Title", default=True)
            assert updated.title == "Updated Title"
            assert updated.default is True
