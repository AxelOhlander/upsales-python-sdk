"""
Integration tests for ProjectPlanStatus endpoint.

Records real API responses with VCR on first run, then replays.
"""

import pytest
import vcr

from upsales import Upsales

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration/projectplanstatus",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED"), ("authorization", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_statuses.yaml")
async def test_list_statuses() -> None:
    async with Upsales.from_env() as upsales:
        statuses = await upsales.project_plan_statuses.list(limit=10)
        assert isinstance(statuses, list)
        # May be empty on some tenants; just ensure call succeeds
        if statuses:
            assert hasattr(statuses[0], "id")
            assert hasattr(statuses[0], "name")
