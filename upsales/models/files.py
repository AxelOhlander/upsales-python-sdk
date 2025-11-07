"""
File models for Upsales API.

Generated from /api/v2/files endpoint.
Analysis based on 2 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, NonEmptyStr, PositiveInt)
- Computed fields (@computed_field)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, NonEmptyStr, PositiveInt


class FileUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a File.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    entity: str
    entityId: int
    filename: str
    extension: str
    mimetype: str
    size: int
    type: str
    private: int
    public: int
    userEditable: bool
    userRemovable: bool
    labels: list[str]
    driveFolderId: int
    order: int


class File(BaseModel):
    """
    File model from /api/v2/files.

    Represents a file attachment in the Upsales system. Files can be attached
    to various entities (accounts, contacts, activities, appointments, etc.).
    Enhanced with Pydantic v2 validators and computed fields.

    Generated from 2 samples with field analysis.

    Example:
        >>> file = await upsales.files.get(1)
        >>> file.filename
        'document.pdf'
        >>> file.is_private  # Computed property
        False
        >>> file.file_size_mb  # Size in MB
        1.5
        >>> await file.edit(filename="renamed.pdf")  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique file ID")
    uploadDate: str = Field(frozen=True, description="Upload timestamp (ISO 8601)")
    encryptedCustomerId: str = Field(frozen=True, description="Encrypted customer identifier")

    # Required fields with validators
    entity: NonEmptyStr = Field(
        description="Entity type (Account, Contact, Activity, Appointment, ProfileImage, etc.)"
    )
    entityId: PositiveInt = Field(description="ID of the entity this file is attached to")
    filename: NonEmptyStr = Field(description="Original filename")
    extension: NonEmptyStr = Field(description="File extension (e.g., '.pdf', '.jpg')")
    mimetype: NonEmptyStr = Field(description="MIME type (e.g., 'application/pdf')")
    size: PositiveInt = Field(description="File size in bytes")
    type: NonEmptyStr = Field(description="File type category (usually 'File')")

    # Binary flags (validated 0 or 1)
    private: BinaryFlag = Field(default=0, description="Private flag (0=no, 1=yes)")
    public: BinaryFlag = Field(default=0, description="Public flag (0=no, 1=yes)")

    # Permission flags
    userEditable: bool = Field(default=True, description="Whether current user can edit this file")
    userRemovable: bool = Field(
        default=True, description="Whether current user can remove this file"
    )

    # Optional fields
    user: PartialUser | None = Field(default=None, description="User who uploaded the file")
    labels: list[str] = Field(default=[], description="File labels/tags")
    order: int | None = Field(default=None, description="Display order")
    driveFolderId: int | None = Field(default=None, description="Google Drive folder ID if synced")

    # Linked entities (null if file is not attached to these)
    activity: dict[str, Any] | None = Field(
        default=None, description="Activity this file is attached to"
    )
    appointment: dict[str, Any] | None = Field(
        default=None, description="Appointment this file is attached to"
    )
    client: dict[str, Any] | None = Field(
        default=None, description="Company/account this file is attached to", alias="client"
    )
    contact: dict[str, Any] | None = Field(
        default=None, description="Contact this file is attached to"
    )

    @computed_field
    @property
    def is_private(self) -> bool:
        """
        Check if file is private.

        Returns:
            True if private flag is 1, False otherwise.

        Example:
            >>> file.is_private
            False
        """
        return self.private == 1

    @computed_field
    @property
    def is_public(self) -> bool:
        """
        Check if file is public.

        Returns:
            True if public flag is 1, False otherwise.

        Example:
            >>> file.is_public
            False
        """
        return self.public == 1

    @computed_field
    @property
    def file_size_mb(self) -> float:
        """
        Get file size in megabytes.

        Returns:
            File size in MB rounded to 2 decimal places.

        Example:
            >>> file.file_size_mb
            0.42
        """
        return round(self.size / (1024 * 1024), 2)

    @computed_field
    @property
    def file_size_kb(self) -> float:
        """
        Get file size in kilobytes.

        Returns:
            File size in KB rounded to 2 decimal places.

        Example:
            >>> file.file_size_kb
            417.71
        """
        return round(self.size / 1024, 2)

    @computed_field
    @property
    def is_image(self) -> bool:
        """
        Check if file is an image.

        Returns:
            True if mimetype starts with 'image/', False otherwise.

        Example:
            >>> file.is_image
            True
        """
        return self.mimetype.startswith("image/")

    @computed_field
    @property
    def is_document(self) -> bool:
        """
        Check if file is a document.

        Returns:
            True if mimetype indicates a document format, False otherwise.

        Example:
            >>> file.is_document
            True
        """
        doc_types = ("application/pdf", "application/msword", "application/vnd.ms-")
        return self.mimetype.startswith(doc_types) or "document" in self.mimetype

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get formatted display name.

        Returns:
            Filename with size in MB.

        Example:
            >>> file.display_name
            'document.pdf (0.42 MB)'
        """
        return f"{self.filename} ({self.file_size_mb} MB)"

    async def edit(self, **kwargs: Unpack[FileUpdateFields]) -> "File":
        """
        Edit this file.

        Uses Pydantic v2's optimized serialization via to_update_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated file with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> file = await upsales.files.get(1)
            >>> updated = await file.edit(
            ...     filename="renamed.pdf",
            ...     private=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.update(self.id, **self.to_update_dict(**kwargs))


class PartialFile(PartialModel):
    """
    Partial File for nested responses.

    Contains minimal fields for when File appears nested in other
    API responses (e.g., as attachments to activities, appointments, etc.).

    Use fetch_full() to get complete File object with all fields.

    Example:
        >>> activity = await upsales.activities.get(1)
        >>> file = activity.files[0]  # PartialFile
        >>> full_file = await file.fetch_full()  # Now File
    """

    id: int = Field(frozen=True, strict=True, description="Unique file ID")
    filename: NonEmptyStr = Field(description="Original filename")
    extension: NonEmptyStr = Field(description="File extension")
    size: PositiveInt = Field(description="File size in bytes")

    async def fetch_full(self) -> File:
        """
        Fetch complete file data.

        Returns:
            Full File object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = activity.files[0]  # PartialFile
            >>> full = await partial.fetch_full()  # File
            >>> full.mimetype  # Now available
            'application/pdf'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.get(self.id)

    async def edit(self, **kwargs: Unpack[FileUpdateFields]) -> File:
        """
        Edit this file.

        Returns full File object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full File object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = activity.files[0]  # PartialFile
            >>> updated = await partial.edit(filename="renamed.pdf")  # Returns File
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.files.update(self.id, **kwargs)
