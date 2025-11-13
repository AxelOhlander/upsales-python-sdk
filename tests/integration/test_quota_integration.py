"""
Integration tests for Quota model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_quota_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_quota_integration/*.yaml
    uv run pytest tests/integration/test_quota_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.quota import Quota

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
@my_vcr.use_cassette("test_quota_integration/test_record_structure.yaml")
async def test_record_api_structure():
    """
    Record real API for offline development.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Quota
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_quota_integration/test_record_structure.yaml
    """
    async with Upsales.from_env() as upsales:
        quotas = await upsales.quota.list(limit=5)
        assert len(quotas) > 0
        print(f"✅ Recorded {len(quotas)} quotas")

        # Verify model structure
        quota = quotas[0]
        assert isinstance(quota, Quota)
        assert isinstance(quota.id, int)
        assert isinstance(quota.year, int)
        assert isinstance(quota.month, int)
