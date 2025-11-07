"""
Tests for MailResource.

Ensures complete CRUD coverage for mail endpoint.
"""

import re

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.mail import Mail, PartialMail
from upsales.resources.mail import MailResource


class TestMailResourceCRUD:
    """Test CRUD operations for MailResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample mail data for testing."""
        return {
            "id": 1,
            "subject": "Meeting follow-up",
            "body": "Thank you for the meeting today.",
            "to": "client@example.com",
            "from": "sales@company.com",
            "fromName": "Sales Team",
            "date": "2025-11-03T10:00:00Z",
            "modDate": "2025-11-03T10:00:00Z",
            "type": "sent",
            "isMap": 0,
            "cc": [],
            "bcc": [],
            "recipients": {},
            "attachments": [],
            "mailBodySnapshotId": 123,
            "mailThreadId": 456,
            "threadId": "thread-789",
            "groupMailId": 1,
            "thread": {},
            "externalMailId": "ext-123",
            "internetMessageId": "<msg-id@example.com>",
            "client": {"id": 10, "name": "ACME Corp"},
            "contact": {"id": 5, "name": "John Doe"},
            "activity": None,
            "opportunity": None,
            "project": None,
            "appointment": None,
            "template": None,
            "users": [],
            "userEditable": True,
            "userRemovable": True,
            "events": [],
            "lastReadDate": None,
            "lastClickDate": None,
            "lastEventDate": None,
            "errorCause": None,
            "jobId": 789,
            "tags": [],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "subject": "Project update"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a mail."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            result = await resource.create(
                subject="Meeting follow-up",
                body="Thank you for the meeting today.",
                to="client@example.com",
                **{"from": "sales@company.com"},
            )

            assert isinstance(result, Mail)
            assert result.id == 1
            assert result.subject == "Meeting follow-up"
            assert result.from_ == "sales@company.com"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single mail."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            result = await resource.get(1)

            assert isinstance(result, Mail)
            assert result.id == 1
            assert result.subject == "Meeting follow-up"
            assert result.type == "sent"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing mails with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, Mail) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a mail."""
        updated_data = {**sample_data, "subject": "Updated subject"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            result = await resource.update(1, subject="Updated subject")

            assert isinstance(result, Mail)
            assert result.id == 1
            assert result.subject == "Updated subject"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a mail."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test searching mails with filters."""
        httpx_mock.add_response(
            url=re.compile(r".*type=sent.*"),
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.search(type="sent")

            assert len(results) == 1
            assert results[0].type == "sent"


class TestMailResourceCustomMethods:
    """Test custom methods specific to MailResource."""

    @pytest.fixture
    def sent_mail(self):
        """Sample sent mail."""
        return {
            "id": 1,
            "subject": "Meeting follow-up",
            "body": "Thank you",
            "to": "client@example.com",
            "from": "sales@company.com",
            "fromName": "Sales Team",
            "date": "2025-11-03T10:00:00Z",
            "modDate": "2025-11-03T10:00:00Z",
            "type": "sent",
            "isMap": 0,
            "cc": [],
            "bcc": [],
            "recipients": {},
            "attachments": [],
            "mailBodySnapshotId": 123,
            "mailThreadId": 456,
            "threadId": None,
            "groupMailId": 1,
            "thread": {},
            "externalMailId": None,
            "internetMessageId": None,
            "client": None,
            "contact": None,
            "activity": None,
            "opportunity": None,
            "project": None,
            "appointment": None,
            "template": None,
            "users": [],
            "userEditable": True,
            "userRemovable": True,
            "events": [],
            "lastReadDate": None,
            "lastClickDate": None,
            "lastEventDate": None,
            "errorCause": None,
            "jobId": 789,
            "tags": [],
        }

    @pytest.fixture
    def received_mail(self, sent_mail):
        """Sample received mail."""
        return {**sent_mail, "id": 2, "type": "received"}

    @pytest.fixture
    def draft_mail(self, sent_mail):
        """Sample draft mail."""
        return {**sent_mail, "id": 3, "type": "draft"}

    @pytest.fixture
    def map_mail(self, sent_mail):
        """Sample MAP email."""
        return {**sent_mail, "id": 4, "isMap": 1}

    @pytest.mark.asyncio
    async def test_get_sent(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting sent emails."""
        httpx_mock.add_response(
            url=re.compile(r".*type=sent.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_sent()

            assert len(results) == 1
            assert results[0].type == "sent"

    @pytest.mark.asyncio
    async def test_get_received(self, httpx_mock: HTTPXMock, received_mail):
        """Test getting received emails."""
        httpx_mock.add_response(
            url=re.compile(r".*type=received.*"),
            json={"error": None, "data": [received_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_received()

            assert len(results) == 1
            assert results[0].type == "received"

    @pytest.mark.asyncio
    async def test_get_drafts(self, httpx_mock: HTTPXMock, draft_mail):
        """Test getting draft emails."""
        httpx_mock.add_response(
            url=re.compile(r".*type=draft.*"),
            json={"error": None, "data": [draft_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_drafts()

            assert len(results) == 1
            assert results[0].type == "draft"

    @pytest.mark.asyncio
    async def test_get_map_emails(self, httpx_mock: HTTPXMock, map_mail):
        """Test getting MAP emails."""
        httpx_mock.add_response(
            url=re.compile(r".*isMap=1.*"),
            json={"error": None, "data": [map_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_map_emails()

            assert len(results) == 1
            assert results[0].is_map_email is True

    @pytest.mark.asyncio
    async def test_get_by_company(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails by company."""
        httpx_mock.add_response(
            url=re.compile(r".*client\.id=10.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_by_company(10)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_contact(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails by contact."""
        httpx_mock.add_response(
            url=re.compile(r".*contact\.id=5.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_by_contact(5)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_opportunity(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails by opportunity."""
        httpx_mock.add_response(
            url=re.compile(r".*opportunity\.id=7.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_by_opportunity(7)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_thread(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails in a thread."""
        httpx_mock.add_response(
            url=re.compile(r".*mailThreadId=456.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_by_thread(456)

            assert len(results) == 1
            assert results[0].mailThreadId == 456

    @pytest.mark.asyncio
    async def test_get_recent(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting recent emails."""
        httpx_mock.add_response(
            url=re.compile(r".*date=.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_recent(days=7)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_with_attachments(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails with attachments."""
        mail_with_attachment = {**sent_mail, "attachments": [{"id": 1, "name": "file.pdf"}]}
        httpx_mock.add_response(
            url=re.compile(r".*/mail\?limit=100&offset=0.*"),
            json={"error": None, "data": [mail_with_attachment, sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_with_attachments()

            assert len(results) == 1
            assert results[0].has_attachments is True

    @pytest.mark.asyncio
    async def test_get_with_tracking(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting emails with tracking events."""
        mail_with_events = {**sent_mail, "events": [{"type": "opened", "date": "2025-11-03"}]}
        httpx_mock.add_response(
            url=re.compile(r".*/mail\?limit=100&offset=0.*"),
            json={"error": None, "data": [mail_with_events, sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_with_tracking()

            assert len(results) == 1
            assert results[0].has_tracking_events is True

    @pytest.mark.asyncio
    async def test_search_by_subject(self, httpx_mock: HTTPXMock, sent_mail):
        """Test searching emails by subject."""
        httpx_mock.add_response(
            url=re.compile(r".*/mail\?limit=100&offset=0.*"),
            json={"error": None, "data": [sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.search_by_subject("meeting")

            assert len(results) == 1
            assert "meeting" in results[0].subject.lower()

    @pytest.mark.asyncio
    async def test_get_failed(self, httpx_mock: HTTPXMock, sent_mail):
        """Test getting failed emails."""
        failed_mail = {**sent_mail, "errorCause": "SMTP error"}
        httpx_mock.add_response(
            url=re.compile(r".*/mail\?limit=100&offset=0.*"),
            json={"error": None, "data": [failed_mail, sent_mail]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailResource(http)
            results = await resource.get_failed()

            assert len(results) == 1
            assert results[0].errorCause is not None


class TestMailModel:
    """Test Mail model functionality."""

    @pytest.fixture
    def sample_data(self):
        """Sample mail data."""
        return {
            "id": 1,
            "subject": "Test",
            "body": "Body",
            "to": "to@example.com",
            "from": "from@example.com",
            "fromName": "From Name",
            "date": "2025-11-03T10:00:00Z",
            "modDate": "2025-11-03T10:00:00Z",
            "type": "sent",
            "isMap": 1,
            "cc": [],
            "bcc": [],
            "recipients": {},
            "attachments": [{"id": 1}],
            "mailBodySnapshotId": 123,
            "mailThreadId": 456,
            "threadId": None,
            "groupMailId": 1,
            "thread": {},
            "externalMailId": None,
            "internetMessageId": None,
            "client": None,
            "contact": None,
            "activity": None,
            "opportunity": None,
            "project": None,
            "appointment": None,
            "template": None,
            "users": [],
            "userEditable": True,
            "userRemovable": True,
            "events": [{"type": "opened"}],
            "lastReadDate": None,
            "lastClickDate": None,
            "lastEventDate": None,
            "errorCause": None,
            "jobId": 789,
            "tags": [],
        }

    def test_mail_model_creation(self, sample_data):
        """Test creating Mail model from data."""
        mail = Mail(**sample_data)

        assert mail.id == 1
        assert mail.subject == "Test"
        assert mail.from_ == "from@example.com"  # Field alias test

    def test_computed_field_is_map_email(self, sample_data):
        """Test is_map_email computed field."""
        mail = Mail(**sample_data)
        assert mail.is_map_email is True

        mail.isMap = 0
        assert mail.is_map_email is False

    def test_computed_field_has_attachments(self, sample_data):
        """Test has_attachments computed field."""
        mail = Mail(**sample_data)
        assert mail.has_attachments is True

        mail.attachments = []
        assert mail.has_attachments is False

    def test_computed_field_has_tracking_events(self, sample_data):
        """Test has_tracking_events computed field."""
        mail = Mail(**sample_data)
        assert mail.has_tracking_events is True

        mail.events = []
        assert mail.has_tracking_events is False

    def test_frozen_fields(self, sample_data):
        """Test that frozen fields cannot be modified."""
        mail = Mail(**sample_data)

        # These should raise ValidationError
        with pytest.raises(Exception):  # Pydantic ValidationError
            mail.id = 999

        with pytest.raises(Exception):
            mail.date = "2025-12-01"

    def test_to_api_dict_excludes_frozen(self, sample_data):
        """Test that to_api_dict excludes frozen fields."""
        mail = Mail(**sample_data)
        api_dict = mail.to_api_dict(subject="Updated")

        # Frozen fields should not be included
        assert "id" not in api_dict
        assert "date" not in api_dict
        assert "modDate" not in api_dict

        # Updated field should be included
        assert api_dict["subject"] == "Updated"


class TestPartialMailModel:
    """Test PartialMail model functionality."""

    def test_partial_mail_creation(self):
        """Test creating PartialMail."""
        partial = PartialMail(id=1, subject="Test", type="sent")

        assert partial.id == 1
        assert partial.subject == "Test"
        assert partial.type == "sent"

    def test_partial_mail_optional_fields(self):
        """Test PartialMail with minimal data."""
        partial = PartialMail(id=1)

        assert partial.id == 1
        assert partial.subject is None
        assert partial.type is None
