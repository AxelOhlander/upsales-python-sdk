"""
Integration tests for ProjectPlanPriority model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_projectplanpriority_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_projectplanpriority_integration/*.yaml
    uv run pytest tests/integration/test_projectplanpriority_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.projectplanpriority import ProjectPlanPriority

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
@my_vcr.use_cassette("test_projectplanpriority_integration/test_get_priority_real_response.yaml")
async def test_get_priority_real_response():
    """
    Test getting a priority with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our ProjectPlanPriority
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_projectplanpriority_integration/test_get_priority_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get priorities (or replay from cassette)
        priorities = await upsales.project_plan_priorities.list(limit=1)

        assert len(priorities) > 0, "Should have at least one priority"
        priority = priorities[0]

        # Validate ProjectPlanPriority model with Pydantic v2 features
        assert isinstance(priority, ProjectPlanPriority)
        assert isinstance(priority.id, int)
        assert isinstance(priority.name, str)
        assert priority.name  # Name should not be empty (NonEmptyStr validator)

        # Validate category field
        assert priority.category in ("LOW", "MEDIUM", "HIGH")

        # Validate isDefault field
        assert isinstance(priority.isDefault, bool)

        # Validate computed fields
        assert isinstance(priority.is_default, bool)
        assert isinstance(priority.is_low, bool)
        assert isinstance(priority.is_medium, bool)
        assert isinstance(priority.is_high, bool)

        print(
            f"[OK] Priority parsed successfully: {priority.name} (ID: {priority.id}, Category: {priority.category})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projectplanpriority_integration/test_list_priorities_real_response.yaml")
async def test_list_priorities_real_response():
    """
    Test listing priorities with real API response.

    Validates that list responses correctly parse and return multiple ProjectPlanPriority objects.

    Cassette: tests/cassettes/integration/test_projectplanpriority_integration/test_list_priorities_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List priorities (or replay from cassette)
        priorities = await upsales.project_plan_priorities.list(limit=10)

        assert isinstance(priorities, list)
        assert all(isinstance(p, ProjectPlanPriority) for p in priorities)

        if len(priorities) > 0:
            # Validate first priority
            priority = priorities[0]
            assert priority.id > 0
            assert priority.name
            assert priority.category in ("LOW", "MEDIUM", "HIGH")

            print(f"[OK] Listed {len(priorities)} priorities successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projectplanpriority_integration/test_priority_computed_fields.yaml")
async def test_priority_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_low, is_medium, is_high, is_default)
    return correct values based on actual API data.

    Cassette: tests/cassettes/integration/test_projectplanpriority_integration/test_priority_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        priorities = await upsales.project_plan_priorities.list(limit=10)

        for priority in priorities:
            # Test computed field: is_default
            assert priority.is_default == priority.isDefault

            # Test computed fields for categories
            if priority.category == "LOW":
                assert priority.is_low is True
                assert priority.is_medium is False
                assert priority.is_high is False
            elif priority.category == "MEDIUM":
                assert priority.is_low is False
                assert priority.is_medium is True
                assert priority.is_high is False
            elif priority.category == "HIGH":
                assert priority.is_low is False
                assert priority.is_medium is False
                assert priority.is_high is True

        print(f"[OK] Computed fields validated for {len(priorities)} priorities")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projectplanpriority_integration/test_priority_custom_methods.yaml")
async def test_priority_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_by_category(), get_defaults(), get_low(), get_medium(),
    get_high(), and get_by_name() methods work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_projectplanpriority_integration/test_priority_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_defaults()
        defaults = await upsales.project_plan_priorities.get_defaults()
        assert isinstance(defaults, list)
        assert all(p.is_default for p in defaults)

        # Test get_by_category()
        low_priorities = await upsales.project_plan_priorities.get_by_category("LOW")
        assert isinstance(low_priorities, list)
        assert all(p.is_low for p in low_priorities)

        # Test convenience methods
        low = await upsales.project_plan_priorities.get_low()
        medium = await upsales.project_plan_priorities.get_medium()
        high = await upsales.project_plan_priorities.get_high()

        assert all(p.is_low for p in low)
        assert all(p.is_medium for p in medium)
        assert all(p.is_high for p in high)

        # Test get_by_name() with first priority
        all_priorities = await upsales.project_plan_priorities.list()
        if len(all_priorities) > 0:
            first_priority = all_priorities[0]
            found_priority = await upsales.project_plan_priorities.get_by_name(first_priority.name)
            assert found_priority is not None
            assert found_priority.id == first_priority.id
            assert found_priority.name == first_priority.name

        print(
            f"[OK] Custom methods validated: {len(defaults)} defaults, "
            f"{len(low)} low, {len(medium)} medium, {len(high)} high"
        )
