"""List views resource manager for Upsales API.

Provides methods to interact with the /listViews/:entity endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     view = await upsales.list_views.get("account", 1)
    ...     views_list = await upsales.list_views.list("account", limit=10)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.list_views import ListView


class ListViewsResource:
    """Resource manager for ListView endpoint.

    The listViews endpoint requires an entity parameter in the path,
    so it doesn't follow the standard BaseResource pattern.

    Example:
        >>> resource = ListViewsResource(http_client)
        >>> view = await resource.get("account", 1)
        >>> all_views = await resource.list("account")
    """

    def __init__(self, http: HTTPClient):
        """Initialize list views resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self.http = http

    async def get(self, entity: str, view_id: int) -> ListView:
        """Get a single list view by ID for a specific entity.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            view_id: List view ID

        Returns:
            ListView instance with all fields populated.

        Raises:
            NotFoundError: If the list view is not found.
            UpsalesError: If the API request fails.

        Example:
            >>> view = await upsales.list_views.get("account", 1)
            >>> view.title
            'Active Accounts'
        """
        response = await self.http.get(f"/listViews/{entity}/{view_id}")
        return ListView.model_validate(response, context={"client": self.http._client})

    async def list(
        self, entity: str, limit: int = 100, offset: int = 0, **params: Any
    ) -> list[ListView]:
        """List list views for a specific entity with pagination.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            limit: Maximum number of results to return (default: 100)
            offset: Number of results to skip (default: 0)
            **params: Additional query parameters

        Returns:
            List of ListView instances.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> views = await upsales.list_views.list("account", limit=10)
            >>> len(views)
            10
        """
        all_params = {"limit": limit, "offset": offset} | params
        response = await self.http.get(f"/listViews/{entity}", params=all_params)
        data_list = response if isinstance(response, list) else [response]
        return [
            ListView.model_validate(item, context={"client": self.http._client})
            for item in data_list
        ]

    async def list_all(self, entity: str, **params: Any) -> list[ListView]:  # type: ignore[valid-type]
        """List all list views for a specific entity with automatic pagination.

        Automatically handles pagination to retrieve all results.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            **params: Additional query parameters

        Returns:
            List of all ListView instances.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> all_views = await upsales.list_views.list_all("account")
            >>> len(all_views)
            45
        """
        all_items: list[ListView] = []
        offset = 0
        limit = 100

        while True:
            batch = await self.list(entity, limit=limit, offset=offset, **params)
            if not batch:
                break
            all_items.extend(batch)
            if len(batch) < limit:
                break
            offset += limit

        return all_items

    async def create(self, entity: str, **data: Any) -> ListView:
        """Create a new list view for a specific entity.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            **data: List view data including required fields:
                   - title (str): View title
                   - listType (str): Type of list
                   - type (str): View type
                   Optional fields: description, grouping, columns, sorting,
                                   filters, limit, roleId, default

        Returns:
            Created ListView instance with ID assigned.

        Raises:
            ValidationError: If required fields are missing.
            UpsalesError: If the API request fails.

        Example:
            >>> view = await upsales.list_views.create(
            ...     "account",
            ...     title="Active Accounts",
            ...     listType="account",
            ...     type="custom"
            ... )
            >>> view.id
            123
        """
        response = await self.http.post(f"/listViews/{entity}", json=data)
        return ListView.model_validate(response, context={"client": self.http._client})

    async def update(self, entity: str, view_id: int, **data: Any) -> ListView:
        """Update an existing list view.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            view_id: List view ID
            **data: Fields to update (title, description, grouping, columns,
                   sorting, filters, limit, default, roleId)

        Returns:
            Updated ListView instance.

        Raises:
            NotFoundError: If the list view is not found.
            ValidationError: If field validation fails.
            UpsalesError: If the API request fails.

        Example:
            >>> updated = await upsales.list_views.update(
            ...     "account",
            ...     1,
            ...     title="Updated Title",
            ...     default=True
            ... )
            >>> updated.title
            'Updated Title'
        """
        response = await self.http.put(f"/listViews/{entity}/{view_id}", json=data)
        return ListView.model_validate(response, context={"client": self.http._client})

    async def delete(self, entity: str, view_id: int) -> None:
        """Delete a list view.

        Args:
            entity: Entity type (e.g., "account", "contact", "order")
            view_id: List view ID

        Raises:
            NotFoundError: If the list view is not found.
            UpsalesError: If the API request fails.

        Example:
            >>> await upsales.list_views.delete("account", 1)
        """
        await self.http.delete(f"/listViews/{entity}/{view_id}")
