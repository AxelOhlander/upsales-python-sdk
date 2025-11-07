# Adding Resources

Guide for creating resource managers for Upsales API endpoints using Python 3.13 type parameter syntax.

## Overview

Resource managers handle CRUD operations for API endpoints. They inherit from `BaseResource` which provides:

- `get(id)` - Get single resource
- `list(limit, offset, **params)` - List with pagination
- `list_all(**params)` - Get all (auto-pagination)
- `update(id, **data)` - Update resource
- `delete(id)` - Delete resource
- `bulk_update(ids, data, max_concurrent)` - Bulk update with concurrency
- `bulk_delete(ids, max_concurrent)` - Bulk delete with concurrency

## Real-World Examples

See these production implementations for reference:
- `upsales/resources/companies.py` - CompaniesResource (accounts endpoint)
- `upsales/resources/products.py` - ProductsResource with custom methods
- `upsales/resources/users.py` - UsersResource with filtering methods

All use Pydantic v2 models with validators, computed fields, and optimized serialization.

## Type Parameter Syntax (Python 3.12+)

Use the clean type parameter syntax `[T, P]`:

### ✅ Correct

```python
from upsales.resources.base import BaseResource
from upsales.models.user import User, PartialUser

class UsersResource(BaseResource[User, PartialUser]):
    pass
```

### ❌ Incorrect (old syntax)

```python
# Don't use this old pattern
from typing import Generic, TypeVar

T = TypeVar('T')
P = TypeVar('P')

class UsersResource(BaseResource, Generic[T, P]):
    pass
```

## Basic Resource Structure

```python
"""
Users resource manager for Upsales API.

Uses Python 3.13 type parameter syntax.
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.user import User, PartialUser
from upsales.resources.base import BaseResource


class UsersResource(BaseResource[User, PartialUser]):
    """
    Resource manager for /users endpoint.

    Inherits all CRUD operations from BaseResource.
    Add endpoint-specific methods for custom functionality.

    Example:
        >>> async with Upsales(token="...") as upsales:
        ...     # Basic operations (from BaseResource)
        ...     user = await upsales.users.get(1)
        ...     users = await upsales.users.list(limit=50)
        ...     updated = await upsales.users.update(1, name="New")
        ...
        ...     # Custom methods
        ...     admin = await upsales.users.get_by_email("admin@company.com")
        ...     admins = await upsales.users.get_administrators()
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize users resource.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/users",
            model_class=User,
            partial_class=PartialUser,
        )

    # Add endpoint-specific methods below
    # ...
```

## Adding Custom Methods

### Query by Field

```python
async def get_by_email(self, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        email: Email address to search for.

    Returns:
        User if found, None otherwise.

    Example:
        >>> user = await upsales.users.get_by_email("john@example.com")
        >>> if user:
        ...     print(f"Found: {user.name}")
    """
    response = await self._http.get(self._endpoint, email=email)
    results = response["data"]
    return (
        self._model_class(**results[0], _client=self._http._client)
        if results
        else None
    )
```

### Filtered Lists

```python
async def get_administrators(self) -> list[User]:
    """
    Get all administrator users.

    Returns:
        List of users with administrator=1.

    Example:
        >>> admins = await upsales.users.get_administrators()
        >>> for admin in admins:
        ...     print(admin.name)
    """
    return await self.list_all(administrator=1)

async def get_active(self) -> list[User]:
    """
    Get all active users.

    Returns:
        List of active users.
    """
    return await self.list_all(active=1)
```

### Custom Bulk Operations

```python
async def bulk_activate(self, ids: list[int]) -> list[Product]:
    """
    Activate multiple products.

    Args:
        ids: List of product IDs to activate.

    Returns:
        List of updated products.

    Example:
        >>> products = await upsales.products.bulk_activate([1, 2, 3])

    Note:
        With Python 3.13 free-threaded mode, activations run in
        true parallel without GIL contention.
    """
    return await self.bulk_update(ids, {"active": 1})

async def bulk_deactivate(self, ids: list[int]) -> list[Product]:
    """
    Deactivate multiple products.

    Args:
        ids: List of product IDs to deactivate.

    Returns:
        List of updated products.
    """
    return await self.bulk_update(ids, {"active": 0})
```

### Complex Searches

```python
async def search(
    self,
    name: str | None = None,
    email: str | None = None,
    active: int | None = None,
    limit: int = 100,
) -> list[User]:
    """
    Search users with multiple filters.

    Args:
        name: Filter by name (partial match).
        email: Filter by email (partial match).
        active: Filter by active status (0 or 1).
        limit: Maximum results to return.

    Returns:
        List of matching users.

    Example:
        >>> # Find active users named John
        >>> users = await upsales.users.search(
        ...     name="John",
        ...     active=1
        ... )
    """
    params: dict[str, Any] = {"limit": limit}

    if name is not None:
        params["name"] = name
    if email is not None:
        params["email"] = email
    if active is not None:
        params["active"] = active

    response = await self._http.get(self._endpoint, **params)
    return [
        self._model_class(**item, _client=self._http._client)
        for item in response["data"]
    ]
```

## Pattern Matching for Response Handling

Use pattern matching for complex response structures:

```python
async def get_with_fallback(self, id: int) -> User | None:
    """
    Get user with graceful fallback on errors.

    Args:
        id: User ID.

    Returns:
        User if found, None if not found or error.
    """
    try:
        response = await self._http.get(f"{self._endpoint}/{id}")
    except Exception as e:
        # Pattern matching for error handling
        match e:
            case NotFoundError():
                return None
            case AuthenticationError():
                raise  # Re-raise auth errors
            case _:
                # Log other errors but return None
                print(f"Error fetching user {id}: {e}")
                return None

    return self._model_class(**response["data"], _client=self._http._client)
```

## Complete Example

Full resource with multiple custom methods:

```python
"""
Products resource manager for Upsales API.

Uses Python 3.13 type parameter syntax.
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.product import Product, PartialProduct
from upsales.resources.base import BaseResource


class ProductsResource(BaseResource[Product, PartialProduct]):
    """
    Resource manager for /products endpoint.

    Provides CRUD operations plus product-specific functionality
    like bulk activation/deactivation and price updates.

    Example:
        >>> async with Upsales(token="...") as upsales:
        ...     # Get products
        ...     product = await upsales.products.get(1)
        ...     active = await upsales.products.get_active()
        ...
        ...     # Bulk operations
        ...     await upsales.products.bulk_deactivate([1, 2, 3])
        ...     await upsales.products.bulk_update_price([4, 5], 99.99)

    Note:
        With Python 3.13 free-threaded mode, bulk operations achieve
        true parallelism. Enable with: python -X gil=0 script.py
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize products resource."""
        super().__init__(
            http=http,
            endpoint="/products",
            model_class=Product,
            partial_class=PartialProduct,
        )

    async def get_active(self) -> list[Product]:
        """
        Get all active products.

        Returns:
            List of products with active=1.

        Example:
            >>> products = await upsales.products.get_active()
            >>> print(f"Found {len(products)} active products")
        """
        return await self.list_all(active=1)

    async def get_by_category(self, category_id: int) -> list[Product]:
        """
        Get products by category.

        Args:
            category_id: Category ID to filter by.

        Returns:
            List of products in the category.
        """
        return await self.list_all(categoryId=category_id)

    async def bulk_activate(self, ids: list[int]) -> list[Product]:
        """
        Activate multiple products.

        Args:
            ids: Product IDs to activate.

        Returns:
            List of updated products.

        Example:
            >>> products = await upsales.products.bulk_activate([1, 2, 3])
        """
        return await self.bulk_update(ids, {"active": 1})

    async def bulk_deactivate(self, ids: list[int]) -> list[Product]:
        """
        Deactivate multiple products.

        Args:
            ids: Product IDs to deactivate.

        Returns:
            List of updated products.

        Example:
            >>> await upsales.products.bulk_deactivate(range(100, 200))

        Note:
            With Python 3.13 free-threaded mode, these 100 deactivations
            can run in true parallel, completing much faster.
        """
        return await self.bulk_update(ids, {"active": 0})

    async def bulk_update_price(
        self,
        ids: list[int],
        price: float,
    ) -> list[Product]:
        """
        Update price for multiple products.

        Args:
            ids: Product IDs to update.
            price: New price to set.

        Returns:
            List of updated products.

        Example:
            >>> products = await upsales.products.bulk_update_price(
            ...     ids=[1, 2, 3],
            ...     price=99.99
            ... )
        """
        return await self.bulk_update(ids, {"price": price})

    async def search(
        self,
        name: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        active: int | None = None,
    ) -> list[Product]:
        """
        Search products with filters.

        Args:
            name: Filter by name (partial match).
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            active: Filter by active status (0 or 1).

        Returns:
            List of matching products.

        Example:
            >>> # Active products under $100
            >>> products = await upsales.products.search(
            ...     max_price=100.0,
            ...     active=1
            ... )
        """
        params: dict[str, Any] = {}

        if name is not None:
            params["name"] = name
        if min_price is not None:
            params["minPrice"] = min_price
        if max_price is not None:
            params["maxPrice"] = max_price
        if active is not None:
            params["active"] = active

        response = await self._http.get(self._endpoint, **params)
        return [
            self._model_class(**item, _client=self._http._client)
            for item in response["data"]
        ]
```

## Updating the Client

After creating a resource, add it to the client:

```python
# upsales/client.py

from upsales.resources.products import ProductsResource

class Upsales:
    def __init__(self, token: str, ...):
        self.http = HTTPClient(token, ...)

        # Add new resource
        self.products = ProductsResource(self.http)
```

## Checklist

Before submitting resources:

- [ ] Uses Python 3.13 type parameter syntax `[T, P]`
- [ ] No old generic syntax (`Generic`, `TypeVar`)
- [ ] Inherits from `BaseResource`
- [ ] Calls `super().__init__()` with correct parameters
- [ ] All custom methods have comprehensive docstrings
- [ ] Examples in all docstrings
- [ ] Uses pattern matching where appropriate
- [ ] Comments about free-threaded mode benefits for bulk operations
- [ ] Type hints use native syntax (no typing imports)
- [ ] Passes mypy strict mode
- [ ] Passes ruff linting
- [ ] 90%+ docstring coverage

## Testing

Create tests for custom methods:

```python
# tests/unit/test_products_resource.py

import pytest
from upsales.resources.products import ProductsResource

@pytest.mark.asyncio
async def test_bulk_activate(mock_http):
    """Test bulk product activation."""
    resource = ProductsResource(mock_http)

    # Mock response
    mock_http.put.return_value = {
        "data": {"id": 1, "name": "Product", "active": 1}
    }

    products = await resource.bulk_activate([1, 2, 3])

    assert len(products) == 3
    assert all(p.active == 1 for p in products)
```
