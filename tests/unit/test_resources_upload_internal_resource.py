"""Unit tests for ResourcesUploadInternalResource."""

from io import BytesIO
from unittest.mock import AsyncMock, Mock

import pytest

from upsales.models.resources_upload_internal import (
    PartialResourcesUploadInternal,
    ResourcesUploadInternal,
)
from upsales.resources.resources_upload_internal import ResourcesUploadInternalResource


@pytest.fixture
def mock_http():
    """Create a mock HTTP client."""
    http = Mock()
    http.request = AsyncMock()
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.delete = AsyncMock()
    http._client = Mock()
    return http


@pytest.fixture
def resource(mock_http):
    """Create a ResourcesUploadInternalResource instance."""
    return ResourcesUploadInternalResource(mock_http)


@pytest.mark.asyncio
async def test_upload_basic(resource, mock_http):
    """Test basic file upload."""
    # Mock API response
    mock_http.request.return_value = {
        "id": 123,
        "filename": "document.pdf",
        "size": 1024,
        "userId": 1,
        "entity": "accounts",
        "entityId": 456,
        "private": 0,
        "uploadDate": "2025-11-14 10:00:00",
    }

    # Create a mock file
    file = BytesIO(b"test content")

    # Call upload
    result = await resource.upload(
        file=file,
        filename="document.pdf",
        entity="accounts",
        entity_id=456,
    )

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.id == 123
    assert result.filename == "document.pdf"
    assert result.entity == "accounts"
    assert result.entityId == 456

    # Verify request was made correctly
    mock_http.request.assert_called_once()
    call_args = mock_http.request.call_args
    assert call_args[0][0] == "POST"
    assert call_args[0][1] == "/resources/upload/internal/accounts/456"
    assert "files" in call_args[1]
    assert "data" in call_args[1]
    assert call_args[1]["data"]["private"] == "false"


@pytest.mark.asyncio
async def test_upload_with_folder(resource, mock_http):
    """Test file upload with folder."""
    # Mock API response
    mock_http.request.return_value = {
        "id": 123,
        "filename": "document.pdf",
        "folderId": 789,
    }

    file = BytesIO(b"test content")

    # Call upload with folder
    result = await resource.upload(
        file=file,
        filename="document.pdf",
        entity="contacts",
        entity_id=456,
        folder_id=789,
    )

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.folderId == 789

    # Verify path includes folder_id
    call_args = mock_http.request.call_args
    assert call_args[0][1] == "/resources/upload/internal/contacts/456/789"


@pytest.mark.asyncio
async def test_upload_private(resource, mock_http):
    """Test private file upload."""
    # Mock API response
    mock_http.request.return_value = {
        "id": 123,
        "filename": "confidential.pdf",
        "private": 1,
    }

    file = BytesIO(b"test content")

    # Call upload with private flag
    result = await resource.upload(
        file=file,
        filename="confidential.pdf",
        entity="accounts",
        entity_id=456,
        private=True,
    )

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.private == 1
    assert result.is_private is True

    # Verify private flag in request
    call_args = mock_http.request.call_args
    assert call_args[1]["data"]["private"] == "true"


@pytest.mark.asyncio
async def test_upload_with_role_ids(resource, mock_http):
    """Test file upload with role restrictions."""
    # Mock API response
    mock_http.request.return_value = {
        "id": 123,
        "filename": "restricted.pdf",
        "private": 1,
    }

    file = BytesIO(b"test content")

    # Call upload with role_ids
    result = await resource.upload(
        file=file,
        filename="restricted.pdf",
        entity="accounts",
        entity_id=456,
        private=True,
        role_ids=[1, 2, 3],
    )

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)

    # Verify roleIds in request
    call_args = mock_http.request.call_args
    assert call_args[1]["data"]["roleIds"] == [1, 2, 3]


@pytest.mark.asyncio
async def test_get(resource, mock_http):
    """Test getting a single resource upload."""
    # Mock API response
    mock_http.get.return_value = {
        "data": {
            "id": 123,
            "filename": "document.pdf",
            "size": 1024,
        }
    }

    # Call get
    result = await resource.get(123)

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.id == 123
    assert result.filename == "document.pdf"

    # Verify request
    mock_http.get.assert_called_once_with(
        "/resources/upload/internal/123",
    )


@pytest.mark.asyncio
async def test_list(resource, mock_http):
    """Test listing resource uploads."""
    # Mock API response
    mock_http.get.return_value = {
        "data": [
            {"id": 1, "filename": "file1.pdf"},
            {"id": 2, "filename": "file2.pdf"},
        ],
        "metadata": {"total": 2},
    }

    # Call list
    result = await resource.list(limit=10, offset=0)

    # Verify result
    assert len(result) == 2
    assert all(isinstance(r, ResourcesUploadInternal) for r in result)
    assert result[0].id == 1
    assert result[1].id == 2


@pytest.mark.asyncio
async def test_update(resource, mock_http):
    """Test updating a resource upload."""
    # Mock API response
    mock_http.put.return_value = {
        "data": {
            "id": 123,
            "filename": "document.pdf",
            "private": 1,
        }
    }

    # Call update
    result = await resource.update(123, private=1)

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.private == 1

    # Verify request
    mock_http.put.assert_called_once()


@pytest.mark.asyncio
async def test_delete(resource, mock_http):
    """Test deleting a resource upload."""
    # Mock API response
    mock_http.delete.return_value = None

    # Call delete
    await resource.delete(123)

    # Verify request
    mock_http.delete.assert_called_once_with(
        "/resources/upload/internal/123",
    )


def test_resource_initialization(mock_http):
    """Test resource initialization."""
    resource = ResourcesUploadInternalResource(mock_http)

    assert resource._http == mock_http
    assert resource._endpoint == "/resources/upload/internal"
    assert resource._model_class == ResourcesUploadInternal
    assert resource._partial_class == PartialResourcesUploadInternal


def test_computed_fields():
    """Test computed fields on ResourcesUploadInternal model."""
    resource = ResourcesUploadInternal(
        id=123,
        filename="test.pdf",
        private=1,
        size=3_210_000,
    )

    # Test is_private
    assert resource.is_private is True

    # Test size_mb
    assert resource.size_mb == 3.21


def test_computed_fields_with_none():
    """Test computed fields when values are None."""
    resource = ResourcesUploadInternal(
        id=123,
        filename="test.pdf",
        private=0,
        size=None,
    )

    # Test is_private with 0
    assert resource.is_private is False

    # Test size_mb with None
    assert resource.size_mb is None


@pytest.mark.asyncio
async def test_model_edit_method(mock_http):
    """Test the edit method on ResourcesUploadInternal model."""
    # Create a resource with client reference
    resource = ResourcesUploadInternal(
        id=123,
        filename="test.pdf",
        private=0,
        _client=mock_http,
    )

    # Mock the update method
    mock_http.resources_upload_internal = Mock()
    mock_http.resources_upload_internal.update = AsyncMock(
        return_value=ResourcesUploadInternal(id=123, filename="test.pdf", private=1)
    )

    # Call edit
    result = await resource.edit(private=1)

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.private == 1


@pytest.mark.asyncio
async def test_model_edit_without_client():
    """Test edit method raises error without client."""
    resource = ResourcesUploadInternal(
        id=123,
        filename="test.pdf",
    )

    with pytest.raises(RuntimeError, match="No client available"):
        await resource.edit(private=1)


@pytest.mark.asyncio
async def test_partial_fetch_full(mock_http):
    """Test PartialResourcesUploadInternal.fetch_full method."""
    partial = PartialResourcesUploadInternal(
        id=123,
        filename="test.pdf",
        _client=mock_http,
    )

    # Mock the get method
    mock_http.resources_upload_internal = Mock()
    mock_http.resources_upload_internal.get = AsyncMock(
        return_value=ResourcesUploadInternal(
            id=123,
            filename="test.pdf",
            size=1024,
        )
    )

    # Call fetch_full
    result = await partial.fetch_full()

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.id == 123
    assert result.size == 1024


@pytest.mark.asyncio
async def test_partial_fetch_full_without_client():
    """Test fetch_full raises error without client."""
    partial = PartialResourcesUploadInternal(
        id=123,
        filename="test.pdf",
    )

    with pytest.raises(RuntimeError, match="No client available"):
        await partial.fetch_full()


@pytest.mark.asyncio
async def test_partial_edit(mock_http):
    """Test PartialResourcesUploadInternal.edit method."""
    partial = PartialResourcesUploadInternal(
        id=123,
        filename="test.pdf",
        _client=mock_http,
    )

    # Mock the update method
    mock_http.resources_upload_internal = Mock()
    mock_http.resources_upload_internal.update = AsyncMock(
        return_value=ResourcesUploadInternal(
            id=123,
            filename="test.pdf",
            private=1,
        )
    )

    # Call edit
    result = await partial.edit(private=1)

    # Verify result
    assert isinstance(result, ResourcesUploadInternal)
    assert result.private == 1
