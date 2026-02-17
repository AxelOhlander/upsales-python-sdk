"""
Integration tests for SoliditetClient model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_soliditet_clients_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_soliditet_clients_integration/
    uv run pytest tests/integration/test_soliditet_clients_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.soliditet_clients import SoliditetClient

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
@my_vcr.use_cassette(
    "test_soliditet_clients_integration/test_list_soliditet_clients_real_response.yaml"
)
async def test_list_soliditet_clients_real_response():
    """
    Test listing soliditet_clients with real API response structure.

    Validates that SoliditetClient model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_soliditet_clients_integration/test_list_soliditet_clients_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.soliditet_clients.list(limit=10)

        assert isinstance(items, list)

        if len(items) == 0:
            pytest.skip("No soliditet_clients found in the system")

        for item in items:
            assert isinstance(item, SoliditetClient)

        # API returns empty objects {} between real records; filter to those with data
        real_items = [i for i in items if i.dunsNo is not None]
        assert len(real_items) > 0, "Expected at least one soliditet client with dunsNo"
        for item in real_items:
            assert item.dunsNo is not None

        print(f"[OK] Listed {len(items)} soliditet_clients ({len(real_items)} with data)")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_soliditet_clients_integration/test_soliditet_client_fields.yaml"
)
async def test_soliditet_client_fields():
    """
    Test that SoliditetClient fields are correctly typed from real API data.

    Note: Soliditet API does NOT support GET-by-ID. Only list is available.
    The API also returns empty objects {} between real records.

    Cassette: tests/cassettes/integration/test_soliditet_clients_integration/test_soliditet_client_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.soliditet_clients.list(limit=10)

        if len(items) == 0:
            pytest.skip("No soliditet_clients found in the system")

        # Filter to real records (API returns empty {} between actual records)
        real_items = [i for i in items if i.dunsNo is not None]
        if len(real_items) == 0:
            pytest.skip("No soliditet_clients with dunsNo found")

        item = real_items[0]
        assert isinstance(item.dunsNo, (str, int))
        assert isinstance(item.name, str)
        assert item.country is None or isinstance(item.country, str)

        print(f"[OK] SoliditetClient fields validated: dunsNo={item.dunsNo}, name={item.name}")
