"""Unit tests for import_mail_campaign_mail resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.models.import_mail_campaign_mail import (
    ImportMailCampaignMailRequest,
    ImportMailCampaignMailResponse,
)


@pytest.mark.asyncio
class TestImportMailCampaignMailResource:
    """Test suite for ImportMailCampaignMailResource."""

    async def test_import_mail_success(self, httpx_mock: HTTPXMock):
        """Test successful mail campaign mail import."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/import/mailcampaign/mail",
            json={"error": None, "data": {"success": True, "message": "Imported successfully"}},
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.import_mail_campaign_mail.import_mail(
                mail_campaign_id=12345, contact_ids=[1, 2, 3, 4, 5]
            )

            # Verify response
            assert isinstance(response, ImportMailCampaignMailResponse)
            assert response.success is True

    async def test_import_mail_with_request_object(self, httpx_mock: HTTPXMock):
        """Test importing mail using request object."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/import/mailcampaign/mail",
            json={"error": None, "data": {"success": True}},
        )

        async with Upsales(token="test_token") as upsales:
            request = ImportMailCampaignMailRequest(mailCampaignId=12345, contactIds=[1, 2, 3])
            response = await upsales.import_mail_campaign_mail.import_mail_from_request(request)

            # Verify response
            assert isinstance(response, ImportMailCampaignMailResponse)
            assert response.success is True

    async def test_import_mail_with_dict(self, httpx_mock: HTTPXMock):
        """Test importing mail using dictionary."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/import/mailcampaign/mail",
            json={"error": None, "data": {"success": True}},
        )

        async with Upsales(token="test_token") as upsales:
            request_dict = {"mailCampaignId": 12345, "contactIds": [1, 2, 3]}
            response = await upsales.import_mail_campaign_mail.import_mail_from_request(
                request_dict
            )

            # Verify response
            assert isinstance(response, ImportMailCampaignMailResponse)
            assert response.success is True

    async def test_import_mail_empty_contact_list(self, httpx_mock: HTTPXMock):
        """Test importing with empty contact list."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/import/mailcampaign/mail",
            json={"error": None, "data": {"success": True, "message": "No contacts to import"}},
        )

        async with Upsales(token="test_token") as upsales:
            response = await upsales.import_mail_campaign_mail.import_mail(
                mail_campaign_id=12345, contact_ids=[]
            )

            # Verify response
            assert isinstance(response, ImportMailCampaignMailResponse)
            assert response.success is True

    async def test_request_model_validation(self):
        """Test request model field validation."""
        # Valid request
        request = ImportMailCampaignMailRequest(mailCampaignId=123, contactIds=[1, 2, 3])
        assert request.mailCampaignId == 123
        assert request.contactIds == [1, 2, 3]

        # Test field serialization
        data = request.model_dump(mode="json")
        assert data["mailCampaignId"] == 123
        assert data["contactIds"] == [1, 2, 3]

    async def test_response_model_validation(self):
        """Test response model validation."""
        # Success response
        response = ImportMailCampaignMailResponse(success=True, message="All good")
        assert response.success is True
        assert response.message == "All good"

        # Default values
        response2 = ImportMailCampaignMailResponse()
        assert response2.success is True
        assert response2.message is None

    async def test_import_mail_request_payload(self, httpx_mock: HTTPXMock):
        """Test that request payload is correctly formatted."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/import/mailcampaign/mail",
            json={"error": None, "data": {"success": True}},
        )

        async with Upsales(token="test_token") as upsales:
            await upsales.import_mail_campaign_mail.import_mail(
                mail_campaign_id=999, contact_ids=[10, 20, 30]
            )

            # Verify request was made
            request = httpx_mock.get_request()
            assert request is not None
            assert request.method == "POST"

            # Verify payload structure
            import json

            content = json.loads(request.content)
            # Extract the actual payload from json wrapper if present
            payload = content.get("json", content)
            assert "mailCampaignId" in payload
            assert "contactIds" in payload
            assert payload["mailCampaignId"] == 999
            assert payload["contactIds"] == [10, 20, 30]
