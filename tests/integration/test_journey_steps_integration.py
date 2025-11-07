"""
Integration tests for journey steps endpoint.

These tests use VCR.py to record/replay real API responses.
First run records cassettes, subsequent runs replay them.
"""

import pytest

from upsales import Upsales


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_list_all_journey_steps():
    """Test listing all journey steps from API."""
    upsales = Upsales.from_env()
    async with upsales:
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


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_by_value():
    """Test getting a specific journey step by value."""
    upsales = Upsales.from_env()
    async with upsales:
        # Get all steps first to find a valid value
        steps = await upsales.journey_steps.list_all()
        assert len(steps) > 0

        # Get first step by value
        first_value = steps[0].value
        step = await upsales.journey_steps.get_by_value(first_value)

        assert step is not None
        assert step.value == first_value
        assert step.name == steps[0].name


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_by_name():
    """Test getting a specific journey step by name."""
    upsales = Upsales.from_env()
    async with upsales:
        # Get all steps first to find a valid name
        steps = await upsales.journey_steps.list_all()
        assert len(steps) > 0

        # Get first step by name
        first_name = steps[0].name
        step = await upsales.journey_steps.get_by_name(first_name)

        assert step is not None
        assert step.name == first_name
        assert step.value == steps[0].value


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_lead_stages():
    """Test getting lead-related journey steps."""
    upsales = Upsales.from_env()
    async with upsales:
        lead_stages = await upsales.journey_steps.get_lead_stages()

        # Verify we got some lead stages
        assert len(lead_stages) > 0

        # All should be lead stages
        for stage in lead_stages:
            assert stage.is_lead_stage


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_customer_stages():
    """Test getting customer-related journey steps."""
    upsales = Upsales.from_env()
    async with upsales:
        customer_stages = await upsales.journey_steps.get_customer_stages()

        # All should be customer stages
        for stage in customer_stages:
            assert stage.is_customer_stage


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_get_sorted_by_priority():
    """Test getting journey steps sorted by priority."""
    upsales = Upsales.from_env()
    async with upsales:
        steps = await upsales.journey_steps.get_sorted_by_priority()

        assert len(steps) > 0

        # Verify sorted by priority
        priorities = [step.priority for step in steps]
        assert priorities == sorted(priorities)


@pytest.mark.vcr()
@pytest.mark.asyncio
async def test_computed_fields():
    """Test computed fields on journey step model."""
    upsales = Upsales.from_env()
    async with upsales:
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
