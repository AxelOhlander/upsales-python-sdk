"""Resources upload internal model for Upsales API.

This module provides models for internal resource upload operations with
folder organization.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag  # noqa: TC001


class ResourcesUploadInternalUpdateFields(TypedDict, total=False):
    """Available fields for updating a ResourcesUploadInternal.

    Note: Resource uploads are typically immutable after creation.
    This is provided for consistency with other models.
    """

    private: int
    entity: str | None
    entityId: int | None
    folderId: int | None


class ResourcesUploadInternal(BaseModel):
    """Represents an internal resource upload in Upsales.

    Internal resource uploads support various file types up to 25MB. They can be
    organized in folders and attached to specific entities (accounts, contacts, etc).

    Attributes:
        id: Unique identifier for the uploaded resource
        userId: ID of the user who uploaded the resource
        extension: File extension (e.g., 'pdf', 'jpg')
        type: File type category
        filename: Original filename
        mimetype: MIME type of the file
        private: Whether the resource is private (0=public, 1=private)
        size: File size in bytes
        entity: Entity type the resource is attached to
        entityId: ID of the entity the resource is attached to
        folderId: ID of the folder containing the resource
        uploadDate: Date and time when the resource was uploaded

    Example:
        >>> resource = await upsales.resources_upload_internal.get(123)
        >>> print(resource.filename)
        'presentation.pdf'
        >>> print(resource.is_private)
        False
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique resource ID")
    userId: int | None = Field(
        None, frozen=True, description="ID of user who uploaded the resource"
    )
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
    entity: str | None = Field(None, description="Entity type the resource is attached to")
    entityId: int | None = Field(None, description="ID of the entity the resource is attached to")
    folderId: int | None = Field(None, description="ID of the folder containing the resource")

    @computed_field
    @property
    def is_private(self) -> bool:
        """Check if the resource is private.

        Returns:
            True if the resource is private, False otherwise

        Example:
            >>> resource = await upsales.resources_upload_internal.get(123)
            >>> if resource.is_private:
            ...     print("This resource is private")
        """
        return self.private == 1

    @computed_field
    @property
    def size_mb(self) -> float | None:
        """Get file size in megabytes.

        Returns:
            File size in MB, or None if size is not available

        Example:
            >>> resource = await upsales.resources_upload_internal.get(123)
            >>> print(f"Size: {resource.size_mb:.2f} MB")
            Size: 3.21 MB
        """
        if self.size is None:
            return None
        return self.size / 1_000_000

    async def edit(
        self, **kwargs: Unpack[ResourcesUploadInternalUpdateFields]
    ) -> ResourcesUploadInternal:
        """Edit this resource upload.

        Note: Resource uploads are typically immutable after creation.
        This method is provided for consistency with other models.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated ResourcesUploadInternal instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> resource = await upsales.resources_upload_internal.get(123)
            >>> updated = await resource.edit(private=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_internal.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialResourcesUploadInternal(PartialModel):
    """Partial resource upload internal model for nested references.

    This model represents a minimal resource upload reference, typically
    found in nested API responses.

    Attributes:
        id: Unique identifier for the resource
        filename: Original filename

    Example:
        >>> account = await upsales.accounts.get(123)
        >>> if account.document:
        ...     full_resource = await account.document.fetch_full()
    """

    id: int = Field(description="Unique resource ID")
    filename: str | None = Field(None, description="Original filename")

    async def fetch_full(self) -> ResourcesUploadInternal:
        """Fetch the complete ResourcesUploadInternal object.

        Returns:
            Full ResourcesUploadInternal instance with all fields

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialResourcesUploadInternal(id=123, filename="doc.pdf")
            >>> full = await partial.fetch_full()
            >>> print(full.size_mb)
            3.21
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_internal.get(self.id)

    async def edit(self, **kwargs: Any) -> ResourcesUploadInternal:
        """Edit this resource upload.

        Note: Resource uploads are typically immutable after creation.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated ResourcesUploadInternal instance

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> partial = PartialResourcesUploadInternal(id=123)
            >>> updated = await partial.edit(private=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_internal.update(self.id, **kwargs)
