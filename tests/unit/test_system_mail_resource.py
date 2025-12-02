"""Unit tests for system mail resource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.system_mail import SystemMailResponse
from upsales.resources.system_mail import SystemMailResource


@pytest.mark.asyncio
class TestSystemMailResource:
    """Test suite for SystemMailResource."""

    async def test_send_single_email(self, httpx_mock: HTTPXMock):
        """Test sending system mail to a single email address."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True, "message": "Email sent successfully"}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(
                template_name="verifyDomains",
                email="admin@example.com",
                additional={"domain": "example.com"},
            )

            # Assert
            assert isinstance(result, SystemMailResponse)
            assert result.success is True
            assert result.message == "Email sent successfully"

            # Verify request was made correctly
            request = httpx_mock.get_request()
            assert request.method == "POST"
            assert "/function/system-mail" in str(request.url)

    async def test_send_multiple_emails(self, httpx_mock: HTTPXMock):
        """Test sending system mail to multiple email addresses."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True, "message": "Emails sent successfully"}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(
                template_name="requestAddon",
                email=["admin@example.com", "support@example.com"],
                additional={"addon": "advanced-reporting"},
            )

            # Assert
            assert isinstance(result, SystemMailResponse)
            assert result.success is True

    async def test_send_without_additional_data(self, httpx_mock: HTTPXMock):
        """Test sending system mail without additional data."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True, "message": "Email sent"}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(template_name="installingScript", email="user@example.com")

            # Assert
            assert isinstance(result, SystemMailResponse)
            assert result.success is True

    async def test_send_installing_script_template(self, httpx_mock: HTTPXMock):
        """Test sending installingScript template."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(
                template_name="installingScript", email="developer@example.com"
            )

            # Assert
            assert result.success is True

    async def test_send_verify_domains_template(self, httpx_mock: HTTPXMock):
        """Test sending verifyDomains template."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(template_name="verifyDomains", email="admin@example.com")

            # Assert
            assert result.success is True

    async def test_send_request_addon_template(self, httpx_mock: HTTPXMock):
        """Test sending requestAddon template."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(template_name="requestAddon", email="sales@example.com")

            # Assert
            assert result.success is True

    async def test_send_with_complex_additional_data(self, httpx_mock: HTTPXMock):
        """Test sending with complex additional data structure."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)
            additional_data = {
                "domain": "example.com",
                "subdomain": "app.example.com",
                "verification_code": "ABC123",
                "expiry": "2025-12-31",
            }

            # Act
            result = await resource.send(
                template_name="verifyDomains", email="admin@example.com", additional=additional_data
            )

            # Assert
            assert result.success is True

    async def test_response_without_message(self, httpx_mock: HTTPXMock):
        """Test handling response without message field."""
        # Arrange
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/system-mail",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token") as http:
            resource = SystemMailResource(http)

            # Act
            result = await resource.send(template_name="verifyDomains", email="admin@example.com")

            # Assert
            assert result.success is True
            assert result.message is None
