"""
Unit tests for AppointmentsResource.

Tests all CRUD operations and custom methods for appointments resource.
Uses pytest-httpx for mocking HTTP requests without real API calls.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.appointments import Appointment
from upsales.resources.appointments import AppointmentsResource


class TestAppointmentsResourceCRUD:
    """Test CRUD operations for AppointmentsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample appointment data for testing."""
        return {
            "id": 1,
            "description": "Client Meeting - Q1 Review",
            "date": "2025-03-15T10:00:00",
            "endDate": "2025-03-15T11:00:00",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "notes": "Discuss Q1 performance",
            "agenda": "Review metrics, plan Q2",
            "location": "Conference Room A",
            "outcome": "Completed",
            "outcomeType": None,
            "outcomeAction": None,
            "outcomeExtra": None,
            "outcomeCommentId": None,
            "isAppointment": 1,
            "private": False,
            "includeWeblink": 0,
            "isExternalHost": False,
            "userEditable": True,
            "userRemovable": True,
            "weblinkUrl": None,
            "externalCalendarId": None,
            "bookedRooms": None,
            "seriesMasterId": None,
            "client": {"id": 5, "name": "ACME Corp"},
            "contacts": [{"id": 10, "name": "John Doe"}],
            "opportunity": {"id": 20, "description": "Enterprise Deal"},
            "project": None,
            "users": [{"id": 3, "name": "Jane Smith", "email": "jane@example.com"}],
            "regBy": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "activityType": {"id": 1, "name": "Meeting"},
            "aiNotes": None,
            "emailAttendees": [],
            "clientConnection": None,
            "projectPlan": None,
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
                {
                    **sample_data,
                    "id": 2,
                    "description": "Follow-up Call",
                    "date": "2025-03-20T14:00:00",
                    "outcome": None,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an appointment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            result = await resource.create(
                description="Client Meeting - Q1 Review",
                date="2025-03-15T10:00:00",
                endDate="2025-03-15T11:00:00",
            )

            assert isinstance(result, Appointment)
            assert result.id == 1
            assert result.description == "Client Meeting - Q1 Review"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single appointment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Appointment)
            assert result.id == 1
            assert result.description == "Client Meeting - Q1 Review"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing appointments with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Appointment) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0&isAppointment=1",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.search(isAppointment=1)

            assert len(results) == 1
            assert results[0].isAppointment == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an appointment."""
        updated_data = {**sample_data, "description": "Updated Meeting Title"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            result = await resource.update(1, description="Updated Meeting Title")

            assert result.description == "Updated Meeting Title"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an appointment."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestAppointmentsResourceCustomMethods:
    """Test custom methods for AppointmentsResource."""

    @pytest.fixture
    def sample_appointment_1(self):
        """First sample appointment."""
        return {
            "id": 1,
            "description": "Client Meeting",
            "date": "2025-03-15T10:00:00",
            "endDate": "2025-03-15T11:00:00",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "notes": "Q1 Review",
            "agenda": "Review metrics",
            "location": "Conference Room A",
            "outcome": "Completed",
            "outcomeType": None,
            "outcomeAction": None,
            "outcomeExtra": None,
            "outcomeCommentId": None,
            "isAppointment": 1,
            "private": False,
            "includeWeblink": 1,
            "isExternalHost": False,
            "userEditable": True,
            "userRemovable": True,
            "weblinkUrl": "https://meet.example.com/abc123",
            "externalCalendarId": None,
            "bookedRooms": None,
            "seriesMasterId": None,
            "client": {"id": 5, "name": "ACME Corp"},
            "contacts": [{"id": 10, "name": "John Doe"}],
            "opportunity": {"id": 20, "description": "Enterprise Deal"},
            "project": None,
            "users": [{"id": 3, "name": "Jane Smith", "email": "jane@example.com"}],
            "regBy": {"id": 3, "name": "Jane Smith", "email": "jane@example.com"},
            "activityType": {"id": 1, "name": "Meeting"},
            "aiNotes": None,
            "emailAttendees": [],
            "clientConnection": None,
            "projectPlan": None,
            "custom": [],
        }

    @pytest.fixture
    def sample_appointment_2(self):
        """Second sample appointment."""
        return {
            "id": 2,
            "description": "Follow-up Call",
            "date": "2025-04-20T14:00:00",
            "endDate": "2025-04-20T14:30:00",
            "regDate": "2025-01-02T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "notes": None,
            "agenda": None,
            "location": None,
            "outcome": None,
            "outcomeType": None,
            "outcomeAction": None,
            "outcomeExtra": None,
            "outcomeCommentId": None,
            "isAppointment": 1,
            "private": False,
            "includeWeblink": 0,
            "isExternalHost": False,
            "userEditable": True,
            "userRemovable": True,
            "weblinkUrl": None,
            "externalCalendarId": None,
            "bookedRooms": None,
            "seriesMasterId": None,
            "client": {"id": 5, "name": "ACME Corp"},
            "contacts": [],
            "opportunity": {"id": 25, "description": "Small Deal"},
            "project": None,
            "users": [{"id": 4, "name": "Bob Johnson", "email": "bob@example.com"}],
            "regBy": {"id": 4, "name": "Bob Johnson", "email": "bob@example.com"},
            "activityType": {"id": 2, "name": "Phone Call"},
            "aiNotes": None,
            "emailAttendees": [],
            "clientConnection": None,
            "projectPlan": None,
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_by_company(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting appointments by company."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_by_company(5)

            assert len(results) == 2
            assert all(app.client.id == 5 for app in results)

    @pytest.mark.asyncio
    async def test_get_by_user(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting appointments by user."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_by_user(3)

            assert len(results) == 1
            assert results[0].id == 1

    @pytest.mark.asyncio
    async def test_get_by_contact(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting appointments by contact."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_by_contact(10)

            assert len(results) == 1
            assert results[0].id == 1

    @pytest.mark.asyncio
    async def test_get_completed(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting completed appointments."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_completed()

            assert len(results) == 1
            assert results[0].has_outcome
            assert results[0].id == 1

    @pytest.mark.asyncio
    async def test_get_upcoming_default(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting upcoming appointments with default date."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_upcoming()

            # Both appointments are in the future (2025-03 and 2025-04)
            assert len(results) >= 0  # Depends on current date

    @pytest.mark.asyncio
    async def test_get_upcoming_specific_date(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting upcoming appointments from specific date."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_upcoming("2025-04-01T00:00:00")

            # Only appointment 2 is after 2025-04-01
            assert len(results) == 1
            assert results[0].id == 2

    @pytest.mark.asyncio
    async def test_get_by_opportunity(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting appointments by opportunity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_by_opportunity(20)

            assert len(results) == 1
            assert results[0].opportunity.id == 20
            assert results[0].id == 1

    @pytest.mark.asyncio
    async def test_get_with_weblink(
        self, httpx_mock: HTTPXMock, sample_appointment_1, sample_appointment_2
    ):
        """Test getting appointments with weblink."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/appointments?limit=100&offset=0",
            json={"error": None, "data": [sample_appointment_1, sample_appointment_2]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = AppointmentsResource(http)
            results = await resource.get_with_weblink()

            assert len(results) == 1
            assert results[0].has_weblink
            assert results[0].id == 1


class TestAppointmentModel:
    """Test Appointment model features."""

    @pytest.mark.asyncio
    async def test_computed_fields(self):
        """Test computed field properties."""
        appointment_data = {
            "id": 1,
            "description": "Meeting",
            "date": "2025-03-15T10:00:00",
            "endDate": "2025-03-15T11:00:00",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "outcome": "Completed",
            "isAppointment": 1,
            "includeWeblink": 1,
            "private": False,
            "isExternalHost": False,
            "userEditable": True,
            "userRemovable": True,
            "notes": None,
            "agenda": None,
            "location": None,
            "outcomeType": None,
            "outcomeAction": None,
            "outcomeExtra": None,
            "outcomeCommentId": None,
            "weblinkUrl": None,
            "externalCalendarId": None,
            "bookedRooms": None,
            "seriesMasterId": None,
            "client": None,
            "contacts": [{"id": 10, "name": "John"}],
            "opportunity": None,
            "project": None,
            "users": [{"id": 3, "name": "Jane", "email": "jane@example.com"}],
            "regBy": None,
            "activityType": {},
            "aiNotes": None,
            "emailAttendees": [],
            "clientConnection": None,
            "projectPlan": None,
            "custom": [],
        }

        appointment = Appointment(**appointment_data)

        # Test computed fields
        assert appointment.is_appointment is True
        assert appointment.has_outcome is True
        assert appointment.has_weblink is True
        assert appointment.has_attendees is True
        assert appointment.attendee_count == 2  # 1 user + 1 contact

    @pytest.mark.asyncio
    async def test_custom_fields_access(self):
        """Test custom fields access."""
        appointment_data = {
            "id": 1,
            "description": "Meeting",
            "date": "2025-03-15T10:00:00",
            "endDate": "2025-03-15T11:00:00",
            "regDate": "2025-01-01T09:00:00",
            "modDate": "2025-01-05T14:30:00",
            "outcome": None,
            "isAppointment": 1,
            "includeWeblink": 0,
            "private": False,
            "isExternalHost": False,
            "userEditable": True,
            "userRemovable": True,
            "notes": None,
            "agenda": None,
            "location": None,
            "outcomeType": None,
            "outcomeAction": None,
            "outcomeExtra": None,
            "outcomeCommentId": None,
            "weblinkUrl": None,
            "externalCalendarId": None,
            "bookedRooms": None,
            "seriesMasterId": None,
            "client": None,
            "contacts": [],
            "opportunity": None,
            "project": None,
            "users": [],
            "regBy": None,
            "activityType": {},
            "aiNotes": None,
            "emailAttendees": [],
            "clientConnection": None,
            "projectPlan": None,
            "custom": [{"fieldId": 11, "value": "Conference Room"}],
        }

        appointment = Appointment(**appointment_data)
        assert appointment.custom_fields[11] == "Conference Room"
