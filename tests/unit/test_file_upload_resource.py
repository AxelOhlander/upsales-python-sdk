"""Unit tests for FileUploadsResource.

Tests CRUD operations and upload method for the file upload endpoint.
"""

import io

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.file_upload import FileUpload, PartialFileUpload
from upsales.resources.file_upload import FileUploadsResource


class TestFileUploadsResourceCRUD:
    """Test CRUD operations for FileUploadsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample file upload data for testing."""
        return {
            "id": 123,
            "userId": 1,
            "extension": ".pdf",
            "type": "document",
            "filename": "test-document.pdf",
            "mimetype": "application/pdf",
            "private": 0,
            "size": 2450000,
            "entity": "Order",
            "entityId": 456,
            "uploadDate": "2025-11-14T10:30:00Z",
        }

    @pytest.fixture
    def http_client(self):
        """Create an HTTP client for testing."""
        return HTTPClient(token="test_token")

    @pytest.fixture
    def resource(self, http_client):
        """Create a FileUploadsResource for testing."""
        return FileUploadsResource(http_client)

    @pytest.mark.asyncio
    async def test_get(self, resource, sample_data, httpx_mock: HTTPXMock):
        """Test getting a single file upload."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload/123",
            method="GET",
            json={"error": None, "data": sample_data},
        )

        result = await resource.get(123)

        assert isinstance(result, FileUpload)
        assert result.id == 123
        assert result.filename == "test-document.pdf"
        assert result.size == 2450000
        assert result.private == 0
        assert result.is_private is False

    @pytest.mark.asyncio
    async def test_list(self, resource, sample_data, httpx_mock: HTTPXMock):
        """Test listing file uploads."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload?limit=10&offset=0",
            method="GET",
            json={
                "error": None,
                "data": [sample_data],
                "metadata": {"total": 1, "limit": 10, "offset": 0},
            },
        )

        results = await resource.list(limit=10)

        assert len(results) == 1
        assert isinstance(results[0], FileUpload)
        assert results[0].filename == "test-document.pdf"

    @pytest.mark.asyncio
    async def test_update(self, resource, sample_data, httpx_mock: HTTPXMock):
        """Test updating a file upload."""
        updated_data = {**sample_data, "private": 1, "entity": "Account"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload/123",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        result = await resource.update(123, private=1, entity="Account")

        assert isinstance(result, FileUpload)
        assert result.private == 1
        assert result.is_private is True
        assert result.entity == "Account"

    @pytest.mark.asyncio
    async def test_delete(self, resource, httpx_mock: HTTPXMock):
        """Test deleting a file upload."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload/123",
            method="DELETE",
            json={"error": None, "data": None},
        )

        await resource.delete(123)
        # Should not raise an exception


class TestFileUploadsResourceUpload:
    """Test upload method for FileUploadsResource."""

    @pytest.fixture
    def http_client(self):
        """Create an HTTP client for testing."""
        return HTTPClient(token="test_token")

    @pytest.fixture
    def resource(self, http_client):
        """Create a FileUploadsResource for testing."""
        return FileUploadsResource(http_client)

    @pytest.mark.asyncio
    async def test_upload_public_file(self, resource, httpx_mock: HTTPXMock):
        """Test uploading a public file."""
        response_data = {
            "id": 123,
            "userId": 1,
            "extension": ".pdf",
            "type": "document",
            "filename": "document.pdf",
            "mimetype": "application/pdf",
            "private": 0,
            "size": 1024000,
            "entity": None,
            "entityId": None,
            "uploadDate": "2025-11-14T10:30:00Z",
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload",
            method="POST",
            json={"error": None, "data": response_data},
        )

        file_content = b"PDF file content here"
        file = io.BytesIO(file_content)

        result = await resource.upload(file=file, filename="document.pdf", private=False)

        assert isinstance(result, FileUpload)
        assert result.id == 123
        assert result.filename == "document.pdf"
        assert result.is_private is False

    @pytest.mark.asyncio
    async def test_upload_private_file_with_roles(self, resource, httpx_mock: HTTPXMock):
        """Test uploading a private file with role restrictions."""
        response_data = {
            "id": 456,
            "userId": 1,
            "extension": ".docx",
            "type": "document",
            "filename": "confidential.docx",
            "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "private": 1,
            "size": 2048000,
            "entity": None,
            "entityId": None,
            "uploadDate": "2025-11-14T11:00:00Z",
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload",
            method="POST",
            json={"error": None, "data": response_data},
        )

        file_content = b"Confidential document content"
        file = io.BytesIO(file_content)

        result = await resource.upload(
            file=file, filename="confidential.docx", private=True, role_ids=[1, 2, 3]
        )

        assert isinstance(result, FileUpload)
        assert result.id == 456
        assert result.filename == "confidential.docx"
        assert result.is_private is True


class TestFileUploadModel:
    """Test FileUpload model methods."""

    @pytest.mark.asyncio
    async def test_computed_field_size_mb(self):
        """Test size_mb computed field."""
        file_upload = FileUpload(
            id=123,
            filename="test.pdf",
            size=2450000,
            private=0,
        )

        assert file_upload.size_mb == 2.45

    @pytest.mark.asyncio
    async def test_computed_field_size_mb_none(self):
        """Test size_mb when size is None."""
        file_upload = FileUpload(id=123, filename="test.pdf", private=0, size=None)

        assert file_upload.size_mb is None

    @pytest.mark.asyncio
    async def test_computed_field_is_private(self):
        """Test is_private computed field."""
        public_file = FileUpload(id=123, filename="public.pdf", private=0)
        private_file = FileUpload(id=456, filename="private.pdf", private=1)

        assert public_file.is_private is False
        assert private_file.is_private is True


class TestPartialFileUploadModel:
    """Test PartialFileUpload model."""

    @pytest.mark.asyncio
    async def test_partial_model_creation(self):
        """Test creating a PartialFileUpload."""
        partial = PartialFileUpload(id=123, filename="test.pdf")

        assert partial.id == 123
        assert partial.filename == "test.pdf"
