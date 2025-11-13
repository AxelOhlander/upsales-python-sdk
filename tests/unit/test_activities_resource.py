"""
Tests for ActivitiesResource.

Ensures complete CRUD coverage for activities endpoint.
"""

import re

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.activities import Activity
from upsales.resources.activities import ActivitiesResource


class TestActivitiesResourceCRUD:
    """Test CRUD operations for ActivitiesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample activity data for testing."""
        return {
            "id": 1,
            "description": "Follow-up call",
            "notes": "Discuss Q4 targets",
            "date": "2025-11-15",
            "regDate": "2025-11-01T10:00:00Z",
            "modDate": "2025-11-01T10:00:00Z",
            "isAppointment": 1,
            "priority": 3,
            "userEditable": True,
            "userRemovable": True,
            "custom": [],
            "activityType": {"id": 1, "name": "Call"},
            "client": {"id": 10, "name": "ACME Corp"},
            "regBy": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "lastOutcome": {},
            "contacts": [],
            "users": [],
            "outcomes": [],
            "opportunity": None,
            "project": None,
            "projectPlan": None,
            "callList": None,
            "agreementId": None,
            "ticketId": None,
            "parentActivityId": None,
            "parentAppointmentId": None,
            "closeDate": None,
            "closeTime": None,
            "time": "14:00:00",
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "description": "Follow-up email"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an activity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            result = await resource.create(
                description="Follow-up call", date="2025-11-15", isAppointment=1
            )

            assert isinstance(result, Activity)
            assert result.id == 1
            assert result.description == "Follow-up call"
            assert result.is_appointment is True

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single activity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            result = await resource.get(1)

            assert isinstance(result, Activity)
            assert result.id == 1
            assert result.description == "Follow-up call"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing activities with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Activity) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?isAppointment=1&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.search(isAppointment=1)

            assert len(results) == 1
            assert results[0].is_appointment is True

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an activity."""
        updated_data = {**sample_data, "description": "Updated description"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            result = await resource.update(1, description="Updated description")

            assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an activity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            result = await resource.delete(1)

            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/activities/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"priority": 5},
            )

            assert len(results) == 3
            assert all(isinstance(item, Activity) for item in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/activities/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestActivitiesResourceCustomMethods:
    """Test custom methods specific to ActivitiesResource."""

    @pytest.fixture
    def appointment_data(self):
        """Sample appointment data."""
        return {
            "id": 1,
            "description": "Meeting",
            "date": "2025-11-15",
            "regDate": "2025-11-01T10:00:00Z",
            "modDate": "2025-11-01T10:00:00Z",
            "isAppointment": 1,
            "priority": 3,
            "userEditable": True,
            "userRemovable": True,
            "custom": [],
            "activityType": {},
            "regBy": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "lastOutcome": {},
            "contacts": [],
            "users": [],
            "outcomes": [],
            "client": None,
            "opportunity": None,
            "project": None,
            "projectPlan": None,
            "callList": None,
            "agreementId": None,
            "ticketId": None,
            "parentActivityId": None,
            "parentAppointmentId": None,
            "closeDate": None,
            "closeTime": None,
            "time": None,
            "notes": "",
        }

    @pytest.fixture
    def task_data(self):
        """Sample task data."""
        return {
            "id": 2,
            "description": "Task",
            "date": "2025-11-15",
            "regDate": "2025-11-01T10:00:00Z",
            "modDate": "2025-11-01T10:00:00Z",
            "isAppointment": 0,
            "priority": 2,
            "userEditable": True,
            "userRemovable": True,
            "custom": [],
            "activityType": {},
            "regBy": {"id": 5, "name": "John Doe", "email": "john@example.com"},
            "lastOutcome": {},
            "contacts": [],
            "users": [],
            "outcomes": [],
            "client": None,
            "opportunity": None,
            "project": None,
            "projectPlan": None,
            "callList": None,
            "agreementId": None,
            "ticketId": None,
            "parentActivityId": None,
            "parentAppointmentId": None,
            "closeDate": None,
            "closeTime": None,
            "time": None,
            "notes": "",
        }

    @pytest.mark.asyncio
    async def test_get_appointments(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_appointments() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?isAppointment=1&limit=100&offset=0",
            json={"error": None, "data": [appointment_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_appointments()

            assert len(results) == 1
            assert all(a.is_appointment for a in results)

    @pytest.mark.asyncio
    async def test_get_tasks(self, httpx_mock: HTTPXMock, task_data):
        """Test get_tasks() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?isAppointment=0&limit=100&offset=0",
            json={"error": None, "data": [task_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_tasks()

            assert len(results) == 1
            assert all(a.is_task for a in results)

    @pytest.mark.asyncio
    async def test_get_open(self, httpx_mock: HTTPXMock, task_data):
        """Test get_open() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?limit=100&offset=0",
            json={"error": None, "data": [task_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_open()

            assert len(results) == 1
            assert all(not a.is_closed for a in results)

    @pytest.mark.asyncio
    async def test_get_by_company(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_by_company() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?client.id=123&limit=100&offset=0",
            json={"error": None, "data": [appointment_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_by_company(123)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_opportunity(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_by_opportunity() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?opportunity.id=456&limit=100&offset=0",
            json={"error": None, "data": [appointment_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_by_opportunity(456)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_date_range(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_by_date_range() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/activities?sort=-date&limit=100&offset=0",
            json={"error": None, "data": [appointment_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_by_date_range("2025-11-01", "2025-11-30")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_high_priority(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_high_priority() custom method."""
        httpx_mock.add_response(
            url=re.compile(r"https://power\.upsales\.com/api/v2/activities"),
            json={"error": None, "data": [{**appointment_data, "priority": 5}]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_high_priority(min_priority=4)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_recent(self, httpx_mock: HTTPXMock, appointment_data):
        """Test get_recent() custom method."""
        # Match any date in the URL (since it's dynamic - uses gte:YYYY-MM-DD format after transformation)
        httpx_mock.add_response(
            url=re.compile(r"https://power\.upsales\.com/api/v2/activities"),
            json={"error": None, "data": [appointment_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ActivitiesResource(http)
            results = await resource.get_recent(days=7)

            assert len(results) == 1


# Coverage target: 100% for ActivitiesResource
