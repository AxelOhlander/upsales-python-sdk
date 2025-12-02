"""Client relations models for Upsales API.

This module provides models for managing relationships between client accounts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from upsales.validators import PositiveInt


class ClientRelationUpdateFields(TypedDict, total=False):
    """Available fields for updating a ClientRelation.

    Attributes:
        clientId: Primary client account ID.
        relatedToClientId: Related client account ID.
        description: Relationship description (parent to child perspective).
        descriptionChildParent: Relationship description (child to parent perspective).
    """

    clientId: int
    relatedToClientId: int
    description: str
    descriptionChildParent: str


class ClientRelation(BaseModel):
    """Represents a relationship between client accounts in Upsales.

    Client relations define hierarchical or associative relationships between
    different client accounts (companies).

    Examples:
        Get a relation:

        >>> upsales = Upsales(token="...")
        >>> relation = await upsales.client_relations.get(1)
        >>> print(f"{relation.clientId} -> {relation.relatedToClientId}")

        Update a relation:

        >>> await relation.edit(
        ...     description="Subsidiary",
        ...     descriptionChildParent="Parent Company"
        ... )

        Create a new relation:

        >>> relation = await upsales.client_relations.create(
        ...     clientId=100,
        ...     relatedToClientId=200,
        ...     description="Branch office"
        ... )
    """

    # Read-only fields
    id: PositiveInt = Field(
        frozen=True, strict=True, description="Unique identifier for the relation"
    )

    # Required updatable fields
    clientId: PositiveInt = Field(description="Primary client account ID")
    relatedToClientId: PositiveInt = Field(description="Related client account ID")

    # Optional updatable fields
    description: str = Field(default="", description="Relationship description (parent to child)")
    descriptionChildParent: str = Field(
        default="", description="Relationship description (child to parent)"
    )

    async def edit(self, **kwargs: Unpack[ClientRelationUpdateFields]) -> ClientRelation:
        """Edit this client relation with the provided field updates.

        Args:
            **kwargs: Field updates (clientId, relatedToClientId, description, etc.).

        Returns:
            Updated ClientRelation instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Update relation descriptions:

            >>> relation = await upsales.client_relations.get(1)
            >>> updated = await relation.edit(
            ...     description="Regional office",
            ...     descriptionChildParent="Headquarters"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.client_relations.update(self.id, **self.to_api_dict(**kwargs))


class PartialClientRelation(PartialModel):
    """Partial client relation model for nested responses.

    This model is used when client relations appear as nested objects
    in other API responses.

    Examples:
        Access from parent object:

        >>> company = await upsales.companies.get(1)
        >>> if company.relations:
        ...     for relation in company.relations:
        ...         print(relation.description)

        Fetch full relation:

        >>> full_relation = await partial_relation.fetch_full()
    """

    id: PositiveInt = Field(description="Unique identifier")
    clientId: PositiveInt = Field(description="Primary client account ID")
    relatedToClientId: PositiveInt = Field(description="Related client account ID")

    async def fetch_full(self) -> ClientRelation:
        """Fetch the complete client relation object.

        Returns:
            Full ClientRelation instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the relation doesn't exist.

        Examples:
            >>> partial = PartialClientRelation(id=1, clientId=100, relatedToClientId=200)
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.client_relations.get(self.id)

    async def edit(self, **kwargs: Unpack[ClientRelationUpdateFields]) -> ClientRelation:
        """Edit this client relation with the provided field updates.

        Args:
            **kwargs: Field updates (clientId, relatedToClientId, description, etc.).

        Returns:
            Updated ClientRelation instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If invalid field values provided.

        Examples:
            Edit from partial:

            >>> partial = PartialClientRelation(id=1, clientId=100, relatedToClientId=200)
            >>> updated = await partial.edit(description="New description")
        """
        if not self._client:
            raise RuntimeError("No client available for this relation")
        return await self._client.client_relations.update(self.id, **kwargs)
