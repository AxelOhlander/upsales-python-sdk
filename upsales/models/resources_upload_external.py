"""Models for resourcesUploadExternal endpoint.

This endpoint is used for uploading AdGear creative files.
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList


class ResourcesUploadExternalUpdateFields(TypedDict, total=False):
    """Available fields for updating a ResourcesUploadExternal.

    Note:
        This endpoint is primarily for POST operations (file uploads).
        Update operations may not be supported.
    """

    custom: list[dict[str, object]]


class ResourcesUploadExternal(BaseModel):
    """Represents an external resource upload in Upsales (AdGear creative file).

    This model represents the response after uploading a creative file to AdGear.

    Attributes:
        id: Unique identifier for the uploaded resource
        entity: Entity type (e.g., 'adCampaign', 'adAccount')
        entityId: ID of the entity the resource is attached to
        filename: Name of the uploaded file
        url: URL of the uploaded resource
        size: File size in bytes
        mimeType: MIME type of the uploaded file
        regDate: Registration date (ISO format)
        custom: Custom fields for the resource

    Example:
        ```python
        # Upload a file
        resource = await upsales.resources_upload_external.upload(
            entity='adCampaign',
            entity_id=123,
            file_path='/path/to/creative.png'
        )
        print(f"Uploaded: {resource.filename} at {resource.url}")
        ```

    Note:
        - Maximum file size: 25MB
        - Image files: max 150KB
        - ZIP files: max 200KB
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique resource ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date")

    # Normal fields
    entity: str | None = Field(None, description="Entity type")
    entityId: int | None = Field(None, description="Entity ID")
    filename: str | None = Field(None, description="Filename")
    url: str | None = Field(None, description="Resource URL")
    size: int | None = Field(None, description="File size in bytes")
    mimeType: str | None = Field(None, description="MIME type")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for accessing custom fields by ID or alias.

        Example:
            ```python
            resource.custom_fields[11] = "value"
            value = resource.custom_fields.get("FIELD_ALIAS", "default")
            ```
        """
        return CustomFields(self.custom)

    async def edit(
        self, **kwargs: Unpack[ResourcesUploadExternalUpdateFields]
    ) -> "ResourcesUploadExternal":
        """Edit this resource upload.

        Args:
            **kwargs: Fields to update (see ResourcesUploadExternalUpdateFields)

        Returns:
            Updated ResourcesUploadExternal instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If field validation fails
            NotFoundError: If resource not found

        Example:
            ```python
            resource = await upsales.resources_upload_external.get(1)
            updated = await resource.edit(custom=[{"fieldId": 11, "value": "test"}])
            ```

        Note:
            This endpoint may not support traditional update operations.
            It is primarily designed for POST (upload) operations.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_external.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialResourcesUploadExternal(PartialModel):
    """Partial model for resourcesUploadExternal (nested references).

    Used when an external resource upload appears in nested responses.

    Attributes:
        id: Unique identifier for the uploaded resource
        filename: Name of the uploaded file
        url: URL of the uploaded resource

    Example:
        ```python
        # Fetch full details
        full = await partial_resource.fetch_full()
        print(full.size, full.mimeType)

        # Or edit directly
        updated = await partial_resource.edit(custom=[...])
        ```
    """

    id: int = Field(description="Unique resource ID")
    filename: str | None = Field(None, description="Filename")
    url: str | None = Field(None, description="Resource URL")

    async def fetch_full(self) -> ResourcesUploadExternal:
        """Fetch complete ResourcesUploadExternal data.

        Returns:
            Full ResourcesUploadExternal instance with all fields

        Raises:
            RuntimeError: If no client is available
            NotFoundError: If resource not found

        Example:
            ```python
            partial = campaign.creative_resource  # Nested reference
            full = await partial.fetch_full()
            print(f"File size: {full.size} bytes")
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_external.get(self.id)

    async def edit(self, **kwargs: object) -> ResourcesUploadExternal:
        """Edit this resource upload using partial data.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated ResourcesUploadExternal instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If field validation fails
            NotFoundError: If resource not found

        Example:
            ```python
            partial = campaign.creative_resource
            updated = await partial.edit(custom=[{"fieldId": 11, "value": "test"}])
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.resources_upload_external.update(self.id, **kwargs)
