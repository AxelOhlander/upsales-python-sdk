"""Unit tests for ValidatePage resource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.models.validate_page import ValidatePageResponse


@pytest.mark.asyncio
class TestValidatePageResource:
    """Test suite for ValidatePageResource."""

    async def test_validate_success(self, httpx_mock: HTTPXMock):
        """Test successful page validation."""
        # Mock successful validation
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/function/validatePage",
            json={
                "data": {"valid": True, "message": "Tracking script found"},
                "error": None,
            },
        )

        async with Upsales(token="test-token") as upsales:
            result = await upsales.validate_page.validate("https://example.com")

            assert isinstance(result, ValidatePageResponse)
            assert result.valid is True
            assert result.message == "Tracking script found"

    async def test_validate_failure(self, httpx_mock: HTTPXMock):
        """Test failed page validation."""
        # Mock failed validation
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/function/validatePage",
            json={
                "data": {"valid": False, "message": "Tracking script not found"},
                "error": None,
            },
        )

        async with Upsales(token="test-token") as upsales:
            result = await upsales.validate_page.validate("https://example.com")

            assert isinstance(result, ValidatePageResponse)
            assert result.valid is False
            assert result.message == "Tracking script not found"

    async def test_validate_request_body(self, httpx_mock: HTTPXMock):
        """Test that request body contains URL."""
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/function/validatePage",
            json={
                "data": {"valid": True, "message": None},
                "error": None,
            },
        )

        async with Upsales(token="test-token") as upsales:
            await upsales.validate_page.validate("https://example.com")

            # Check the request was made with correct body
            request = httpx_mock.get_request()
            assert request.method == "POST"
            assert (
                b'"url":"https://example.com"' in request.content
                or b'"url": "https://example.com"' in request.content
            )

    async def test_validate_different_urls(self, httpx_mock: HTTPXMock):
        """Test validation with different URLs."""
        test_urls = [
            "https://example.com",
            "https://example.com/page",
            "http://subdomain.example.com",
        ]

        for _ in test_urls:
            httpx_mock.add_response(
                method="POST",
                url="https://power.upsales.com/api/v2/function/validatePage",
                json={
                    "data": {"valid": True, "message": "OK"},
                    "error": None,
                },
            )

        async with Upsales(token="test-token") as upsales:
            for url in test_urls:
                result = await upsales.validate_page.validate(url)
                assert result.valid is True

    async def test_validate_with_none_message(self, httpx_mock: HTTPXMock):
        """Test validation when message is None."""
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/function/validatePage",
            json={
                "data": {"valid": True, "message": None},
                "error": None,
            },
        )

        async with Upsales(token="test-token") as upsales:
            result = await upsales.validate_page.validate("https://example.com")

            assert result.valid is True
            assert result.message is None
