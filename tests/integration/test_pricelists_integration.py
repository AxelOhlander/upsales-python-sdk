"""
Integration tests for Pricelist model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_pricelists_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_pricelists_integration/*.yaml
    uv run pytest tests/integration/test_pricelists_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.pricelist import Pricelist

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
@my_vcr.use_cassette("test_pricelists_integration/test_get_pricelist_real_response.yaml")
async def test_get_pricelist_real_response():
    """
    Test getting a pricelist with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Pricelist
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_get_pricelist_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real pricelist (or replay from cassette)
        pricelists = await upsales.pricelists.list(limit=1)

        assert len(pricelists) > 0, "Should have at least one pricelist"
        pricelist = pricelists[0]

        # Validate Pricelist model
        assert isinstance(pricelist, Pricelist)
        assert isinstance(pricelist.id, int)
        assert isinstance(pricelist.name, str)
        assert isinstance(pricelist.active, bool)
        assert isinstance(pricelist.isDefault, bool)
        assert isinstance(pricelist.showDiscount, bool)

        # Validate computed fields
        assert isinstance(pricelist.is_active, bool)
        assert pricelist.is_active == pricelist.active
        assert isinstance(pricelist.is_default, bool)
        assert pricelist.is_default == pricelist.isDefault

        # Validate frozen fields exist
        assert hasattr(pricelist, "regBy")
        assert hasattr(pricelist, "modBy")
        assert hasattr(pricelist, "modDate")

        print(f"[OK] Pricelist parsed successfully: {pricelist.name} (ID: {pricelist.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_pricelists_integration/test_list_pricelists_real_response.yaml")
async def test_list_pricelists_real_response():
    """
    Test listing pricelists with real API response structure.

    Validates pagination metadata and multiple pricelist objects.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_list_pricelists_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get pricelists with limit
        pricelists = await upsales.pricelists.list(limit=10)

        assert isinstance(pricelists, list)
        assert len(pricelists) <= 10

        for pricelist in pricelists:
            assert isinstance(pricelist, Pricelist)
            assert pricelist.id > 0
            assert len(pricelist.name) > 0
            assert isinstance(pricelist.active, bool)

        print(f"[OK] Listed {len(pricelists)} pricelists successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_pricelists_integration/test_pricelist_computed_fields_with_real_data.yaml"
)
async def test_pricelist_computed_fields_with_real_data():
    """
    Test computed fields work correctly with real API data.

    Validates all computed properties return expected types and values.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_pricelist_computed_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        pricelists = await upsales.pricelists.list(limit=5)

        for pricelist in pricelists:
            # Test is_active computed field
            assert isinstance(pricelist.is_active, bool)
            assert pricelist.is_active == pricelist.active

            # Test is_default computed field
            assert isinstance(pricelist.is_default, bool)
            assert pricelist.is_default == pricelist.isDefault

        print(f"[OK] Computed fields validated for {len(pricelists)} pricelists")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_pricelists_integration/test_get_default_pricelist_with_real_data.yaml")
async def test_get_default_pricelist_with_real_data():
    """
    Test getting the default pricelist with real API data.

    Validates custom resource method works with real data.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_get_default_pricelist_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        default = await upsales.pricelists.get_default()

        if default:
            assert isinstance(default, Pricelist)
            assert default.isDefault is True
            assert default.is_default is True
            print(f"[OK] Found default pricelist: {default.name}")
        else:
            print("[SKIP] No default pricelist found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_pricelists_integration/test_get_active_pricelists_with_real_data.yaml")
async def test_get_active_pricelists_with_real_data():
    """
    Test getting active pricelists with real API data.

    Validates custom resource method works with real data.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_get_active_pricelists_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        active = await upsales.pricelists.get_active()

        assert isinstance(active, list)

        for pricelist in active:
            assert isinstance(pricelist, Pricelist)
            assert pricelist.active is True
            assert pricelist.is_active is True

        print(f"[OK] Found {len(active)} active pricelists")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_pricelists_integration/test_get_pricelist_by_code_with_real_data.yaml")
async def test_get_pricelist_by_code_with_real_data():
    """
    Test getting pricelist by code with real API data.

    Validates custom resource method works with real data.

    Cassette: tests/cassettes/integration/test_pricelists_integration/test_get_pricelist_by_code_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all pricelists first to find one with a code
        pricelists = await upsales.pricelists.list_all()

        pricelist_with_code = None
        for pl in pricelists:
            if pl.code:
                pricelist_with_code = pl
                break

        if pricelist_with_code:
            # Test get_by_code
            found = await upsales.pricelists.get_by_code(pricelist_with_code.code)
            assert found is not None
            assert isinstance(found, Pricelist)
            assert found.code == pricelist_with_code.code
            print(f"[OK] Found pricelist by code: {found.code}")
        else:
            print("[SKIP] No pricelists with codes found")
