"""Unsubs resource manager for Upsales API.

Provides methods to unsubscribe and resubscribe contacts from email communications.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Unsubscribe a contact
        unsub = await upsales.unsub.unsubscribe(contact_id=123)

        # Resubscribe a contact
        await upsales.unsub.resubscribe(contact_id=123)
    ```
"""

from upsales.http import HTTPClient
from upsales.models.unsub import PartialUnsub, Unsub
from upsales.resources.base import BaseResource


class UnsubsResource(BaseResource[Unsub, PartialUnsub]):
    """Resource manager for Unsub endpoint.

    This endpoint manages contact unsubscribe/resubscribe operations for email communications.
    It only supports two operations:
    - POST: Unsubscribe a contact
    - DELETE: Resubscribe a contact

    Note:
        This endpoint does not support GET, list, or update operations.

    Example:
        ```python
        resource = UnsubsResource(http_client)
        # Unsubscribe contact
        unsub = await resource.unsubscribe(contact_id=123)
        # Resubscribe contact
        await resource.resubscribe(contact_id=123)
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize unsub resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/function/unsub",
            model_class=Unsub,
            partial_class=PartialUnsub,
        )

    async def unsubscribe(self, contact_id: int) -> Unsub:
        """Unsubscribe a contact from email communications.

        Args:
            contact_id: The ID of the contact to unsubscribe.

        Returns:
            Unsub instance representing the unsubscribe record.

        Raises:
            ValidationError: If the contact_id is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If the server encounters an error.

        Example:
            ```python
            # Unsubscribe contact 123
            unsub = await upsales.unsub.unsubscribe(contact_id=123)
            print(f"Unsubscribed contact {unsub.id}")
            ```
        """
        return await self.create(id=contact_id)

    async def resubscribe(self, contact_id: int) -> None:
        """Resubscribe a contact to email communications.

        Requires Administrator or mailAdmin permissions.

        Args:
            contact_id: The ID of the contact to resubscribe.

        Raises:
            NotFoundError: If the contact is not unsubscribed.
            AuthenticationError: If authentication fails or insufficient permissions.
            ServerError: If the server encounters an error.

        Example:
            ```python
            # Resubscribe contact 123
            await upsales.unsub.resubscribe(contact_id=123)
            print("Contact resubscribed successfully")
            ```
        """
        await self.delete(contact_id)
