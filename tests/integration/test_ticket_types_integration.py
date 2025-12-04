"""
Integration tests for TicketType model with real API responses.

⚠️ NOTE: The /ticketType endpoint returns 404 in this Upsales environment.
This is likely a permissions or configuration issue. TicketType objects exist
(visible as nested objects in tickets), but cannot be queried directly.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_ticket_types_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_ticket_types_integration/
    uv run pytest tests/integration/test_ticket_types_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import NotFoundError
from upsales.models.ticket_types import PartialTicketType, TicketType

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
@my_vcr.use_cassette("test_ticket_types_integration/test_endpoint_not_available.yaml")
async def test_endpoint_not_available():
    """
    Test that /ticketType endpoint returns 404 in this environment.

    This documents a known limitation: while TicketType objects exist
    (visible as nested objects in tickets.type), the dedicated ticketType
    endpoint is not available in this Upsales account.

    Cassette: tests/cassettes/integration/test_ticket_types_integration/test_endpoint_not_available.yaml
    """
    async with Upsales.from_env() as upsales:
        # Attempt to list ticket types - should fail with 404
        with pytest.raises(NotFoundError) as exc_info:
            await upsales.ticket_types.list(limit=1)

        assert "Resource not found: /ticketType" in str(exc_info.value)
        print(
            "[OK] Confirmed: /ticketType endpoint returns 404 (not available in this environment)"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_types_integration/test_partial_from_ticket.yaml")
async def test_partial_from_ticket():
    """
    Test that PartialTicketType correctly parses nested data from tickets.

    Even though the dedicated /ticketType endpoint is not available,
    ticket types appear as nested objects in ticket responses.

    Cassette: tests/cassettes/integration/test_ticket_types_integration/test_partial_from_ticket.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get tickets to find a type
        tickets = await upsales.tickets.list(limit=10)

        if len(tickets) == 0:
            pytest.skip("No tickets found in the system")

        # Find a ticket with a type
        ticket_with_type = None
        for ticket in tickets:
            if ticket.type is not None:
                ticket_with_type = ticket
                break

        if ticket_with_type is None:
            pytest.skip("No tickets with type found")

        # Validate PartialTicketType
        ticket_type = ticket_with_type.type
        assert isinstance(ticket_type, PartialTicketType)
        assert isinstance(ticket_type.id, int)
        assert ticket_type.id > 0
        assert isinstance(ticket_type.name, str)
        assert len(ticket_type.name) > 0

        print(f"[OK] PartialTicketType from ticket: {ticket_type.name} (ID: {ticket_type.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_types_integration/test_model_validation.yaml")
async def test_model_validation():
    """
    Test that TicketType and PartialTicketType models validate correctly.

    Tests model instantiation with mock data to ensure validators work.

    Cassette: tests/cassettes/integration/test_ticket_types_integration/test_model_validation.yaml
    """
    # Test PartialTicketType instantiation
    partial = PartialTicketType(id=1, name="Test Type")
    assert partial.id == 1
    assert partial.name == "Test Type"
    print("[OK] PartialTicketType validation works")

    # Test TicketType instantiation with minimal data
    ticket_type = TicketType(
        id=1,
        name="Test Type",
        isDefault=False,
    )
    assert ticket_type.id == 1
    assert ticket_type.name == "Test Type"
    assert ticket_type.isDefault is False
    assert ticket_type.is_default is False

    # Test with isDefault=True
    default_type = TicketType(
        id=2,
        name="Default Type",
        isDefault=True,
    )
    assert default_type.is_default is True
    print("[OK] TicketType validation works")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_types_integration/test_computed_fields.yaml")
async def test_computed_fields():
    """
    Test computed fields work correctly with model data.

    Tests the is_default computed property.

    Cassette: tests/cassettes/integration/test_ticket_types_integration/test_computed_fields.yaml
    """
    # Test is_default computed field
    non_default = TicketType(id=1, name="Regular", isDefault=False)
    assert non_default.is_default is False
    assert non_default.is_default == non_default.isDefault

    default = TicketType(id=2, name="Default", isDefault=True)
    assert default.is_default is True
    assert default.is_default == default.isDefault

    print("[OK] Computed field is_default works correctly")


# NOTE: The following tests are SKIPPED because /ticketType endpoint is not available


@pytest.mark.skip(reason="Endpoint /ticketType not available in this environment (returns 404)")
@pytest.mark.asyncio
async def test_list_ticket_types_real_response():
    """
    SKIPPED: Test listing ticket types with real API response structure.

    This test is skipped because the /ticketType endpoint returns 404
    in this Upsales environment. The endpoint may require special permissions
    or may not be enabled in all Upsales accounts.
    """
    pass


@pytest.mark.skip(reason="Endpoint /ticketType not available in this environment (returns 404)")
@pytest.mark.asyncio
async def test_get_ticket_type_real_response():
    """
    SKIPPED: Test getting a single ticket type with real API response structure.

    This test is skipped because the /ticketType endpoint returns 404
    in this Upsales environment.
    """
    pass


@pytest.mark.skip(reason="Endpoint /ticketType not available in this environment (returns 404)")
@pytest.mark.asyncio
async def test_ticket_type_get_by_name():
    """
    SKIPPED: Test getting ticket type by name using custom resource method.

    This test is skipped because the /ticketType endpoint returns 404
    in this Upsales environment.
    """
    pass


@pytest.mark.skip(reason="Endpoint /ticketType not available in this environment (returns 404)")
@pytest.mark.asyncio
async def test_ticket_type_get_default():
    """
    SKIPPED: Test getting the default ticket type using custom resource method.

    This test is skipped because the /ticketType endpoint returns 404
    in this Upsales environment.
    """
    pass
