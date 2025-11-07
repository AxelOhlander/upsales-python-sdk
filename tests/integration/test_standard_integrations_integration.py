"""
Simplified integration tests for StandardIntegration model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_standard_integrations_integration_simple.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_standard_integrations_integration_simple/*.yaml
    uv run pytest tests/integration/test_standard_integrations_integration_simple.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.standard_integration import StandardIntegration

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
@my_vcr.use_cassette(
    "test_standard_integrations_integration_simple/test_model_parses_real_data.yaml"
)
async def test_model_parses_real_data():
    """
    Test that StandardIntegration model correctly parses real API data.

    This is the core integration test - validates that our model definition
    matches the actual API response structure.

    Cassette: tests/cassettes/integration/test_standard_integrations_integration_simple/test_model_parses_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get integrations from API (or replay from cassette)
        integrations = await upsales.standard_integrations.list(limit=10)

        # Basic validation - ensure we got data and it parses
        assert len(integrations) > 0, "Should have at least one integration"
        assert all(isinstance(i, StandardIntegration) for i in integrations)

        # Validate first integration has required fields
        integration = integrations[0]
        assert isinstance(integration.id, int)
        assert isinstance(integration.name, str)
        assert isinstance(integration.active, bool)
        assert isinstance(integration.visible, bool)

        # Computed fields work
        assert isinstance(integration.is_active, bool)
        assert integration.is_active == integration.active

        print(f"[OK] Successfully parsed {len(integrations)} integrations")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_standard_integrations_integration_simple/test_list_all_works.yaml")
async def test_list_all_works():
    """
    Test that list_all() auto-pagination works with real API.

    Cassette: tests/cassettes/integration/test_standard_integrations_integration_simple/test_list_all_works.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test list_all auto-pagination
        all_integrations = await upsales.standard_integrations.list_all()

        assert isinstance(all_integrations, list)
        assert len(all_integrations) > 0
        assert all(isinstance(i, StandardIntegration) for i in all_integrations)

        print(f"[OK] list_all() returned {len(all_integrations)} integrations")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_standard_integrations_integration_simple/test_custom_methods.yaml")
async def test_custom_methods():
    """
    Test custom resource methods with real data.

    Cassette: tests/cassettes/integration/test_standard_integrations_integration_simple/test_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active = await upsales.standard_integrations.get_active()
        assert isinstance(active, list)
        if len(active) > 0:
            assert all(i.is_active for i in active)

        # Test get_by_name() if we have any integrations
        all_integrations = await upsales.standard_integrations.list_all()
        if len(all_integrations) > 0:
            first = all_integrations[0]
            found = await upsales.standard_integrations.get_by_name(first.name)
            if found:
                assert found.id == first.id

        print("[OK] Custom methods work correctly")
