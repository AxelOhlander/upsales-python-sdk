"""
Base resource manager (TEMPLATE for Claude to replicate).

Uses Python 3.13 features:
- Type parameter syntax [T, P] for clean generics (no Generic[T] needed)
- Native type hints (no typing imports)
- Exception groups for bulk operations (Python 3.11+)
- Dictionary merge operator | (Python 3.9+)
- Free-threaded mode benefits for true parallelism

This is the TEMPLATE file that Claude should replicate when creating
new resource managers for API endpoints.

Example Subclass:
    >>> from upsales.models.user import User, PartialUser
    >>>
    >>> class UsersResource(BaseResource[User, PartialUser]):
    ...     def __init__(self, http: HTTPClient):
    ...         super().__init__(
    ...             http=http,
    ...             endpoint="/users",
    ...             model_class=User,
    ...             partial_class=PartialUser,
    ...         )
    ...
    ...     # Add endpoint-specific methods here
    ...     async def get_by_email(self, email: str) -> User | None:
    ...         response = await self._http.get(
    ...             self._endpoint,
    ...             email=email,
    ...         )
    ...         results = response["data"]
    ...         return self._model_class(**results[0]) if results else None
"""

from __future__ import annotations  # Required for type parameter syntax with subscripting

import asyncio
from typing import TYPE_CHECKING, Any

from upsales.http import HTTPClient

if TYPE_CHECKING:
    from upsales.http import HTTPClient  # noqa: F401

from upsales.models.base import BaseModel, PartialModel


class BaseResource[T: BaseModel, P: PartialModel]:
    """
    Base resource manager for API endpoints.

    This is a TEMPLATE class - subclasses implement specific resources
    (users, accounts, products, etc.) by inheriting from this class.

    Uses Python 3.13 type parameter syntax [T, P] for clean generic types.
    All CRUD operations are built-in: create(), get(), list(), update(), delete().
    Subclasses can add endpoint-specific methods.

    Type Parameters:
        T: Full model class (inherits from BaseModel).
        P: Partial model class (inherits from PartialModel).

    Args:
        http: HTTP client instance for making API requests.
        endpoint: API endpoint path (e.g., "/users", "/accounts").
        model_class: Full model class for this resource.
        partial_class: Partial model class for this resource.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path.
        _model_class: Class for full models.
        _partial_class: Class for partial models.

    Example:
        >>> class UsersResource(BaseResource[User, PartialUser]):
        ...     def __init__(self, http: HTTPClient):
        ...         super().__init__(
        ...             http=http,
        ...             endpoint="/users",
        ...             model_class=User,
        ...             partial_class=PartialUser,
        ...         )

    Note:
        With Python 3.13 free-threaded mode, bulk operations can achieve
        true parallelism without GIL contention, maximizing throughput
        within the Upsales API rate limits (200 req/10 sec).
    """

    def __init__(
        self,
        http: HTTPClient,
        endpoint: str,
        model_class: type[T],
        partial_class: type[P],
    ) -> None:
        """
        Initialize resource manager.

        Args:
            http: HTTP client instance.
            endpoint: API endpoint path (e.g., "/users").
            model_class: Full model class.
            partial_class: Partial model class.
        """
        self._http = http
        self._endpoint = endpoint
        self._model_class = model_class
        self._partial_class = partial_class

    def _prepare_http_kwargs(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Prepare HTTP kwargs, injecting the auto-initialization flag when needed.

        Args:
            params: Existing kwargs (query params, etc.).

        Returns:
            Updated kwargs dict.
        """
        kwargs = dict(params or {})
        if getattr(self._http, "_auto_allow_uninitialized", None) is True:
            kwargs["_allow_uninitialized"] = True
        return kwargs

    async def create(self, **data: Any) -> T:
        """
        Create a new resource.

        Makes a POST request to create a new resource with the provided data.

        Args:
            **data: Field values for the new resource.

        Returns:
            Newly created resource object with generated ID and server data.

        Raises:
            ValidationError: If required fields are missing or invalid (HTTP 400).
            AuthenticationError: If not authorized to create (HTTP 401/403).

        Example:
            >>> # Create a new user
            >>> user = await client.users.create(
            ...     name="John Doe",
            ...     email="john@example.com",
            ...     active=1,
            ...     administrator=0
            ... )
            >>> print(f"Created user {user.id}: {user.name}")
            >>>
            >>> # Create a company
            >>> company = await client.companies.create(
            ...     name="ACME Corporation",
            ...     phone="+1-555-0123",
            ...     active=1
            ... )

        Note:
            The API generates the ID and timestamps (regDate, modDate).
            These will be present in the returned object.
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.post(self._endpoint, **request_kwargs, **data)
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def get(self, resource_id: int) -> T:
        """
        Get a single resource by ID.

        Args:
            resource_id: Resource ID.

        Returns:
            Full resource object.

        Raises:
            NotFoundError: If resource with given ID doesn't exist.
            AuthenticationError: If authentication fails.

        Example:
            >>> user = await client.users.get(1)
            >>> print(f"{user.name = }, {user.email = }")
        """
        response = await self._http.get(
            f"{self._endpoint}/{resource_id}",
            **self._prepare_http_kwargs(),
        )
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def _list_with_metadata(
        self,
        limit: int = 100,
        offset: int = 0,
        fields: list[str] | None = None,
        sort: str | list[str] | None = None,
        **params: Any,
    ) -> tuple[list[T], dict[str, Any]]:
        """
        Internal helper for fetching a page with accompanying metadata.

        Returns:
            Tuple of (items, metadata dict).
        """
        all_params = params | {"limit": limit, "offset": offset}
        if fields:
            all_params["f[]"] = fields
        if sort:
            all_params["sort"] = sort
        response = await self._http.get(
            self._endpoint,
            **self._prepare_http_kwargs(all_params),
        )
        metadata = response.get("metadata") or {}
        items = [
            self._model_class(**item, _client=self._http._upsales_client)
            for item in response["data"]
        ]
        return items, metadata

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        fields: list[str] | None = None,
        sort: str | list[str] | None = None,
        **params: Any,
    ) -> list[T]:
        """
        List resources with pagination.

        Args:
            limit: Maximum results per page (default: 100).
            offset: Offset for pagination (default: 0).
            fields: Optional list of field names to return (optimization).
                   If specified, only these fields will be returned in response.
                   Use for faster queries and reduced bandwidth.
            sort: Optional sort field(s). Use "-field" for descending.
                 Single field: sort="name" or sort="-regDate"
                 Multiple fields: sort=["name", "-id"]
            **params: Additional query parameters for filtering.

        Returns:
            List of full resource objects.

        Example:
            >>> # Get first 50 users
            >>> users = await client.users.list(limit=50)
            >>>
            >>> # Sorted by name (ascending)
            >>> users = await client.users.list(sort="name")
            >>>
            >>> # Sorted by date (descending, newest first)
            >>> users = await client.users.list(sort="-regDate")
            >>>
            >>> # Multi-field sort
            >>> users = await client.users.list(sort=["name", "-id"])
            >>>
            >>> # With field selection (faster, reduced bandwidth)
            >>> users = await client.users.list(
            ...     limit=100,
            ...     fields=["id", "name", "email"]  # Only return these fields
            ... )
            >>>
            >>> # Everything combined!
            >>> active_users = await client.users.list(
            ...     active=1,
            ...     sort="-regDate",              # Newest first
            ...     fields=["id", "name", "email"]  # Optimized
            ... )

        Note:
            Field selection (f[] parameter) reduces response size and improves
            performance. Useful for dashboards and mobile apps.

            Sorting with "-field" (minus prefix) sorts descending. Not all fields
            may support sorting - test with your specific endpoint.
        """
        items, _ = await self._list_with_metadata(
            limit=limit,
            offset=offset,
            fields=fields,
            sort=sort,
            **params,
        )
        return items

    async def list_all(
        self,
        batch_size: int = 100,
        fields: list[str] | None = None,
        sort: str | list[str] | None = None,
        **params: Any,
    ) -> list[T]:
        """
        List all resources by automatically handling pagination.

        Fetches all pages and returns a combined list. Use with caution
        for large datasets.

        Args:
            batch_size: Number of items per request (default: 100).
            fields: Optional list of field names to return (optimization).
                   Reduces response size and improves performance.
            sort: Optional sort field(s). Use "-field" for descending.
                 Example: sort="name" or sort="-regDate" or sort=["name", "-id"]
            **params: Additional query parameters for filtering.

        Returns:
            List of all resource objects.

        Example:
            >>> # Get ALL users (careful with large datasets)
            >>> all_users = await client.users.list_all()
            >>>
            >>> # Sorted by name
            >>> users = await client.users.list_all(sort="name")
            >>>
            >>> # Sorted by date, newest first
            >>> users = await client.users.list_all(sort="-regDate")
            >>>
            >>> # With field selection for faster queries
            >>> users = await client.users.list_all(
            ...     fields=["id", "name", "email"],  # Only these fields
            ...     sort="name"                      # Sorted
            ... )
            >>>
            >>> # Everything combined!
            >>> active_users = await client.users.list_all(
            ...     active=1,
            ...     fields=["id", "name"],
            ...     sort="-regDate"  # Newest active users
            ... )

        Note:
            With Python 3.13 free-threaded mode, pagination requests
            can be fetched in parallel for better performance.

            Field selection reduces bandwidth and improves query speed.
            Sorting maintains order across all paginated requests.
        """
        collected: list[T] = []
        offset = 0
        total: int | None = None

        while True:
            page, metadata = await self._list_with_metadata(
                limit=batch_size,
                offset=offset,
                fields=fields,
                sort=sort,
                **params,
            )
            collected.extend(page)

            if total is None:
                total = metadata.get("total")

            fetch_more = True
            if total is not None and total < batch_size and offset == 0:
                fetch_more = False
            if total is not None:
                if len(collected) >= total or not page:
                    fetch_more = False
            else:
                if len(page) < batch_size:
                    fetch_more = False

            if not fetch_more:
                break

            offset += batch_size

        return collected

    async def search(
        self,
        fields: list[str] | None = None,
        sort: str | list[str] | None = None,
        **filters: Any,
    ) -> list[T]:
        """
        Search resources using comparison operators.

        Wrapper around list_all() that exposes Upsales API filtering capabilities.
        Supports both natural Python operators and Upsales API operator syntax.

        Filter Syntax (Natural Operators - Recommended):
            field=value              # Equals (default)
            field=">=value"          # Greater than or equals
            field=">value"           # Greater than
            field="<=value"          # Less than or equals
            field="<value"           # Less than
            field="=value"           # Equals (explicit)
            field="!=value"          # Not equals
            field="=1,2,3"           # Multiple values (IN)
            field="*value"           # Substring search (contains)

        Filter Syntax (API Syntax - Also Supported):
            field="gte:value"        # Greater than or equals
            field="gt:value"         # Greater than
            field="lte:value"        # Less than or equals
            field="lt:value"         # Less than
            field="eq:value"         # Equals
            field="ne:value"         # Not equals
            field="src:value"        # Substring search
            custom="eq:fieldId:val"  # Custom field filtering

        Args:
            fields: Optional list of field names to return (optimization).
                   Only specified fields will be included in response.
            sort: Optional sort field(s). Use "-field" for descending.
                 Example: sort="name" or sort="-regDate" or sort=["name", "-id"]
            **filters: Field-value pairs with optional comparison operators.

        Returns:
            List of resources matching ALL filter criteria (AND logic).

        Example:
            >>> # Simple equality
            >>> active_users = await client.users.search(active=1)
            >>>
            >>> # Natural operators (recommended)
            >>> recent_users = await client.users.search(
            ...     active=1,
            ...     regDate=">=2024-01-01"  # Natural syntax
            ... )
            >>>
            >>> # API syntax (also works)
            >>> recent_users = await client.users.search(
            ...     active=1,
            ...     regDate="gte:2024-01-01"  # API syntax
            ... )
            >>>
            >>> # Range queries with natural operators
            >>> products = await client.products.search(
            ...     active=1,
            ...     listPrice=">100",      # Natural syntax
            ...     listPrice="<1000"      # Natural syntax
            ... )
            >>>
            >>> # Multiple values with natural syntax
            >>> users = await client.users.search(
            ...     role_id="=1,2,3"  # Natural IN operator
            ... )
            >>>
            >>> # Custom fields (both syntaxes work)
            >>> companies = await client.companies.search(
            ...     custom="=11:Technology"      # Natural
            ...     # OR: custom="eq:11:Technology"  # API syntax
            ... )
            >>>
            >>> # Substring search (wildcard)
            >>> contacts = await client.contacts.search(
            ...     phone="*555"  # Contains "555"
            ... )
            >>> companies = await client.companies.search(
            ...     name="*ACME"  # Name contains "ACME"
            ... )
            >>>
            >>> # Field selection with search (performance optimization)
            >>> companies = await client.companies.search(
            ...     active=1,
            ...     name="*Tech",
            ...     fields=["id", "name", "phone"]  # Only return these
            ... )
            >>>
            >>> # Search with sorting
            >>> recent_users = await client.users.search(
            ...     active=1,
            ...     sort="-regDate"  # Newest first
            ... )
            >>>
            >>> # Everything combined!
            >>> results = await client.companies.search(
            ...     name="*Tech",
            ...     employees=">10",
            ...     fields=["id", "name", "phone"],
            ...     sort="-regDate"  # Newest tech companies with 10+ employees
            ... )

        Note:
            Natural operators (>=, >, <, <=, =, !=, *) are automatically
            transformed to Upsales API syntax (gte:, gt:, lt:, lte:, eq:, ne:, src:).
            Both syntaxes work - use whichever you prefer!

            Field selection reduces response size and improves query performance.
            Especially useful for mobile apps, dashboards, or large result sets.

            Not all fields support all operators. Binary flags (0/1) typically
            only support eq/=, ne/!=. Date and numeric fields support full range.
            Substring search (*) works on string fields.
        """
        # Transform natural operators to Upsales API syntax
        # Operator mapping: Natural Python → Upsales API
        # Check longer operators first (>= before >) to avoid partial matches
        operator_map = {
            ">=": "gte:",
            "<=": "lte:",
            "!=": "ne:",
            ">": "gt:",
            "<": "lt:",
            "=": "eq:",
            "*": "src:",  # Substring search (wildcard)
        }

        transformed_filters: dict[str, Any] = {}
        for field, value in filters.items():
            if isinstance(value, str):
                # Check if value starts with a natural operator
                for natural_op, api_op in operator_map.items():
                    if value.startswith(natural_op):
                        # Transform: ">=100" → "gte:100"
                        transformed_value = api_op + value[len(natural_op) :]
                        transformed_filters[field] = transformed_value
                        break
                else:
                    # No natural operator found - pass through unchanged
                    # This maintains backward compatibility with "gte:", "gt:", etc.
                    transformed_filters[field] = value
            else:
                # Non-string values pass through unchanged (e.g., active=1)
                transformed_filters[field] = value

        return await self.list_all(fields=fields, sort=sort, **transformed_filters)

    async def update(self, resource_id: int, **data: Any) -> T:
        """
        Update a resource.

        Args:
            resource_id: Resource ID to update.
            **data: Fields to update with new values.

        Returns:
            Updated resource object with fresh data from API.

        Example:
            >>> user = await client.users.update(1, name="New Name")
            >>> print(f"{user.name = }")
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.put(
            f"{self._endpoint}/{resource_id}",
            **request_kwargs,
            **data,
        )
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def delete(self, resource_id: int) -> dict[str, Any]:
        """
        Delete a resource.

        Args:
            resource_id: Resource ID to delete.

        Returns:
            Response data from API.

        Example:
            >>> await client.users.delete(1)
        """
        return await self._http.delete(
            f"{self._endpoint}/{resource_id}",
            **self._prepare_http_kwargs(),
        )

    async def bulk_update(
        self,
        ids: list[int],
        data: dict[str, Any],
        max_concurrent: int | None = None,
    ) -> list[T]:
        """
        Bulk update multiple resources with rate limiting.

        Leverages Python 3.13 free-threaded mode for true parallelism,
        allowing concurrent requests to run without GIL contention.

        Uses a semaphore to limit concurrent requests and respect the
        Upsales API rate limit (200 req/10 sec).

        Args:
            ids: List of resource IDs to update.
            data: Fields to update (applied to all resources).
            max_concurrent: Maximum concurrent requests (default: from client).

        Returns:
            List of updated resource objects.

        Raises:
            ExceptionGroup: If any updates fail. Contains all exceptions
                that occurred during the bulk operation (Python 3.11+).

        Example:
            >>> # Deactivate 100 products
            >>> products = await client.products.bulk_update(
            ...     ids=list(range(1, 101)),
            ...     data={"active": 0},
            ... )
            >>>
            >>> # With custom concurrency
            >>> products = await client.products.bulk_update(
            ...     ids=[1, 2, 3],
            ...     data={"price": 99.99},
            ...     max_concurrent=10,
            ... )

        Note:
            With Python 3.13's free-threaded mode, these requests can truly
            run in parallel without GIL contention. This maximizes throughput
            within the 200 req/10 sec rate limit, especially for I/O-bound
            operations like API requests.

            To enable free-threaded mode:
                python -X gil=0 your_script.py
        """
        max_concurrent = max_concurrent or self._http.max_concurrent
        semaphore = asyncio.Semaphore(max_concurrent)

        async def update_one(item_id: int) -> T:
            """Update a single resource with semaphore control."""
            async with semaphore:
                return await self.update(item_id, **data)

        # Gather all results, including exceptions
        results = await asyncio.gather(
            *[update_one(item_id) for item_id in ids],
            return_exceptions=True,
        )

        # Separate successes and failures
        successes: list[T] = [r for r in results if not isinstance(r, Exception)]
        errors: list[Exception] = [r for r in results if isinstance(r, Exception)]

        # Use ExceptionGroup if there are errors (Python 3.11+)
        if errors:
            raise ExceptionGroup(
                f"Failed to update {len(errors)}/{len(ids)} items",
                errors,
            )

        return successes

    async def bulk_delete(
        self,
        ids: list[int],
        max_concurrent: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Bulk delete multiple resources with rate limiting.

        Args:
            ids: List of resource IDs to delete.
            max_concurrent: Maximum concurrent requests (default: from client).

        Returns:
            List of response dicts from API.

        Raises:
            ExceptionGroup: If any deletes fail (Python 3.11+).

        Example:
            >>> await client.users.bulk_delete([1, 2, 3])

        Note:
            With Python 3.13 free-threaded mode, delete operations can
            run in true parallel without GIL contention.
        """
        max_concurrent = max_concurrent or self._http.max_concurrent
        semaphore = asyncio.Semaphore(max_concurrent)

        async def delete_one(item_id: int) -> dict[str, Any]:
            """Delete a single resource with semaphore control."""
            async with semaphore:
                return await self.delete(item_id)

        # Gather all results, including exceptions
        results = await asyncio.gather(
            *[delete_one(item_id) for item_id in ids],
            return_exceptions=True,
        )

        # Separate successes and failures
        successes: list[dict[str, Any]] = [r for r in results if not isinstance(r, Exception)]
        errors: list[Exception] = [r for r in results if isinstance(r, Exception)]

        # Use ExceptionGroup if there are errors
        if errors:
            raise ExceptionGroup(
                f"Failed to delete {len(errors)}/{len(ids)} items",
                errors,
            )

        return successes
