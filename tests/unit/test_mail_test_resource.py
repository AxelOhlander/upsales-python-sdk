"""Unit tests for MailTestResource."""

from unittest.mock import AsyncMock

import pytest

from upsales.exceptions import ValidationError
from upsales.models.mail_test import MailTestResponse
from upsales.resources.mail_test import MailTestResource


class TestMailTestResource:
    """Test suite for MailTestResource."""

    @pytest.fixture
    def http_client(self):
        """Create a mock HTTP client."""
        mock = AsyncMock()
        mock.request = AsyncMock()
        return mock

    @pytest.fixture
    def resource(self, http_client):
        """Create MailTestResource instance."""
        return MailTestResource(http_client)

    @pytest.mark.asyncio
    async def test_send_success_minimal(self, resource, http_client):
        """Test sending test email with minimal required fields."""
        # Arrange
        http_client.request.return_value = {"success": True}

        # Act
        response = await resource.send(client=123, contact=456)

        # Assert
        assert isinstance(response, MailTestResponse)
        assert response.success is True
        http_client.request.assert_called_once_with(
            "POST",
            "/mail/test",
            json={"client": 123, "contact": 456},
        )

    @pytest.mark.asyncio
    async def test_send_success_all_fields(self, resource, http_client):
        """Test sending test email with all fields."""
        # Arrange
        http_client.request.return_value = {"success": True, "message": "Email sent"}

        # Act
        response = await resource.send(
            client=123,
            contact=456,
            subject="Test Subject",
            body="Test Body",
            to="test@example.com",
            from_address="sender@example.com",
            from_name="Test Sender",
        )

        # Assert
        assert isinstance(response, MailTestResponse)
        assert response.success is True
        assert response.message == "Email sent"
        http_client.request.assert_called_once_with(
            "POST",
            "/mail/test",
            json={
                "client": 123,
                "contact": 456,
                "subject": "Test Subject",
                "body": "Test Body",
                "to": "test@example.com",
                "from": "sender@example.com",  # Note: API uses 'from' not 'from_address'
                "fromName": "Test Sender",
            },
        )

    @pytest.mark.asyncio
    async def test_send_missing_client(self, resource):
        """Test sending test email without client ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Both 'client' and 'contact' are required"):
            await resource.send(client=0, contact=456)

    @pytest.mark.asyncio
    async def test_send_missing_contact(self, resource):
        """Test sending test email without contact ID raises ValidationError."""
        with pytest.raises(ValidationError, match="Both 'client' and 'contact' are required"):
            await resource.send(client=123, contact=0)

    @pytest.mark.asyncio
    async def test_send_missing_both(self, resource):
        """Test sending test email without both required fields raises ValidationError."""
        with pytest.raises(ValidationError, match="Both 'client' and 'contact' are required"):
            await resource.send(client=0, contact=0)

    @pytest.mark.asyncio
    async def test_send_non_dict_response(self, resource, http_client):
        """Test sending test email with non-dict API response."""
        # Arrange
        http_client.request.return_value = "OK"

        # Act
        response = await resource.send(client=123, contact=456)

        # Assert
        assert isinstance(response, MailTestResponse)
        assert response.success is True
        assert response.message == "OK"

    @pytest.mark.asyncio
    async def test_send_with_subject_only(self, resource, http_client):
        """Test sending test email with subject but no body."""
        # Arrange
        http_client.request.return_value = {"success": True}

        # Act
        response = await resource.send(
            client=123,
            contact=456,
            subject="Test Subject",
        )

        # Assert
        assert isinstance(response, MailTestResponse)
        http_client.request.assert_called_once_with(
            "POST",
            "/mail/test",
            json={
                "client": 123,
                "contact": 456,
                "subject": "Test Subject",
            },
        )

    @pytest.mark.asyncio
    async def test_send_with_to_only(self, resource, http_client):
        """Test sending test email with 'to' address only."""
        # Arrange
        http_client.request.return_value = {"success": True}

        # Act
        response = await resource.send(
            client=123,
            contact=456,
            to="recipient@example.com",
        )

        # Assert
        assert isinstance(response, MailTestResponse)
        http_client.request.assert_called_once_with(
            "POST",
            "/mail/test",
            json={
                "client": 123,
                "contact": 456,
                "to": "recipient@example.com",
            },
        )

    @pytest.mark.asyncio
    async def test_send_preserves_none_values(self, resource, http_client):
        """Test that None values are not included in the payload."""
        # Arrange
        http_client.request.return_value = {"success": True}

        # Act
        response = await resource.send(
            client=123,
            contact=456,
            subject=None,  # Explicitly None
            body=None,
        )

        # Assert
        assert isinstance(response, MailTestResponse)
        # Verify that None values are not in the payload
        call_args = http_client.request.call_args
        payload = call_args.kwargs["json"]
        assert "subject" not in payload
        assert "body" not in payload
        assert payload == {"client": 123, "contact": 456}
