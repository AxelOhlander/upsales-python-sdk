"""Resources upload internal resource manager for Upsales API.

Provides methods to interact with the /resources/upload/internal endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Upload a document to an account
    ...     with open("proposal.pdf", "rb") as f:
    ...         resource = await upsales.resources_upload_internal.upload(
    ...             file=f,
    ...             filename="proposal.pdf",
    ...             entity="accounts",
    ...             entity_id=123,
    ...             private=True
    ...         )
    ...     print(f"Uploaded: {resource.filename}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from upsales.models.resources_upload_internal import (
    PartialResourcesUploadInternal,
    ResourcesUploadInternal,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ResourcesUploadInternalResource(
    BaseResource[ResourcesUploadInternal, PartialResourcesUploadInternal]
):
    """Resource manager for internal resource upload endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single resource upload
    - list(limit, offset, **params) - List resource uploads with pagination
    - list_all(**params) - Auto-paginated list of all resource uploads
    - update(id, **data) - Update resource upload metadata
    - delete(id) - Delete resource upload
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - upload(file, filename, entity, entity_id, folder_id, private, role_ids) - Upload a new resource

    Example:
        >>> resource_mgr = ResourcesUploadInternalResource(http_client)
        >>> with open("document.pdf", "rb") as f:
        ...     resource = await resource_mgr.upload(
        ...         file=f,
        ...         filename="document.pdf",
        ...         entity="accounts",
        ...         entity_id=123
        ...     )
        >>> print(resource.filename)
        'document.pdf'
    """

    def __init__(self, http: HTTPClient):
        """Initialize resources upload internal resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/resources/upload/internal",
            model_class=ResourcesUploadInternal,
            partial_class=PartialResourcesUploadInternal,
        )

    async def upload(
        self,
        file: BinaryIO,
        filename: str,
        entity: str,
        entity_id: int,
        folder_id: int | None = None,
        private: bool = False,
        role_ids: list[int] | None = None,
    ) -> ResourcesUploadInternal:
        """Upload an internal resource to Upsales.

        Uploads a file to a specific entity (account, contact, etc.) with optional
        folder organization. Files can be up to 25MB.

        Args:
            file: Binary file object to upload (e.g., from open())
            filename: Name for the file
            entity: Entity type to attach to (e.g., 'accounts', 'contacts')
            entity_id: ID of the entity to attach to
            folder_id: Optional folder ID for organization
            private: Whether to mark the resource as private (default: False)
            role_ids: List of role IDs that can access the resource (optional)

        Returns:
            ResourcesUploadInternal object with upload details

        Raises:
            ValidationError: If file is too large (>25MB) or invalid
            AuthenticationError: If authentication fails
            NotFoundError: If entity or folder not found
            ServerError: If the upload fails

        Example:
            >>> # Upload a public document to an account
            >>> with open("proposal.pdf", "rb") as f:
            ...     resource = await upsales.resources_upload_internal.upload(
            ...         file=f,
            ...         filename="proposal.pdf",
            ...         entity="accounts",
            ...         entity_id=123
            ...     )

            >>> # Upload a private document to a specific folder
            >>> with open("confidential.pdf", "rb") as f:
            ...     resource = await upsales.resources_upload_internal.upload(
            ...         file=f,
            ...         filename="confidential.pdf",
            ...         entity="contacts",
            ...         entity_id=456,
            ...         folder_id=789,
            ...         private=True,
            ...         role_ids=[1, 2, 3]
            ...     )

        Note:
            Maximum file size is 25MB (25,000,000 bytes).
            The entity parameter should match the API endpoint name
            (e.g., 'accounts', 'contacts', 'opportunities').
        """
        # Build the endpoint path with entity and entity_id
        path_parts = [self._endpoint, entity, str(entity_id)]
        if folder_id is not None:
            path_parts.append(str(folder_id))
        upload_path = "/".join(path_parts)

        # Prepare multipart form data
        files = {"file": (filename, file)}
        data: dict[str, str | list[int]] = {
            "private": "true" if private else "false",
        }

        if role_ids:
            data["roleIds"] = role_ids

        request_kwargs = self._prepare_http_kwargs()
        response_data = await self._http.request(
            "POST",
            upload_path,
            **request_kwargs,
            files=files,
            data=data,
        )

        # Inject client reference
        if isinstance(response_data, dict):
            response_data["_client"] = self._http._client

        return self._model_class.model_validate(response_data)
