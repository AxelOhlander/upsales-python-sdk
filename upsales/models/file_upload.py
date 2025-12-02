"""File upload model for Upsales API.

This module provides models for file upload operations.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag  # noqa: TC001


class FileUploadUpdateFields(TypedDict, total=False):
    """Available fields for updating a FileUpload.

    Note: File uploads are typically immutable after creation.
    This is provided for consistency with other models.
    """

    private: int
    entity: str | None
    entityId: int | None


class FileUpload(BaseModel):
    """Represents a file upload in Upsales.

    File uploads support various file types up to 25MB. They can be
    marked as private and restricted to specific roles.

    Attributes:
        id: Unique identifier for the uploaded file
        userId: ID of the user who uploaded the file
        extension: File extension (e.g., 'pdf', 'jpg')
        type: File type category
        filename: Original filename
        mimetype: MIME type of the file
        private: Whether the file is private (0=public, 1=private)
        size: File size in bytes
        entity: Entity type the file is attached to
        entityId: ID of the entity the file is attached to
        uploadDate: Date and time when the file was uploaded

    Example:
        >>> file_upload = await upsales.file_uploads.get(123)
        >>> print(file_upload.filename)
        'document.pdf'
        >>> print(file_upload.is_private)
        True
    """

    # Read-only fields
    id: int = Field(default=0, frozen=True, strict=True, description="Unique file ID")
    userId: int | None = Field(None, frozen=True, description="ID of user who uploaded the file")
    uploadDate: str | None = Field(None, frozen=True, description="Upload date and time")

    # File metadata fields (typically read-only after upload)
    extension: str | None = Field(None, description="File extension")
    type: str | None = Field(None, description="File type category")
    filename: str | None = Field(None, description="Original filename")
    mimetype: str | None = Field(None, description="MIME type")
    size: int | None = Field(None, description="File size in bytes")

    # Access control fields
    private: BinaryFlag = Field(default=0, description="Private flag (0=public, 1=private)")

    # Entity relationship fields
    entity: str | None = Field(None, description="Entity type the file is attached to")
    entityId: int | None = Field(None, description="ID of the entity the file is attached to")

    @computed_field
    @property
    def is_private(self) -> bool:
        """Check if the file is private.

        Returns:
            True if the file is private, False otherwise

        Example:
            >>> file_upload = await upsales.file_uploads.get(123)
            >>> if file_upload.is_private:
            ...     print("This file is private")
        """
        return self.private == 1

    @computed_field
    @property
    def size_mb(self) -> float | None:
        """Get file size in megabytes.

        Returns:
            File size in MB, or None if size is not available

        Example:
            >>> file_upload = await upsales.file_uploads.get(123)
            >>> print(f"Size: {file_upload.size_mb:.2f} MB")
            Size: 2.45 MB
        """
        if self.size is None:
            return None
        return self.size / 1_000_000

    async def edit(self, **kwargs: Unpack[FileUploadUpdateFields]) -> FileUpload:
        """Edit this file upload.

        Note: File uploads are typically immutable after creation.
        This method is provided for consistency with other models.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated FileUpload instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> file_upload = await upsales.file_uploads.get(123)
            >>> updated = await file_upload.edit(private=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.file_uploads.update(self.id, **self.to_api_dict(**kwargs))


class PartialFileUpload(PartialModel):
    """Partial file upload model for nested references.

    This model represents a minimal file upload reference, typically
    found in nested API responses.

    Attributes:
        id: Unique identifier for the file
        filename: Original filename

    Example:
        >>> contact = await upsales.contacts.get(123)
        >>> if contact.attachment:
        ...     full_file = await contact.attachment.fetch_full()
    """

    id: int = Field(description="Unique file ID")
    filename: str | None = Field(None, description="Original filename")

    async def fetch_full(self) -> FileUpload:
        """Fetch the complete FileUpload object.

        Returns:
            Full FileUpload instance with all fields

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialFileUpload(id=123, filename="doc.pdf")
            >>> full = await partial.fetch_full()
            >>> print(full.size_mb)
            2.45
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.file_uploads.get(self.id)

    async def edit(self, **kwargs: Any) -> FileUpload:
        """Edit this file upload.

        Note: File uploads are typically immutable after creation.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated FileUpload instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialFileUpload(id=123)
            >>> updated = await partial.edit(private=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.file_uploads.update(self.id, **kwargs)
