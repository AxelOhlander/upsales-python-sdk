"""Unit tests for MailEditorResource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.mail_editor import MailEditorToken
from upsales.resources.mail_editor import MailEditorResource


class TestMailEditorResource:
    """Test suite for MailEditorResource."""

    @pytest.fixture
    def sample_token(self):
        """Sample BEE mail editor token response."""
        return {
            "access_token": "bee_token_abc123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    @pytest.mark.asyncio
    async def test_authenticate_success(self, httpx_mock: HTTPXMock, sample_token):
        """Test successful authentication with BEE mail editor."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/mailEditor",
            method="POST",
            json={"error": None, "data": sample_token},
        )

        # Act
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailEditorResource(http)
            result = await resource.authenticate()

        # Assert
        assert isinstance(result, MailEditorToken)
        assert result.access_token == "bee_token_abc123"
        assert result.token_type == "Bearer"
        assert result.expires_in == 3600

    @pytest.mark.asyncio
    async def test_authenticate_with_different_token_types(self, httpx_mock: HTTPXMock):
        """Test authentication with different token type values."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/mailEditor",
            method="POST",
            json={
                "error": None,
                "data": {
                    "access_token": "custom_token",
                    "token_type": "Custom",
                    "expires_in": 7200,
                },
            },
        )

        # Act
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailEditorResource(http)
            result = await resource.authenticate()

        # Assert
        assert result.token_type == "Custom"
        assert result.expires_in == 7200
        assert result.access_token == "custom_token"

    @pytest.mark.asyncio
    async def test_authenticate_validates_response(self, httpx_mock: HTTPXMock):
        """Test that authenticate validates the response structure."""
        # Arrange - missing required fields
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/mailEditor",
            method="POST",
            json={
                "error": None,
                "data": {
                    "access_token": "token",
                    # Missing token_type and expires_in
                },
            },
        )

        # Act & Assert
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailEditorResource(http)
            with pytest.raises(Exception):  # Pydantic validation error
                await resource.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_endpoint_path(self, httpx_mock: HTTPXMock, sample_token):
        """Test that authenticate calls the correct endpoint path."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/mailEditor",
            method="POST",
            json={"error": None, "data": sample_token},
        )

        # Act
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailEditorResource(http)
            await resource.authenticate()

        # Assert - verify the request was made
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert "/function/mailEditor" in str(request.url)
