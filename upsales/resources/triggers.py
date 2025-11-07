"""
Triggers resource manager for Upsales API.

Provides methods to interact with the /triggers endpoint using Trigger models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single trigger
    ...     trigger = await upsales.triggers.get(1001003)
    ...     print(trigger.name, trigger.is_active)
    ...
    ...     # List triggers
    ...     triggers = await upsales.triggers.list(limit=10)
    ...
    ...     # Get all active triggers
    ...     active = await upsales.triggers.get_active()
    ...
    ...     # Get triggers by event
    ...     order_triggers = await upsales.triggers.get_by_event("after_order_insert")
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
    - create(**data) - Create new trigger
    - update(id, **data) - Update trigger
    - delete(id) - Delete trigger
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active triggers
    - get_by_name(name) - Get trigger by name
    - get_by_event(event) - Get triggers for specific event

    Example:
        >>> triggers = TriggersResource(http_client)
        >>> trigger = await triggers.get(1001003)
        >>> active = await triggers.get_active()
        >>> order_triggers = await triggers.get_by_event("after_order_insert")
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
            List of triggers with active=1.

        Example:
            >>> active_triggers = await upsales.triggers.get_active()
            >>> for trigger in active_triggers:
            ...     print(f"{trigger.name} - {len(trigger.events)} events")
        """
        all_triggers: list[Trigger] = await self.list_all()
        return [trigger for trigger in all_triggers if trigger.is_active]

    async def get_by_name(self, name: str) -> Trigger | None:
        """
        Get trigger by name.

        Args:
            name: Trigger name to search for (case-insensitive).

        Returns:
            Trigger object if found, None otherwise.

        Example:
            >>> trigger = await upsales.triggers.get_by_name("Order Meeting Creator")
            >>> if trigger:
            ...     print(len(trigger.actions))
        """
        all_triggers: list[Trigger] = await self.list_all()
        for trigger in all_triggers:
            if trigger.name.lower() == name.lower():
                return trigger
        return None

    async def get_by_event(self, event: str) -> list[Trigger]:
        """
        Get all triggers that respond to a specific event.

        Args:
            event: Event name to filter by (e.g., "after_order_insert").

        Returns:
            List of triggers that have the specified event in their events list.

        Example:
            >>> order_triggers = await upsales.triggers.get_by_event("after_order_insert")
            >>> for trigger in order_triggers:
            ...     print(f"{trigger.name} - {len(trigger.actions)} actions")
        """
        all_triggers: list[Trigger] = await self.list_all()
        return [trigger for trigger in all_triggers if event in trigger.events]
