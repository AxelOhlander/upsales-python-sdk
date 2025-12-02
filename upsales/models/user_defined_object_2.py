"""User-defined object 2 models for Upsales API.

This module defines models for user-defined custom objects (slot 2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import UserDefinedObject2UpdateFields


class UserDefinedObject2(BaseModel):
    """User-defined object 2 model.

    Represents a flexible custom entity with associations to clients, contacts, projects,
    users, and roles (second slot).

    Attributes:
        id: Unique object ID (read-only).
        notes: Main notes field.
        notes1: Additional notes field 1.
        notes2: Additional notes field 2.
        notes3: Additional notes field 3.
        notes4: Additional notes field 4.
        clientId: Associated client ID.
        contactId: Associated contact ID.
        projectId: Associated project ID.
        userId: Associated user ID.
        roleId: Associated role ID.
        regDate: Registration date (read-only).
        regTime: Registration time (read-only).
        modDate: Modification date (read-only).
        modTime: Modification time (read-only).
        custom: Custom fields list.
        categories: Category assignments.

    Example:
        ```python
        # Create user-defined object
        obj = await upsales.user_defined_object_2.create(
            notes="Main notes",
            clientId=1
        )

        # Update object
        obj.notes = "Updated notes"
        updated = await obj.edit()

        # Or use edit with parameters
        updated = await obj.edit(notes="Updated", userId=2)
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique object ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    regTime: str | None = Field(None, frozen=True, description="Registration time")
    modDate: str | None = Field(None, frozen=True, description="Modification date")
    modTime: str | None = Field(None, frozen=True, description="Modification time")

    # Updatable fields
    notes: str | None = Field(None, description="Main notes")
    notes1: str | None = Field(None, description="Additional notes 1")
    notes2: str | None = Field(None, description="Additional notes 2")
    notes3: str | None = Field(None, description="Additional notes 3")
    notes4: str | None = Field(None, description="Additional notes 4")
    clientId: int | None = Field(None, description="Associated client ID")
    contactId: int | None = Field(None, description="Associated contact ID")
    projectId: int | None = Field(None, description="Associated project ID")
    userId: int = Field(0, description="Associated user ID")
    roleId: int = Field(0, description="Associated role ID")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")
    categories: list[dict] | None = Field(None, description="Category assignments")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            obj = await upsales.user_defined_object_2.get(1)
            value = obj.custom_fields.get(11)
            obj.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    async def edit(self, **kwargs: Unpack[UserDefinedObject2UpdateFields]) -> UserDefinedObject2:
        """Edit this user-defined object with type-safe field updates.

        Args:
            **kwargs: Fields to update (notes, notes1-4, clientId, contactId,
                     projectId, userId, roleId, custom, categories).

        Returns:
            Updated UserDefinedObject2 instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If object no longer exists.

        Example:
            ```python
            obj = await upsales.user_defined_object_2.get(1)

            # Update single field
            updated = await obj.edit(notes="Updated notes")

            # Update multiple fields
            updated = await obj.edit(
                notes="Updated",
                clientId=2,
                userId=3
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.user_defined_object_2.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialUserDefinedObject2(PartialModel):
    """Partial user-defined object 2 model for nested responses.

    Used when user-defined objects appear as nested objects in API responses.

    Attributes:
        id: Unique object ID.
        notes: Main notes field.

    Example:
        ```python
        # Fetch full object from partial
        partial: PartialUserDefinedObject2 = some_object.user_defined_object
        full: UserDefinedObject2 = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(notes="Updated")
        ```
    """

    id: int = Field(description="Unique object ID")
    notes: str | None = Field(None, description="Main notes")

    async def fetch_full(self) -> UserDefinedObject2:
        """Fetch complete user-defined object data.

        Returns:
            Full UserDefinedObject2 instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If object not found.

        Example:
            ```python
            partial = PartialUserDefinedObject2(id=1, notes="Notes")
            full = await partial.fetch_full()
            print(full.clientId)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.user_defined_object_2.get(self.id)

    async def edit(self, **kwargs: Unpack[UserDefinedObject2UpdateFields]) -> UserDefinedObject2:
        """Edit this user-defined object.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated UserDefinedObject2 instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If object not found.

        Example:
            ```python
            partial = PartialUserDefinedObject2(id=1, notes="Notes")
            updated = await partial.edit(clientId=2)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.user_defined_object_2.update(self.id, **kwargs)
