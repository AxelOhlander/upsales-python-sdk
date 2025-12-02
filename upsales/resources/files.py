"""
Files resource manager for Upsales API.

Provides methods to interact with the /files endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     file = await upsales.files.get(1)
    ...     files_list = await upsales.files.list(limit=10)
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
    - update(id, **data) - Update file
    - delete(id) - Delete file
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = FilesResource(http_client)
        >>> file = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
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
            entity: Entity type (e.g., 'Account', 'Contact', 'Order').
            entity_id: ID of the entity.

        Returns:
            List of files attached to the entity.

        Example:
            >>> files = await upsales.files.get_by_entity("Account", 123)
        """
        return await self.list_all(entity=entity, entityId=entity_id)

    async def get_images(self) -> list[File]:
        """
        Get all image files.

        Returns:
            List of image files.

        Example:
            >>> images = await upsales.files.get_images()
        """
        all_files: list[File] = await self.list_all()
        return [f for f in all_files if f.is_image]

    async def get_documents(self) -> list[File]:
        """
        Get all document files (PDF, Word, Excel, etc.).

        Returns:
            List of document files.

        Example:
            >>> documents = await upsales.files.get_documents()
        """
        all_files: list[File] = await self.list_all()
        return [f for f in all_files if f.is_document]

    async def get_private(self) -> list[File]:
        """
        Get all private files.

        Returns:
            List of private files.

        Example:
            >>> private_files = await upsales.files.get_private()
        """
        return await self.list_all(private=1)

    async def get_public(self) -> list[File]:
        """
        Get all public files.

        Returns:
            List of public files.

        Example:
            >>> public_files = await upsales.files.get_public()
        """
        return await self.list_all(public=1)

    async def get_by_filename(self, filename: str, case_sensitive: bool = False) -> list[File]:
        """
        Get files by filename.

        Args:
            filename: Filename to search for.
            case_sensitive: Whether search should be case-sensitive (default: False).

        Returns:
            List of files matching the filename.

        Example:
            >>> files = await upsales.files.get_by_filename("image.jpg")
            >>> files_case = await upsales.files.get_by_filename("IMAGE.JPG", case_sensitive=True)
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
            extension: File extension (with or without leading dot).

        Returns:
            List of files with the specified extension.

        Example:
            >>> pdfs = await upsales.files.get_by_extension(".pdf")
            >>> jpgs = await upsales.files.get_by_extension("jpg")
        """
        # Ensure extension has leading dot
        if not extension.startswith("."):
            extension = f".{extension}"
        return await self.list_all(extension=extension)
