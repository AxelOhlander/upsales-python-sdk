"""Integration tests for Project Plan Stages endpoint."""

import pytest
import vcr

from upsales import Upsales
from upsales.models.project_plan_stages import ProjectPlanStage

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration/test_project_plan_stages_integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("set-cookie", "REDACTED"),  # Safety: redact tokens from responses
    ],
    filter_query_parameters=[
        ("token", "REDACTED"),  # Safety: redact token in query if ever present
    ],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_record_structure.yaml")
async def test_record_api_structure():
    """Record real API for offline development."""
    async with Upsales.from_env() as upsales:
        stages = await upsales.project_plan_stages.list(limit=5)
        assert len(stages) > 0
        print(f"✅ Recorded {len(stages)} project plan stages")

        # Verify we got ProjectPlanStage instances
        assert isinstance(stages[0], ProjectPlanStage)
        print(f"   First stage: id={stages[0].id}, name={stages[0].name}")
