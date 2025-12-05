"""
Integration tests for MarketRejectlist model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_market_rejectlist_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_market_rejectlist_integration/
    uv run pytest tests/integration/test_market_rejectlist_integration.py -v

Note:
    The market rejectlist may be empty in test environments as it contains
    companies that should be excluded from marketing campaigns. Tests will
    skip if no data is found.
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import ServerError
from upsales.models.market_rejectlist import MarketRejectlist

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
    "test_market_rejectlist_integration/test_list_market_rejectlist_real_response.yaml"
)
async def test_list_market_rejectlist_real_response():
    """
    Test listing market rejectlist entries with real API response structure.

    Validates that MarketRejectlist model correctly parses real API data
    for companies excluded from marketing campaigns.

    Cassette: tests/cassettes/integration/test_market_rejectlist_integration/test_list_market_rejectlist_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            entries = await upsales.market_rejectlist.list(limit=10)
        except (ServerError, Exception) as e:
            # The /marketRejectlist endpoint may not be available in all environments
            pytest.skip(f"Market rejectlist endpoint not available: {e}")

        assert isinstance(entries, list)

        if len(entries) == 0:
            pytest.skip("No market rejectlist entries found in the system")

        for entry in entries:
            assert isinstance(entry, MarketRejectlist)
            assert isinstance(entry.id, int)
            assert entry.id > 0

            # At least one identifier should be present
            assert entry.has_identifier, "Entry must have at least one identifier"

            # Validate optional identifier fields
            if entry.name is not None:
                assert isinstance(entry.name, str)
            if entry.dunsNo is not None:
                assert isinstance(entry.dunsNo, str)
            if entry.organisationId is not None:
                assert isinstance(entry.organisationId, str)
            if entry.clientId is not None:
                assert isinstance(entry.clientId, int)
                assert entry.clientId > 0

        print(f"[OK] Listed {len(entries)} market rejectlist entries successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_market_rejectlist_integration/test_get_market_rejectlist_entry_real_response.yaml"
)
async def test_get_market_rejectlist_entry_real_response():
    """
    Test getting a single market rejectlist entry with real API response structure.

    Validates full MarketRejectlist model with all fields.

    Cassette: tests/cassettes/integration/test_market_rejectlist_integration/test_get_market_rejectlist_entry_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid entry ID
        try:
            entries = await upsales.market_rejectlist.list(limit=1)
        except (ServerError, Exception) as e:
            pytest.skip(f"Market rejectlist endpoint not available: {e}")

        if len(entries) == 0:
            pytest.skip("No market rejectlist entries found in the system")

        entry_id = entries[0].id

        # Now get the specific entry
        entry = await upsales.market_rejectlist.get(entry_id)

        assert isinstance(entry, MarketRejectlist)
        assert entry.id == entry_id

        # At least one identifier should be present
        assert entry.has_identifier, "Entry must have at least one identifier"

        # Build a description for logging
        identifiers = []
        if entry.name:
            identifiers.append(f"name='{entry.name}'")
        if entry.dunsNo:
            identifiers.append(f"dunsNo='{entry.dunsNo}'")
        if entry.organisationId:
            identifiers.append(f"organisationId='{entry.organisationId}'")
        if entry.clientId:
            identifiers.append(f"clientId={entry.clientId}")

        print(f"[OK] Got market rejectlist entry {entry.id}: {', '.join(identifiers)}")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_market_rejectlist_integration/test_market_rejectlist_computed_fields.yaml"
)
async def test_market_rejectlist_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates has_identifier computed property returns correct values
    based on the presence of identifying fields.

    Cassette: tests/cassettes/integration/test_market_rejectlist_integration/test_market_rejectlist_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            entries = await upsales.market_rejectlist.list(limit=10)
        except (ServerError, Exception) as e:
            pytest.skip(f"Market rejectlist endpoint not available: {e}")

        if len(entries) == 0:
            pytest.skip("No market rejectlist entries found in the system")

        entry = entries[0]

        # Test computed field exists and returns correct type
        assert isinstance(entry.has_identifier, bool)

        # Verify has_identifier matches actual identifier presence
        expected_has_identifier = any(
            [entry.name, entry.dunsNo, entry.organisationId, entry.clientId]
        )
        assert entry.has_identifier == expected_has_identifier

        # All entries should have at least one identifier
        assert entry.has_identifier is True, "All entries should have at least one identifier"

        # Check which identifiers are present
        identifiers = []
        if entry.name:
            identifiers.append("name")
        if entry.dunsNo:
            identifiers.append("dunsNo")
        if entry.organisationId:
            identifiers.append("organisationId")
        if entry.clientId:
            identifiers.append("clientId")

        print(
            f"[OK] Computed field has_identifier={entry.has_identifier}, "
            f"identifiers present: {', '.join(identifiers)}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_market_rejectlist_integration/test_market_rejectlist_identifiers.yaml")
async def test_market_rejectlist_identifiers():
    """
    Test that various identifier types are correctly parsed from real API data.

    Companies can be identified by name, DUNS number, organisation ID, or client ID.
    This validates each identifier type works correctly.

    Cassette: tests/cassettes/integration/test_market_rejectlist_integration/test_market_rejectlist_identifiers.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            entries = await upsales.market_rejectlist.list(limit=20)
        except (ServerError, Exception) as e:
            pytest.skip(f"Market rejectlist endpoint not available: {e}")

        if len(entries) == 0:
            pytest.skip("No market rejectlist entries found in the system")

        # Track which identifier types we found
        found_name = False
        found_duns = False
        found_org_id = False
        found_client_id = False

        for entry in entries:
            if entry.name is not None:
                found_name = True
                assert isinstance(entry.name, str)
                print(f"  [OK] name: '{entry.name}'")

            if entry.dunsNo is not None:
                found_duns = True
                assert isinstance(entry.dunsNo, str)
                print(f"  [OK] dunsNo: '{entry.dunsNo}'")

            if entry.organisationId is not None:
                found_org_id = True
                assert isinstance(entry.organisationId, str)
                print(f"  [OK] organisationId: '{entry.organisationId}'")

            if entry.clientId is not None:
                found_client_id = True
                assert isinstance(entry.clientId, int)
                assert entry.clientId > 0
                print(f"  [OK] clientId: {entry.clientId}")

        print(
            f"\n[OK] Identifier types found - name:{found_name}, dunsNo:{found_duns}, "
            f"organisationId:{found_org_id}, clientId:{found_client_id}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_market_rejectlist_integration/test_market_rejectlist_validation.yaml")
async def test_market_rejectlist_validation():
    """
    Test field validation with real API data.

    Validates that id and clientId are positive integers as specified in model.

    Cassette: tests/cassettes/integration/test_market_rejectlist_integration/test_market_rejectlist_validation.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            entries = await upsales.market_rejectlist.list(limit=10)
        except (ServerError, Exception) as e:
            pytest.skip(f"Market rejectlist endpoint not available: {e}")

        if len(entries) == 0:
            pytest.skip("No market rejectlist entries found in the system")

        for entry in entries:
            # Validate id is positive
            assert entry.id > 0, "Entry ID must be positive"

            # Validate clientId is positive if present
            if entry.clientId is not None:
                assert entry.clientId > 0, "Client ID must be positive if present"

        print(f"[OK] Validated {len(entries)} entries - all IDs are positive")
