"""
Tests for MailCampaignsResource.

Ensures complete CRUD coverage for mail campaigns endpoint.
"""

import re

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.mail_campaigns import MailCampaign, PartialMailCampaign
from upsales.resources.mail_campaigns import MailCampaignsResource


class TestMailCampaignsResourceCRUD:
    """Test CRUD operations for MailCampaignsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample mail campaign data for testing."""
        return {
            "id": 1,
            "name": "Q4 Product Launch",
            "subject": "Introducing Our New Product",
            "body": "<html><body>Check out our new product!</body></html>",
            "bodyJson": "{}",
            "from": "marketing@company.com",
            "fromName": "Marketing Team",
            "status": "SENT",
            "sendDate": "2025-11-01 10:00:00",
            "mailSent": 1000,
            "mailRead": 450,
            "mailClicked": 120,
            "mailError": 0,
            "mailPending": 0,
            "mailUnsub": 5,
            "project": {"id": 10, "name": "Q4 Campaign"},
            "segment": None,
            "segments": [],
            "isArchived": 0,
            "modDate": "2025-11-01 10:00:00",
            "version": 1,
            "jobId": 123,
            "template": {"id": 5, "name": "Product Launch Template"},
            "category": {"id": 2, "name": "Marketing"},
            "user": {"id": 1, "name": "Admin User", "email": "admin@company.com"},
            "attachments": [],
            "labels": [],
            "filter": None,
            "filterConfig": None,
            "socialEventId": None,
            "socialEventSendToStatus": None,
            "flowId": None,
            "externalId": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Holiday Sale", "status": "DRAFT"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a mail campaign."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            result = await resource.create(
                name="Q4 Product Launch",
                subject="Introducing Our New Product",
                body="<html><body>Check out our new product!</body></html>",
                **{"from": "marketing@company.com"},
                fromName="Marketing Team",
            )

            assert isinstance(result, MailCampaign)
            assert result.id == 1
            assert result.name == "Q4 Product Launch"
            assert result.from_email == "marketing@company.com"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single mail campaign."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            result = await resource.get(1)

            assert isinstance(result, MailCampaign)
            assert result.id == 1
            assert result.name == "Q4 Product Launch"
            assert result.status == "SENT"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing mail campaigns with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, MailCampaign) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a mail campaign."""
        updated_data = {**sample_data, "name": "Updated Campaign Name"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            result = await resource.update(1, name="Updated Campaign Name")

            assert isinstance(result, MailCampaign)
            assert result.id == 1
            assert result.name == "Updated Campaign Name"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a mail campaign."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mailCampaigns/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test searching mail campaigns with filters."""
        httpx_mock.add_response(
            url=re.compile(r".*status=SENT.*"),
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.search(status="SENT")

            assert len(results) == 1
            assert results[0].status == "SENT"


class TestMailCampaignsResourceCustomMethods:
    """Test custom methods specific to MailCampaignsResource."""

    @pytest.fixture
    def draft_campaign(self):
        """Sample draft campaign."""
        return {
            "id": 1,
            "name": "Draft Campaign",
            "subject": "Test Subject",
            "body": "<html><body>Test</body></html>",
            "bodyJson": "{}",
            "from": "test@company.com",
            "fromName": "Test",
            "status": "DRAFT",
            "sendDate": None,
            "mailSent": 0,
            "mailRead": 0,
            "mailClicked": 0,
            "mailError": 0,
            "mailPending": 0,
            "mailUnsub": 0,
            "project": None,
            "segment": None,
            "segments": [],
            "isArchived": 0,
            "modDate": None,
            "version": 1,
            "jobId": 0,
            "template": None,
            "category": None,
            "user": {"id": 1, "name": "User", "email": "user@company.com"},
            "attachments": [],
            "labels": [],
            "filter": None,
            "filterConfig": None,
            "socialEventId": None,
            "socialEventSendToStatus": None,
            "flowId": None,
            "externalId": None,
        }

    @pytest.fixture
    def sent_campaign(self, draft_campaign):
        """Sample sent campaign."""
        return {
            **draft_campaign,
            "id": 2,
            "status": "SENT",
            "mailSent": 1000,
            "mailRead": 450,
        }

    @pytest.fixture
    def archived_campaign(self, draft_campaign):
        """Sample archived campaign."""
        return {**draft_campaign, "id": 3, "isArchived": 1}

    @pytest.mark.asyncio
    async def test_get_drafts(self, httpx_mock: HTTPXMock, draft_campaign):
        """Test getting draft campaigns."""
        httpx_mock.add_response(
            url=re.compile(r".*status=DRAFT.*"),
            json={"error": None, "data": [draft_campaign]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.get_drafts()

            assert len(results) == 1
            assert results[0].status == "DRAFT"
            assert results[0].is_draft is True

    @pytest.mark.asyncio
    async def test_get_sent(self, httpx_mock: HTTPXMock, sent_campaign):
        """Test getting sent campaigns."""
        httpx_mock.add_response(
            url=re.compile(r".*status=SENT.*"),
            json={"error": None, "data": [sent_campaign]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.get_sent()

            assert len(results) == 1
            assert results[0].status == "SENT"
            assert results[0].is_sent is True

    @pytest.mark.asyncio
    async def test_get_archived(self, httpx_mock: HTTPXMock, archived_campaign):
        """Test getting archived campaigns."""
        httpx_mock.add_response(
            url=re.compile(r".*isArchived=1.*"),
            json={"error": None, "data": [archived_campaign]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailCampaignsResource(http)
            results = await resource.get_archived()

            assert len(results) == 1
            assert results[0].isArchived == 1
            assert results[0].is_archived is True


class TestMailCampaignModel:
    """Test MailCampaign model functionality."""

    @pytest.fixture
    def sample_data(self):
        """Sample mail campaign data."""
        return {
            "id": 1,
            "name": "Test Campaign",
            "subject": "Test Subject",
            "body": "<html><body>Test</body></html>",
            "bodyJson": "{}",
            "from": "test@company.com",
            "fromName": "Test User",
            "status": "SENT",
            "sendDate": "2025-11-01 10:00:00",
            "mailSent": 1000,
            "mailRead": 450,
            "mailClicked": 120,
            "mailError": 10,
            "mailPending": 0,
            "mailUnsub": 5,
            "project": None,
            "segment": None,
            "segments": [],
            "isArchived": 1,
            "modDate": "2025-11-01 10:00:00",
            "version": 1,
            "jobId": 123,
            "template": None,
            "category": None,
            "user": {"id": 1, "name": "User", "email": "user@company.com"},
            "attachments": [],
            "labels": [],
            "filter": None,
            "filterConfig": None,
            "socialEventId": None,
            "socialEventSendToStatus": None,
            "flowId": None,
            "externalId": None,
        }

    def test_mail_campaign_model_creation(self, sample_data):
        """Test creating MailCampaign model from data."""
        campaign = MailCampaign(**sample_data)

        assert campaign.id == 1
        assert campaign.name == "Test Campaign"
        assert campaign.from_email == "test@company.com"  # Field alias test

    def test_computed_field_is_archived(self, sample_data):
        """Test is_archived computed field."""
        campaign = MailCampaign(**sample_data)
        assert campaign.is_archived is True

        campaign.isArchived = 0
        assert campaign.is_archived is False

    def test_computed_field_is_draft(self, sample_data):
        """Test is_draft computed field."""
        campaign = MailCampaign(**sample_data)
        assert campaign.is_draft is False

        sample_data["status"] = "DRAFT"
        draft_campaign = MailCampaign(**sample_data)
        assert draft_campaign.is_draft is True

    def test_computed_field_is_sent(self, sample_data):
        """Test is_sent computed field."""
        campaign = MailCampaign(**sample_data)
        assert campaign.is_sent is True

        sample_data["status"] = "DRAFT"
        draft_campaign = MailCampaign(**sample_data)
        assert draft_campaign.is_sent is False

    def test_computed_field_open_rate(self, sample_data):
        """Test open_rate computed field."""
        campaign = MailCampaign(**sample_data)
        # 450 / 1000 * 100 = 45.0
        assert campaign.open_rate == 45.0

        # Test with zero sent emails
        sample_data["mailSent"] = 0
        zero_campaign = MailCampaign(**sample_data)
        assert zero_campaign.open_rate == 0.0

    def test_computed_field_click_rate(self, sample_data):
        """Test click_rate computed field."""
        campaign = MailCampaign(**sample_data)
        # 120 / 1000 * 100 = 12.0
        assert campaign.click_rate == 12.0

        # Test with zero sent emails
        sample_data["mailSent"] = 0
        zero_campaign = MailCampaign(**sample_data)
        assert zero_campaign.click_rate == 0.0

    def test_frozen_fields(self, sample_data):
        """Test that frozen fields cannot be modified."""
        campaign = MailCampaign(**sample_data)

        # These should raise ValidationError
        with pytest.raises(Exception):  # Pydantic ValidationError
            campaign.id = 999

        with pytest.raises(Exception):
            campaign.status = "DRAFT"

        with pytest.raises(Exception):
            campaign.mailSent = 500

    def test_to_api_dict_excludes_frozen(self, sample_data):
        """Test that to_api_dict excludes frozen fields."""
        campaign = MailCampaign(**sample_data)
        api_dict = campaign.to_api_dict(name="Updated Name")

        # Frozen fields should not be included
        assert "id" not in api_dict
        assert "status" not in api_dict
        assert "mailSent" not in api_dict
        assert "mailRead" not in api_dict
        assert "mailClicked" not in api_dict

        # Updated field should be included
        assert api_dict["name"] == "Updated Name"


class TestPartialMailCampaignModel:
    """Test PartialMailCampaign model functionality."""

    def test_partial_mail_campaign_creation(self):
        """Test creating PartialMailCampaign."""
        partial = PartialMailCampaign(id=1, name="Test Campaign")

        assert partial.id == 1
        assert partial.name == "Test Campaign"

    def test_partial_mail_campaign_minimal_data(self):
        """Test PartialMailCampaign with minimal required fields."""
        partial = PartialMailCampaign(id=1, name="Test")

        assert partial.id == 1
        assert partial.name == "Test"
