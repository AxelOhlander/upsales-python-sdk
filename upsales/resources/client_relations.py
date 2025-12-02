"""Client relations resource manager for Upsales API.

This module provides the resource manager for client relation operations,
including CRUD operations for managing relationships between client accounts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.client_relations import ClientRelation, PartialClientRelation
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ClientRelationsResource(BaseResource[ClientRelation, PartialClientRelation]):
    """Resource manager for client relation operations.

    Handles all client relation-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Bulk operations

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create relation
        >>> relation = await upsales.client_relations.create(
        ...     clientId=100,
        ...     relatedToClientId=200,
        ...     description="Subsidiary"
        ... )
        >>>
        >>> # Get relation
        >>> relation = await upsales.client_relations.get(1)
        >>>
        >>> # List all relations
        >>> relations = await upsales.client_relations.list_all()
        >>>
        >>> # Update relation
        >>> updated = await upsales.client_relations.update(
        ...     1,
        ...     description="Branch office",
        ...     descriptionChildParent="Main office"
        ... )
        >>>
        >>> # Delete relation
        >>> await upsales.client_relations.delete(1)

        Find relations for a specific client:

        >>> relations = await upsales.client_relations.get_by_client(100)
        >>> for rel in relations:
        ...     print(f"Related to: {rel.relatedToClientId}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the client relations resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/clientrelations",
            model_class=ClientRelation,
            partial_class=PartialClientRelation,
        )

    async def get_by_client(self, client_id: int) -> list[ClientRelation]:
        """Get all relations for a specific client.

        Args:
            client_id: The client account ID to find relations for.

        Returns:
            List of ClientRelation objects where the client is involved.

        Examples:
            >>> relations = await upsales.client_relations.get_by_client(100)
            >>> print(f"Found {len(relations)} relations")
        """
        all_relations: list[ClientRelation] = await self.list_all()
        return [
            rel
            for rel in all_relations
            if rel.clientId == client_id or rel.relatedToClientId == client_id
        ]

    async def get_children(self, parent_client_id: int) -> list[ClientRelation]:
        """Get all child relations for a parent client.

        Args:
            parent_client_id: The parent client account ID.

        Returns:
            List of ClientRelation objects where this client is the parent.

        Examples:
            >>> children = await upsales.client_relations.get_children(100)
            >>> for child in children:
            ...     print(f"Child: {child.relatedToClientId}")
        """
        all_relations: list[ClientRelation] = await self.list_all()
        return [rel for rel in all_relations if rel.clientId == parent_client_id]
