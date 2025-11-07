"""
Unit tests for SegmentsResource.

Tests CRUD operations and custom methods for the segments endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.segments import Segment
from upsales.resources.segments import SegmentsResource


class TestSegmentsResourceCRUD:
    """Test CRUD operations for SegmentsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample segment data for testing."""
        return {
            "id": 1,
            "name": "Test Segment",
            "description": "Test description",
            "active": 1,
            "nrOfContacts": 106,
            "regBy": 1,
            "modBy": 1,
            "createDate": "2025-05-07T17:32:59.000Z",
            "modDate": "2025-05-07T17:32:59.000Z",
            "filter": [
                {
                    "id": 1,
                    "segmentId": 1,
                    "body": {"q": [{"a": "active", "c": "eq", "v": True}]},
                    "config": {
                        "Active": {
                            "comparisonType": "Equals",
                            "filterName": "Active",
                            "dataType": "radio",
                            "field": "active",
                            "value": True,
                            "inactive": False,
                        }
                    },
                    "isExclude": False,
                    "date": "2025-05-07T17:32:59.000Z",
                    "orGroup": False,
                }
            ],
            "version": 2,
            "flowStatus": None,
            "flowName": None,
            "sourceTemplate": None,
            "usedForProspectingMonitor": 0,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Test Segment 2", "nrOfContacts": 50},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a segment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            result = await resource.create(
                name="Test Segment", description="Test description", active=1
            )

            assert isinstance(result, Segment)
            assert result.id == 1
            assert result.name == "Test Segment"
            assert result.is_active

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single segment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Segment)
            assert result.id == 1
            assert result.name == "Test Segment"
            assert result.has_contacts
            assert result.nrOfContacts == 106

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing segments with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Segment) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a segment."""
        updated_data = {**sample_data, "name": "Updated Segment"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            result = await resource.update(1, name="Updated Segment")

            assert isinstance(result, Segment)
            assert result.name == "Updated Segment"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a segment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestSegmentsResourceCustomMethods:
    """Test custom methods for SegmentsResource."""

    @pytest.fixture
    def sample_segments(self):
        """Sample segments data."""
        return [
            {
                "id": 1,
                "name": "Active Contacts",
                "active": 1,
                "nrOfContacts": 106,
                "regBy": 1,
                "modBy": 1,
                "createDate": "2025-05-07T17:32:59.000Z",
                "modDate": "2025-05-07T17:32:59.000Z",
                "filter": [],
                "version": 2,
                "usedForProspectingMonitor": 0,
            },
            {
                "id": 2,
                "name": "Inactive Contacts",
                "active": 0,
                "nrOfContacts": 0,
                "regBy": 1,
                "modBy": 1,
                "createDate": "2025-05-07T17:32:59.000Z",
                "modDate": "2025-05-07T17:32:59.000Z",
                "filter": [],
                "version": 2,
                "usedForProspectingMonitor": 0,
            },
            {
                "id": 3,
                "name": "VIP Contacts",
                "active": 1,
                "nrOfContacts": 25,
                "regBy": 1,
                "modBy": 1,
                "createDate": "2025-05-07T17:32:59.000Z",
                "modDate": "2025-05-07T17:32:59.000Z",
                "filter": [],
                "version": 2,
                "usedForProspectingMonitor": 0,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_segments):
        """Test getting all active segments."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={"error": None, "data": sample_segments},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            active = await resource.get_active()

            assert len(active) == 2  # Only active=1
            assert all(seg.is_active for seg in active)
            assert active[0].name == "Active Contacts"
            assert active[1].name == "VIP Contacts"

    @pytest.mark.asyncio
    async def test_get_populated(self, httpx_mock: HTTPXMock, sample_segments):
        """Test getting segments with contacts."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={"error": None, "data": sample_segments},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            populated = await resource.get_populated()

            assert len(populated) == 2  # Only segments with nrOfContacts > 0
            assert all(seg.has_contacts for seg in populated)
            assert populated[0].nrOfContacts == 106
            assert populated[1].nrOfContacts == 25

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_segments):
        """Test getting segment by name."""
        # Add two responses since we call list_all twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={"error": None, "data": sample_segments},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={"error": None, "data": sample_segments},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)

            # Test exact match (case-insensitive)
            segment = await resource.get_by_name("Active Contacts")
            assert segment is not None
            assert segment.name == "Active Contacts"

            # Test case-insensitive
            segment = await resource.get_by_name("active contacts")
            assert segment is not None
            assert segment.name == "Active Contacts"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_segments):
        """Test getting segment by name when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/segments?limit=100&offset=0",
            json={"error": None, "data": sample_segments},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SegmentsResource(http)
            segment = await resource.get_by_name("Nonexistent Segment")
            assert segment is None
