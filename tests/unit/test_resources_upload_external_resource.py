"""Unit tests for ResourcesUploadExternalResource."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from upsales.models.resources_upload_external import ResourcesUploadExternal
from upsales.resources.resources_upload_external import ResourcesUploadExternalResource


@pytest.fixture
def mock_http():
    """Create a mock HTTP client."""
    http = MagicMock()
    http._upsales_client = None
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.delete = AsyncMock()
    return http


@pytest.fixture
def resource(mock_http):
    """Create a ResourcesUploadExternalResource instance."""
    return ResourcesUploadExternalResource(mock_http)


class TestResourcesUploadExternalResource:
    """Test suite for ResourcesUploadExternalResource."""

    @pytest.mark.asyncio
    async def test_init(self, resource, mock_http):
        """Test resource initialization."""
        assert resource._http == mock_http
        assert resource._endpoint == "/resources/upload/external"
        assert resource._model_class == ResourcesUploadExternal

    @pytest.mark.asyncio
    async def test_upload_success(self, resource, mock_http, tmp_path):
        """Test successful file upload."""
        # Create temporary test file
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test content")

        # Mock response
        mock_http.post.return_value = {
            "id": 1,
            "entity": "adCampaign",
            "entityId": 123,
            "filename": "test.png",
            "url": "https://example.com/test.png",
            "size": 12,
            "mimeType": "image/png",
            "regDate": "2025-01-01T00:00:00Z",
        }

        # Upload file
        result = await resource.upload(entity="adCampaign", entity_id=123, file_path=str(test_file))

        # Verify
        assert isinstance(result, ResourcesUploadExternal)
        assert result.id == 1
        assert result.entity == "adCampaign"
        assert result.entityId == 123
        assert result.filename == "test.png"
        assert result.url == "https://example.com/test.png"
        assert result.size == 12
        assert result.mimeType == "image/png"

        # Verify HTTP call
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/resources/upload/external/adCampaign/123"
        assert "file" in call_args[1]["files"]

    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, resource):
        """Test upload with non-existent file."""
        with pytest.raises(FileNotFoundError):
            await resource.upload(
                entity="adCampaign",
                entity_id=123,
                file_path="/nonexistent/file.png",
            )

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, resource, tmp_path):
        """Test upload with file exceeding size limit."""
        # Create a file path that would be too large
        test_file = tmp_path / "large.zip"

        # Mock file size check
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=26_000_000)  # 26MB
            with patch.object(Path, "exists", return_value=True):
                with pytest.raises(ValueError, match="exceeds maximum"):
                    await resource.upload(
                        entity="adCampaign",
                        entity_id=123,
                        file_path=str(test_file),
                    )

    @pytest.mark.asyncio
    async def test_upload_with_path_object(self, resource, mock_http, tmp_path):
        """Test upload with Path object instead of string."""
        # Create temporary test file
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test content")

        # Mock response
        mock_http.post.return_value = {
            "id": 1,
            "entity": "adCampaign",
            "entityId": 123,
            "filename": "test.png",
            "url": "https://example.com/test.png",
            "size": 12,
            "mimeType": "image/png",
            "regDate": "2025-01-01T00:00:00Z",
        }

        # Upload file using Path object
        result = await resource.upload(entity="adCampaign", entity_id=123, file_path=test_file)

        # Verify
        assert isinstance(result, ResourcesUploadExternal)
        assert result.filename == "test.png"

    def test_guess_mime_type(self, resource):
        """Test MIME type guessing."""
        assert resource._guess_mime_type(Path("test.png")) == "image/png"
        assert resource._guess_mime_type(Path("test.jpg")) == "image/jpeg"
        # ZIP can be either application/zip or application/x-zip-compressed on Windows
        zip_type = resource._guess_mime_type(Path("test.zip"))
        assert zip_type in ("application/zip", "application/x-zip-compressed")
        assert resource._guess_mime_type(Path("test.unknown")) == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_get(self, resource, mock_http):
        """Test getting a single resource upload."""
        mock_http.get.return_value = {
            "data": {
                "id": 1,
                "entity": "adCampaign",
                "entityId": 123,
                "filename": "test.png",
                "url": "https://example.com/test.png",
                "size": 12,
                "mimeType": "image/png",
            }
        }

        result = await resource.get(1)

        assert isinstance(result, ResourcesUploadExternal)
        assert result.id == 1
        assert result.filename == "test.png"
        mock_http.get.assert_called_once_with("/resources/upload/external/1")

    @pytest.mark.asyncio
    async def test_list(self, resource, mock_http):
        """Test listing resource uploads."""
        mock_http.get.return_value = {
            "data": [
                {
                    "id": 1,
                    "entity": "adCampaign",
                    "entityId": 123,
                    "filename": "test1.png",
                    "url": "https://example.com/test1.png",
                    "size": 12,
                    "mimeType": "image/png",
                },
                {
                    "id": 2,
                    "entity": "adCampaign",
                    "entityId": 124,
                    "filename": "test2.png",
                    "url": "https://example.com/test2.png",
                    "size": 15,
                    "mimeType": "image/png",
                },
            ],
            "metadata": {"total": 2, "limit": 100, "offset": 0},
        }

        result = await resource.list(limit=100, offset=0)

        assert len(result) == 2
        assert all(isinstance(item, ResourcesUploadExternal) for item in result)
        assert result[0].id == 1
        assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_update(self, resource, mock_http):
        """Test updating a resource upload."""
        mock_http.put.return_value = {
            "data": {
                "id": 1,
                "entity": "adCampaign",
                "entityId": 123,
                "filename": "test.png",
                "url": "https://example.com/test.png",
                "size": 12,
                "mimeType": "image/png",
                "custom": [{"fieldId": 11, "value": "updated"}],
            }
        }

        result = await resource.update(1, custom=[{"fieldId": 11, "value": "updated"}])

        assert isinstance(result, ResourcesUploadExternal)
        assert result.id == 1
        assert len(result.custom) == 1

    @pytest.mark.asyncio
    async def test_delete(self, resource, mock_http):
        """Test deleting a resource upload."""
        mock_http.delete.return_value = {"data": None}

        await resource.delete(1)

        mock_http.delete.assert_called_once_with("/resources/upload/external/1")
