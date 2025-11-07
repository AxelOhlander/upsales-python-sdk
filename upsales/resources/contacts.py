"""
Contacts resource manager for Upsales API.

Provides methods to interact with the /contacts endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     contact = await upsales.contacts.get(1)
    ...     contacts = await upsales.contacts.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.contacts import Contact, PartialContact
from upsales.resources.base import BaseResource


class ContactsResource(BaseResource[Contact, PartialContact]):
    """
    Resource manager for Contact endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single contact
    - list(limit, offset, **params) - List contacts with pagination
    - list_all(**params) - Auto-paginated list of all contacts
    - update(id, **data) - Update contact
    - delete(id) - Delete contact
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> contacts = ContactsResource(http_client)
        >>> contact = await contacts.get(1)
        >>> all_active = await contacts.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize contacts resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/contacts",
            model_class=Contact,
            partial_class=PartialContact,
        )

    async def get_by_email(self, email: str) -> Contact | None:
        """
        Get contact by email address.

        Args:
            email: Email address to search for.

        Returns:
            Contact if found, None otherwise.

        Example:
            >>> contact = await upsales.contacts.get_by_email("john@example.com")
            >>> if contact:
            ...     print(contact.name)
        """
        all_contacts: list[Contact] = await self.list_all()
        for contact in all_contacts:
            if contact.email.lower() == email.lower():
                return contact
        return None

    async def get_by_company(self, company_id: int) -> list[Contact]:
        """
        Get all contacts for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of contacts belonging to the company.

        Example:
            >>> contacts = await upsales.contacts.get_by_company(123)
            >>> len(contacts)
            5
        """
        # Note: Uses 'client' as the API field name for company filter
        all_contacts: list[Contact] = await self.list_all()
        return [
            contact
            for contact in all_contacts
            if contact.client and contact.client.id == company_id
        ]

    async def get_active(self) -> list[Contact]:
        """
        Get all active contacts.

        Returns:
            List of contacts with active=1.

        Example:
            >>> active = await upsales.contacts.get_active()
            >>> all(c.is_active for c in active)
            True
        """
        return await self.list_all(active=1)

    async def get_priority(self) -> list[Contact]:
        """
        Get all priority contacts.

        Returns:
            List of contacts with isPriority=True.

        Example:
            >>> priority = await upsales.contacts.get_priority()
            >>> all(c.isPriority for c in priority)
            True
        """
        all_contacts: list[Contact] = await self.list_all()
        return [contact for contact in all_contacts if contact.isPriority]
