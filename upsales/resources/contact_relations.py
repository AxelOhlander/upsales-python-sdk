"""Contact relations resource manager for Upsales API.

This module provides the resource manager for contact relation operations,
including CRUD operations for managing relationships between contacts and client accounts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.contact_relations import ContactRelation, PartialContactRelation
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ContactRelationsResource(BaseResource[ContactRelation, PartialContactRelation]):
    """Resource manager for contact relation operations.

    Handles all contact relation-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Bulk operations

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create relation
        >>> relation = await upsales.contact_relations.create(
        ...     contactId=500,
        ...     relatedToClientId=100,
        ...     description="Consultant"
        ... )
        >>>
        >>> # Get relation
        >>> relation = await upsales.contact_relations.get(1)
        >>>
        >>> # List all relations
        >>> relations = await upsales.contact_relations.list_all()
        >>>
        >>> # Update relation
        >>> updated = await upsales.contact_relations.update(
        ...     1, description="Senior consultant"
        ... )
        >>>
        >>> # Delete relation
        >>> await upsales.contact_relations.delete(1)

        Find relations for a specific contact:

        >>> relations = await upsales.contact_relations.get_by_contact(500)
        >>> for rel in relations:
        ...     print(f"Related to client: {rel.relatedToClientId}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the contact relations resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/contactrelation",
            model_class=ContactRelation,
            partial_class=PartialContactRelation,
        )

    async def get_by_contact(self, contact_id: int) -> list[ContactRelation]:
        """Get all relations for a specific contact.

        Args:
            contact_id: The contact ID to find relations for.

        Returns:
            List of ContactRelation objects for this contact.

        Examples:
            >>> relations = await upsales.contact_relations.get_by_contact(500)
            >>> print(f"Found {len(relations)} relations")
        """
        all_relations: list[ContactRelation] = await self.list_all()
        return [rel for rel in all_relations if rel.contactId == contact_id]

    async def get_by_client(self, client_id: int) -> list[ContactRelation]:
        """Get all relations for a specific client.

        Args:
            client_id: The client account ID to find relations for.

        Returns:
            List of ContactRelation objects associated with this client.

        Examples:
            >>> relations = await upsales.contact_relations.get_by_client(100)
            >>> for rel in relations:
            ...     print(f"Contact: {rel.contactId}")
        """
        all_relations: list[ContactRelation] = await self.list_all()
        return [rel for rel in all_relations if rel.relatedToClientId == client_id]
