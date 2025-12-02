"""
Unit tests for ProvisioningResource.

Tests pass-through operations for the provisioning endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.resources.provisioning import ProvisioningResource


class TestProvisioningResource:
    """Test pass-through operations for ProvisioningResource."""

    @pytest.fixture
    def sample_response_data(self):
        """Sample provisioning response data."""
        return {
            "status": "success",
            "message": "Provisioning operation completed",
            "data": {"customerId": 123, "result": "provisioned"},
        }

    @pytest.mark.asyncio
    async def test_forward_get(self, httpx_mock: HTTPXMock, sample_response_data):
        """Test forwarding GET request with query parameters."""
        # Match any provisioning endpoint with params
        import re

        httpx_mock.add_response(
            url=re.compile(r"https://power\.upsales\.com/api/v2/provisioning.*"),
            method="GET",
            json={"error": None, "data": sample_response_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProvisioningResource(http)
            result = await resource.forward_get(action="status", id=123)

            assert result == sample_response_data
            assert result["status"] == "success"
            assert result["data"]["customerId"] == 123

    @pytest.mark.asyncio
    async def test_forward_post(self, httpx_mock: HTTPXMock, sample_response_data):
        """Test forwarding POST request with body."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/provisioning",
            method="POST",
            json={"error": None, "data": sample_response_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProvisioningResource(http)
            request_data = {
                "action": "provision",
                "customerId": 123,
                "config": {"feature": "enabled"},
            }
            result = await resource.forward_post(request_data)

            assert result == sample_response_data
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_forward_get_empty_response(self, httpx_mock: HTTPXMock):
        """Test forward_get with empty response."""
        import re

        httpx_mock.add_response(
            url=re.compile(r"https://power\.upsales\.com/api/v2/provisioning.*"),
            method="GET",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProvisioningResource(http)
            result = await resource.forward_get(action="check")

            assert result == {}

    @pytest.mark.asyncio
    async def test_forward_post_complex_data(self, httpx_mock: HTTPXMock):
        """Test forward_post with complex nested data."""
        response_data = {
            "status": "success",
            "operations": [
                {"id": 1, "type": "create", "result": "ok"},
                {"id": 2, "type": "update", "result": "ok"},
            ],
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/provisioning",
            method="POST",
            json={"error": None, "data": response_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProvisioningResource(http)
            request_data = {
                "action": "bulk_provision",
                "customers": [
                    {"id": 1, "plan": "premium"},
                    {"id": 2, "plan": "basic"},
                ],
            }
            result = await resource.forward_post(request_data)

            assert result["status"] == "success"
            assert len(result["operations"]) == 2
            assert result["operations"][0]["result"] == "ok"
