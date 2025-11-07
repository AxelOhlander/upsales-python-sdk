"""
Unit tests for ContactsResource.

Tests all CRUD operations and custom methods for contacts resource.
Uses pytest-httpx for mocking HTTP requests without real API calls.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.contacts import Contact, PartialContact
from upsales.resources.contacts import ContactsResource


class TestContactsResourceCRUD:
    """Test CRUD operations for ContactsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample contact data for testing."""
        return {
            "id": 1,
            "name": "John Doe",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "active": 1,
            "regDate": "2024-01-01",
            "modDate": "2024-01-15",
            "emailBounceReason": "",
            "journeyStep": "lead",
            "hasForm": False,
            "hasMail": True,
            "hasVisit": True,
            "isPriority": False,
            "userEditable": True,
            "userRemovable": True,
            "score": 75,
            "custom": [],
            "categories": [],
            "connectedClients": [],
            "mailBounces": [],
            "optins": [],
            "projects": [],
            "segments": [
                {"id": 1, "name": "Active Contacts", "active": 1},
                {"id": 2, "name": "High Value", "active": 1},
            ],
            "socialEvent": [],
            "client": {"id": 5, "name": "ACME Corp"},
            "firstTouch": {},
            "regBy": {},
            "supportTickets": {},
            "cellPhone": None,
            "cellPhoneCountryCode": None,
            "hadActivity": None,
            "hadAppointment": None,
            "hadOpportunity": None,
            "hadOrder": None,
            "hasActivity": None,
            "hasAppointment": None,
            "hasOpportunity": None,
            "hasOrder": None,
            "importId": None,
            "linkedin": None,
            "notes": None,
            "phone": "+1-555-0123",
            "phoneCountryCode": "1",
            "salutation": "Mr.",
            "scoreUpdateDate": None,
            "title": "CEO",
            "titleCategory": None,
            "unsubscribed": None,
            "unsubscribedMailCampaign": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a contact."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.create(
                name="John Doe",
                firstName="John",
                lastName="Doe",
                email="john@example.com",
            )

            assert isinstance(result, Contact)
            assert result.id == 1
            assert result.name == "John Doe"
            assert result.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single contact."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Contact)
            assert result.id == 1
            assert result.name == "John Doe"
            assert result.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing contacts with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Contact) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0&active=1",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.search(active=1)

            assert len(results) == 1
            assert results[0].active == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a contact."""
        updated_data = {**sample_data, "name": "John Updated"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.update(1, name="John Updated")

            assert isinstance(result, Contact)
            assert result.id == 1
            assert result.name == "John Updated"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a contact."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="DELETE",
            json={"error": None, "data": {"id": 1}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk updating contacts."""
        updated_data = {**sample_data, "active": 0}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/2",
            method="PUT",
            json={"error": None, "data": {**updated_data, "id": 2}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.bulk_update(ids=[1, 2], data={"active": 0})

            assert len(results) == 2
            assert all(isinstance(item, Contact) for item in results)
            assert all(item.active == 0 for item in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk deleting contacts."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/2",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.bulk_delete(ids=[1, 2])

            assert len(results) == 2
            assert all(isinstance(r, dict) for r in results)


class TestContactsResourceCustomMethods:
    """Test custom methods specific to ContactsResource."""

    @pytest.fixture
    def sample_contacts(self):
        """Sample contacts list."""
        return [
            {
                "id": 1,
                "name": "John Doe",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "active": 1,
                "regDate": "2024-01-01",
                "modDate": "2024-01-15",
                "emailBounceReason": "",
                "journeyStep": "lead",
                "hasForm": False,
                "hasMail": True,
                "hasVisit": True,
                "isPriority": True,
                "userEditable": True,
                "userRemovable": True,
                "score": 75,
                "custom": [],
                "categories": [],
                "connectedClients": [],
                "mailBounces": [],
                "optins": [],
                "projects": [],
                "segments": [
                    {"id": 1, "name": "Active Contacts", "active": 1},
                    {"id": 2, "name": "High Value", "active": 1},
                ],
                "socialEvent": [],
                "client": {"id": 5, "name": "ACME Corp"},
                "firstTouch": {},
                "regBy": {},
                "supportTickets": {},
                "cellPhone": None,
                "cellPhoneCountryCode": None,
                "hadActivity": None,
                "hadAppointment": None,
                "hadOpportunity": None,
                "hadOrder": None,
                "hasActivity": None,
                "hasAppointment": None,
                "hasOpportunity": None,
                "hasOrder": None,
                "importId": None,
                "linkedin": None,
                "notes": None,
                "phone": "+1-555-0123",
                "phoneCountryCode": "1",
                "salutation": "Mr.",
                "scoreUpdateDate": None,
                "title": "CEO",
                "titleCategory": None,
                "unsubscribed": None,
                "unsubscribedMailCampaign": None,
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane@example.com",
                "active": 0,
                "regDate": "2024-01-01",
                "modDate": "2024-01-15",
                "emailBounceReason": "",
                "journeyStep": "customer",
                "hasForm": True,
                "hasMail": False,
                "hasVisit": False,
                "isPriority": False,
                "userEditable": True,
                "userRemovable": True,
                "score": 50,
                "custom": [],
                "categories": [],
                "connectedClients": [],
                "mailBounces": [],
                "optins": [],
                "projects": [],
                "segments": [
                    {"id": 3, "name": "Customers", "active": 1},
                ],
                "socialEvent": [],
                "client": {"id": 10, "name": "Tech Co"},
                "firstTouch": {},
                "regBy": {},
                "supportTickets": {},
                "cellPhone": None,
                "cellPhoneCountryCode": None,
                "hadActivity": None,
                "hadAppointment": None,
                "hadOpportunity": None,
                "hadOrder": None,
                "hasActivity": None,
                "hasAppointment": None,
                "hasOpportunity": None,
                "hasOrder": None,
                "importId": None,
                "linkedin": None,
                "notes": None,
                "phone": None,
                "phoneCountryCode": None,
                "salutation": "Ms.",
                "scoreUpdateDate": None,
                "title": "CTO",
                "titleCategory": None,
                "unsubscribed": None,
                "unsubscribedMailCampaign": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_by_email(self, httpx_mock: HTTPXMock, sample_contacts):
        """Test getting contact by email."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={"error": None, "data": sample_contacts},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.get_by_email("john@example.com")

            assert result is not None
            assert isinstance(result, Contact)
            assert result.email == "john@example.com"
            assert result.name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, httpx_mock: HTTPXMock, sample_contacts):
        """Test getting contact by email when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={"error": None, "data": sample_contacts},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.get_by_email("nonexistent@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_company(self, httpx_mock: HTTPXMock, sample_contacts):
        """Test getting contacts by company ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={"error": None, "data": sample_contacts},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.get_by_company(5)

            assert len(results) == 1
            assert results[0].client.id == 5
            assert results[0].name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_contacts):
        """Test getting all active contacts."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0&active=1",
            json={"error": None, "data": [sample_contacts[0]]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.get_active()

            assert len(results) == 1
            assert all(c.is_active for c in results)

    @pytest.mark.asyncio
    async def test_get_priority(self, httpx_mock: HTTPXMock, sample_contacts):
        """Test getting all priority contacts."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={"error": None, "data": sample_contacts},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            results = await resource.get_priority()

            assert len(results) == 1
            assert all(c.isPriority for c in results)
            assert results[0].name == "John Doe"


class TestContactModel:
    """Test Contact model computed fields and methods."""

    @pytest.fixture
    def sample_contact_data(self):
        """Sample contact data."""
        return {
            "id": 1,
            "name": "John Doe",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "active": 1,
            "regDate": "2024-01-01",
            "modDate": "2024-01-15",
            "emailBounceReason": "",
            "journeyStep": "lead",
            "hasForm": False,
            "hasMail": True,
            "hasVisit": True,
            "isPriority": True,
            "userEditable": True,
            "userRemovable": True,
            "score": 75,
            "custom": [{"fieldId": 11, "value": "test_value"}],
            "categories": [],
            "connectedClients": [],
            "mailBounces": [],
            "optins": [],
            "projects": [],
            "segments": [
                {"id": 1, "name": "Active Contacts", "active": 1},
            ],
            "socialEvent": [],
            "client": {"id": 5, "name": "ACME Corp"},
            "firstTouch": {},
            "regBy": {},
            "supportTickets": {},
            "phone": "+1-555-0123",
            "cellPhone": "+1-555-9999",
        }

    def test_is_active_computed_field(self, sample_contact_data):
        """Test is_active computed field."""
        contact = Contact(**sample_contact_data)
        assert contact.is_active is True

        contact_inactive = Contact(**{**sample_contact_data, "active": 0})
        assert contact_inactive.is_active is False

    def test_full_name_computed_field(self, sample_contact_data):
        """Test full_name computed field."""
        contact = Contact(**sample_contact_data)
        assert contact.full_name == "John Doe"

    def test_has_phone_computed_field(self, sample_contact_data):
        """Test has_phone computed field."""
        contact = Contact(**sample_contact_data)
        assert contact.has_phone is True

        no_phone = Contact(**{**sample_contact_data, "phone": None, "cellPhone": None})
        assert no_phone.has_phone is False

    def test_custom_fields_computed_field(self, sample_contact_data):
        """Test custom_fields computed field."""
        contact = Contact(**sample_contact_data)
        assert contact.custom_fields[11] == "test_value"

    @pytest.mark.skip(
        reason="Requires full Upsales client integration - tested in integration tests"
    )
    @pytest.mark.asyncio
    async def test_edit_method(self, httpx_mock: HTTPXMock, sample_contact_data):
        """Test edit method on Contact instance."""
        updated_data = {**sample_contact_data, "name": "John Updated"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        from upsales import Upsales

        async with Upsales(token="test_token") as upsales:
            contact = Contact(**sample_contact_data)
            contact._client = upsales

            updated = await contact.edit(name="John Updated")

            assert isinstance(updated, Contact)
            assert updated.name == "John Updated"


class TestPartialContactModel:
    """Test PartialContact model methods."""

    @pytest.fixture
    def partial_contact_data(self):
        """Sample partial contact data."""
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "title": "CEO",
        }

    @pytest.fixture
    def full_contact_data(self):
        """Full contact data for fetch_full test."""
        return {
            "id": 1,
            "name": "John Doe",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "active": 1,
            "regDate": "2024-01-01",
            "modDate": "2024-01-15",
            "emailBounceReason": "",
            "journeyStep": "lead",
            "hasForm": False,
            "hasMail": True,
            "hasVisit": True,
            "isPriority": True,
            "userEditable": True,
            "userRemovable": True,
            "score": 75,
            "custom": [],
            "categories": [],
            "connectedClients": [],
            "mailBounces": [],
            "optins": [],
            "projects": [],
            "segments": [],
            "socialEvent": [],
            "client": {"id": 5, "name": "ACME Corp"},
            "firstTouch": {},
            "regBy": {},
            "supportTickets": {},
            "title": "CEO",
        }

    @pytest.mark.skip(
        reason="Requires full Upsales client integration - tested in integration tests"
    )
    @pytest.mark.asyncio
    async def test_fetch_full(self, httpx_mock: HTTPXMock, partial_contact_data, full_contact_data):
        """Test fetching full contact from partial."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            json={"error": None, "data": full_contact_data},
        )

        from upsales import Upsales

        async with Upsales(token="test_token") as upsales:
            partial = PartialContact(**partial_contact_data)
            partial._client = upsales

            full = await partial.fetch_full()

            assert isinstance(full, Contact)
            assert full.id == 1
            assert full.name == "John Doe"
            assert hasattr(full, "score")

    @pytest.mark.skip(
        reason="Requires full Upsales client integration - tested in integration tests"
    )
    @pytest.mark.asyncio
    async def test_partial_edit(
        self, httpx_mock: HTTPXMock, partial_contact_data, full_contact_data
    ):
        """Test editing via partial contact."""
        updated_data = {**full_contact_data, "name": "John Updated"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        from upsales import Upsales

        async with Upsales(token="test_token") as upsales:
            partial = PartialContact(**partial_contact_data)
            partial._client = upsales

            updated = await partial.edit(name="John Updated")

            assert isinstance(updated, Contact)
            assert updated.name == "John Updated"
