"""
Integration tests for ProjectPlanTypesResource using VCR.py.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_project_plan_types_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_project_plan_types_integration/*.yaml
    uv run pytest tests/integration/test_project_plan_types_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.project_plan_types import ProjectPlanType

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
@my_vcr.use_cassette("test_project_plan_types_integration/test_list_plan_types_real_response.yaml")
async def test_list_plan_types_real_response():
    """Test listing project plan types with real API response."""
    async with Upsales.from_env() as upsales:
        plan_types = await upsales.project_plan_types.list_all()

        assert isinstance(plan_types, list)

        for plan_type in plan_types:
            assert isinstance(plan_type, ProjectPlanType)
            assert isinstance(plan_type.id, int)
            assert isinstance(plan_type.name, str)
            assert hasattr(plan_type, "category")
            assert hasattr(plan_type, "stages")
            assert hasattr(plan_type, "isDefault")

        print(f"[OK] Listed {len(plan_types)} project plan types")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_project_plan_types_integration/test_get_plan_type_real_response.yaml")
async def test_get_plan_type_real_response():
    """Test getting a single project plan type with real API response."""
    async with Upsales.from_env() as upsales:
        # Get plan types first to find a valid ID
        plan_types = await upsales.project_plan_types.list_all()

        if len(plan_types) == 0:
            pytest.skip("No project plan types available for testing")

        plan_type_id = plan_types[0].id
        plan_type = await upsales.project_plan_types.get(plan_type_id)

        assert isinstance(plan_type, ProjectPlanType)
        assert plan_type.id == plan_type_id
        assert isinstance(plan_type.name, str)

        # Validate read-only fields
        assert hasattr(plan_type, "regDate")
        assert hasattr(plan_type, "regBy")
        assert hasattr(plan_type, "modDate")
        assert hasattr(plan_type, "modBy")

        print(f"[OK] Got plan type: {plan_type.name} (ID: {plan_type.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_project_plan_types_integration/test_plan_type_stages.yaml")
async def test_plan_type_stages():
    """Test project plan type stages structure."""
    async with Upsales.from_env() as upsales:
        plan_types = await upsales.project_plan_types.list_all()

        if len(plan_types) == 0:
            pytest.skip("No project plan types available for testing")

        found_with_stages = False

        for plan_type in plan_types:
            assert isinstance(plan_type.stages, list)

            if len(plan_type.stages) > 0:
                found_with_stages = True
                # Validate stage structure if present
                for stage in plan_type.stages:
                    assert isinstance(stage, dict)

        print(f"[OK] Stages validated, found_with_stages={found_with_stages}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_project_plan_types_integration/test_plan_type_default_flag.yaml")
async def test_plan_type_default_flag():
    """Test project plan type default flag."""
    async with Upsales.from_env() as upsales:
        plan_types = await upsales.project_plan_types.list_all()

        if len(plan_types) == 0:
            pytest.skip("No project plan types available for testing")

        default_count = 0

        for plan_type in plan_types:
            assert isinstance(plan_type.isDefault, bool)
            if plan_type.isDefault:
                default_count += 1

        print(f"[OK] Found {default_count} default plan type(s)")
