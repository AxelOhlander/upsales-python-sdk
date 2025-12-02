"""File uploads resource manager for Upsales API.

Provides methods to interact with the /file/upload endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Upload a file
    ...     with open("document.pdf", "rb") as f:
    ...         file_upload = await upsales.file_uploads.upload(
    ...             file=f,
    ...             filename="document.pdf",
    ...             private=True
    ...         )
    ...     print(f"Uploaded: {file_upload.filename}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from upsales.models.file_upload import FileUpload, PartialFileUpload
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FileUploadsResource(BaseResource[FileUpload, PartialFileUpload]):
    """Resource manager for file upload endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single file upload
    - list(limit, offset, **params) - List file uploads with pagination
    - list_all(**params) - Auto-paginated list of all file uploads
    - update(id, **data) - Update file upload metadata
    - delete(id) - Delete file upload
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - upload(file, filename, private, role_ids) - Upload a new file

    Example:
        >>> resource = FileUploadsResource(http_client)
        >>> with open("document.pdf", "rb") as f:
        ...     file_upload = await resource.upload(f, "document.pdf")
        >>> print(file_upload.filename)
        'document.pdf'
    """

    def __init__(self, http: HTTPClient):
        """Initialize file upload resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/file/upload",
            model_class=FileUpload,
            partial_class=PartialFileUpload,
        )

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        private: bool = False,
        role_ids: list[int] | None = None,
    ) -> FileUpload:
        """Upload a file to Upsales.

        Uploads a file using multipart/form-data. Files can be up to 25MB.

        Args:
            file: Binary file object to upload (e.g., from open())
            filename: Name for the file
            private: Whether to mark the file as private (default: False)
            role_ids: List of role IDs that can access the file (optional)

        Returns:
            FileUpload object with upload details

        Raises:
            ValidationError: If file is too large (>25MB) or invalid
            AuthenticationError: If authentication fails
            ServerError: If the upload fails

        Example:
            >>> # Upload a public file
            >>> with open("document.pdf", "rb") as f:
            ...     file_upload = await upsales.file_uploads.upload(
            ...         file=f,
            ...         filename="document.pdf"
            ...     )

            >>> # Upload a private file restricted to specific roles
            >>> with open("confidential.pdf", "rb") as f:
            ...     file_upload = await upsales.file_uploads.upload(
            ...         file=f,
            ...         filename="confidential.pdf",
            ...         private=True,
            ...         role_ids=[1, 2, 3]
            ...     )

        Note:
            Maximum file size is 25MB (25,000,000 bytes).
            Maximum field size is 10MB.
        """
        # Prepare multipart form data
        files = {"file": (filename, file)}
        data: dict[str, str | list[int]] = {
            "private": "true" if private else "false",
        }

        if role_ids:
            data["roleIds"] = role_ids

        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.request(
            "POST",
            self._endpoint,
            **request_kwargs,
            files=files,
            data=data,
        )

        payload = response.get("data", response)

        return self._model_class(
            **payload,
            _client=self._http._upsales_client,
        )
