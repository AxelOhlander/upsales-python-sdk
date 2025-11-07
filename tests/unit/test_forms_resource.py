"""
Unit tests for FormsResource.

Tests CRUD operations and custom methods for the forms endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.forms import Form
from upsales.resources.forms import FormsResource


class TestFormsResourceCRUD:
    """Test CRUD operations for FormsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample form data for testing."""
        return {
            "id": 1,
            "title": "Contact Us",
            "name": "contact_form",
            "internalName": "",
            "description": "Fill out the form and we'll contact you",
            "landingPage": "",
            "buttonText": "Submit",
            "thankYouTitle": "Thank you",
            "thankYouTitleOnDemand": "Thank you",
            "thankYouText": "We'll contact you soon.",
            "thankYouTextOnDemand": "We'll contact you soon.",
            "formType": None,
            "supportEmailId": None,
            "buttonBgColor": "#000000",
            "buttonTextColor": "#ffffff",
            "backgroundColor": "#ffffff",
            "backgroundColorOnDemand": "",
            "textColor": "#000000",
            "linkColor": "#4A90E2",
            "user": {
                "name": "Test User",
                "id": 1,
                "role": {"name": "admin", "id": 1},
                "email": "test@example.com",
            },
            "score": 40,
            "views": 150,
            "redirect": 0,
            "showTitle": 1,
            "regDate": "2025-05-17T04:31:51Z",
            "modDate": "2025-05-17T04:48:01.000Z",
            "fields": [
                {
                    "name": "Contact.email",
                    "title": "Email",
                    "required": True,
                    "datatype": "text",
                    "options": "",
                    "sort": 1,
                    "placeholder": "",
                    "info": "",
                    "language": None,
                    "formId": 1,
                }
            ],
            "actions": [],
            "uuid": "test-uuid-123",
            "submits": 42,
            "lastSubmitDate": "2025-05-20T10:30:00.000Z",
            "userRemovable": True,
            "userEditable": True,
            "landingPageBody": None,
            "html": "<!doctype html><html>...</html>",
            "isArchived": 0,
            "socialMediaTags": "{}",
            "brandId": 1,
            "labels": [],
            "projects": [],
            "thankYouElement": None,
            "thankYouElementOnDemand": None,
            "socialEventId": None,
            "domain": None,
            "urlName": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "newsletter_form", "submits": 0},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a form."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.create(
                title="Contact Us", name="contact_form", buttonText="Submit"
            )

            assert isinstance(result, Form)
            assert result.id == 1
            assert result.title == "Contact Us"
            assert not result.is_archived

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single form."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Form)
            assert result.id == 1
            assert result.title == "Contact Us"
            assert result.submission_count == 42
            assert result.has_submissions

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing forms."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            results = await resource.list()

            assert len(results) == 2
            assert all(isinstance(f, Form) for f in results)
            assert results[0].id == 1
            assert results[1].id == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a form."""
        updated_data = {**sample_data, "title": "Updated Title"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.update(1, title="Updated Title")

            assert isinstance(result, Form)
            assert result.id == 1
            assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a form."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            await resource.delete(1)


class TestFormsResourceCustomMethods:
    """Test custom methods for FormsResource."""

    @pytest.fixture
    def sample_forms(self):
        """Sample forms for testing."""
        base_user = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "role": {"id": 1, "name": "admin"},
        }
        return [
            {
                "id": 1,
                "title": "Active Form",
                "name": "active_form",
                "internalName": "",
                "description": "",
                "buttonText": "Submit",
                "thankYouTitle": "Thanks",
                "thankYouTitleOnDemand": "Thanks",
                "thankYouText": "",
                "thankYouTextOnDemand": "",
                "buttonBgColor": "#000000",
                "buttonTextColor": "#ffffff",
                "backgroundColor": "#ffffff",
                "backgroundColorOnDemand": "",
                "textColor": "#000000",
                "linkColor": "#4A90E2",
                "landingPage": "",
                "score": 0,
                "redirect": 0,
                "showTitle": 1,
                "isArchived": 0,
                "fields": [],
                "actions": [],
                "labels": [],
                "projects": [],
                "user": base_user,
                "submits": 10,
                "views": 100,
                "uuid": "uuid1",
                "regDate": "2025-01-01T00:00:00Z",
                "modDate": "2025-01-01T00:00:00Z",
                "html": "",
                "socialMediaTags": "{}",
                "brandId": 1,
                "userEditable": True,
                "userRemovable": True,
                "lastSubmitDate": None,
                "landingPageBody": None,
                "thankYouElement": None,
                "thankYouElementOnDemand": None,
                "formType": None,
                "supportEmailId": None,
                "socialEventId": None,
                "domain": None,
                "urlName": None,
            },
            {
                "id": 2,
                "title": "Archived Form",
                "name": "archived_form",
                "internalName": "",
                "description": "",
                "buttonText": "Submit",
                "thankYouTitle": "Thanks",
                "thankYouTitleOnDemand": "Thanks",
                "thankYouText": "",
                "thankYouTextOnDemand": "",
                "buttonBgColor": "#000000",
                "buttonTextColor": "#ffffff",
                "backgroundColor": "#ffffff",
                "backgroundColorOnDemand": "",
                "textColor": "#000000",
                "linkColor": "#4A90E2",
                "landingPage": "",
                "score": 0,
                "redirect": 0,
                "showTitle": 1,
                "isArchived": 1,
                "fields": [],
                "actions": [],
                "labels": [],
                "projects": [],
                "user": base_user,
                "submits": 5,
                "views": 50,
                "uuid": "uuid2",
                "regDate": "2025-01-01T00:00:00Z",
                "modDate": "2025-01-01T00:00:00Z",
                "html": "",
                "socialMediaTags": "{}",
                "brandId": 1,
                "userEditable": True,
                "userRemovable": True,
                "lastSubmitDate": None,
                "landingPageBody": None,
                "thankYouElement": None,
                "thankYouElementOnDemand": None,
                "formType": None,
                "supportEmailId": None,
                "socialEventId": None,
                "domain": None,
                "urlName": None,
            },
            {
                "id": 3,
                "title": "No Submissions",
                "name": "no_submissions",
                "internalName": "",
                "description": "",
                "buttonText": "Submit",
                "thankYouTitle": "Thanks",
                "thankYouTitleOnDemand": "Thanks",
                "thankYouText": "",
                "thankYouTextOnDemand": "",
                "buttonBgColor": "#000000",
                "buttonTextColor": "#ffffff",
                "backgroundColor": "#ffffff",
                "backgroundColorOnDemand": "",
                "textColor": "#000000",
                "linkColor": "#4A90E2",
                "landingPage": "",
                "score": 0,
                "redirect": 0,
                "showTitle": 1,
                "isArchived": 0,
                "fields": [],
                "actions": [],
                "labels": [],
                "projects": [],
                "user": base_user,
                "submits": 0,
                "views": 20,
                "uuid": "uuid3",
                "regDate": "2025-01-01T00:00:00Z",
                "modDate": "2025-01-01T00:00:00Z",
                "html": "",
                "socialMediaTags": "{}",
                "brandId": 1,
                "userEditable": True,
                "userRemovable": True,
                "lastSubmitDate": None,
                "landingPageBody": None,
                "thankYouElement": None,
                "thankYouElementOnDemand": None,
                "formType": None,
                "supportEmailId": None,
                "socialEventId": None,
                "domain": None,
                "urlName": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting active forms."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            results = await resource.get_active()

            assert len(results) == 2  # Only active forms
            assert all(not f.is_archived for f in results)
            assert results[0].id == 1
            assert results[1].id == 3

    @pytest.mark.asyncio
    async def test_get_archived(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting archived forms."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            results = await resource.get_archived()

            assert len(results) == 1  # Only archived forms
            assert all(f.is_archived for f in results)
            assert results[0].id == 2

    @pytest.mark.asyncio
    async def test_get_with_submissions(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting forms with submissions."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            results = await resource.get_with_submissions()

            assert len(results) == 2  # Only forms with submissions > 0
            assert all(f.has_submissions for f in results)
            assert results[0].id == 1
            assert results[1].id == 2

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting form by name."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.get_by_name("active_form")

            assert result is not None
            assert result.id == 1
            assert result.name == "active_form"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting form by name when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.get_by_name("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_title(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting form by title."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.get_by_title("Active Form")

            assert result is not None
            assert result.id == 1
            assert result.title == "Active Form"

    @pytest.mark.asyncio
    async def test_get_by_title_case_insensitive(self, httpx_mock: HTTPXMock, sample_forms):
        """Test getting form by title is case-insensitive."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/forms?limit=100&offset=0",
            json={"error": None, "metadata": {"total": 3}, "data": sample_forms},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormsResource(http)
            result = await resource.get_by_title("active form")

            assert result is not None
            assert result.id == 1
