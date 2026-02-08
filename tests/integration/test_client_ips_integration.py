"""
Integration tests for ClientIp model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_client_ips_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_client_ips_integration/
    uv run pytest tests/integration/test_client_ips_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.client_ips import ClientIp

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
@my_vcr.use_cassette("test_client_ips_integration/test_list_client_ips_real_response.yaml")
async def test_list_client_ips_real_response():
    """
    Test listing client_ips with real API response structure.

    Validates that ClientIp model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_client_ips_integration/test_list_client_ips_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.client_ips.list(limit=10)

        assert isinstance(items, list)

        if len(items) == 0:
            pytest.skip("No client_ips found in the system")

        for item in items:
            assert isinstance(item, ClientIp)
            assert isinstance(item.id, int)
            assert item.id > 0

        print(f"[OK] Listed {len(items)} client_ips successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_ips_integration/test_get_client_ips_real_response.yaml")
async def test_get_client_ips_real_response():
    """
    Test getting a single client_ips with real API response.

    Cassette: tests/cassettes/integration/test_client_ips_integration/test_get_client_ips_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.client_ips.list(limit=1)

        if len(items) == 0:
            pytest.skip("No client_ips found in the system")

        item = await upsales.client_ips.get(items[0].id)
        assert isinstance(item, ClientIp)
        assert item.id == items[0].id

        print(f"[OK] Got client_ips ID={item.id} successfully")
