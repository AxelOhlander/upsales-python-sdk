"""
Integration tests for journey steps endpoint.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_journey_steps_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_journey_steps_integration/*.yaml
    uv run pytest tests/integration/test_journey_steps_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
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
@my_vcr.use_cassette("test_journey_steps_integration/test_list_all_journey_steps.yaml")
async def test_list_all_journey_steps():
    """Test listing all journey steps from API."""
    async with Upsales.from_env() as upsales:
        steps = await upsales.journey_steps.list_all()

        # Verify we got journey steps
        assert len(steps) > 0

        # Verify structure
        for step in steps:
            assert hasattr(step, "value")
            assert hasattr(step, "name")
            assert hasattr(step, "priority")
            assert hasattr(step, "color")
            assert hasattr(step, "colorName")
            assert isinstance(step.value, str)
            assert isinstance(step.name, str)
            assert isinstance(step.priority, int)

        print(f"[OK] Listed {len(steps)} journey steps")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_get_by_value.yaml")
async def test_get_by_value():
    """Test getting a specific journey step by value."""
    async with Upsales.from_env() as upsales:
        # Get all steps first to find a valid value
        steps = await upsales.journey_steps.list_all()
        assert len(steps) > 0

        # Get first step by value
        first_value = steps[0].value
        step = await upsales.journey_steps.get_by_value(first_value)

        assert step is not None
        assert step.value == first_value
        assert step.name == steps[0].name

        print(f"[OK] Got journey step by value: {first_value}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """Test getting a specific journey step by name."""
    async with Upsales.from_env() as upsales:
        # Get all steps first to find a valid name
        steps = await upsales.journey_steps.list_all()
        assert len(steps) > 0

        # Get first step by name
        first_name = steps[0].name
        step = await upsales.journey_steps.get_by_name(first_name)

        assert step is not None
        assert step.name == first_name
        assert step.value == steps[0].value

        print(f"[OK] Got journey step by name: {first_name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_get_lead_stages.yaml")
async def test_get_lead_stages():
    """Test getting lead-related journey steps."""
    async with Upsales.from_env() as upsales:
        lead_stages = await upsales.journey_steps.get_lead_stages()

        # Verify we got some lead stages
        assert len(lead_stages) > 0

        # All should be lead stages
        for stage in lead_stages:
            assert stage.is_lead_stage

        print(f"[OK] Got {len(lead_stages)} lead stages")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_get_customer_stages.yaml")
async def test_get_customer_stages():
    """Test getting customer-related journey steps."""
    async with Upsales.from_env() as upsales:
        customer_stages = await upsales.journey_steps.get_customer_stages()

        # All should be customer stages
        for stage in customer_stages:
            assert stage.is_customer_stage

        print(f"[OK] Got {len(customer_stages)} customer stages")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_get_sorted_by_priority.yaml")
async def test_get_sorted_by_priority():
    """Test getting journey steps sorted by priority."""
    async with Upsales.from_env() as upsales:
        steps = await upsales.journey_steps.get_sorted_by_priority()

        assert len(steps) > 0

        # Verify sorted by priority
        priorities = [step.priority for step in steps]
        assert priorities == sorted(priorities)

        print(f"[OK] Got {len(steps)} steps sorted by priority")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_journey_steps_integration/test_computed_fields.yaml")
async def test_computed_fields():
    """Test computed fields on journey step model."""
    async with Upsales.from_env() as upsales:
        steps = await upsales.journey_steps.list_all()

        # Test that computed fields work
        for step in steps:
            # Computed fields should be accessible
            assert isinstance(step.is_lead_stage, bool)
            assert isinstance(step.is_customer_stage, bool)
            assert isinstance(step.is_opportunity_stage, bool)
            assert isinstance(step.is_negative_outcome, bool)

            # Test some logical relationships
            if step.value.lower() in {"lead", "mql", "sql", "assigned"}:
                assert step.is_lead_stage
            if step.value.lower() in {"customer", "lost_customer"}:
                assert step.is_customer_stage
            if step.value.lower() == "pipeline":
                assert step.is_opportunity_stage
            if step.value.lower() in {"lost_opportunity", "disqualified", "lost_customer"}:
                assert step.is_negative_outcome

        print("[OK] Computed fields validated")
