"""
Integration tests for Flow model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_flows_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_flows_integration/
    uv run pytest tests/integration/test_flows_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.flows import Flow

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
@my_vcr.use_cassette("test_flows_integration/test_list_flows_real_response.yaml")
async def test_list_flows_real_response():
    """
    Test listing flows with real API response structure.

    Validates that Flow model correctly parses real API data including
    nested objects and complex path structures.

    Cassette: tests/cassettes/integration/test_flows_integration/test_list_flows_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        flows = await upsales.flows.list(limit=5)

        assert isinstance(flows, list)

        if len(flows) == 0:
            pytest.skip("No flows found in the system")

        for flow in flows:
            assert isinstance(flow, Flow)
            assert isinstance(flow.id, int)
            assert flow.id > 0

            # Validate read-only fields are present
            if flow.regDate is not None:
                assert isinstance(flow.regDate, str)

            # Validate status field
            assert isinstance(flow.status, str)
            assert flow.status in ("draft", "active", "paused")

            # Validate loop field (boolean with default)
            assert isinstance(flow.loop, bool)

            # Validate loopUnit field
            assert isinstance(flow.loopUnit, str)

            # Validate endCriterias field (list with default)
            assert isinstance(flow.endCriterias, list)

        print(f"[OK] Listed {len(flows)} flows successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_flows_integration/test_get_flow_real_response.yaml")
async def test_get_flow_real_response():
    """
    Test getting a single flow with real API response structure.

    Validates full Flow model including all fields and nested objects.

    Cassette: tests/cassettes/integration/test_flows_integration/test_get_flow_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid flow ID
        flows = await upsales.flows.list(limit=1)

        if len(flows) == 0:
            pytest.skip("No flows found in the system")

        flow_id = flows[0].id

        # Now get the specific flow
        flow = await upsales.flows.get(flow_id)

        assert isinstance(flow, Flow)
        assert flow.id == flow_id

        # Validate read-only fields
        assert isinstance(flow.id, int)
        if flow.regDate is not None:
            assert isinstance(flow.regDate, str)

        # Validate status
        assert isinstance(flow.status, str)
        assert flow.status in ("draft", "active", "paused")

        # Validate loop configuration
        assert isinstance(flow.loop, bool)
        assert isinstance(flow.loopUnit, str)
        if flow.loopTime is not None:
            assert isinstance(flow.loopTime, int)

        # Validate time configuration
        if flow.startTime is not None:
            assert isinstance(flow.startTime, str)
        if flow.endTime is not None:
            assert isinstance(flow.endTime, str)
        if flow.timezone is not None:
            assert isinstance(flow.timezone, str)

        # Validate flags
        if flow.skipWeekends is not None:
            assert isinstance(flow.skipWeekends, bool)
        if flow.hasBeenActive is not None:
            assert isinstance(flow.hasBeenActive, bool)

        # Validate segment
        if flow.segmentId is not None:
            assert isinstance(flow.segmentId, int)
        if flow.segment is not None:
            assert isinstance(flow.segment, dict)

        # Validate path (complex object)
        if flow.path is not None:
            assert isinstance(flow.path, dict)

        # Validate end criterias
        assert isinstance(flow.endCriterias, list)

        # Validate brand ID
        assert isinstance(flow.brandId, int)

        # Validate completion count
        if flow.completedContactCount is not None:
            assert isinstance(flow.completedContactCount, int)

        print(f"[OK] Got flow {flow.id}: {flow.name or '(unnamed)'}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_flows_integration/test_flow_nested_objects.yaml")
async def test_flow_nested_objects():
    """
    Test that nested objects (regBy, modBy, segment) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_flows_integration/test_flow_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        flows = await upsales.flows.list(limit=10)

        if len(flows) == 0:
            pytest.skip("No flows found in the system")

        # Check various nested objects across flows
        found_regby = False
        found_modby = False
        found_segment = False
        found_path = False

        for flow in flows:
            if flow.regBy is not None:
                found_regby = True
                assert isinstance(flow.regBy, (dict, int))
                print(f"  [OK] regBy: {flow.regBy} (type: {type(flow.regBy).__name__})")

            if flow.modBy is not None:
                found_modby = True
                assert isinstance(flow.modBy, (dict, int))
                print(f"  [OK] modBy: {flow.modBy} (type: {type(flow.modBy).__name__})")

            if flow.segment is not None:
                found_segment = True
                assert isinstance(flow.segment, dict)
                print(f"  [OK] segment: {flow.segment}")

            if flow.path is not None:
                found_path = True
                assert isinstance(flow.path, dict)
                print(
                    f"  [OK] path: {type(flow.path).__name__} with keys: {list(flow.path.keys())[:3]}..."
                )

        print(
            f"\n[OK] Nested objects found - regBy:{found_regby}, modBy:{found_modby}, "
            f"segment:{found_segment}, path:{found_path}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_flows_integration/test_flow_computed_fields.yaml")
async def test_flow_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_active, is_draft, is_paused computed properties.

    Cassette: tests/cassettes/integration/test_flows_integration/test_flow_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        flows = await upsales.flows.list(limit=10)

        if len(flows) == 0:
            pytest.skip("No flows found in the system")

        # Test computed fields across different statuses
        for flow in flows:
            # Test computed fields exist and return correct types
            assert isinstance(flow.is_active, bool)
            assert flow.is_active == (flow.status == "active")

            assert isinstance(flow.is_draft, bool)
            assert flow.is_draft == (flow.status == "draft")

            assert isinstance(flow.is_paused, bool)
            assert flow.is_paused == (flow.status == "paused")

            print(
                f"[OK] Flow {flow.id}: status={flow.status}, "
                f"is_active={flow.is_active}, is_draft={flow.is_draft}, is_paused={flow.is_paused}"
            )

            # Validate exactly one status flag is True
            status_flags = [flow.is_active, flow.is_draft, flow.is_paused]
            assert sum(status_flags) == 1, "Exactly one status flag should be True"
