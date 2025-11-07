"""
Integration tests for Trigger model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_triggers_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_triggers_integration/*.yaml
    uv run pytest tests/integration/test_triggers_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.triggers import Trigger

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
@my_vcr.use_cassette("test_triggers_integration/test_get_trigger_real_response.yaml")
async def test_get_trigger_real_response():
    """
    Test getting a trigger with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Trigger
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_triggers_integration/test_get_trigger_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real trigger (or replay from cassette)
        triggers = await upsales.triggers.list(limit=1)

        assert len(triggers) > 0, "Should have at least one trigger"
        trigger = triggers[0]

        # Validate Trigger model with Pydantic v2 features
        assert isinstance(trigger, Trigger)
        assert isinstance(trigger.id, int)
        assert isinstance(trigger.name, str)
        assert trigger.name  # Name should not be empty (NonEmptyStr validator)

        # Validate BinaryFlag field (0 or 1)
        assert trigger.active in (0, 1)

        # Validate list fields
        assert isinstance(trigger.events, list)
        assert isinstance(trigger.actions, list)
        assert isinstance(trigger.criterias, list)

        # Validate computed fields
        assert isinstance(trigger.is_active, bool)
        assert isinstance(trigger.has_events, bool)
        assert isinstance(trigger.has_actions, bool)
        assert isinstance(trigger.has_criterias, bool)

        print(
            f"[OK] Trigger parsed successfully: {trigger.name} (ID: {trigger.id}, "
            f"Events: {len(trigger.events)}, Actions: {len(trigger.actions)})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_triggers_integration/test_list_triggers_real_response.yaml")
async def test_list_triggers_real_response():
    """
    Test listing triggers with real API response.

    Validates that list responses correctly parse and return multiple Trigger objects.

    Cassette: tests/cassettes/integration/test_triggers_integration/test_list_triggers_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List triggers (or replay from cassette)
        triggers = await upsales.triggers.list(limit=10)

        assert isinstance(triggers, list)
        assert all(isinstance(trig, Trigger) for trig in triggers)

        if len(triggers) > 0:
            # Validate first trigger
            trigger = triggers[0]
            assert trigger.id > 0
            assert trigger.name
            assert trigger.active in (0, 1)
            assert isinstance(trigger.events, list)

            print(f"[OK] Listed {len(triggers)} triggers successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_triggers_integration/test_trigger_computed_fields.yaml")
async def test_trigger_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_active, has_events, etc.)
    return correct values based on actual API data.

    Cassette: tests/cassettes/integration/test_triggers_integration/test_trigger_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        triggers = await upsales.triggers.list(limit=5)

        for trigger in triggers:
            # Test computed field: is_active
            if trigger.active == 1:
                assert trigger.is_active is True
            else:
                assert trigger.is_active is False

            # Test computed field: has_events
            if len(trigger.events) > 0:
                assert trigger.has_events is True
            else:
                assert trigger.has_events is False

            # Test computed field: has_actions
            if len(trigger.actions) > 0:
                assert trigger.has_actions is True
            else:
                assert trigger.has_actions is False

            # Test computed field: has_criterias
            if len(trigger.criterias) > 0:
                assert trigger.has_criterias is True
            else:
                assert trigger.has_criterias is False

        print(f"[OK] Computed fields validated for {len(triggers)} triggers")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_triggers_integration/test_trigger_custom_methods.yaml")
async def test_trigger_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_active(), get_by_name(), and get_by_event() methods
    work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_triggers_integration/test_trigger_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active_triggers = await upsales.triggers.get_active()
        assert isinstance(active_triggers, list)
        assert all(trig.is_active for trig in active_triggers)

        # Test get_by_name() with first trigger
        if len(active_triggers) > 0:
            first_trigger = active_triggers[0]
            found_trigger = await upsales.triggers.get_by_name(first_trigger.name)
            assert found_trigger is not None
            assert found_trigger.id == first_trigger.id
            assert found_trigger.name == first_trigger.name

            # Test get_by_event() with first event from first trigger
            if len(first_trigger.events) > 0:
                first_event = first_trigger.events[0]
                event_triggers = await upsales.triggers.get_by_event(first_event)
                assert isinstance(event_triggers, list)
                assert len(event_triggers) > 0
                assert all(first_event in trig.events for trig in event_triggers)

        print(f"[OK] Custom methods validated: {len(active_triggers)} active triggers")
