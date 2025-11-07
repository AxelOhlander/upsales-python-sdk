"""
Integration tests for OpportunityAI model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that OpportunityAI model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_opportunity_ai_integration.py -v

Note:
    OpportunityAI is a READ-ONLY resource, so we only test GET operations.
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.opportunity_ai import OpportunityAI

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunity_ai_integration/test_get_opportunity_ai_real_response.yaml")
async def test_get_opportunity_ai_real_response():
    """
    Test getting OpportunityAI with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our OpportunityAI
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get all opportunities AI data first to find a valid ID
        all_data = await upsales.opportunity_ai.get_all()

        assert isinstance(all_data, dict), "get_all() should return dict"
        assert len(all_data) > 0, "Should have at least one opportunity AI data"

        # Get first opportunity ID
        opportunity_id = list(all_data.keys())[0]
        print(f"Testing with opportunity ID: {opportunity_id}")

        # Get detailed AI analysis for this opportunity
        ai_data = await upsales.opportunity_ai.get(opportunity_id)

        # Validate OpportunityAI model with Pydantic v2 features
        assert isinstance(ai_data, OpportunityAI)
        assert isinstance(ai_data.id, int)
        assert ai_data.id == opportunity_id

        # Validate all fields are frozen (read-only)
        model_fields = ai_data.__class__.model_fields
        assert model_fields["id"].frozen, "id should be frozen"
        assert model_fields["appointment"].frozen, "appointment should be frozen"
        assert model_fields["activity"].frozen, "activity should be frozen"
        assert model_fields["opportunity"].frozen, "opportunity should be frozen"

        # Validate required fields exist
        assert hasattr(ai_data, "appointment")
        assert hasattr(ai_data, "activity")
        assert hasattr(ai_data, "allActivity")
        assert hasattr(ai_data, "opportunity")

        # Validate opportunity object structure
        assert isinstance(ai_data.opportunity, dict)
        assert "id" in ai_data.opportunity
        assert ai_data.opportunity["id"] == opportunity_id

        # Validate computed fields work
        assert isinstance(ai_data.opportunity_description, str)
        assert isinstance(ai_data.opportunity_value, int)
        assert isinstance(ai_data.opportunity_stage, dict)
        assert isinstance(ai_data.has_appointment, bool)
        assert isinstance(ai_data.has_activity, bool)

        # Validate boolean fields
        assert isinstance(ai_data.isDecisionMakerInvolved, bool)

        print(
            f"[OK] OpportunityAI parsed successfully: ID {ai_data.id}, "
            f"Description: {ai_data.opportunity_description[:50]}..., "
            f"Value: {ai_data.opportunity_value}, "
            f"Has appointment: {ai_data.has_appointment}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_opportunity_ai_integration/test_get_all_opportunity_ai_real_response.yaml"
)
async def test_get_all_opportunity_ai_real_response():
    """Test getting all opportunities AI data with real API response structure."""
    async with Upsales.from_env() as upsales:
        all_data = await upsales.opportunity_ai.get_all()

        # Validate response structure
        assert isinstance(all_data, dict)
        assert len(all_data) > 0, "Should have at least one opportunity"

        # Check first opportunity data structure
        first_id, first_data = next(iter(all_data.items()))

        assert isinstance(first_id, int)
        assert isinstance(first_data, dict)

        # Validate expected fields in simplified structure
        expected_fields = [
            "meeting",
            "activity",
            "allActivity",
            "confirmedBudget",
            "confirmedSolution",
            "checklist",
        ]

        for field in expected_fields:
            assert field in first_data, f"Field '{field}' should exist in AI data"

        # Validate field types
        assert isinstance(first_data["confirmedBudget"], bool)
        assert isinstance(first_data["confirmedSolution"], bool)
        assert isinstance(first_data["checklist"], list)

        print(f"[OK] get_all() returned {len(all_data)} opportunities with AI analysis")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunity_ai_integration/test_computed_fields_real_response.yaml")
async def test_computed_fields_real_response():
    """Test that computed fields work correctly with real API data."""
    async with Upsales.from_env() as upsales:
        # Get all opportunities AI data
        all_data = await upsales.opportunity_ai.get_all()
        opportunity_id = list(all_data.keys())[0]

        # Get detailed AI data
        ai_data = await upsales.opportunity_ai.get(opportunity_id)

        # Test ID extraction from nested opportunity
        assert ai_data.id == ai_data.opportunity.get("id")

        # Test opportunity_description extraction
        expected_desc = ai_data.opportunity.get("description", "")
        assert ai_data.opportunity_description == expected_desc

        # Test opportunity_value extraction
        expected_value = ai_data.opportunity.get("value", 0)
        assert ai_data.opportunity_value == expected_value

        # Test opportunity_stage extraction
        expected_stage = ai_data.opportunity.get("stage", {})
        assert ai_data.opportunity_stage == expected_stage

        # Test has_appointment logic
        if ai_data.appointment and len(ai_data.appointment) > 0:
            assert ai_data.has_appointment is True
        else:
            assert ai_data.has_appointment is False

        # Test has_activity logic
        has_activity_data = bool(ai_data.activity) or bool(ai_data.allActivity)
        assert ai_data.has_activity == has_activity_data

        print(f"[OK] All computed fields working correctly for opportunity {opportunity_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunity_ai_integration/test_model_immutability_real_response.yaml")
async def test_model_immutability_real_response():
    """Test that OpportunityAI model is immutable (all fields frozen)."""
    async with Upsales.from_env() as upsales:
        all_data = await upsales.opportunity_ai.get_all()
        opportunity_id = list(all_data.keys())[0]
        ai_data = await upsales.opportunity_ai.get(opportunity_id)

        # Verify model's edit() method raises error (read-only resource)
        with pytest.raises(RuntimeError, match="read-only"):
            await ai_data.edit()

        # Verify all regular fields are frozen
        frozen_fields = ["id", "appointment", "activity", "opportunity"]
        model_fields = ai_data.__class__.model_fields

        for field_name in frozen_fields:
            assert model_fields[field_name].frozen, f"Field '{field_name}' should be frozen"

        print("[OK] OpportunityAI model is properly immutable (read-only)")
