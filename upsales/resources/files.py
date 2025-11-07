"""
Files resource manager for Upsales API.

Provides methods to interact with the /files endpoint using File models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single file
    ...     file = await upsales.files.get(1)
    ...     print(file.filename, file.file_size_mb)
    ...
    ...     # List files
    ...     files = await upsales.files.list(limit=10)
    ...
    ...     # Get files by entity
    ...     account_files = await upsales.files.get_by_entity("Account", 123)
    ...
    ...     # Get all image files
    ...     images = await upsales.files.get_images()
"""

from upsales.http import HTTPClient
from upsales.models.files import File, PartialFile
from upsales.resources.base import BaseResource


class FilesResource(BaseResource[File, PartialFile]):
    """
    Resource manager for File endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single file
    - list(limit, offset, **params) - List files with pagination
    - list_all(**params) - Auto-paginated list of all files
    - update(id, **data) - Update file metadata
    - delete(id) - Delete file
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_entity(entity, entity_id) - Get files attached to specific entity
    - get_images() - Get all image files
    - get_documents() - Get all document files
    - get_private() - Get all private files
    - get_public() - Get all public files

    Example:
        >>> files = FilesResource(http_client)
        >>> file = await files.get(1)
        >>> account_files = await files.get_by_entity("Account", 123)
        >>> images = await files.get_images()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize files resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/files",
            model_class=File,
            partial_class=PartialFile,
        )

    async def get_by_entity(self, entity: str, entity_id: int) -> list[File]:
        """
        Get all files attached to a specific entity.

        Args:
            entity: Entity type (e.g., "Account", "Contact", "Activity", "Appointment").
            entity_id: ID of the entity.

        Returns:
            List of files attached to the entity.

        Example:
            >>> # Get files for account ID 123
            >>> files = await upsales.files.get_by_entity("Account", 123)
            >>> for file in files:
            ...     print(f"{file.filename} ({file.file_size_mb} MB)")
        """
        return await self.list_all(entity=entity, entityId=entity_id)

    async def get_images(self) -> list[File]:
        """
        Get all image files.

        Filters files where mimetype starts with 'image/'.

        Returns:
            List of image files (JPEG, PNG, GIF, etc.).

        Example:
            >>> images = await upsales.files.get_images()
            >>> for img in images:
            ...     print(f"{img.filename} - {img.mimetype}")
        """
        all_files: list[File] = await self.list_all()
        return [f for f in all_files if f.is_image]

    async def get_documents(self) -> list[File]:
        """
        Get all document files.

        Filters files with document-related mimetypes (PDF, Word, etc.).

        Returns:
            List of document files.

        Example:
            >>> docs = await upsales.files.get_documents()
            >>> for doc in docs:
            ...     print(f"{doc.filename} - {doc.mimetype}")
        """
        all_files: list[File] = await self.list_all()
        return [f for f in all_files if f.is_document]

    async def get_private(self) -> list[File]:
        """
        Get all private files.

        Returns:
            List of files with private=1.

        Example:
            >>> private_files = await upsales.files.get_private()
            >>> for file in private_files:
            ...     print(f"{file.filename} (private)")
        """
        return await self.list_all(private=1)

    async def get_public(self) -> list[File]:
        """
        Get all public files.

        Returns:
            List of files with public=1.

        Example:
            >>> public_files = await upsales.files.get_public()
            >>> for file in public_files:
            ...     print(f"{file.filename} (public)")
        """
        return await self.list_all(public=1)

    async def get_by_filename(self, filename: str, case_sensitive: bool = False) -> list[File]:
        """
        Get files by filename.

        Args:
            filename: Filename to search for.
            case_sensitive: If True, perform case-sensitive search. Default False.

        Returns:
            List of files matching the filename.

        Example:
            >>> files = await upsales.files.get_by_filename("document.pdf")
            >>> for file in files:
            ...     print(f"ID: {file.id}, Entity: {file.entity}")
        """
        all_files: list[File] = await self.list_all()
        if case_sensitive:
            return [f for f in all_files if f.filename == filename]
        else:
            filename_lower = filename.lower()
            return [f for f in all_files if f.filename.lower() == filename_lower]

    async def get_by_extension(self, extension: str) -> list[File]:
        """
        Get files by extension.

        Args:
            extension: File extension (with or without dot, e.g., ".pdf" or "pdf").

        Returns:
            List of files with the specified extension.

        Example:
            >>> pdf_files = await upsales.files.get_by_extension(".pdf")
            >>> jpg_files = await upsales.files.get_by_extension("jpg")
        """
        # Normalize extension (ensure it starts with dot)
        if not extension.startswith("."):
            extension = f".{extension}"

        return await self.list_all(extension=extension)
