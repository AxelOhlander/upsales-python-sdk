"""
Events resource manager for Upsales API.

Provides methods to interact with the /events endpoint.

Note: The events endpoint has special requirements:
- List operations require a 'q' filter parameter
- Update (PUT/PATCH) operations are not supported
- Only CREATE, DELETE, and filtered LIST operations are available

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # List with filter (required)
    ...     events_list = await upsales.events.list(q="entityType:manual")
    ...     # Create new event
    ...     event = await upsales.events.create(
    ...         entityType="manual",
    ...         score=5,
    ...         client={"id": 1}
    ...     )
    ...     # Delete event
    ...     await upsales.events.delete(event.id)
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.events import Event, PartialEvent
from upsales.resources.base import BaseResource


class EventsResource(BaseResource[Event, PartialEvent]):
    """
    Resource manager for Event endpoint.

    Note: Events have limited operations compared to other resources:
    - CREATE (POST) - Supported
    - DELETE - Supported
    - LIST - Supported (requires 'q' filter parameter)
    - GET by ID - Supported via list filtering
    - UPDATE (PUT/PATCH) - NOT supported by API

    Inherited operations from BaseResource:
    - create(**data) - Create new event
    - list(limit, offset, **params) - List events with required filter
    - list_all(**params) - Auto-paginated list of all events
    - delete(id) - Delete event
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Not supported:
    - update(id, **data) - Raises NotImplementedError
    - bulk_update(ids, data, max_concurrent) - Raises NotImplementedError

    Example:
        >>> resource = EventsResource(http_client)
        >>> # List manual events
        >>> manual = await resource.list(q="entityType:manual")
        >>> # Create marketing event
        >>> event = await resource.create(
        ...     entityType="marketingCustom",
        ...     score=10,
        ...     client={"id": 5},
        ...     notify=True
        ... )
        >>> # Delete event
        >>> await resource.delete(event.id)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize events resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/events",
            model_class=Event,
            partial_class=PartialEvent,
        )

    async def update(self, resource_id: int, **data: Any) -> Event:
        """
        Update an event.

        Note: The Upsales API does not support updating events.
        Events can only be created and deleted.

        Args:
            resource_id: Event ID to update.
            **data: Fields to update.

        Returns:
            Updated Event object.

        Raises:
            NotImplementedError: Events cannot be updated via API.

        Example:
            >>> await resource.update(1, score=5)  # Raises NotImplementedError
        """
        raise NotImplementedError(
            "Events cannot be updated. API only supports CREATE and DELETE operations."
        )

    async def get_by_type(self, entity_type: str, limit: int = 100) -> list[Event]:
        """
        Get events by entity type.

        Convenience method for filtering by entityType.

        Args:
            entity_type: Entity type to filter ('manual', 'marketingCustom', 'news', etc.).
            limit: Maximum number of events to return.

        Returns:
            List of events matching the entity type.

        Example:
            >>> manual_events = await resource.get_by_type("manual")
            >>> marketing = await resource.get_by_type("marketingCustom", limit=50)
        """
        return await self.list(q=f"entityType:{entity_type}", limit=limit)

    async def get_by_company(self, company_id: int, limit: int = 100) -> list[Event]:
        """
        Get events for a specific company.

        Args:
            company_id: Company/client ID to filter by.
            limit: Maximum number of events to return.

        Returns:
            List of events for the company.

        Example:
            >>> company_events = await resource.get_by_company(5)
        """
        return await self.list(q=f"client.id:{company_id}", limit=limit)
