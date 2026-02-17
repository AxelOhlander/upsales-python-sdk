"""
Integration tests for Unsub model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_unsub_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_unsub_integration/
    uv run pytest tests/integration/test_unsub_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.unsub import Unsub

pytestmark = pytest.mark.skip(reason="Endpoint returns 404 - may be removed or renamed")

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
@my_vcr.use_cassette("test_unsub_integration/test_list_unsub_real_response.yaml")
async def test_list_unsub_real_response():
    """
    Test listing unsub with real API response structure.

    Validates that Unsub model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_unsub_integration/test_list_unsub_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.unsub.list(limit=10)

        assert isinstance(items, list)

        if len(items) == 0:
            pytest.skip("No unsub found in the system")

        for item in items:
            assert isinstance(item, Unsub)
            assert isinstance(item.id, int)
            assert item.id > 0

        print(f"[OK] Listed {len(items)} unsub successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_unsub_integration/test_get_unsub_real_response.yaml")
async def test_get_unsub_real_response():
    """
    Test getting a single unsub with real API response.

    Cassette: tests/cassettes/integration/test_unsub_integration/test_get_unsub_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.unsub.list(limit=1)

        if len(items) == 0:
            pytest.skip("No unsub found in the system")

        item = await upsales.unsub.get(items[0].id)
        assert isinstance(item, Unsub)
        assert item.id == items[0].id

        print(f"[OK] Got unsub ID={item.id} successfully")
