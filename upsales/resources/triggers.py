"""
Triggers resource manager for Upsales API.

Provides methods to interact with the /triggers endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     trigger = await upsales.triggers.get(1)
    ...     triggers_list = await upsales.triggers.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.triggers import PartialTrigger, Trigger
from upsales.resources.base import BaseResource


class TriggersResource(BaseResource[Trigger, PartialTrigger]):
    """
    Resource manager for Trigger endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single trigger
    - list(limit, offset, **params) - List triggers with pagination
    - list_all(**params) - Auto-paginated list of all triggers
    - update(id, **data) - Update trigger
    - delete(id) - Delete trigger
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = TriggersResource(http_client)
        >>> trigger = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize triggers resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/triggers",
            model_class=Trigger,
            partial_class=PartialTrigger,
        )

    async def get_active(self) -> list[Trigger]:
        """
        Get all active triggers.

        Returns:
            List of active triggers (active == 1).

        Example:
            >>> resource = TriggersResource(http_client)
            >>> active_triggers = await resource.get_active()
            >>> assert all(t.is_active for t in active_triggers)
        """
        all_triggers: list[Trigger] = await self.list_all()
        return [t for t in all_triggers if t.is_active]

    async def get_by_name(self, name: str) -> Trigger | None:
        """
        Get trigger by name.

        Args:
            name: Trigger name to search for.

        Returns:
            Trigger if found, None otherwise.

        Example:
            >>> resource = TriggersResource(http_client)
            >>> trigger = await resource.get_by_name("My Trigger")
        """
        all_triggers: list[Trigger] = await self.list_all()
        for trigger in all_triggers:
            if trigger.name == name:
                return trigger
        return None

    async def get_by_event(self, event: str) -> list[Trigger]:
        """
        Get triggers that listen to a specific event.

        Args:
            event: Event name (e.g., "after_order_insert").

        Returns:
            List of triggers containing the specified event.

        Example:
            >>> resource = TriggersResource(http_client)
            >>> order_triggers = await resource.get_by_event("after_order_insert")
        """
        all_triggers: list[Trigger] = await self.list_all()
        return [t for t in all_triggers if event in t.events]
