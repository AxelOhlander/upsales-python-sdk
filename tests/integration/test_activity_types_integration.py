"""
Integration tests for ActivityType model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_activity_types_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_activity_types_integration/
    uv run pytest tests/integration/test_activity_types_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.activity_types import ActivityType

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
@my_vcr.use_cassette("test_activity_types_integration/test_list_activity_types_real_response.yaml")
async def test_list_activity_types_real_response():
    """
    Test listing activity types with real API response structure.

    Validates that ActivityType model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_activity_types_integration/test_list_activity_types_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity types with limit
        activity_types = await upsales.activity_types.list(limit=10)

        assert isinstance(activity_types, list)
        assert len(activity_types) <= 10

        if len(activity_types) == 0:
            pytest.skip("No activity types found in the system")

        for activity_type in activity_types:
            assert isinstance(activity_type, ActivityType)
            assert isinstance(activity_type.id, int)
            assert activity_type.id > 0
            assert isinstance(activity_type.name, str)

            # Validate core fields
            assert isinstance(activity_type.roles, list)
            # hasOutcome is BinaryFlag (0 or 1, not bool)
            assert activity_type.hasOutcome in (0, 1)

        print(f"[OK] Listed {len(activity_types)} activity types successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_types_integration/test_activity_type_computed_fields.yaml")
async def test_activity_type_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates has_outcome computed property.

    Cassette: tests/cassettes/integration/test_activity_types_integration/test_activity_type_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        activity_types = await upsales.activity_types.list(limit=5)

        if len(activity_types) == 0:
            pytest.skip("No activity types found in the system")

        activity_type = activity_types[0]

        # Test has_outcome computed field
        assert isinstance(activity_type.has_outcome, bool)
        assert activity_type.has_outcome == (activity_type.hasOutcome == 1)
        print(
            f"[OK] has_outcome: {activity_type.has_outcome} (hasOutcome={activity_type.hasOutcome})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_types_integration/test_activity_type_roles.yaml")
async def test_activity_type_roles():
    """
    Test roles field parsing with real API data.

    Validates roles list structure if present.

    Cassette: tests/cassettes/integration/test_activity_types_integration/test_activity_type_roles.yaml
    """
    async with Upsales.from_env() as upsales:
        activity_types = await upsales.activity_types.list(limit=20)

        if len(activity_types) == 0:
            pytest.skip("No activity types found in the system")

        # Find an activity type with roles
        activity_type_with_roles = None
        for activity_type in activity_types:
            if activity_type.roles:
                activity_type_with_roles = activity_type
                break

        if activity_type_with_roles:
            # Validate roles structure
            assert isinstance(activity_type_with_roles.roles, list)
            print(f"[OK] Roles validated: {len(activity_type_with_roles.roles)} roles")
        else:
            print("[SKIP] No activity types with roles found in sample")
