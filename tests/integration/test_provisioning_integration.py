"""
Integration tests for ProvisioningRequest model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
This resource is POST-only, so only basic availability is tested.

To record cassettes:
    uv run pytest tests/integration/test_provisioning_integration.py -v
"""

import pytest

from upsales import Upsales


@pytest.mark.asyncio
async def test_provisioning_resource_available():
    """
    Test that provisioning resource is properly registered on client.
    """
    async with Upsales(token="test_token") as upsales:
        assert hasattr(upsales, "provisioning")
        print("[OK] provisioning resource is registered")
