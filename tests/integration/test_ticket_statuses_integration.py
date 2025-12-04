"""
Integration tests for TicketStatus model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_ticket_statuses_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_ticket_statuses_integration/
    uv run pytest tests/integration/test_ticket_statuses_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.ticket_statuses import PartialTicketStatus, TicketStatus

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
@my_vcr.use_cassette(
    "test_ticket_statuses_integration/test_list_ticket_statuses_real_response.yaml"
)
async def test_list_ticket_statuses_real_response():
    """
    Test listing ticket statuses with real API response structure.

    Validates that TicketStatus model correctly parses real API data.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_list_ticket_statuses_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        statuses = await upsales.ticket_statuses.list(limit=20)

        assert isinstance(statuses, list)

        if len(statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        for status in statuses:
            assert isinstance(status, TicketStatus)
            assert isinstance(status.id, int)
            assert status.id > 0
            assert isinstance(status.name, str)
            assert len(status.name) > 0

            # Validate boolean field
            assert isinstance(status.closed, bool)

            # Validate read-only fields (can be None for new statuses)
            if status.regDate is not None:
                assert isinstance(status.regDate, str)
            if status.modDate is not None:
                assert isinstance(status.modDate, str)

        print(f"[OK] Listed {len(statuses)} ticket statuses successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_statuses_integration/test_get_ticket_status_real_response.yaml")
async def test_get_ticket_status_real_response():
    """
    Test getting a single ticket status with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our TicketStatus
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_get_ticket_status_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get statuses first to find a valid ID
        statuses = await upsales.ticket_statuses.list(limit=1)

        if len(statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        status_id = statuses[0].id

        # Get single status by ID
        status = await upsales.ticket_statuses.get(status_id)

        # Validate TicketStatus model
        assert isinstance(status, TicketStatus)
        assert status.id == status_id
        assert isinstance(status.name, str)
        assert len(status.name) > 0

        # Validate boolean field
        assert isinstance(status.closed, bool)

        # Validate timestamps
        if status.regDate is not None:
            assert isinstance(status.regDate, str)
        if status.modDate is not None:
            assert isinstance(status.modDate, str)

        print(f"[OK] Status parsed successfully: {status.name} (ID: {status.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_statuses_integration/test_ticket_status_nested_objects.yaml")
async def test_ticket_status_nested_objects():
    """
    Test that nested objects (regBy, modBy) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_ticket_status_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        statuses = await upsales.ticket_statuses.list(limit=20)

        if len(statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        # Check various nested objects across statuses
        found_regby = False
        found_modby = False

        for status in statuses:
            # Test regBy if present (can be dict or int)
            if status.regBy is not None:
                found_regby = True
                # API returns 0 when not set, dict when set
                if isinstance(status.regBy, dict):
                    # Should have at least an id
                    if "id" in status.regBy:
                        assert isinstance(status.regBy["id"], int)
                        print(f"  [OK] regBy: id={status.regBy['id']}")
                elif isinstance(status.regBy, int):
                    assert status.regBy == 0, "Integer regBy should be 0"
                    print("  [OK] regBy: 0 (not set)")

            # Test modBy if present (can be dict or int)
            if status.modBy is not None:
                found_modby = True
                # API returns 0 when not set, dict when set
                if isinstance(status.modBy, dict):
                    # Should have at least an id
                    if "id" in status.modBy:
                        assert isinstance(status.modBy["id"], int)
                        print(f"  [OK] modBy: id={status.modBy['id']}")
                elif isinstance(status.modBy, int):
                    assert status.modBy == 0, "Integer modBy should be 0"
                    print("  [OK] modBy: 0 (not set)")

        print(f"\n[OK] Nested objects found - regBy:{found_regby}, modBy:{found_modby}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_statuses_integration/test_ticket_status_computed_fields.yaml")
async def test_ticket_status_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_closed computed property.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_ticket_status_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        statuses = await upsales.ticket_statuses.list(limit=10)

        if len(statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        # Test computed fields on multiple statuses
        for status in statuses:
            # Test is_closed computed field
            assert isinstance(status.is_closed, bool)
            assert status.is_closed == status.closed

        print(
            f"[OK] Computed fields validated on {len(statuses)} statuses: "
            f"open={sum(1 for s in statuses if not s.is_closed)}, "
            f"closed={sum(1 for s in statuses if s.is_closed)}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_statuses_integration/test_ticket_status_methods.yaml")
async def test_ticket_status_methods():
    """
    Test resource-specific methods with real API data.

    Validates get_by_name, get_open_statuses, get_closed_statuses methods.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_ticket_status_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test list_all (no limit)
        all_statuses = await upsales.ticket_statuses.list_all()

        if len(all_statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        assert isinstance(all_statuses, list)
        print(f"[OK] list_all returned {len(all_statuses)} statuses")

        # Test get_open_statuses
        open_statuses = await upsales.ticket_statuses.get_open_statuses()
        assert isinstance(open_statuses, list)
        for status in open_statuses:
            assert isinstance(status, TicketStatus)
            assert not status.closed
        print(f"[OK] get_open_statuses returned {len(open_statuses)} open statuses")

        # Test get_closed_statuses
        closed_statuses = await upsales.ticket_statuses.get_closed_statuses()
        assert isinstance(closed_statuses, list)
        for status in closed_statuses:
            assert isinstance(status, TicketStatus)
            assert status.closed
        print(f"[OK] get_closed_statuses returned {len(closed_statuses)} closed statuses")

        # Test get_by_name
        if all_statuses:
            test_status = all_statuses[0]
            found_status = await upsales.ticket_statuses.get_by_name(test_status.name)
            if found_status:
                assert isinstance(found_status, TicketStatus)
                assert found_status.id == test_status.id
                assert found_status.name == test_status.name
                print(f"[OK] get_by_name found status: {found_status.name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ticket_statuses_integration/test_partial_ticket_status.yaml")
async def test_partial_ticket_status():
    """
    Test PartialTicketStatus functionality.

    Validates fetch_full method on partial objects.

    Cassette: tests/cassettes/integration/test_ticket_statuses_integration/test_partial_ticket_status.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a status
        statuses = await upsales.ticket_statuses.list(limit=1)

        if len(statuses) == 0:
            pytest.skip("No ticket statuses found in the system")

        status = statuses[0]

        # Create a partial status manually
        partial = PartialTicketStatus(id=status.id, name=status.name)
        partial._client = upsales

        # Test fetch_full
        full_status = await partial.fetch_full()
        assert isinstance(full_status, TicketStatus)
        assert full_status.id == status.id
        assert full_status.name == status.name
        print(f"[OK] PartialTicketStatus.fetch_full() works: {full_status.name}")
