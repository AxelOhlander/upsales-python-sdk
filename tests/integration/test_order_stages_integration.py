"""
Integration tests for OrderStage model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that OrderStage model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_order_stages_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.orderStages import OrderStage

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_order_stages_integration/test_get_order_stage_real_response.yaml")
async def test_get_order_stage_real_response():
    """
    Test getting order stage with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our OrderStage
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get order stages to find a valid ID
        stages = await upsales.order_stages.list(limit=1)

        assert len(stages) > 0, "Should have at least one order stage"
        stage = stages[0]

        # Validate OrderStage model with Pydantic v2 features
        assert isinstance(stage, OrderStage)
        assert isinstance(stage.id, int)
        assert isinstance(stage.name, str)
        assert len(stage.name) > 0  # NonEmptyStr validator

        # Validate Percentage field (should be 0-100)
        assert isinstance(stage.probability, int)
        assert 0 <= stage.probability <= 100

        # Validate BinaryFlag field (should be 0 or 1)
        assert stage.exclude in (0, 1)

        # Validate computed fields work
        assert isinstance(stage.is_excluded, bool)
        assert isinstance(stage.probability_decimal, float)
        assert 0.0 <= stage.probability_decimal <= 1.0
        # Verify computation is correct
        assert stage.probability_decimal == stage.probability / 100.0

        print(
            f"[OK] OrderStage parsed successfully: {stage.name} "
            f"(ID: {stage.id}, Probability: {stage.probability}%)"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_order_stages_integration/test_list_order_stages_real_response.yaml")
async def test_list_order_stages_real_response():
    """Test listing order stages with real API response structure."""
    async with Upsales.from_env() as upsales:
        stages = await upsales.order_stages.list(limit=10)

        assert isinstance(stages, list)
        assert len(stages) <= 10

        for stage in stages:
            assert isinstance(stage, OrderStage)
            assert stage.id > 0
            assert len(stage.name) > 0
            # Probability must be 0-100
            assert 0 <= stage.probability <= 100
            # Exclude must be 0 or 1
            assert stage.exclude in (0, 1)

        print(f"[OK] Listed {len(stages)} order stages successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_order_stages_integration/test_order_stage_serialization.yaml")
async def test_order_stage_serialization_real_data():
    """
    Test to_update_dict_minimal() serialization with real order stage data.

    Validates that serialization excludes frozen fields and only sends
    changed + required fields (probability).
    """
    async with Upsales.from_env() as upsales:
        stages = await upsales.order_stages.list(limit=1)
        stage = stages[0]

        # Get minimal update dict
        minimal_dict = stage.to_update_dict_minimal()

        # Validate frozen fields excluded
        assert "id" not in minimal_dict

        # Validate computed fields excluded
        assert "is_excluded" not in minimal_dict
        assert "probability_decimal" not in minimal_dict

        # Should only include required field (probability)
        assert "probability" in minimal_dict
        assert minimal_dict["probability"] == stage.probability

        # With overrides, should include changed fields + required
        minimal_with_changes = stage.to_update_dict_minimal(name="New Name")
        assert "name" in minimal_with_changes
        assert "probability" in minimal_with_changes  # Still includes required
        assert minimal_with_changes["name"] == "New Name"

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(minimal_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {stage.name}")
        print(f"[OK] Minimal payload: {minimal_dict}")
        print(f"[OK] With changes: {minimal_with_changes}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_order_stages_integration/test_get_included_stages.yaml")
async def test_get_included_stages():
    """
    Test get_included() custom method with real data.

    Validates that custom methods work correctly with the order stages endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Get stages included in pipeline (exclude=0)
        included = await upsales.order_stages.get_included()

        assert isinstance(included, list)
        # All should have exclude=0
        for stage in included:
            assert stage.exclude == 0
            assert not stage.is_excluded  # Computed field check

        print(f"[OK] Found {len(included)} included stages (exclude=0)")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_order_stages_integration/test_get_sorted_by_probability.yaml")
async def test_get_sorted_by_probability():
    """
    Test get_sorted_by_probability() with real data.

    Validates sorting works correctly.
    """
    async with Upsales.from_env() as upsales:
        # Get stages sorted by probability (ascending)
        stages = await upsales.order_stages.get_sorted_by_probability()

        assert isinstance(stages, list)
        if len(stages) > 1:
            # Verify sorting (each stage should have >= probability than previous)
            for i in range(1, len(stages)):
                assert stages[i].probability >= stages[i - 1].probability, (
                    f"Not sorted: {stages[i - 1].probability} > {stages[i].probability}"
                )

        print(f"[OK] Sorted {len(stages)} stages by probability: {[s.probability for s in stages]}")
