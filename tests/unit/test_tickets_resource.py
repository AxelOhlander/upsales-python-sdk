"""
Unit tests for TicketsResource.

Tests CRUD operations and custom methods for tickets endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.tickets import Ticket
from upsales.resources.tickets import TicketsResource


class TestTicketsResourceCRUD:
    """Test CRUD operations for TicketsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample ticket data for testing."""
        return {
            "id": 1,
            "title": "Customer needs help",
            "userId": 10,
            "statusId": 1,
            "typeId": 1,
            "clientId": 100,
            "contactId": 200,
            "priority": 2,
            "isArchived": False,
            "isPending": False,
            "isRead": True,
            "isMultiMatch": False,
            "source": "email",
            "emailUsed": "support@company.com",
            "snoozeDate": None,
            "resolveDate": None,
            "firstResolveDate": None,
            "firstReplyDate": None,
            "lastUpdated": "2024-01-01T10:00:00Z",
            "regDate": "2024-01-01T09:00:00Z",
            "modDate": "2024-01-01T10:00:00Z",
            "regBy": {"id": 10, "name": "John Doe", "email": "john.doe@example.com"},
            "modBy": 10,
            "activityId": None,
            "appointmentId": None,
            "opportunityId": None,
            "relatedTicketId": None,
            "agreementId": None,
            "projectPlanId": None,
            "mergedWithId": None,
            "client": {"id": 100, "name": "Acme Corp"},
            "contact": {"id": 200, "name": "Jane Smith"},
            "user": {"id": 10, "name": "John Doe", "email": "john.doe@example.com"},
            "status": {"id": 1, "name": "Open"},
            "type": {"id": 1, "name": "Support"},
            "involved": [],
            "externalContacts": [],
            "mergedTickets": [],
            "directlyMergedTicketIds": [],
            "multiMatchClientContacts": [],
            "customStatusSort": 0,
            "unreadComments": 0,
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
                    "title": "Another ticket",
                    "priority": 1,
                    "isRead": False,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a ticket."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            result = await resource.create(
                title="Customer needs help",
                statusId=1,
                typeId=1,
                clientId=100,
                priority=2,
            )

            assert isinstance(result, Ticket)
            assert result.id == 1
            assert result.title == "Customer needs help"
            assert result.priority == 2
            assert result.is_read

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single ticket."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Ticket)
            assert result.id == 1
            assert result.title == "Customer needs help"
            assert result.is_read
            assert not result.is_archived
            assert not result.is_pending

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing tickets with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            result = await resource.list(limit=10, offset=0)

            assert len(result) == 2
            assert all(isinstance(ticket, Ticket) for ticket in result)
            assert result[0].id == 1
            assert result[1].id == 2
            assert result[0].priority == 2
            assert result[1].priority == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a ticket."""
        updated_data = {**sample_data, "title": "Updated title", "priority": 3, "isRead": True}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            result = await resource.update(1, title="Updated title", priority=3, isRead=True)

            assert isinstance(result, Ticket)
            assert result.id == 1
            assert result.title == "Updated title"
            assert result.priority == 3
            assert result.is_read

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a ticket."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets/1",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            await resource.delete(1)  # Should not raise

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test searching tickets."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/tickets?statusId=1&priority__gte=2&limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TicketsResource(http)
            result = await resource.search(statusId=1, priority__gte=2)

            assert len(result) == 2
            assert all(isinstance(ticket, Ticket) for ticket in result)


class TestTicketModel:
    """Test Ticket model methods and properties."""

    @pytest.fixture
    def sample_ticket_data(self):
        """Sample ticket data."""
        return {
            "id": 1,
            "title": "Test Ticket",
            "userId": 10,
            "statusId": 1,
            "typeId": 1,
            "clientId": 100,
            "contactId": 200,
            "priority": 2,
            "isArchived": False,
            "isPending": True,
            "isRead": True,
            "isMultiMatch": False,
            "source": "email",
            "emailUsed": "test@example.com",
            "snoozeDate": None,
            "resolveDate": None,
            "firstResolveDate": None,
            "firstReplyDate": None,
            "lastUpdated": "2024-01-01T10:00:00Z",
            "regDate": "2024-01-01T09:00:00Z",
            "modDate": "2024-01-01T10:00:00Z",
            "regBy": {"id": 10, "name": "John Doe", "email": "john.doe@example.com"},
            "modBy": 10,
            "activityId": None,
            "appointmentId": None,
            "opportunityId": None,
            "relatedTicketId": None,
            "agreementId": None,
            "projectPlanId": None,
            "mergedWithId": None,
            "client": {"id": 100, "name": "Acme Corp"},
            "contact": {"id": 200, "name": "Jane Smith"},
            "user": {"id": 10, "name": "John Doe", "email": "john.doe@example.com"},
            "status": {"id": 1, "name": "Open"},
            "type": {"id": 1, "name": "Support"},
            "involved": [],
            "externalContacts": [],
            "mergedTickets": [],
            "directlyMergedTicketIds": [],
            "multiMatchClientContacts": [],
            "customStatusSort": 0,
            "unreadComments": 0,
            "custom": [{"fieldId": 11, "value": "test"}],
        }

    def test_computed_fields(self, sample_ticket_data):
        """Test computed properties."""
        ticket = Ticket(**sample_ticket_data)

        assert ticket.is_archived == False
        assert ticket.is_pending == True
        assert ticket.is_read == True

    def test_custom_fields(self, sample_ticket_data):
        """Test custom fields access."""
        ticket = Ticket(**sample_ticket_data)

        assert ticket.custom_fields[11] == "test"
        assert len(ticket.custom) == 1

    def test_validation(self):
        """Test field validation."""
        # Priority must be 0-3
        with pytest.raises(ValueError):
            Ticket(
                id=1,
                title="Test",
                priority=5,  # Invalid
                regDate="2024-01-01",
                modDate="2024-01-01",
                lastUpdated="2024-01-01",
                regBy={"id": 1, "name": "Test", "email": "test@example.com"},
                modBy=1,
            )

    def test_frozen_fields(self, sample_ticket_data):
        """Test that frozen fields cannot be modified."""
        ticket = Ticket(**sample_ticket_data)

        # ID is frozen
        with pytest.raises(ValueError):
            ticket.id = 999

    def test_title_max_length(self, sample_ticket_data):
        """Test title maximum length validation."""
        sample_ticket_data["title"] = "x" * 151  # Too long
        with pytest.raises(ValueError):
            Ticket(**sample_ticket_data)
