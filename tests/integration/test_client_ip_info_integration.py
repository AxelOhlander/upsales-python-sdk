"""
Integration tests for ClientIpInfo model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
This resource is POST-only, so only basic availability is tested.

To record cassettes:
    uv run pytest tests/integration/test_client_ip_info_integration.py -v
"""

import pytest

from upsales import Upsales


@pytest.mark.asyncio
async def test_client_ip_info_resource_available():
    """
    Test that client_ip_info resource is properly registered on client.
    """
    async with Upsales(token="test_token") as upsales:
        assert hasattr(upsales, "client_ip_info")
        print("[OK] client_ip_info resource is registered")
