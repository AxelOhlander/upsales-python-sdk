"""
Unit tests for TriggersResource.

Tests CRUD operations and custom methods for the triggers endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.triggers import Trigger
from upsales.resources.triggers import TriggersResource


class TestTriggersResourceCRUD:
    """Test CRUD operations for TriggersResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample trigger data for testing."""
        return {
            "id": 1001003,
            "name": "Test Trigger",
            "description": "Test description",
            "active": 1,
            "events": ["after_order_insert", "after_order_update"],
            "actions": [
                {
                    "properties": [
                        {"name": "AppointmentType", "value": "7"},
                        {"name": "Description", "value": "Test"},
                    ],
                    "id": 1001429,
                    "action": "",
                    "description": None,
                    "alias": "CreateAppointment",
                }
            ],
            "criterias": [
                {
                    "id": 1004847,
                    "type": "and",
                    "attribute": "Order.Stage",
                    "operator": "Equals",
                    "value": "12",
                    "orGroup": 0,
                    "valueText": "12",
                }
            ],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 1001010, "name": "Test Trigger 2"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a trigger."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            result = await resource.create(
                name="Test Trigger",
                description="Test description",
                active=1,
                events=["after_order_insert"],
            )

            assert isinstance(result, Trigger)
            assert result.id == 1001003
            assert result.name == "Test Trigger"
            assert result.is_active

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single trigger."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers/1001003",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            result = await resource.get(1001003)

            assert isinstance(result, Trigger)
            assert result.id == 1001003
            assert result.name == "Test Trigger"
            assert result.has_events
            assert result.has_actions
            assert result.has_criterias

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing triggers with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Trigger) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a trigger."""
        updated_data = {**sample_data, "name": "Updated Trigger"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers/1001003",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            result = await resource.update(1001003, name="Updated Trigger")

            assert isinstance(result, Trigger)
            assert result.name == "Updated Trigger"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a trigger."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers/1001003",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            await resource.delete(1001003)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestTriggersResourceCustomMethods:
    """Test custom methods for TriggersResource."""

    @pytest.fixture
    def sample_triggers(self):
        """Sample triggers for testing."""
        return [
            {
                "id": 1,
                "name": "Active Order Trigger",
                "active": 1,
                "events": ["after_order_insert", "after_order_update"],
                "actions": [],
                "criterias": [],
                "description": None,
            },
            {
                "id": 2,
                "name": "Inactive Contact Trigger",
                "active": 0,
                "events": ["after_contact_insert"],
                "actions": [],
                "criterias": [],
                "description": None,
            },
            {
                "id": 3,
                "name": "Active Client Trigger",
                "active": 1,
                "events": ["after_client_update"],
                "actions": [],
                "criterias": [],
                "description": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_triggers):
        """Test getting active triggers."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={"error": None, "data": sample_triggers},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.get_active()

            assert len(results) == 2
            assert all(trigger.is_active for trigger in results)
            assert results[0].name == "Active Order Trigger"
            assert results[1].name == "Active Client Trigger"

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_triggers):
        """Test getting trigger by name."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={"error": None, "data": sample_triggers},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            result = await resource.get_by_name("Active Order Trigger")

            assert result is not None
            assert result.name == "Active Order Trigger"
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_triggers):
        """Test getting trigger by name when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={"error": None, "data": sample_triggers},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            result = await resource.get_by_name("Nonexistent Trigger")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_event(self, httpx_mock: HTTPXMock, sample_triggers):
        """Test getting triggers by event."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={"error": None, "data": sample_triggers},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.get_by_event("after_order_insert")

            assert len(results) == 1
            assert results[0].name == "Active Order Trigger"
            assert "after_order_insert" in results[0].events

    @pytest.mark.asyncio
    async def test_get_by_event_multiple_results(self, httpx_mock: HTTPXMock, sample_triggers):
        """Test getting triggers by event with multiple results."""
        # Add another trigger with the same event
        sample_triggers.append(
            {
                "id": 4,
                "name": "Another Order Trigger",
                "active": 1,
                "events": ["after_order_insert", "after_order_delete"],
                "actions": [],
                "criterias": [],
                "description": None,
            }
        )

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggers?limit=100&offset=0",
            json={"error": None, "data": sample_triggers},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggersResource(http)
            results = await resource.get_by_event("after_order_insert")

            assert len(results) == 2
            assert all("after_order_insert" in trigger.events for trigger in results)
