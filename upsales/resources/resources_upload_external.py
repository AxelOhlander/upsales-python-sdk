"""ResourcesUploadExternal resource manager for Upsales API.

Provides methods to upload AdGear creative files to the Upsales API.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Upload a creative file
        resource = await upsales.resources_upload_external.upload(
            entity='adCampaign',
            entity_id=123,
            file_path='/path/to/creative.png'
        )
        print(f"Uploaded: {resource.filename} at {resource.url}")
    ```
"""

from pathlib import Path

from upsales.http import HTTPClient
from upsales.models.resources_upload_external import (
    PartialResourcesUploadExternal,
    ResourcesUploadExternal,
)
from upsales.resources.base import BaseResource


class ResourcesUploadExternalResource(
    BaseResource[ResourcesUploadExternal, PartialResourcesUploadExternal]
):
    """Resource manager for external resource uploads (AdGear creative files).

    This resource manager provides methods for uploading creative files to AdGear
    through the Upsales API.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single resource upload
    - list(limit, offset, **params) - List resource uploads with pagination
    - list_all(**params) - Auto-paginated list of all resource uploads
    - update(id, **data) - Update resource upload metadata
    - delete(id) - Delete resource upload

    Additional methods:
    - upload(entity, entity_id, file_path) - Upload a creative file

    Example:
        ```python
        resource_mgr = ResourcesUploadExternalResource(http_client)
        uploaded = await resource_mgr.upload(
            entity='adCampaign',
            entity_id=123,
            file_path='/path/to/creative.png'
        )
        ```

    Note:
        - Maximum file size: 25MB
        - Image files: max 150KB recommended
        - ZIP files: max 200KB recommended
    """

    def __init__(self, http: HTTPClient):
        """Initialize resources_upload_external resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/resources/upload/external",
            model_class=ResourcesUploadExternal,
            partial_class=PartialResourcesUploadExternal,
        )

    async def upload(
        self, entity: str, entity_id: int, file_path: str | Path
    ) -> ResourcesUploadExternal:
        """Upload a creative file to AdGear.

        Args:
            entity: Entity type (e.g., 'adCampaign', 'adAccount')
            entity_id: ID of the entity to attach the file to
            file_path: Path to the file to upload

        Returns:
            ResourcesUploadExternal instance with upload details

        Raises:
            FileNotFoundError: If file_path does not exist
            ValidationError: If file exceeds size limits
            ServerError: If upload fails

        Example:
            ```python
            # Upload campaign creative
            resource = await upsales.resources_upload_external.upload(
                entity='adCampaign',
                entity_id=123,
                file_path='/path/to/banner.png'
            )
            print(f"Uploaded to: {resource.url}")
            ```

        Note:
            - Maximum file size: 25MB
            - Image files: recommended max 150KB
            - ZIP files: recommended max 200KB
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size (25MB max)
        max_size = 25_000_000  # 25MB in bytes
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)")

        url = f"{self._endpoint}/{entity}/{entity_id}"

        # Open file and upload
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, self._guess_mime_type(file_path))}
            response = await self._http.post(
                url,
                **self._prepare_http_kwargs(),
                files=files,
            )

        return self._model_class(**response, _client=self._http._upsales_client)

    def _guess_mime_type(self, file_path: Path) -> str:
        """Guess MIME type from file extension.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string

        Note:
            Falls back to 'application/octet-stream' for unknown types.
        """
        import mimetypes

        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"
