"""Unit tests for ImageComposeResource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.models.image_compose import ImageComposeResponse


@pytest.mark.asyncio
class TestImageComposeResource:
    """Test suite for ImageComposeResource."""

    async def test_compose_success(self, httpx_mock: HTTPXMock):
        """Test composing an image with YouTube play button."""
        # Mock the API response
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/image/compose",
            method="POST",
            json={
                "error": None,
                "data": {
                    "url": "https://example.com/composed_image.jpg",
                    "path": "/uploads/composed_image.jpg",
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.image_compose.compose(
                sourcepath="/uploads/video_thumbnail.jpg",
                composition="addYouTubePlayButton",
            )

            assert isinstance(result, ImageComposeResponse)
            assert result.url == "https://example.com/composed_image.jpg"
            assert result.path == "/uploads/composed_image.jpg"

    async def test_compose_with_minimal_response(self, httpx_mock: HTTPXMock):
        """Test composing with minimal response fields."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/image/compose",
            method="POST",
            json={
                "error": None,
                "data": {
                    "url": "https://example.com/image.jpg",
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.image_compose.compose(
                sourcepath="/path/to/image.jpg", composition="addYouTubePlayButton"
            )

            assert isinstance(result, ImageComposeResponse)
            assert result.url == "https://example.com/image.jpg"
            assert result.path is None

    async def test_compose_request_parameters(self, httpx_mock: HTTPXMock):
        """Test that compose sends correct request parameters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/image/compose",
            method="POST",
            json={"error": None, "data": {"url": "https://example.com/test.jpg"}},
        )

        async with Upsales(token="test_token") as upsales:
            await upsales.image_compose.compose(
                sourcepath="/test/path.jpg", composition="addYouTubePlayButton"
            )

            # Verify request was made with correct parameters
            request = httpx_mock.get_request()
            assert request is not None
            assert request.method == "POST"
            assert "/image/compose" in str(request.url)
