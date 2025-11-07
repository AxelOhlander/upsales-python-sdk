"""
Unit tests for FilesResource.

Tests CRUD operations and custom methods for the files endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.files import File
from upsales.resources.files import FilesResource


class TestFilesResourceCRUD:
    """Test CRUD operations for FilesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample file data for testing."""
        return {
            "id": 1,
            "activity": None,
            "appointment": None,
            "client": None,
            "contact": None,
            "encryptedCustomerId": "0",
            "entity": "ProfileImage",
            "entityId": 1,
            "extension": ".jpg",
            "filename": "test-image.jpg",
            "mimetype": "image/jpeg",
            "order": None,
            "private": 0,
            "public": 0,
            "size": 417713,
            "type": "File",
            "uploadDate": "2025-05-20T13:20:25Z",
            "user": {
                "name": "Test User",
                "id": 1,
                "role": {"name": "Admin", "id": 1},
                "email": "test@example.com",
            },
            "userEditable": True,
            "userRemovable": True,
            "labels": [],
            "driveFolderId": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {
                    **sample_data,
                    "id": 2,
                    "filename": "document.pdf",
                    "extension": ".pdf",
                    "mimetype": "application/pdf",
                    "size": 1024000,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a file."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            result = await resource.create(
                filename="test-image.jpg",
                extension=".jpg",
                mimetype="image/jpeg",
                size=417713,
                entity="ProfileImage",
                entityId=1,
                type="File",
            )

            assert isinstance(result, File)
            assert result.id == 1
            assert result.filename == "test-image.jpg"
            assert result.is_image

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single file."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            result = await resource.get(1)

            assert isinstance(result, File)
            assert result.id == 1
            assert result.filename == "test-image.jpg"
            assert result.file_size_mb == 0.4
            assert not result.is_private

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing files with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, File) for item in results)
            assert results[0].filename == "test-image.jpg"
            assert results[1].filename == "document.pdf"

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a file."""
        updated_data = {**sample_data, "filename": "renamed.jpg", "private": 1}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            result = await resource.update(1, filename="renamed.jpg", private=1)

            assert isinstance(result, File)
            assert result.id == 1
            assert result.filename == "renamed.jpg"
            assert result.is_private

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a file."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files/1",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestFilesResourceCustomMethods:
    """Test custom methods for FilesResource."""

    @pytest.fixture
    def sample_image_file(self):
        """Sample image file."""
        return {
            "id": 1,
            "filename": "image.jpg",
            "extension": ".jpg",
            "mimetype": "image/jpeg",
            "size": 500000,
            "entity": "Account",
            "entityId": 100,
            "type": "File",
            "private": 0,
            "public": 0,
            "encryptedCustomerId": "0",
            "uploadDate": "2025-05-20T13:20:25Z",
            "user": {
                "name": "Test User",
                "id": 1,
                "role": {"name": "Admin", "id": 1},
                "email": "test@example.com",
            },
            "userEditable": True,
            "userRemovable": True,
            "labels": [],
            "driveFolderId": None,
            "activity": None,
            "appointment": None,
            "client": None,
            "contact": None,
            "order": None,
        }

    @pytest.fixture
    def sample_pdf_file(self):
        """Sample PDF file."""
        return {
            "id": 2,
            "filename": "document.pdf",
            "extension": ".pdf",
            "mimetype": "application/pdf",
            "size": 1024000,
            "entity": "Contact",
            "entityId": 200,
            "type": "File",
            "private": 1,
            "public": 0,
            "encryptedCustomerId": "0",
            "uploadDate": "2025-05-20T14:30:00Z",
            "user": {
                "name": "Test User",
                "id": 1,
                "role": {"name": "Admin", "id": 1},
                "email": "test@example.com",
            },
            "userEditable": True,
            "userRemovable": True,
            "labels": [],
            "driveFolderId": None,
            "activity": None,
            "appointment": None,
            "client": None,
            "contact": None,
            "order": None,
        }

    @pytest.mark.asyncio
    async def test_get_by_entity(self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file):
        """Test getting files by entity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0&entity=Account&entityId=100",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_image_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.get_by_entity("Account", 100)

            assert len(results) == 1
            assert results[0].entity == "Account"
            assert results[0].entityId == 100

    @pytest.mark.asyncio
    async def test_get_images(self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file):
        """Test getting only image files."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [sample_image_file, sample_pdf_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.get_images()

            assert len(results) == 1
            assert results[0].is_image
            assert results[0].mimetype == "image/jpeg"

    @pytest.mark.asyncio
    async def test_get_documents(self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file):
        """Test getting only document files."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [sample_image_file, sample_pdf_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.get_documents()

            assert len(results) == 1
            assert results[0].is_document
            assert results[0].mimetype == "application/pdf"

    @pytest.mark.asyncio
    async def test_get_private(self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file):
        """Test getting only private files."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0&private=1",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_pdf_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.get_private()

            assert len(results) == 1
            assert results[0].is_private

    @pytest.mark.asyncio
    async def test_get_public(self, httpx_mock: HTTPXMock, sample_image_file):
        """Test getting only public files."""
        public_file = {**sample_image_file, "public": 1}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0&public=1",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [public_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results = await resource.get_public()

            assert len(results) == 1
            assert results[0].is_public

    @pytest.mark.asyncio
    async def test_get_by_filename(self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file):
        """Test getting files by filename."""
        # Register response twice since we call list_all() twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [sample_image_file, sample_pdf_file],
            },
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [sample_image_file, sample_pdf_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)

            # Case insensitive by default
            results = await resource.get_by_filename("IMAGE.JPG")
            assert len(results) == 1
            assert results[0].filename == "image.jpg"

            # Case sensitive
            results_sensitive = await resource.get_by_filename("image.jpg", case_sensitive=True)
            assert len(results_sensitive) == 1

    @pytest.mark.asyncio
    async def test_get_by_extension(
        self, httpx_mock: HTTPXMock, sample_image_file, sample_pdf_file
    ):
        """Test getting files by extension."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0&extension=.pdf",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_pdf_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)

            # With dot
            results = await resource.get_by_extension(".pdf")
            assert len(results) == 1
            assert results[0].extension == ".pdf"

        # Test without dot
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/files?limit=100&offset=0&extension=.jpg",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_image_file],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = FilesResource(http)
            results_no_dot = await resource.get_by_extension("jpg")
            assert len(results_no_dot) == 1
            assert results_no_dot[0].extension == ".jpg"
