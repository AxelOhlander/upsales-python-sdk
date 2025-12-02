"""
Unit tests for FormSubmitsResource.

Tests CRUD operations and custom methods for the formSubmits endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.form_submits import FormSubmit
from upsales.resources.form_submits import FormSubmitsResource


class TestFormSubmitsResourceCRUD:
    """Test CRUD operations for FormSubmitsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample form submission data for testing."""
        return {
            "id": 1,
            "formId": 123,
            "form": {"id": 123, "name": "Contact Form"},
            "contact": {"id": 456, "name": "John Doe"},
            "client": {"id": 789, "name": "Acme Corp"},
            "score": 85,
            "regDate": "2025-11-14T10:00:00Z",
            "processedDate": "2025-11-14T10:05:00Z",
            "fieldValues": [
                {"fieldId": 1, "value": "john@example.com"},
                {"fieldId": 2, "value": "Hello, I'm interested in your services"},
            ],
            "userRemovable": 1,
            "userEditable": 1,
            "brandId": 1,
            "visit": {"id": 999, "url": "https://example.com"},
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "score": 70, "visit": None},
            ],
        }

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single form submission."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/formSubmits/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormSubmitsResource(http)
            result = await resource.get(1)

            assert isinstance(result, FormSubmit)
            assert result.id == 1
            assert result.formId == 123
            assert result.score == 85
            assert result.is_removable
            assert result.is_editable

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing form submissions."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/formSubmits?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormSubmitsResource(http)
            results = await resource.list()

            assert len(results) == 2
            assert all(isinstance(s, FormSubmit) for s in results)
            assert results[0].id == 1
            assert results[1].id == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a form submission."""
        updated_data = {**sample_data, "score": 95}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/formSubmits/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormSubmitsResource(http)
            result = await resource.update(1, score=95)

            assert isinstance(result, FormSubmit)
            assert result.id == 1
            assert result.score == 95

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a form submission."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/formSubmits/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormSubmitsResource(http)
            await resource.delete(1)


class TestFormSubmitsResourceCustomMethods:
    """Test custom methods for FormSubmitsResource."""

    @pytest.fixture
    def sample_submissions(self):
        """Sample submissions for testing."""
        base_contact = {"id": 1, "name": "Test Contact"}
        base_client = {"id": 1, "name": "Test Company"}
        base_form = {"id": 123, "name": "Contact Form"}

        return [
            {
                "id": 1,
                "formId": 123,
                "form": base_form,
                "contact": base_contact,
                "client": base_client,
                "score": 85,
                "regDate": "2025-11-14T10:00:00Z",
                "processedDate": "2025-11-14T10:05:00Z",
                "fieldValues": [],
                "userRemovable": 1,
                "userEditable": 1,
                "brandId": 1,
                "visit": None,
            },
            {
                "id": 2,
                "formId": 456,
                "form": {"id": 456, "name": "Newsletter Form"},
                "contact": base_contact,
                "client": base_client,
                "score": 70,
                "regDate": "2025-11-14T11:00:00Z",
                "processedDate": "2025-11-14T11:05:00Z",
                "fieldValues": [],
                "userRemovable": 1,
                "userEditable": 1,
                "brandId": 1,
                "visit": None,
            },
            {
                "id": 3,
                "formId": 123,
                "form": base_form,
                "contact": base_contact,
                "client": base_client,
                "score": 90,
                "regDate": "2025-11-14T12:00:00Z",
                "processedDate": "2025-11-14T12:05:00Z",
                "fieldValues": [],
                "userRemovable": 1,
                "userEditable": 1,
                "brandId": 1,
                "visit": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_by_form_id(self, httpx_mock: HTTPXMock, sample_submissions):
        """Test getting submissions by form ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/formSubmits?limit=100&offset=0&formId=123",
            json={
                "error": None,
                "metadata": {"total": 2},
                "data": [sample_submissions[0], sample_submissions[2]],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FormSubmitsResource(http)
            results = await resource.get_by_form_id(123)

            assert len(results) == 2
            assert all(s.formId == 123 for s in results)
            assert results[0].id == 1
            assert results[1].id == 3


class TestFormSubmitModel:
    """Test FormSubmit model methods."""

    @pytest.fixture
    def sample_submission_data(self):
        """Sample submission data."""
        return {
            "id": 1,
            "formId": 123,
            "form": {"id": 123, "name": "Contact Form"},
            "contact": {"id": 456, "name": "John Doe"},
            "client": {"id": 789, "name": "Acme Corp"},
            "score": 85,
            "regDate": "2025-11-14T10:00:00Z",
            "processedDate": "2025-11-14T10:05:00Z",
            "fieldValues": [{"fieldId": 1, "value": "test@example.com"}],
            "userRemovable": 1,
            "userEditable": 1,
            "brandId": 1,
            "visit": None,
        }

    def test_computed_fields(self, sample_submission_data):
        """Test computed field properties."""
        submission = FormSubmit(**sample_submission_data)

        assert submission.is_removable is True
        assert submission.is_editable is True

        # Test with False values
        submission_no_perms = FormSubmit(
            **{**sample_submission_data, "userRemovable": 0, "userEditable": 0}
        )
        assert submission_no_perms.is_removable is False
        assert submission_no_perms.is_editable is False

    def test_frozen_fields(self, sample_submission_data):
        """Test that frozen fields cannot be modified."""
        submission = FormSubmit(**sample_submission_data)

        # Frozen fields should raise ValidationError on modification
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            submission.id = 999

        with pytest.raises(Exception):
            submission.userRemovable = 0

        with pytest.raises(Exception):
            submission.brandId = 999
