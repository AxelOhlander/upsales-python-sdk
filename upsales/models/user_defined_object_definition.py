"""User-defined object definition models for Upsales CRM.

This module provides models for creating and deleting user-defined object
configurations in the Upsales CRM API.

Note:
    This endpoint only supports POST (create) and DELETE operations.
    There are no GET operations available for this endpoint.
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class UserDefinedObjectDefinitionUpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObjectDefinition.

    Note:
        This endpoint only supports POST and DELETE operations.
        Update operations are not available.
    """

    name: str
    description: str
    fields: list[dict[str, Any]]


class UserDefinedObjectDefinition(BaseModel):
    """Represents a user-defined object definition in Upsales CRM.

    User-defined objects allow custom entity types to be created in the system.
    This model handles the definition structure for those custom objects.

    Attributes:
        id: Unique identifier for the definition
        name: Name of the user-defined object type
        description: Description of the user-defined object type
        fields: Field definitions for the custom object type

    Example:
        Create a new user-defined object definition:

        >>> definition = await upsales.user_defined_object_definitions.create(
        ...     name="Custom Entity",
        ...     description="A custom entity type",
        ...     fields=[
        ...         {"name": "field1", "type": "string"},
        ...         {"name": "field2", "type": "number"}
        ...     ]
        ... )
        >>> print(definition.name)
        Custom Entity

        Delete a definition:

        >>> await upsales.user_defined_object_definitions.delete(definition.id)
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique definition ID")

    # Updatable fields
    name: str | None = Field(None, description="Name of the object type")
    description: str | None = Field(None, description="Description of the object type")
    fields: list[dict[str, Any]] | None = Field(
        None, description="Field definitions for the custom object"
    )

    async def edit(
        self, **kwargs: Unpack[UserDefinedObjectDefinitionUpdateFields]
    ) -> UserDefinedObjectDefinition:
        """Edit this user-defined object definition.

        Note:
            This endpoint only supports POST and DELETE operations.
            Update operations are not available through the API.

        Args:
            **kwargs: Fields to update (name, description, fields)

        Returns:
            Updated UserDefinedObjectDefinition instance

        Raises:
            NotImplementedError: Update operations are not supported by this endpoint

        Example:
            >>> definition = await upsales.user_defined_object_definitions.get(1)
            >>> updated = await definition.edit(name="New Name")  # Not supported
        """
        raise NotImplementedError(
            "Update operations are not supported for user-defined object definitions. "
            "Only POST (create) and DELETE operations are available."
        )


class PartialUserDefinedObjectDefinition(PartialModel):
    """Partial representation of a user-defined object definition.

    Used when definitions appear as nested objects in other API responses.

    Attributes:
        id: Unique identifier for the definition
        name: Name of the user-defined object type

    Example:
        Fetch the full definition from a partial:

        >>> partial = some_object.definition  # PartialUserDefinedObjectDefinition
        >>> full = await partial.fetch_full()
        >>> print(full.description)
    """

    id: int = Field(description="Unique definition ID")
    name: str | None = Field(None, description="Name of the object type")

    async def fetch_full(self) -> UserDefinedObjectDefinition:
        """Fetch the complete definition object.

        Note:
            This endpoint does not support GET operations, so this method
            cannot retrieve the full definition from the API.

        Returns:
            Full UserDefinedObjectDefinition instance

        Raises:
            NotImplementedError: GET operations are not supported by this endpoint

        Example:
            >>> partial = some_object.definition
            >>> full = await partial.fetch_full()  # Not supported
        """
        raise NotImplementedError(
            "GET operations are not supported for user-defined object definitions. "
            "Only POST (create) and DELETE operations are available."
        )

    async def edit(
        self, **kwargs: Unpack[UserDefinedObjectDefinitionUpdateFields]
    ) -> UserDefinedObjectDefinition:
        """Edit this user-defined object definition.

        Note:
            This endpoint only supports POST and DELETE operations.
            Update operations are not available through the API.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated UserDefinedObjectDefinition instance

        Raises:
            NotImplementedError: Update operations are not supported by this endpoint

        Example:
            >>> partial = some_object.definition
            >>> updated = await partial.edit(name="New Name")  # Not supported
        """
        raise NotImplementedError(
            "Update operations are not supported for user-defined object definitions. "
            "Only POST (create) and DELETE operations are available."
        )
