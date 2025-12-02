"""Unit tests for MailMultiResource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.client import Upsales
from upsales.models.mail_multi import MailMultiResponse


@pytest.mark.asyncio
class TestMailMultiResource:
    """Test suite for MailMultiResource."""

    async def test_send_batch_success(self, httpx_mock: HTTPXMock):
        """Test sending batch of emails successfully."""
        # Mock API response
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/multi",
            method="POST",
            json={
                "error": None,
                "data": {
                    "success": True,
                    "results": [
                        {"id": 1, "status": "sent"},
                        {"id": 2, "status": "sent"},
                    ],
                    "errors": [],
                    "total_sent": 2,
                    "total_failed": 0,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.mail_multi.send_batch(
                [
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 123,
                        "contactId": 456,
                        "subject": "Email 1",
                        "body": "<p>Content 1</p>",
                        "to": "customer1@example.com",
                        "from_address": "sales@company.com",
                        "fromName": "Sales Team",
                    },
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 789,
                        "contactId": 101,
                        "subject": "Email 2",
                        "body": "<p>Content 2</p>",
                        "to": "customer2@example.com",
                        "from_address": "sales@company.com",
                        "fromName": "Sales Team",
                    },
                ]
            )

        assert isinstance(response, MailMultiResponse)
        assert response.success is True
        assert response.total_sent == 2
        assert response.total_failed == 0
        assert len(response.results) == 2
        assert len(response.errors) == 0

    async def test_send_batch_with_failures(self, httpx_mock: HTTPXMock):
        """Test sending batch with some failures."""
        # Mock API response with partial failures
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/multi",
            method="POST",
            json={
                "error": None,
                "data": {
                    "success": False,
                    "results": [{"id": 1, "status": "sent"}],
                    "errors": [{"index": 1, "error": "Invalid email address"}],
                    "total_sent": 1,
                    "total_failed": 1,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.mail_multi.send_batch(
                [
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 123,
                        "subject": "Valid Email",
                        "body": "<p>Content</p>",
                        "to": "valid@example.com",
                        "from_address": "sales@company.com",
                        "fromName": "Sales",
                    },
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 456,
                        "subject": "Invalid Email",
                        "body": "<p>Content</p>",
                        "to": "invalid-email",
                        "from_address": "sales@company.com",
                        "fromName": "Sales",
                    },
                ]
            )

        assert isinstance(response, MailMultiResponse)
        assert response.success is False
        assert response.total_sent == 1
        assert response.total_failed == 1
        assert len(response.errors) == 1

    async def test_send_batch_empty_list_raises_error(self):
        """Test that empty email list raises ValueError."""
        async with Upsales(token="test_token") as upsales:
            with pytest.raises(ValueError, match="Cannot send empty batch of emails"):
                await upsales.mail_multi.send_batch([])

    async def test_send_batch_with_cc_and_bcc(self, httpx_mock: HTTPXMock):
        """Test sending batch with CC and BCC recipients."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/multi",
            method="POST",
            json={
                "error": None,
                "data": {
                    "success": True,
                    "results": [{"id": 1, "status": "sent"}],
                    "errors": [],
                    "total_sent": 1,
                    "total_failed": 0,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.mail_multi.send_batch(
                [
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 123,
                        "subject": "Email with CC/BCC",
                        "body": "<p>Content</p>",
                        "to": "primary@example.com",
                        "cc": ["cc1@example.com", "cc2@example.com"],
                        "bcc": ["bcc@example.com"],
                        "from_address": "sales@company.com",
                        "fromName": "Sales Team",
                    }
                ]
            )

        assert response.success is True
        assert response.total_sent == 1

    async def test_send_batch_with_attachments(self, httpx_mock: HTTPXMock):
        """Test sending batch with attachments."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/multi",
            method="POST",
            json={
                "error": None,
                "data": {
                    "success": True,
                    "results": [{"id": 1, "status": "sent"}],
                    "errors": [],
                    "total_sent": 1,
                    "total_failed": 0,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.mail_multi.send_batch(
                [
                    {
                        "date": "2025-01-01",
                        "type": "out",
                        "clientId": 123,
                        "subject": "Email with Attachment",
                        "body": "<p>See attached</p>",
                        "to": "customer@example.com",
                        "from_address": "sales@company.com",
                        "fromName": "Sales",
                        "attachments": [{"filename": "document.pdf", "content": "base64data"}],
                    }
                ]
            )

        assert response.success is True
        assert response.total_sent == 1

    async def test_send_batch_request_payload(self, httpx_mock: HTTPXMock):
        """Test that the request payload is correctly formatted."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/multi",
            method="POST",
            json={
                "error": None,
                "data": {
                    "success": True,
                    "results": [],
                    "errors": [],
                    "total_sent": 0,
                    "total_failed": 0,
                },
            },
        )

        test_emails = [
            {
                "date": "2025-01-01",
                "type": "out",
                "subject": "Test",
                "body": "<p>Test</p>",
                "to": "test@example.com",
                "from_address": "sales@company.com",
                "fromName": "Sales",
            }
        ]

        async with Upsales(token="test_token") as upsales:
            await upsales.mail_multi.send_batch(test_emails)

        # Verify the request was made with correct structure
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert "array" in request.content.decode()
