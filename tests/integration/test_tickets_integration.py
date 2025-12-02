"""
Integration tests for Ticket model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_tickets_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_tickets_integration/
    uv run pytest tests/integration/test_tickets_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.tickets import PartialTicket, Ticket

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_list_tickets_real_response.yaml")
async def test_list_tickets_real_response():
    """
    Test listing tickets with real API response structure.

    Validates that Ticket model correctly parses real API data including
    nested objects like PartialUser, PartialCompany, PartialContact, etc.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_list_tickets_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        tickets = await upsales.tickets.list(limit=5)

        assert isinstance(tickets, list)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        for ticket in tickets:
            assert isinstance(ticket, Ticket)
            assert isinstance(ticket.id, int)
            assert ticket.id > 0
            assert isinstance(ticket.title, str)

            # Validate read-only fields are present (set by API)
            # These can be None for newly created tickets but should be present for existing ones
            if ticket.regDate is not None:
                assert isinstance(ticket.regDate, str)
            if ticket.modDate is not None:
                assert isinstance(ticket.modDate, str)
            if ticket.lastUpdated is not None:
                assert isinstance(ticket.lastUpdated, str)

        print(f"[OK] Listed {len(tickets)} tickets successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_get_ticket_real_response.yaml")
async def test_get_ticket_real_response():
    """
    Test getting a single ticket with real API response structure.

    Validates full Ticket model including all nested objects.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_get_ticket_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid ticket ID
        tickets = await upsales.tickets.list(limit=1)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        ticket_id = tickets[0].id

        # Now get the specific ticket
        ticket = await upsales.tickets.get(ticket_id)

        assert isinstance(ticket, Ticket)
        assert ticket.id == ticket_id
        assert isinstance(ticket.title, str)

        print(f"[OK] Got ticket {ticket.id}: {ticket.title}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_ticket_nested_objects.yaml")
async def test_ticket_nested_objects():
    """
    Test that nested objects (PartialUser, PartialCompany, etc.) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_ticket_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        tickets = await upsales.tickets.list(limit=10)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        # Check various nested objects across tickets
        found_user = False
        found_client = False
        found_contact = False
        found_status = False
        found_type = False
        found_regby = False

        for ticket in tickets:
            if ticket.user is not None:
                found_user = True
                assert hasattr(ticket.user, "id")
                assert hasattr(ticket.user, "name")
                print(f"  [OK] user: id={ticket.user.id}, name={ticket.user.name}")

            if ticket.client is not None:
                found_client = True
                assert hasattr(ticket.client, "id")
                assert hasattr(ticket.client, "name")
                print(f"  [OK] client: id={ticket.client.id}, name={ticket.client.name}")

            if ticket.contact is not None:
                found_contact = True
                assert hasattr(ticket.contact, "id")
                print(f"  [OK] contact: id={ticket.contact.id}")

            if ticket.status is not None:
                found_status = True
                assert hasattr(ticket.status, "id")
                print(f"  [OK] status: id={ticket.status.id}")

            if ticket.type is not None:
                found_type = True
                assert hasattr(ticket.type, "id")
                print(f"  [OK] type: id={ticket.type.id}")

            if ticket.regBy is not None:
                found_regby = True
                assert hasattr(ticket.regBy, "id")
                assert hasattr(ticket.regBy, "name")
                print(f"  [OK] regBy: id={ticket.regBy.id}, name={ticket.regBy.name}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, client:{found_client}, "
            f"contact:{found_contact}, status:{found_status}, type:{found_type}, regBy:{found_regby}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_ticket_computed_fields.yaml")
async def test_ticket_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_archived, is_pending, is_read computed properties.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_ticket_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        tickets = await upsales.tickets.list(limit=5)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        ticket = tickets[0]

        # Test computed fields exist and return correct types
        assert isinstance(ticket.is_archived, bool)
        assert ticket.is_archived == ticket.isArchived

        assert isinstance(ticket.is_pending, bool)
        assert ticket.is_pending == ticket.isPending

        assert isinstance(ticket.is_read, bool)
        assert ticket.is_read == ticket.isRead

        # Test custom_fields property
        assert hasattr(ticket, "custom_fields")

        print(
            f"[OK] Computed fields: is_archived={ticket.is_archived}, "
            f"is_pending={ticket.is_pending}, is_read={ticket.is_read}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_ticket_custom_fields.yaml")
async def test_ticket_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_ticket_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        tickets = await upsales.tickets.list(limit=20)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        # Find a ticket with custom fields
        ticket_with_custom = None
        for ticket in tickets:
            if ticket.custom:
                ticket_with_custom = ticket
                break

        if ticket_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(ticket_with_custom.custom, list)
            for field in ticket_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = ticket_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(ticket_with_custom.custom)} fields")
        else:
            print("[SKIP] No tickets with custom fields found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_tickets_integration/test_ticket_search.yaml")
async def test_ticket_search():
    """
    Test searching tickets with filters.

    Validates search functionality works with real API.

    Cassette: tests/cassettes/integration/test_tickets_integration/test_ticket_search.yaml
    """
    async with Upsales.from_env() as upsales:
        # Search for non-archived tickets
        tickets = await upsales.tickets.search(isArchived=False)

        assert isinstance(tickets, list)

        for ticket in tickets:
            assert isinstance(ticket, Ticket)
            assert ticket.isArchived is False

        print(f"[OK] Found {len(tickets)} non-archived tickets")
