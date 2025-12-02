"""Contact relations models for Upsales API.

This module provides models for managing relationships between contacts and client accounts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from upsales.validators import PositiveInt


class ContactRelationUpdateFields(TypedDict, total=False):
    """Available fields for updating a ContactRelation.

    Attributes:
        contactId: Contact ID.
        relatedToClientId: Related client account ID.
        description: Relationship description.
    """

    contactId: int
    relatedToClientId: int
    description: str


class ContactRelation(BaseModel):
    """Represents a relationship between a contact and a client account in Upsales.

    Contact relations define associations between individual contacts and
    client accounts (companies).

    Examples:
        Get a relation:

        >>> upsales = Upsales(token="...")
        >>> relation = await upsales.contact_relations.get(1)
        >>> print(f"Contact {relation.contactId} -> Client {relation.relatedToClientId}")

        Update a relation:

        >>> await relation.edit(description="Board member")

        Create a new relation:

        >>> relation = await upsales.contact_relations.create(
        ...     contactId=500,
        ...     relatedToClientId=100,
        ...     description="Consultant"
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(
        frozen=True, strict=True, description="Unique identifier for the relation"
    )

    # Required updatable fields
    contactId: PositiveInt = Field(description="Contact ID")
    relatedToClientId: PositiveInt = Field(description="Related client account ID")

    # Optional updatable fields
    description: str = Field(default="", description="Relationship description")

    async def edit(self, **kwargs: Unpack[ContactRelationUpdateFields]) -> ContactRelation:
        """Edit this contact relation with the provided field updates.

        Args:
            **kwargs: Field updates (contactId, relatedToClientId, description).

        Returns:
            Updated ContactRelation instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update relation description:

            >>> relation = await upsales.contact_relations.get(1)
            >>> updated = await relation.edit(description="Primary consultant")
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.contact_relations.update(self.id, **self.to_api_dict(**kwargs))


class PartialContactRelation(PartialModel):
    """Partial contact relation model for nested responses.

    This model is used when contact relations appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> contact = await upsales.contacts.get(1)
        >>> if contact.relations:
        ...     for relation in contact.relations:
        ...         print(relation.description)

        Fetch full relation:

        >>> full_relation = await partial_relation.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    contactId: PositiveInt = Field(description="Contact ID")
    relatedToClientId: PositiveInt = Field(description="Related client account ID")

    async def fetch_full(self) -> ContactRelation:
        """Fetch the complete contact relation object.

        Returns:
            Full ContactRelation instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the relation doesn't exist.

        Examples:
            >>> partial = PartialContactRelation(id=1, contactId=500, relatedToClientId=100)
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.contact_relations.get(self.id)

    async def edit(self, **kwargs: Unpack[ContactRelationUpdateFields]) -> ContactRelation:
        """Edit this contact relation with the provided field updates.

        Args:
            **kwargs: Field updates (contactId, relatedToClientId, description).

        Returns:
            Updated ContactRelation instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialContactRelation(id=1, contactId=500, relatedToClientId=100)
            >>> updated = await partial.edit(description="New role")
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.contact_relations.update(self.id, **kwargs)
