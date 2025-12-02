"""Esign models for Upsales API.

This module defines models for esigns (electronic signature documents via Scrive integration).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import EsignUpdateFields


class Esign(BaseModel):
    """Esign model.

    Represents an electronic signature document (Scrive integration).

    Attributes:
        id: Unique esign ID (read-only).
        clientId: Associated client ID.
        userId: User ID (required for creation).
        opportunityId: Associated opportunity ID.
        documentId: Scrive document ID (read-only).
        upsalesStatus: Upsales status (read-only).
        type: Document type (read-only).
        state: Document state.
        title: Document title (required for creation).
        fileId: Associated file ID.
        signDate: Signature date.
        involved: List of involved parties.
        custom: Custom fields list.

    Example:
        ```python
        # Create esign
        esign = await upsales.esigns.create(
            userId=1,
            title="Contract Agreement"
        )

        # Update esign
        esign.state = "signed"
        updated = await esign.edit()

        # Or use edit with parameters
        updated = await esign.edit(state="signed", signDate="2024-01-15")
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique esign ID")
    documentId: str | None = Field(None, frozen=True, description="Scrive document ID")
    upsalesStatus: str | None = Field(None, frozen=True, description="Upsales status")
    type: str | None = Field(None, frozen=True, description="Document type")

    # Updatable fields
    userId: int = Field(description="User ID")
    title: str = Field(description="Document title")
    clientId: int = Field(0, description="Associated client ID")
    opportunityId: int = Field(0, description="Associated opportunity ID")
    state: str | None = Field(None, description="Document state")
    fileId: int | None = Field(None, description="Associated file ID")
    signDate: str | None = Field(None, description="Signature date")
    involved: list[dict] | None = Field(None, description="Involved parties")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            esign = await upsales.esigns.get(1)
            value = esign.custom_fields.get(11)
            esign.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    async def edit(self, **kwargs: Unpack[EsignUpdateFields]) -> Esign:
        """Edit this esign with type-safe field updates.

        Args:
            **kwargs: Fields to update (clientId, userId, opportunityId, title,
                     state, fileId, signDate, involved, custom).

        Returns:
            Updated Esign instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If esign no longer exists.

        Example:
            ```python
            esign = await upsales.esigns.get(1)

            # Update single field
            updated = await esign.edit(state="signed")

            # Update multiple fields
            updated = await esign.edit(
                state="signed",
                signDate="2024-01-15"
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.esigns.update(self.id, **self.to_api_dict(**kwargs))


class PartialEsign(PartialModel):
    """Partial esign model for nested responses.

    Used when esigns appear as nested objects in API responses.

    Attributes:
        id: Unique esign ID.
        title: Document title.

    Example:
        ```python
        # Fetch full esign from partial
        partial: PartialEsign = some_object.esign
        full: Esign = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(state="signed")
        ```
    """

    id: int = Field(description="Unique esign ID")
    title: str | None = Field(None, description="Document title")

    async def fetch_full(self) -> Esign:
        """Fetch complete esign data.

        Returns:
            Full Esign instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If esign not found.

        Example:
            ```python
            partial = PartialEsign(id=1, title="Contract")
            full = await partial.fetch_full()
            print(full.state)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.esigns.get(self.id)

    async def edit(self, **kwargs: Unpack[EsignUpdateFields]) -> Esign:
        """Edit this esign.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated Esign instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If esign not found.

        Example:
            ```python
            partial = PartialEsign(id=1, title="Contract")
            updated = await partial.edit(state="signed")
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.esigns.update(self.id, **kwargs)
