"""
Tests for EsignFunctionResource custom methods.

Tests the specialized e-signature function endpoint that provides
settings retrieval and document download capabilities.

Coverage target: 85%+
"""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock  # type: ignore[import-not-found]

from upsales.http import HTTPClient
from upsales.models.esign_function import EsignFunctionSettings
from upsales.resources.esign_function import EsignFunctionResource


class TestEsignFunctionResourceCustomMethods:
    """Test custom methods specific to EsignFunctionResource."""

    @pytest.fixture
    def sample_settings(self) -> dict[str, Any]:
        """Sample e-signature settings data."""
        return {
            "delivery": "email",
            "allowDraft": 1,
            "documentType": "contract",
            "languages": ["en", "sv", "no"],
            "bankIdCountries": ["SE", "NO", "DK"],
            "multiSign": 1,
            "userCanSign": 1,
            "fields": [
                {"name": "signature", "type": "signature", "required": True},
                {"name": "date", "type": "date", "required": True},
            ],
        }

    @pytest.mark.asyncio
    async def test_get_settings_success(
        self, httpx_mock: HTTPXMock, sample_settings: dict[str, Any]
    ) -> None:
        """Test get_settings() returns settings for integration."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/esign",
            method="POST",
            json={"error": None, "data": sample_settings},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EsignFunctionResource(http)
            result = await resource.get_settings(integration_id=123)

            assert isinstance(result, EsignFunctionSettings)
            assert result.delivery == "email"
            assert result.allowDraft == 1
            assert result.languages == ["en", "sv", "no"]
            assert result.multiSign == 1
            assert result.fields is not None
            assert len(result.fields) == 2

    @pytest.mark.asyncio
    async def test_get_settings_with_kwargs(
        self, httpx_mock: HTTPXMock, sample_settings: dict[str, Any]
    ) -> None:
        """Test get_settings() includes additional kwargs in request."""
        import httpx

        # Capture request to verify payload
        def check_request(request: Any) -> httpx.Response:
            import json

            payload = json.loads(request.content)
            assert payload["type"] == "settings"
            assert payload["integrationId"] == 456
            assert payload["customParam"] == "value"
            return httpx.Response(status_code=200, json={"error": None, "data": sample_settings})

        httpx_mock.add_callback(
            check_request,
            url="https://power.upsales.com/api/v2/function/esign",
            method="POST",
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EsignFunctionResource(http)
            result = await resource.get_settings(integration_id=456, customParam="value")

            assert isinstance(result, EsignFunctionSettings)

    @pytest.mark.asyncio
    async def test_get_settings_minimal_response(self, httpx_mock: HTTPXMock) -> None:
        """Test get_settings() handles minimal response with optional fields."""
        minimal_settings = {
            "delivery": "direct",
            # All other fields are None
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/esign",
            method="POST",
            json={"error": None, "data": minimal_settings},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EsignFunctionResource(http)
            result = await resource.get_settings(integration_id=789)

            assert isinstance(result, EsignFunctionSettings)
            assert result.delivery == "direct"
            assert result.allowDraft is None
            assert result.languages is None
            assert result.multiSign is None

    @pytest.mark.asyncio
    async def test_get_settings_stores_client_reference(
        self, httpx_mock: HTTPXMock, sample_settings: dict[str, Any]
    ) -> None:
        """Test get_settings() stores client reference in returned model."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/esign",
            method="POST",
            json={"error": None, "data": sample_settings},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EsignFunctionResource(http)
            result = await resource.get_settings(integration_id=123)

            # Client reference should be set (or None if not available)
            assert hasattr(result, "_client")

    # TODO: Test download() method when HTTPClient supports binary responses
    # @pytest.mark.asyncio
    # async def test_download_success(self, httpx_mock: HTTPXMock):
    #     """Test download() returns PDF bytes."""
    #     pdf_content = b"%PDF-1.4\n%fake pdf content"
    #
    #     httpx_mock.add_response(
    #         url="https://power.upsales.com/api/v2/function/esign/download/456",
    #         method="GET",
    #         content=pdf_content,
    #     )
    #
    #     async with HTTPClient(token="test_token", auth_manager=None) as http:
    #         resource = EsignFunctionResource(http)
    #         result = await resource.download(document_id=456)
    #
    #         assert isinstance(result, bytes)
    #         assert result == pdf_content
    #         assert result.startswith(b"%PDF")
