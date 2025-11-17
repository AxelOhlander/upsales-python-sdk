"""
File models for Upsales API.

Generated from /api/v2/files endpoint.
Analysis based on 89 samples.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag


class FileUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a File.

    All fields are optional. Based on API spec PUT allowed fields.
    """

    private: int
    clientId: int
    entity: str
    entityId: int
    public: int
    driveFolderId: int


class File(BaseModel):
    """
    File model from /api/v2/files.

    Represents file metadata in the Upsales system. Files can be attached
    to various entities like accounts, contacts, orders, and activities.

    Based on API spec:
    - Read-only: id, userId, extension, type, filename, mimetype, size, uploadDate
    - Updatable: private, clientId, entity, entityId, public, driveFolderId
    """

    # Read-only fields (frozen)
    id: int = Field(frozen=True, strict=True, description="Unique file ID")
    extension: str = Field(frozen=True, description="File extension (e.g., 'pdf', 'jpg')")
    type: str = Field(frozen=True, description="File type")
    filename: str = Field(frozen=True, description="Original filename")
    mimetype: str = Field(frozen=True, description="MIME type (e.g., 'application/pdf')")
    size: int = Field(frozen=True, description="File size in bytes")
    uploadDate: str | None = Field(None, frozen=True, description="Upload timestamp")
    encryptedCustomerId: str = Field(frozen=True, description="Encrypted customer ID")
    user: PartialUser | None = Field(None, frozen=True, description="User who uploaded the file")

    # Updatable fields
    private: BinaryFlag = Field(default=0, description="Whether file is private (0=no, 1=yes)")
    public: BinaryFlag = Field(
        default=0, description="Whether file is publicly accessible (0=no, 1=yes)"
    )
    entity: str | None = Field(
        None, description="Entity type (e.g., 'account', 'contact', 'order')"
    )
    entityId: int | None = Field(None, description="ID of the entity this file is attached to")
    client: PartialCompany | None = Field(
        None, alias="clientId", description="Company this file belongs to"
    )
    driveFolderId: int | None = Field(None, description="Google Drive folder ID if integrated")

    # Reference fields (read-only)
    activity: Any | None = Field(None, frozen=True, description="Associated activity")
    appointment: Any | None = Field(None, frozen=True, description="Associated appointment")
    contact: Any | None = Field(None, frozen=True, description="Associated contact")
    order: Any | None = Field(None, frozen=True, description="Associated order")
    labels: list[Any] = Field(default=[], frozen=True, description="File labels")
    userEditable: bool = Field(frozen=True, description="Whether current user can edit this file")
    userRemovable: bool = Field(
        frozen=True, description="Whether current user can delete this file"
    )

    @computed_field
    @property
    def is_private(self) -> bool:
        """Check if file is private."""
        return self.private == 1

    @computed_field
    @property
    def is_public(self) -> bool:
        """Check if file is publicly accessible."""
        return self.public == 1

    @computed_field
    @property
    def size_kb(self) -> float:
        """File size in kilobytes."""
        return round(self.size / 1024, 2)

    @computed_field
    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.size / (1024 * 1024), 2)

    @computed_field
    @property
    def file_size_kb(self) -> float:
        """File size in kilobytes (alias for compatibility)."""
        return self.size_kb

    @computed_field
    @property
    def file_size_mb(self) -> float:
        """File size in megabytes (alias for compatibility)."""
        return self.size_mb

    @computed_field
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        image_mimetypes = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
        }
        return self.mimetype in image_mimetypes

    @computed_field
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        document_mimetypes = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        return self.mimetype in document_mimetypes

    @computed_field
    @property
    def display_name(self) -> str:
        """Human-friendly display string with filename and size."""
        return f"{self.filename} ({self.file_size_mb} MB)"

    async def edit(self, **kwargs: Unpack[FileUpdateFields]) -> "File":
        """
        Edit this file metadata.

        Args:
            **kwargs: Fields to update (private, clientId, entity, entityId, public, driveFolderId).

        Returns:
            Updated file.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> file = await upsales.files.get(1)
            >>> updated = await file.edit(private=1, entity="account", entityId=123)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.update(self.id, **self.to_api_dict(**kwargs))


class PartialFile(PartialModel):
    """
    Partial File for nested responses.

    Contains minimal file information when files appear in nested responses
    (e.g., within accounts, contacts, orders).
    """

    id: int = Field(description="Unique file ID")
    filename: str | None = Field(None, description="Original filename")
    extension: str | None = Field(None, description="File extension")
    mimetype: str | None = Field(None, description="MIME type")
    size: int | None = Field(None, description="File size in bytes")

    async def fetch_full(self) -> File:
        """
        Fetch full file data from API.

        Returns:
            Complete File object with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = contact.files[0]
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.get(self.id)

    async def edit(self, **kwargs: Unpack[FileUpdateFields]) -> File:
        """
        Edit this file metadata.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated File object.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = contact.files[0]
            >>> updated = await partial.edit(private=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.update(self.id, **kwargs)
