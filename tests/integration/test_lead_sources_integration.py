"""
Integration tests for LeadSource model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_lead_sources_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_lead_sources_integration/
    uv run pytest tests/integration/test_lead_sources_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.lead_sources import LeadSource

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
@my_vcr.use_cassette("test_lead_sources_integration/test_list_lead_sources_real_response.yaml")
async def test_list_lead_sources_real_response():
    """
    Test listing lead_sources with real API response structure.

    Validates that LeadSource model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_lead_sources_integration/test_list_lead_sources_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.lead_sources.list(limit=10)

        assert isinstance(items, list)

        if len(items) == 0:
            pytest.skip("No lead_sources found in the system")

        for item in items:
            assert isinstance(item, LeadSource)
            assert isinstance(item.id, int)
            assert item.id > 0

        print(f"[OK] Listed {len(items)} lead_sources successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_lead_sources_integration/test_get_lead_sources_real_response.yaml")
async def test_get_lead_sources_real_response():
    """
    Test getting a single lead_sources with real API response.

    Cassette: tests/cassettes/integration/test_lead_sources_integration/test_get_lead_sources_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.lead_sources.list(limit=1)

        if len(items) == 0:
            pytest.skip("No lead_sources found in the system")

        item = await upsales.lead_sources.get(items[0].id)
        assert isinstance(item, LeadSource)
        assert item.id == items[0].id

        print(f"[OK] Got lead_sources ID={item.id} successfully")
