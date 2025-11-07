# Upsales SDK - API Methods Design Document

**Version**: 1.0
**Date**: 2025-01-02
**Status**: Draft for Review

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Method Categories](#method-categories)
4. [Naming Conventions](#naming-conventions)
5. [Method Specifications](#method-specifications)
6. [Instance vs Manager Methods](#instance-vs-manager-methods)
7. [Applicability Matrix](#applicability-matrix)
8. [Discord.py Pattern Analysis](#discordpy-pattern-analysis)
9. [Current Implementation Status](#current-implementation-status)
10. [Recommendations](#recommendations)
11. [Migration Path](#migration-path)
12. [Examples](#examples)

---

## Executive Summary

This document defines the complete method structure for Upsales SDK resources, establishing patterns for CRUD operations, bulk operations, search/filtering, and relationship access. The design is informed by:

- Current Upsales SDK architecture
- Discord.py API wrapper patterns (industry-leading async Python library)
- Modern Python 3.13+ best practices
- Real-world Upsales API capabilities

### Key Decisions

1. **Keep `get()` over `fetch()`** - No caching layer means fetch/get distinction unnecessary
2. **Use `edit()` over `update()`** - More natural, matches discord.py, already implemented
3. **Add `create()` to BaseResource** - Critical missing CRUD operation
4. **Standardize bulk operations** - Already superior to discord.py
5. **Support both manager and instance methods** - Best of both worlds

---

## Design Philosophy

### Core Principles

1. **Consistency**: Same operations have same names across all resources
2. **Discoverability**: IDE autocomplete reveals available operations
3. **Type Safety**: Full type hints with Python 3.13+ native syntax
4. **Performance**: Async-first with bulk operations and concurrency control
5. **Developer Experience**: Intuitive naming, clear semantics, comprehensive docs

### Method Organization

```
Upsales SDK
├── Manager Methods (on upsales.{resource})
│   ├── CRUD operations
│   ├── Bulk operations
│   ├── Search & filtering
│   └── Pagination
│
└── Instance Methods (on model objects)
    ├── Update operations (edit)
    ├── Delete operations (delete)
    ├── Expansion (fetch_full for PartialModels)
    └── Computed properties
```

---

## Method Categories

### 1. CRUD Operations (Core)

The fundamental operations every resource manager should support:

| Operation | Method | Location | Returns |
|-----------|--------|----------|---------|
| **Create** | `create(**data)` | Manager | Full model (T) |
| **Read Single** | `get(id)` | Manager | Full model (T) |
| **Read Multiple** | `list(limit, offset, **params)` | Manager | List[T] |
| **Read All** | `list_all(**params)` | Manager | List[T] |
| **Update** | `update(id, **data)` | Manager | Full model (T) |
| **Delete** | `delete(id)` | Manager | dict |

### 2. Instance Operations

Methods that operate on a specific model instance:

| Operation | Method | Location | Returns |
|-----------|--------|----------|---------|
| **Update Self** | `edit(**kwargs)` | Instance | Updated model |
| **Delete Self** | `delete()` | Instance | None |
| **Expand Partial** | `fetch_full()` | PartialModel | Full model |
| **Refresh** | `refresh()` | Instance | Updated self |

### 3. Bulk Operations

Parallel operations on multiple resources:

| Operation | Method | Location | Returns |
|-----------|--------|----------|---------|
| **Bulk Create** | `bulk_create(items, max_concurrent)` | Manager | List[T] |
| **Bulk Update** | `bulk_update(ids, data, max_concurrent)` | Manager | List[T] |
| **Bulk Delete** | `bulk_delete(ids, max_concurrent)` | Manager | List[dict] |
| **Bulk Fetch** | `bulk_get(ids, max_concurrent)` | Manager | List[T] |

### 4. Search & Filtering

Querying resources by criteria:

| Operation | Method | Location | Returns |
|-----------|--------|----------|---------|
| **By Field** | `get_by_{field}(value)` | Manager | T \| None or List[T] |
| **By Status** | `get_{status}()` | Manager | List[T] |
| **Generic Search** | `search(**filters)` | Manager | List[T] |
| **Count** | `count(**filters)` | Manager | int |
| **Exists** | `exists(id)` | Manager | bool |

### 5. Relationship Access

Accessing related resources (when applicable):

| Operation | Method | Location | Returns |
|-----------|--------|----------|---------|
| **Get Related** | `get_{relation}()` | Instance | List[RelatedModel] |
| **Add Relation** | `add_{relation}(id)` | Instance | Updated self |
| **Remove Relation** | `remove_{relation}(id)` | Instance | Updated self |
| **Fetch Related** | `fetch_{relation}()` | Instance | List[RelatedModel] |

### 6. Specialized Operations

Domain-specific operations beyond generic CRUD:

| Domain | Example Methods |
|--------|-----------------|
| **Users** | `get_administrators()`, `get_active()`, `authenticate()` |
| **Products** | `get_active()`, `get_recurring()`, `bulk_deactivate()` |
| **Companies** | `get_by_org_no()`, `get_monitored()`, `get_prospects()` |
| **Campaigns** | `send()`, `schedule()`, `get_recipients()`, `add_recipients()` |
| **Orders** | `submit()`, `approve()`, `cancel()`, `get_by_date_range()` |

---

## Naming Conventions

### Verb Choices

Based on industry standards and discord.py patterns:

| Purpose | Chosen Verb | Alternatives | Rationale |
|---------|-------------|--------------|-----------|
| **Retrieve single** | `get` | fetch, find, retrieve | Simple, familiar, no caching distinction needed |
| **Retrieve multiple** | `list` | get_all, find_all, query | Clear pagination semantics |
| **Create new** | `create` | add, new, make | Standard CRUD terminology |
| **Modify existing** | `edit` (instance)<br>`update` (manager) | modify, change, patch | `edit` feels natural for instances,<br>`update` for managers |
| **Remove** | `delete` | remove, destroy | Standard CRUD terminology |
| **Check existence** | `exists` | has, contains | Boolean query semantics |
| **Get count** | `count` | total, size | SQL-like familiarity |
| **Expand partial** | `fetch_full` | expand, load_full | Signals API call for complete data |
| **Reload** | `refresh` | reload, sync | Updates instance from API |

### Prefixes & Patterns

| Pattern | Example | Usage |
|---------|---------|-------|
| **`get_by_{field}`** | `get_by_email()` | Lookup by specific field |
| **`get_{status}`** | `get_active()`, `get_archived()` | Filter by status flag |
| **`get_{plural}`** | `get_administrators()`, `get_products()` | Filter by category |
| **`bulk_{operation}`** | `bulk_create()`, `bulk_update()` | Parallel operations |
| **`fetch_{relation}`** | `fetch_contacts()`, `fetch_orders()` | Load related resources |
| **`add_{relation}`** | `add_user()`, `add_tag()` | Create relationship |
| **`remove_{relation}`** | `remove_user()`, `remove_tag()` | Delete relationship |

### Method Naming Rules

1. **Use verbs, not nouns**: `get_user()` not `user()`
2. **Be explicit**: `get_active_users()` better than `active()`
3. **Avoid abbreviations**: `get_by_email()` not `get_by_em()`
4. **Match domain language**: If Upsales UI says "deactivate", use `deactivate()` not `set_inactive()`
5. **Consistent plurality**: `list()` returns many, `get()` returns one
6. **Signal API calls**: `fetch_*()` when explicitly fetching related resources

---

## Method Specifications

### CRUD Operations

#### `create(**data: Any) -> T`

**Purpose**: Create a new resource
**Location**: Manager (BaseResource)
**HTTP Method**: POST
**Status**: ✅ Implemented (BaseResource line 111)

```python
async def create(self, **data: Any) -> T:
    """
    Create a new resource.

    Args:
        **data: Field values for the new resource.

    Returns:
        Newly created resource with generated ID.

    Raises:
        ValidationError: If required fields missing or invalid.
        AuthenticationError: If not authorized to create.

    Example:
        >>> user = await upsales.users.create(
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     administrator=0
        ... )
        >>> print(f"Created user {user.id}: {user.name}")
    """
    response = await self._http.post(self._endpoint, **data)
    return self._model_class(**response["data"], _client=self._http._upsales_client)
```

**Applicability**: All writable resources (users, companies, products, campaigns, etc.)

**NOT applicable to**:
- Read-only calculated fields (soliditet, growth, ads)
- System-generated nested objects
- Relationship objects managed elsewhere

---

#### `get(resource_id: int) -> T`

**Purpose**: Retrieve single resource by ID
**Location**: Manager (BaseResource)
**HTTP Method**: GET
**Status**: ✅ Implemented

```python
async def get(self, resource_id: int) -> T:
    """
    Get a single resource by ID.

    Args:
        resource_id: Unique identifier for the resource.

    Returns:
        Full resource object.

    Raises:
        NotFoundError: If resource doesn't exist.
        AuthenticationError: If not authorized to read.

    Example:
        >>> user = await upsales.users.get(123)
        >>> print(f"{user.name} <{user.email}>")
    """
    response = await self._http.get(f"{self._endpoint}/{resource_id}")
    return self._model_class(**response["data"], _client=self._http._upsales_client)
```

**Applicability**: All resources with endpoints

---

#### `list(limit: int = 100, offset: int = 0, **params: Any) -> list[T]`

**Purpose**: Paginated list of resources with optional filtering
**Location**: Manager (BaseResource)
**HTTP Method**: GET
**Status**: ✅ Implemented

```python
async def list(
    self,
    limit: int = 100,
    offset: int = 0,
    **params: Any,
) -> list[T]:
    """
    List resources with pagination.

    Args:
        limit: Maximum results per page (default: 100, max: 1000).
        offset: Offset for pagination (default: 0).
        **params: Additional query parameters for filtering.

    Returns:
        List of resource objects for this page.

    Example:
        >>> # First page
        >>> users = await upsales.users.list(limit=50)
        >>>
        >>> # Second page
        >>> more_users = await upsales.users.list(limit=50, offset=50)
        >>>
        >>> # With filters
        >>> admins = await upsales.users.list(administrator=1)
    """
    all_params = params | {"limit": limit, "offset": offset}
    response = await self._http.get(self._endpoint, **all_params)
    return [
        self._model_class(**item, _client=self._http._upsales_client)
        for item in response["data"]
    ]
```

**Applicability**: All resources with list endpoints

---

#### `list_all(batch_size: int = 100, **params: Any) -> list[T]`

**Purpose**: Auto-paginated fetch of all resources
**Location**: Manager (BaseResource)
**HTTP Method**: GET (multiple)
**Status**: ✅ Implemented

```python
async def list_all(self, batch_size: int = 100, **params: Any) -> list[T]:
    """
    List all resources by automatically handling pagination.

    Fetches all pages sequentially and returns combined list.
    Use with caution for large datasets.

    Args:
        batch_size: Number of items per request (default: 100).
        **params: Additional query parameters for filtering.

    Returns:
        List of all matching resource objects.

    Example:
        >>> # Get ALL users (could be thousands)
        >>> all_users = await upsales.users.list_all()
        >>> print(f"Total users: {len(all_users)}")
        >>>
        >>> # With filters
        >>> active_users = await upsales.users.list_all(active=1)
    """
    # Implementation continues...
```

**Applicability**: All resources with list endpoints

**⚠️ Warning**: Can be slow for large datasets. Consider filtering or using `list()` with pagination.

---

#### `update(resource_id: int, **data: Any) -> T`

**Purpose**: Update existing resource by ID
**Location**: Manager (BaseResource)
**HTTP Method**: PUT
**Status**: ✅ Implemented

```python
async def update(self, resource_id: int, **data: Any) -> T:
    """
    Update a resource.

    Args:
        resource_id: ID of resource to update.
        **data: Fields to update with new values.

    Returns:
        Updated resource object with fresh data from API.

    Example:
        >>> user = await upsales.users.update(
        ...     123,
        ...     name="Jane Smith",
        ...     email="jane@example.com"
        ... )
        >>> print(f"Updated: {user.name}")
    """
    response = await self._http.put(f"{self._endpoint}/{resource_id}", **data)
    return self._model_class(**response["data"], _client=self._http._upsales_client)
```

**Applicability**: All writable resources

**NOT applicable to**: Read-only resources, system-calculated fields

---

#### `delete(resource_id: int) -> dict[str, Any]`

**Purpose**: Delete resource by ID
**Location**: Manager (BaseResource)
**HTTP Method**: DELETE
**Status**: ✅ Implemented

```python
async def delete(self, resource_id: int) -> dict[str, Any]:
    """
    Delete a resource.

    Args:
        resource_id: ID of resource to delete.

    Returns:
        Response data from API (typically success message).

    Example:
        >>> await upsales.users.delete(123)
        >>> # User 123 has been deleted
    """
    return await self._http.delete(f"{self._endpoint}/{resource_id}")
```

**Applicability**: All deletable resources

**NOT applicable to**:
- System resources (yourself, system users)
- Read-only calculated fields
- Resources with cascade protection

---

### Instance Operations

#### `edit(**kwargs: Any) -> Self`

**Purpose**: Update this specific instance
**Location**: Instance (BaseModel & PartialModel)
**HTTP Method**: PUT
**Status**: ✅ Implemented

```python
async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
    """
    Edit this user.

    Uses Pydantic v2's optimized serialization via to_api_dict().
    Full IDE autocomplete support via TypedDict.

    Args:
        **kwargs: Fields to update (IDE provides autocomplete).

    Returns:
        Updated user with fresh data from API.

    Raises:
        RuntimeError: If no client reference available.

    Example:
        >>> user = await upsales.users.get(123)
        >>> await user.edit(name="New Name", active=1)
        >>> print(f"Updated: {user.name}")
    """
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.users.update(
        self.id,
        **self.to_api_dict(**kwargs)
    )
```

**Applicability**: All writable BaseModel and PartialModel instances

**Benefits**:
- Natural OOP pattern: `user.edit()` vs `client.users.update(user.id, ...)`
- IDE autocomplete via TypedDict + Unpack
- Automatically excludes frozen fields
- Instance updates itself with response

---

#### `delete() -> None`

**Purpose**: Delete this specific instance
**Location**: Instance (BaseModel)
**HTTP Method**: DELETE
**Status**: ❌ Not yet implemented

```python
async def delete(self) -> None:
    """
    Delete this resource.

    After calling this method, the instance should not be used.

    Raises:
        RuntimeError: If no client reference available.

    Example:
        >>> user = await upsales.users.get(123)
        >>> await user.delete()
        >>> # User has been deleted from Upsales
    """
    if not self._client:
        raise RuntimeError("No client available")
    await self._client.users.delete(self.id)
```

**Applicability**: All deletable BaseModel instances

**Design note**: Matches discord.py pattern (`await message.delete()`)

---

#### `fetch_full() -> BaseModel`

**Purpose**: Expand PartialModel to full BaseModel
**Location**: Instance (PartialModel only)
**HTTP Method**: GET
**Status**: ✅ Implemented (subclasses must implement)

```python
async def fetch_full(self) -> Company:
    """
    Fetch complete company data.

    Returns:
        Full Company object with all fields populated.

    Raises:
        RuntimeError: If no client reference available.
        NotFoundError: If resource no longer exists.

    Example:
        >>> # contact.company is PartialCompany (only id & name)
        >>> partial = contact.company
        >>> print(partial.name)  # ✅ Available
        >>> print(partial.phone)  # ❌ AttributeError
        >>>
        >>> # Fetch full version
        >>> full = await partial.fetch_full()
        >>> print(full.phone)  # ✅ Now available
    """
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.companies.get(self.id)
```

**Applicability**: All PartialModel subclasses

**Purpose**: Convert minimal nested objects to full objects when needed

---

#### `refresh() -> Self`

**Purpose**: Reload instance data from API
**Location**: Instance (BaseModel)
**HTTP Method**: GET
**Status**: ❌ Not yet implemented

```python
async def refresh(self) -> "User":
    """
    Refresh this instance with latest data from API.

    Useful when data might have changed externally.

    Returns:
        Self with updated data.

    Raises:
        RuntimeError: If no client reference available.
        NotFoundError: If resource no longer exists.

    Example:
        >>> user = await upsales.users.get(123)
        >>> print(user.name)  # "Old Name"
        >>>
        >>> # Someone else updates the user...
        >>>
        >>> await user.refresh()
        >>> print(user.name)  # "New Name"
    """
    if not self._client:
        raise RuntimeError("No client available")
    fresh = await self._client.users.get(self.id)
    # Update self with fresh data
    for field, value in fresh.__dict__.items():
        setattr(self, field, value)
    return self
```

**Applicability**: All BaseModel instances

**Use case**: When you need to ensure data is current without creating a new object

---

### Bulk Operations

#### `bulk_create(items: list[dict[str, Any]], max_concurrent: int | None = None) -> list[T]`

**Purpose**: Create multiple resources in parallel
**Location**: Manager (BaseResource)
**HTTP Method**: POST (multiple)
**Status**: ❌ Not yet implemented

```python
async def bulk_create(
    self,
    items: list[dict[str, Any]],
    max_concurrent: int | None = None,
) -> list[T]:
    """
    Bulk create multiple resources with rate limiting.

    Args:
        items: List of data dicts for new resources.
        max_concurrent: Maximum concurrent requests (default: from client).

    Returns:
        List of created resource objects.

    Raises:
        ExceptionGroup: If any creations fail. Contains all exceptions
            that occurred during the bulk operation.

    Example:
        >>> users_data = [
        ...     {"name": "John", "email": "john@example.com"},
        ...     {"name": "Jane", "email": "jane@example.com"},
        ...     {"name": "Bob", "email": "bob@example.com"},
        ... ]
        >>> users = await upsales.users.bulk_create(users_data)
        >>> print(f"Created {len(users)} users")

    Note:
        With Python 3.13 free-threaded mode, these requests can truly
        run in parallel without GIL contention.
    """
    max_concurrent = max_concurrent or self._http.max_concurrent
    semaphore = asyncio.Semaphore(max_concurrent)

    async def create_one(data: dict[str, Any]) -> T:
        async with semaphore:
            return await self.create(**data)

    results = await asyncio.gather(
        *[create_one(item) for item in items],
        return_exceptions=True,
    )

    successes: list[T] = [r for r in results if not isinstance(r, Exception)]
    errors: list[Exception] = [r for r in results if isinstance(r, Exception)]

    if errors:
        raise ExceptionGroup(
            f"Failed to create {len(errors)}/{len(items)} items",
            errors,
        )

    return successes
```

**Applicability**: All creatable resources

**Use case**: Importing data, batch user creation, etc.

---

#### `bulk_update(ids: list[int], data: dict[str, Any], max_concurrent: int | None = None) -> list[T]`

**Purpose**: Update multiple resources in parallel
**Location**: Manager (BaseResource)
**HTTP Method**: PUT (multiple)
**Status**: ✅ Implemented

```python
async def bulk_update(
    self,
    ids: list[int],
    data: dict[str, Any],
    max_concurrent: int | None = None,
) -> list[T]:
    """
    Bulk update multiple resources with rate limiting.

    Args:
        ids: List of resource IDs to update.
        data: Fields to update (applied to all resources).
        max_concurrent: Maximum concurrent requests (default: from client).

    Returns:
        List of updated resource objects.

    Raises:
        ExceptionGroup: If any updates fail.

    Example:
        >>> # Activate 100 products
        >>> products = await upsales.products.bulk_update(
        ...     ids=list(range(1, 101)),
        ...     data={"active": 1},
        ... )
    """
    # Implementation...
```

**Applicability**: All updatable resources

---

#### `bulk_delete(ids: list[int], max_concurrent: int | None = None) -> list[dict[str, Any]]`

**Purpose**: Delete multiple resources in parallel
**Location**: Manager (BaseResource)
**HTTP Method**: DELETE (multiple)
**Status**: ✅ Implemented

```python
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
        ExceptionGroup: If any deletes fail.

    Example:
        >>> await upsales.users.bulk_delete([1, 2, 3, 4, 5])
    """
    # Implementation...
```

**Applicability**: All deletable resources

---

#### `bulk_get(ids: list[int], max_concurrent: int | None = None) -> list[T]`

**Purpose**: Fetch multiple resources in parallel
**Location**: Manager (BaseResource)
**HTTP Method**: GET (multiple)
**Status**: ❌ Not yet implemented

```python
async def bulk_get(
    self,
    ids: list[int],
    max_concurrent: int | None = None,
) -> list[T]:
    """
    Bulk fetch multiple resources with rate limiting.

    More efficient than individual get() calls when fetching many resources.

    Args:
        ids: List of resource IDs to fetch.
        max_concurrent: Maximum concurrent requests (default: from client).

    Returns:
        List of resource objects (order may not match input order).

    Raises:
        ExceptionGroup: If any fetches fail.

    Example:
        >>> user_ids = [1, 5, 10, 15, 20]
        >>> users = await upsales.users.bulk_get(user_ids)
        >>> for user in users:
        ...     print(user.name)
    """
    max_concurrent = max_concurrent or self._http.max_concurrent
    semaphore = asyncio.Semaphore(max_concurrent)

    async def get_one(resource_id: int) -> T:
        async with semaphore:
            return await self.get(resource_id)

    results = await asyncio.gather(
        *[get_one(resource_id) for resource_id in ids],
        return_exceptions=True,
    )

    successes: list[T] = [r for r in results if not isinstance(r, Exception)]
    errors: list[Exception] = [r for r in results if isinstance(r, Exception)]

    if errors:
        raise ExceptionGroup(
            f"Failed to fetch {len(errors)}/{len(ids)} items",
            errors,
        )

    return successes
```

**Applicability**: All resources

**Use case**: Fetching specific users, products, or companies when you have their IDs

---

### Search & Filtering

#### `get_by_{field}(value: Any) -> T | None` or `-> list[T]`

**Purpose**: Find resource(s) by specific field value
**Location**: Manager (custom per resource)
**HTTP Method**: GET with query param
**Status**: ✅ Implemented for some (e.g., `get_by_email`)

```python
async def get_by_email(self, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        email: Email address to search for.

    Returns:
        User object if found, None otherwise.

    Example:
        >>> user = await upsales.users.get_by_email("john@example.com")
        >>> if user:
        ...     print(f"Found: {user.name}")
    """
    # Implementation varies by API support
    # Option 1: API supports filtering
    response = await self._http.get(self._endpoint, email=email)
    results = [
        self._model_class(**item, _client=self._http._upsales_client)
        for item in response["data"]
    ]
    return results[0] if results else None

    # Option 2: Client-side filtering
    all_items = await self.list_all()
    for item in all_items:
        if item.email.lower() == email.lower():
            return item
    return None
```

**Common patterns**:
- `get_by_email(email)` - Users
- `get_by_org_no(org_no)` - Companies
- `get_by_name(name)` - Products, Roles, Categories
- `get_by_article_no(article_no)` - Products

**Applicability**: Resource-specific, based on common lookup patterns

---

#### `get_{status}() -> list[T]`

**Purpose**: Filter resources by status flag
**Location**: Manager (custom per resource)
**HTTP Method**: GET with query param
**Status**: ✅ Implemented for some (e.g., `get_active`)

```python
async def get_active(self) -> list[User]:
    """
    Get all active users.

    Returns:
        List of users where active=1.

    Example:
        >>> active_users = await upsales.users.get_active()
        >>> print(f"Active users: {len(active_users)}")
    """
    return await self.list_all(active=1)
```

**Common patterns**:
- `get_active()` / `get_inactive()` - Most resources
- `get_archived()` - Resources with archive status
- `get_monitored()` - Companies
- `get_recurring()` - Products

**Applicability**: Resources with boolean/binary status flags

---

#### `search(**filters: Any) -> list[T]`

**Purpose**: Complex multi-field search with comparison operators
**Location**: Manager (custom per resource)
**HTTP Method**: GET with multiple query params
**Status**: ✅ Implemented (BaseResource line 332)

**Upsales API Filter Format**:

Upsales supports sophisticated filtering with comparison operators:

**Standard Attributes**:
```
attribute=comparisontype:value
```

**Custom Fields**:
```
custom=comparisontype:fieldId:value
```

**Comparison Types**:
| Type | Name | Description | Example |
|------|------|-------------|---------|
| `eq` | Equals | Exact matches (default if omitted) | `active=eq:1` or `active=1` |
| `ne` | Not equals | Exact non-matches | `active=ne:0` |
| `gt` | Greater than | Value greater than | `listPrice=gt:100` |
| `gte` | Greater than equals | Value greater than/equals | `listPrice=gte:100` |
| `lt` | Less than | Value less than | `listPrice=lt:1000` |
| `lte` | Less than equals | Value less than/equals | `listPrice=lte:1000` |

**Multiple Values**:
```
attribute=comparisontype:1,2,3,4,7
```

**Implementation Approach**: Two-level API

**Level 1: Simple Filtering (Most Common)**
```python
# Simple equality (no operators needed)
users = await upsales.users.search(active=1, administrator=1)
# API request: /users?active=1&administrator=1

products = await upsales.products.search(active=1)
# API request: /products?active=1
```

**Level 2: Advanced Filtering (With Operators)**
```python
# Using comparison operators
products = await upsales.products.search(
    active=1,
    listPrice="gt:100",        # Greater than 100
    purchaseCost="lte:50"      # Less than or equal to 50
)
# API request: /products?active=1&listPrice=gt:100&purchaseCost=lte:50

# Multiple values (IN operator)
users = await upsales.users.search(
    role_id="eq:1,2,3"         # role_id IN (1, 2, 3)
)
# API request: /users?role_id=eq:1,2,3

# Custom fields
companies = await upsales.companies.search(
    active=1,
    custom="eq:11:Technology"  # custom field #11 equals "Technology"
)
# API request: /accounts?active=1&custom=eq:11:Technology
```

**Proposed Implementation**:

```python
# Option 1: String-based operators (flexible but less type-safe)
async def search(self, **filters: Any) -> list[T]:
    """
    Search with comparison operators.

    Standard filters:
        field=value              # Equals (default)
        field="eq:value"         # Equals (explicit)
        field="ne:value"         # Not equals
        field="gt:value"         # Greater than
        field="gte:value"        # Greater than or equals
        field="lt:value"         # Less than
        field="lte:value"        # Less than or equals
        field="eq:1,2,3"         # Multiple values (IN)

    Custom fields:
        custom="eq:fieldId:value"
        custom="gt:fieldId:value"

    Example:
        >>> # Simple equality
        >>> products = await upsales.products.search(active=1)
        >>>
        >>> # With operators
        >>> products = await upsales.products.search(
        ...     active=1,
        ...     listPrice="gt:100",
        ...     purchaseCost="lte:50"
        ... )
        >>>
        >>> # Multiple values
        >>> users = await upsales.users.search(role_id="eq:1,2,3")
        >>>
        >>> # Custom fields
        >>> companies = await upsales.companies.search(
        ...     active=1,
        ...     custom="eq:11:Technology"
        ... )
    """
    return await self.list_all(**filters)
```

**Option 2: Helper Classes (More Pythonic)**

```python
from upsales.filters import Filter, CustomField

# Use filter helper classes
products = await upsales.products.search(
    active=1,
    listPrice=Filter.gt(100),
    purchaseCost=Filter.lte(50)
)

# Multiple values
users = await upsales.users.search(
    role_id=Filter.in_([1, 2, 3])
)

# Custom fields
companies = await upsales.companies.search(
    active=1,
    custom=CustomField(11).equals("Technology")
)

# Filter helper implementation:
class Filter:
    @staticmethod
    def eq(value: Any) -> str:
        return f"eq:{value}"

    @staticmethod
    def ne(value: Any) -> str:
        return f"ne:{value}"

    @staticmethod
    def gt(value: Any) -> str:
        return f"gt:{value}"

    @staticmethod
    def gte(value: Any) -> str:
        return f"gte:{value}"

    @staticmethod
    def lt(value: Any) -> str:
        return f"lt:{value}"

    @staticmethod
    def lte(value: Any) -> str:
        return f"lte:{value}"

    @staticmethod
    def in_(values: list) -> str:
        return f"eq:{','.join(map(str, values))}"

class CustomField:
    def __init__(self, field_id: int):
        self.field_id = field_id

    def equals(self, value: Any) -> str:
        return f"eq:{self.field_id}:{value}"

    def gt(self, value: Any) -> str:
        return f"gt:{self.field_id}:{value}"

    # ... other operators
```

**Recommendation**: **Start with Option 1 (string-based)**, add Option 2 (helpers) later if needed.

**Reasoning**:
- ✅ String-based is simpler and matches API format directly
- ✅ Less code to maintain
- ✅ Users familiar with Upsales API can use operators immediately
- ✅ Can always add helpers later without breaking changes

**TypedDict Update**:

Since we support operators, TypedDict becomes less useful for type checking (values can be int, str with operators, or lists). Instead, provide good documentation:

```python
class UsersResource(BaseResource[User, PartialUser]):
    async def search(self, **filters: Any) -> list[User]:
        """
        Search users with comparison operators.

        Supports Upsales API filter syntax:
        - field=value (equals)
        - field="gt:value" (greater than)
        - field="gte:value" (greater than or equals)
        - field="lt:value" (less than)
        - field="lte:value" (less than or equals)
        - field="ne:value" (not equals)
        - field="eq:1,2,3" (multiple values / IN)
        - custom="eq:fieldId:value" (custom fields)

        Common filters:
            active: int or str - User active status (0 or 1)
            administrator: int or str - Administrator flag (0 or 1)
            email: str - User email (supports operators)
            name: str - User name (supports operators)
            role_id: int or str - Filter by role ID

        Example:
            >>> # Simple equality
            >>> active_users = await upsales.users.search(active=1)
            >>>
            >>> # With operators
            >>> users = await upsales.users.search(
            ...     active=1,
            ...     regDate="gte:2024-01-01"  # Registered after 2024
            ... )
            >>>
            >>> # Multiple values (IN)
            >>> users = await upsales.users.search(
            ...     role_id="eq:1,2,3"  # Role ID in (1, 2, 3)
            ... )
            >>>
            >>> # Custom fields
            >>> users = await upsales.users.search(
            ...     active=1,
            ...     custom="eq:11:Senior"  # Custom field #11 = "Senior"
            ... )
        """
        return await self.list_all(**filters)
```

**Benefits**:
- ✅ **Powerful filtering** - Full Upsales API capabilities exposed
- ✅ **Simple for simple cases** - `active=1` just works
- ✅ **Advanced when needed** - Operators available for complex queries
- ✅ **Consistent** - Same pattern across all resources
- ✅ **Well-documented** - Docstrings explain operator syntax

**Comparison Operators Summary**:

| Use Case | Example | API Format |
|----------|---------|------------|
| Equals | `active=1` | `active=1` |
| Equals (explicit) | `active="eq:1"` | `active=eq:1` |
| Not equals | `active="ne:0"` | `active=ne:0` |
| Greater than | `listPrice="gt:100"` | `listPrice=gt:100` |
| Greater than/equals | `regDate="gte:2024-01-01"` | `regDate=gte:2024-01-01` |
| Less than | `listPrice="lt:1000"` | `listPrice=lt:1000` |
| Less than/equals | `regDate="lte:2024-12-31"` | `regDate=lte:2024-12-31` |
| Multiple values (IN) | `role_id="eq:1,2,3"` | `role_id=eq:1,2,3` |
| Custom field | `custom="eq:11:value"` | `custom=eq:11:value` |

**Applicability**: All resources - Upsales API supports filtering on most fields

**Important**:
- Most fields are filterable
- Discovery tool should verify which comparison types work for each field
- Some fields might only support `eq` (equals), not range operators

---

#### `count(**filters: Any) -> int`

**Purpose**: Count resources matching criteria
**Location**: Manager (custom per resource)
**HTTP Method**: GET with query params
**Status**: ❌ Not yet implemented

```python
async def count(self, **filters: Any) -> int:
    """
    Count resources matching filter criteria.

    More efficient than fetching all and counting.

    Args:
        **filters: Field-value pairs to filter by.

    Returns:
        Number of matching resources.

    Example:
        >>> total_users = await upsales.users.count()
        >>> active_users = await upsales.users.count(active=1)
        >>> print(f"{active_users}/{total_users} users are active")
    """
    # If API provides count in metadata
    response = await self._http.get(self._endpoint, limit=1, **filters)
    return response.get("metadata", {}).get("total", 0)

    # Otherwise, fetch and count (less efficient)
    # items = await self.list_all(**filters)
    # return len(items)
```

**Applicability**: All resources

**Note**: Efficiency depends on whether API returns count in metadata

---

#### `exists(resource_id: int) -> bool`

**Purpose**: Check if resource exists
**Location**: Manager (BaseResource)
**HTTP Method**: GET or HEAD
**Status**: ❌ Not yet implemented

```python
async def exists(self, resource_id: int) -> bool:
    """
    Check if a resource exists.

    More efficient than get() when you only need to check existence.

    Args:
        resource_id: ID to check.

    Returns:
        True if resource exists, False otherwise.

    Example:
        >>> if await upsales.users.exists(123):
        ...     print("User 123 exists")
        ... else:
        ...     print("User 123 not found")
    """
    try:
        await self.get(resource_id)
        return True
    except NotFoundError:
        return False
```

**Applicability**: All resources

**Optimization**: Could use HEAD request if API supports it

---

### Relationship Access

*Note: This section is exploratory - depends on Upsales API relationship capabilities*

#### Instance Methods for Related Resources

```python
class Company(BaseModel):
    # ... fields ...

    async def fetch_contacts(self, limit: int = 100) -> list[Contact]:
        """
        Fetch contacts for this company.

        Returns:
            List of contacts belonging to this company.

        Example:
            >>> company = await upsales.companies.get(123)
            >>> contacts = await company.fetch_contacts()
            >>> for contact in contacts:
            ...     print(contact.name)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.list_all(client_id=self.id)

    async def fetch_orders(self, limit: int = 100) -> list[Order]:
        """Fetch orders for this company."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.orders.list_all(client_id=self.id)

    async def add_user(self, user_id: int) -> "Company":
        """
        Add a user to this company.

        Args:
            user_id: ID of user to add.

        Returns:
            Updated company.

        Example:
            >>> company = await upsales.companies.get(123)
            >>> await company.add_user(456)
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Implementation depends on API
        current_users = [u["id"] for u in self.users]
        current_users.append(user_id)
        return await self.edit(users=current_users)
```

**Applicability**: Resources with relationships (companies ↔ contacts, campaigns ↔ companies, etc.)

**Design considerations**:
- Use `fetch_*()` for read operations (signals API call)
- Use `add_*()` / `remove_*()` for write operations
- Consider whether relationship is one-to-many or many-to-many
- Check if API supports nested writes or requires separate calls

---

## Instance vs Manager Methods

### When to Use Manager Methods

**Use manager methods** (`upsales.users.*`) when:

1. **Creating new resources**: `await upsales.users.create(...)`
2. **Fetching by ID**: `await upsales.users.get(123)`
3. **Listing/searching**: `await upsales.users.list()`, `await upsales.users.search(...)`
4. **Bulk operations**: `await upsales.users.bulk_update([1,2,3], {...})`
5. **You don't have an instance yet**: When starting from scratch

**Example**:
```python
# Create a new user
user = await upsales.users.create(name="John", email="john@example.com")

# Find users
all_users = await upsales.users.list_all()
admin = await upsales.users.get_by_email("admin@company.com")

# Bulk operations
await upsales.products.bulk_update([1,2,3], {"active": 1})
```

### When to Use Instance Methods

**Use instance methods** (`user.*`) when:

1. **You already have the object**: After get(), create(), or list()
2. **Updating specific instance**: `await user.edit(name="Jane")`
3. **Deleting specific instance**: `await user.delete()`
4. **Expanding partial to full**: `await partial_user.fetch_full()`
5. **Working with object-oriented patterns**: Feels more natural

**Example**:
```python
# Get a user
user = await upsales.users.get(123)

# Update via instance method (cleaner)
await user.edit(name="Jane", active=0)

# vs manager method (more verbose)
await upsales.users.update(123, name="Jane", active=0)

# Delete
await user.delete()
```

### Both Are Valid

The SDK should support both patterns for flexibility:

```python
# These are equivalent:
await user.edit(name="Jane")
await upsales.users.update(user.id, name="Jane")

# These are equivalent:
await user.delete()
await upsales.users.delete(user.id)
```

**Benefits of dual support**:
- **Instance methods**: Better OOP, more intuitive, less repetition
- **Manager methods**: Useful when you only have the ID, consistent interface

---

## Applicability Matrix

Which methods apply to which resource types:

| Method | Users | Companies | Products | Contacts | Orders | Activities | Campaigns | Roles | Categories | soliditet |
|--------|-------|-----------|----------|----------|--------|------------|-----------|-------|------------|-----------|
| **create()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❓ | ❓ | ❌ |
| **get()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **list()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **list_all()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **update()** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❓ | ❓ | ❌ |
| **delete()** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❓ | ❓ | ❌ |
| **edit()** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❓ | ❓ | ❌ |
| **bulk_create()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **bulk_update()** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ❌ |
| **bulk_delete()** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ❌ |
| **bulk_get()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **search()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **count()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **exists()** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

**Legend**:
- ✅ = Fully applicable
- ⚠️ = Might have restrictions (e.g., orders might not be deletable after certain status)
- ❓ = Need to verify with API (roles/categories might be system-managed)
- ❌ = Not applicable

### Read-Only Resources

Resources like `soliditet`, `growth`, `ads` are **read-only calculated fields** nested in other objects (e.g., `company.soliditet`):

- ❌ No create/update/delete operations
- ❌ No dedicated endpoints (`/soliditet` doesn't exist)
- ✅ Accessed as properties on parent objects
- ✅ Represented by models for type safety

```python
# Read-only nested object
company = await upsales.companies.get(123)
if company.soliditet:
    print(f"Credit rating: {company.soliditet.creditRating}")
    print(f"Employees: {company.soliditet.noEmployees}")

# You cannot:
# await upsales.soliditet.create(...)  # ❌ No endpoint
# await company.soliditet.edit(...)     # ❌ Read-only
```

### Restricted Operations

Some resources might have restricted operations based on:

**Business rules**:
- Can't delete your own user account
- Can't delete orders in certain states
- Can't edit system-generated activities

**API limitations**:
- Some endpoints might not support filtering
- Bulk operations might have size limits
- Rate limits might apply more strictly to certain operations

**Document these restrictions** in resource-specific documentation.

---

## Discord.py Pattern Analysis

### Key Insights from Discord.py

#### 1. fetch vs get (Caching Pattern)

**Discord.py approach**:
- `get_*()` = Cache lookup (fast, might be stale)
- `fetch_*()` = API call (slow, always fresh)

**Upsales SDK decision**:
- **Don't adopt this pattern** - No caching layer means no distinction needed
- Use `get()` for single resource retrieval
- Use `fetch_full()` only for expanding PartialModels
- Optionally use `fetch_*()` for relationship access to signal "this makes an API call"

**Rationale**: Upsales doesn't have real-time websocket updates, so caching would be complex without clear benefit.

#### 2. edit vs update

**Discord.py approach**:
- Uses `edit()` consistently for instance modifications
- `await message.edit(content="new")`, `await member.edit(nick="name")`

**Upsales SDK decision**:
- ✅ **Use `edit()` for instance methods** - Already implemented!
- Keep `update()` for manager methods (when you have ID but not object)
- Feels more natural: "edit this user" vs "update user #123"

#### 3. Instance Methods Dominance

**Discord.py approach**:
- Most operations are instance methods
- `await message.delete()`, `await channel.edit(...)`, `await role.delete()`

**Upsales SDK decision**:
- ✅ **Support both instance and manager methods**
- Instance methods for convenience and OOP feel
- Manager methods for when you only have IDs or for bulk operations

#### 4. create on Parent Objects

**Discord.py approach**:
- `await guild.create_text_channel()`
- `await guild.create_role()`
- Parent creates children

**Upsales SDK decision**:
- **Consider for relationships**: `await company.create_contact(...)`
- **Keep manager method**: `await upsales.contacts.create(...)`
- Support both patterns where it makes sense

#### 5. Relationship Access

**Discord.py approach**:
- Properties for cached collections: `guild.members`, `guild.channels`
- Async iterators for pagination: `async for member in guild.fetch_members()`

**Upsales SDK decision**:
- Use `fetch_*()` methods: `await company.fetch_contacts()`
- Return lists (simpler than async iterators for REST API)
- Consider `@property` for relationships that are always loaded (e.g., `contact.company`)

#### 6. Bulk Operations

**Discord.py approach**:
- Limited bulk support: `await channel.purge()` for bulk delete messages
- Most operations are individual

**Upsales SDK decision**:
- ✅ **SDK is more advanced** - Explicit `bulk_*()` methods with exception groups
- Keep current design - it's actually better than discord.py!

#### 7. Domain-Specific Verbs

**Discord.py approach**:
- `send()` for messages (not `create_message()`)
- `ban()` / `unban()` for members (not `update(banned=True)`)
- `pin()` / `unpin()` for messages

**Upsales SDK decision**:
- **Consider domain-specific methods** for common operations:
  - `await campaign.send()` instead of `await campaign.edit(status='sent')`
  - `await company.activate()` / `await company.deactivate()`
  - `await order.approve()`, `await order.reject()`

---

## Current Implementation Status

### ✅ Already Implemented

| Method | Location | Status |
|--------|----------|--------|
| `get(id)` | BaseResource | ✅ Complete |
| `list(limit, offset, **params)` | BaseResource | ✅ Complete |
| `list_all(**params)` | BaseResource | ✅ Complete |
| `update(id, **data)` | BaseResource | ✅ Complete |
| `delete(id)` | BaseResource | ✅ Complete |
| `create(**data)` | BaseResource | ✅ Complete (line 111) |
| `search(**filters)` | BaseResource | ✅ Complete (line 332) |
| `bulk_update(ids, data, max_concurrent)` | BaseResource | ✅ Complete |
| `bulk_delete(ids, max_concurrent)` | BaseResource | ✅ Complete |
| `edit(**kwargs)` | BaseModel & PartialModel | ✅ Complete (subclasses implement) |
| `fetch_full()` | PartialModel | ✅ Complete (subclasses implement) |
| `get_by_email(email)` | UsersResource | ✅ Complete |
| `get_active()` | UsersResource, ProductsResource | ✅ Complete |
| `get_administrators()` | UsersResource | ✅ Complete |
| `get_recurring()` | ProductsResource | ✅ Complete |
| `bulk_deactivate(ids)` | ProductsResource | ✅ Complete (helper) |

### ❌ Missing - High Priority

| Method | Location | Priority | Reason |
|--------|----------|----------|--------|
| `bulk_create(items, max_concurrent)` | BaseResource | **🔴 HIGH** | Needed for imports/migrations |
| `bulk_get(ids, max_concurrent)` | BaseResource | **🟡 MEDIUM** | Optimization for fetching multiple |
| `delete()` (instance) | BaseModel | **🟡 MEDIUM** | Natural OOP pattern |
| `refresh()` | BaseModel | **🟢 LOW** | Nice to have for data sync |
| `count(**filters)` | BaseResource | **🟢 LOW** | Optimization for counting |
| `exists(id)` | BaseResource | **🟢 LOW** | Convenience method |

### ❓ Exploratory - Need API Research

| Method | Reason |
|--------|--------|
| Relationship methods (`fetch_contacts()`, `add_user()`) | Need to verify API relationship capabilities |
| Domain-specific verbs (`send()`, `approve()`, `activate()`) | Nice to have but not essential |
| Advanced search operators | Depends on API query parameter support |

---

## Recommendations

### Phase 1: Critical Missing CRUD (Priority 1)

**Goal**: Complete the basic CRUD operations

1. **Add `create()` to BaseResource**
   ```python
   async def create(self, **data: Any) -> T:
       response = await self._http.post(self._endpoint, **data)
       return self._model_class(**response["data"], _client=self._http._upsales_client)
   ```

2. **Test with all major resources**:
   - `await upsales.users.create(...)`
   - `await upsales.companies.create(...)`
   - `await upsales.products.create(...)`
   - `await upsales.contacts.create(...)`

3. **Document which resources support create**:
   - Mark read-only resources explicitly
   - Add validation to prevent creating read-only resources

**Impact**: Enables full CRUD for all resources, SDK becomes production-ready

---

### Phase 2: Bulk Operations Enhancement (Priority 2)

**Goal**: Complete bulk operation suite

1. **Add `bulk_create()` to BaseResource**
   - For imports and batch data loading
   - Follow same pattern as `bulk_update()` and `bulk_delete()`

2. **Add `bulk_get()` to BaseResource**
   - Optimization when fetching multiple specific resources
   - More efficient than individual `get()` calls

3. **Add convenience bulk helpers** (resource-specific):
   - `bulk_activate(ids)` / `bulk_deactivate(ids)`
   - Wrappers around `bulk_update()` for common operations

**Impact**: Improves performance for batch operations, better import/export support

---

### Phase 3: Instance Method Completeness (Priority 3)

**Goal**: Full OOP pattern support

1. **Add `delete()` instance method to BaseModel**
   ```python
   async def delete(self) -> None:
       if not self._client:
           raise RuntimeError("No client available")
       await self._client.{resource}.delete(self.id)
   ```

2. **Add `refresh()` instance method to BaseModel**
   ```python
   async def refresh(self) -> Self:
       if not self._client:
           raise RuntimeError("No client available")
       fresh = await self._client.{resource}.get(self.id)
       # Update self with fresh data
       self.__dict__.update(fresh.__dict__)
       return self
   ```

**Impact**: Better OOP support, more intuitive API

---

### Phase 4: Search & Filtering (Priority 4)

**Goal**: Better query capabilities

1. **Standardize search pattern**:
   - `search(**filters)` method on resources that support filtering
   - Document which filters each resource supports

2. **Add common `get_by_*` methods**:
   - `get_by_name()` for products, categories, roles
   - `get_by_org_no()` for companies
   - Resource-specific lookups based on common use cases

3. **Add `count()` and `exists()` convenience methods**:
   - Optimization for checking existence
   - Useful for validation and UI display

**Impact**: Easier data lookup, better developer experience

---

### Phase 5: Relationship Access (Priority 5)

**Goal**: Explore relationship patterns

1. **Research Upsales API relationship capabilities**:
   - How does API handle related resources?
   - Can you filter by related resource IDs?
   - Are nested writes supported?

2. **Implement relationship patterns where appropriate**:
   - `await company.fetch_contacts()` if supported
   - `await contact.fetch_activities()` if supported
   - Consider parent-child patterns like discord.py

3. **Document relationship structure**:
   - Which relationships exist
   - How to navigate them
   - Performance considerations

**Impact**: More intuitive navigation of related data

---

### Phase 6: Domain-Specific Methods (Priority 6)

**Goal**: Natural domain operations

1. **Identify common workflows**:
   - Campaign management: `send()`, `schedule()`, `cancel()`
   - Order processing: `approve()`, `reject()`, `fulfill()`
   - User management: `activate()`, `deactivate()`, `reset_password()`

2. **Implement as wrappers**:
   - Build on top of `edit()` and `update()`
   - Provide semantic names that match business operations

3. **Document business rules**:
   - When can you approve an order?
   - What happens when you send a campaign?
   - State transitions and validations

**Impact**: SDK that speaks the business language, not just CRUD

---

## Migration Path

### For Adding `create()`

**Non-breaking change** - Just adds new functionality:

```python
# Before: Had to use HTTP client directly (if at all)
# Not well-supported

# After: Standard CRUD operation
user = await upsales.users.create(
    name="John Doe",
    email="john@example.com",
    administrator=0
)
```

**Migration steps**:
1. Add `create()` to BaseResource
2. Test with all major resources
3. Document which resources support creation
4. Update examples in documentation

---

### For Adding Instance Methods

**Non-breaking change** - Adds convenience, doesn't remove existing:

```python
# Before: Manager method only
user = await upsales.users.get(123)
await upsales.users.delete(user.id)

# After: Can use either approach
user = await upsales.users.get(123)
await user.delete()  # ✅ More natural
# OR
await upsales.users.delete(user.id)  # ✅ Still works
```

**Migration steps**:
1. Add instance methods to BaseModel
2. Update documentation to show both patterns
3. Explain when to use each approach
4. No breaking changes for existing code

---

### For Any Renaming (NOT RECOMMENDED)

**If we were to rename `get()` → `fetch()`** (NOT RECOMMENDED):

This would be a **breaking change** requiring major version bump:

```python
# Before (v1.x)
user = await upsales.users.get(123)

# After (v2.0)
user = await upsales.users.fetch(123)
```

**Migration steps** (if we did this - but we shouldn't):
1. Add deprecation warning to `get()` in v1.x
2. Support both for transition period
3. Remove `get()` in v2.0
4. Update all documentation and examples

**Recommendation**: **DON'T RENAME** - No benefit, causes breaking changes

---

## Examples

### Complete CRUD Example

```python
from upsales import Upsales

async def main():
    async with Upsales.from_env() as upsales:
        # CREATE
        user = await upsales.users.create(
            name="John Doe",
            email="john@example.com",
            active=1,
            administrator=0
        )
        print(f"Created user {user.id}: {user.name}")

        # READ - Single
        user = await upsales.users.get(user.id)
        print(f"Retrieved: {user.name} <{user.email}>")

        # READ - Multiple
        all_users = await upsales.users.list(limit=50)
        print(f"Found {len(all_users)} users")

        # READ - All (auto-paginated)
        all_active = await upsales.users.list_all(active=1)
        print(f"Total active users: {len(all_active)}")

        # UPDATE - Manager method
        user = await upsales.users.update(
            user.id,
            name="Jane Doe",
            email="jane@example.com"
        )
        print(f"Updated to: {user.name}")

        # UPDATE - Instance method (cleaner)
        await user.edit(administrator=1)
        print(f"Made admin: {user.is_admin}")

        # DELETE - Instance method
        await user.delete()
        print("User deleted")

        # DELETE - Manager method (equivalent)
        # await upsales.users.delete(user.id)
```

### Bulk Operations Example

```python
async def bulk_operations_example():
    async with Upsales.from_env() as upsales:
        # BULK CREATE
        users_data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"},
        ]
        users = await upsales.users.bulk_create(users_data, max_concurrent=10)
        print(f"Created {len(users)} users")

        # BULK UPDATE
        user_ids = [u.id for u in users]
        updated = await upsales.users.bulk_update(
            ids=user_ids,
            data={"active": 1},
            max_concurrent=10
        )
        print(f"Activated {len(updated)} users")

        # BULK GET
        specific_ids = [1, 5, 10, 15, 20]
        specific_users = await upsales.users.bulk_get(
            ids=specific_ids,
            max_concurrent=10
        )
        print(f"Fetched {len(specific_users)} specific users")

        # BULK DELETE
        await upsales.users.bulk_delete(user_ids, max_concurrent=10)
        print(f"Deleted {len(user_ids)} users")
```

### Search & Filtering Example

```python
async def search_example():
    async with Upsales.from_env() as upsales:
        # BY FIELD
        user = await upsales.users.get_by_email("admin@company.com")
        if user:
            print(f"Found admin: {user.name}")

        company = await upsales.companies.get_by_org_no("556677-8899")
        if company:
            print(f"Found company: {company.name}")

        # BY STATUS
        active_users = await upsales.users.get_active()
        print(f"Active users: {len(active_users)}")

        recurring_products = await upsales.products.get_recurring()
        print(f"Recurring products: {len(recurring_products)}")

        # GENERIC SEARCH
        admins = await upsales.users.search(active=1, administrator=1)
        print(f"Active administrators: {len(admins)}")

        # COUNT
        total_users = await upsales.users.count()
        active_count = await upsales.users.count(active=1)
        print(f"{active_count}/{total_users} users are active")

        # EXISTS
        if await upsales.users.exists(123):
            print("User 123 exists")
```

### Instance vs Manager Methods Example

```python
async def instance_vs_manager_example():
    async with Upsales.from_env() as upsales:
        # Scenario 1: You have the object
        user = await upsales.users.get(123)

        # Instance method (natural OOP)
        await user.edit(name="New Name")
        await user.delete()

        # vs Manager method (more verbose)
        await upsales.users.update(123, name="New Name")
        await upsales.users.delete(123)

        # Scenario 2: You only have the ID
        user_id = 456

        # Manager method is cleaner here
        await upsales.users.update(user_id, active=0)
        await upsales.users.delete(user_id)

        # vs fetching first (unnecessary)
        user = await upsales.users.get(user_id)
        await user.edit(active=0)
        await user.delete()
```

### Partial to Full Example

```python
async def partial_to_full_example():
    async with Upsales.from_env() as upsales:
        # Get contact (includes partial company)
        contact = await upsales.contacts.get(123)

        # Access partial company (only id & name available)
        print(f"Company: {contact.company.name}")

        # Need more details? Fetch full version
        full_company = await contact.company.fetch_full()
        print(f"Phone: {full_company.phone}")
        print(f"Website: {full_company.webpage}")
        print(f"Contacts: {full_company.numberOfContacts}")
```

### Relationship Access Example (Future)

```python
async def relationship_example():
    """Example of potential relationship access patterns."""
    async with Upsales.from_env() as upsales:
        company = await upsales.companies.get(123)

        # Fetch related resources
        contacts = await company.fetch_contacts(limit=100)
        orders = await company.fetch_orders(limit=50)
        activities = await company.fetch_activities(limit=20)

        print(f"Company: {company.name}")
        print(f"- {len(contacts)} contacts")
        print(f"- {len(orders)} orders")
        print(f"- {len(activities)} activities")

        # Add relationship
        await company.add_user(user_id=456)

        # Remove relationship
        await company.remove_user(user_id=789)
```

### Domain-Specific Methods Example (Future)

```python
async def domain_specific_example():
    """Example of potential domain-specific operations."""
    async with Upsales.from_env() as upsales:
        # Campaign operations
        campaign = await upsales.campaigns.get(123)
        await campaign.schedule(send_date="2025-01-15")
        await campaign.add_recipients(company_ids=[1, 2, 3])
        await campaign.send()

        # Order operations
        order = await upsales.orders.get(456)
        await order.approve()
        await order.fulfill(tracking_number="ABC123")

        # User operations
        user = await upsales.users.get(789)
        await user.activate()
        await user.reset_password()
```

---

## Conclusion

This design document establishes a comprehensive, consistent method structure for the Upsales SDK that:

1. **Completes CRUD operations** by adding the missing `create()` method
2. **Enhances bulk operations** with `bulk_create()` and `bulk_get()`
3. **Improves OOP support** with instance methods like `delete()` and `refresh()`
4. **Standardizes search patterns** with `search()`, `count()`, `exists()`
5. **Follows industry standards** informed by discord.py and modern API wrappers
6. **Maintains consistency** with clear naming conventions and method organization
7. **Preserves flexibility** by supporting both instance and manager methods

The design prioritizes developer experience, type safety, and performance while maintaining the SDK's current strengths (Python 3.13+ features, Pydantic v2, async-first architecture).

### Next Steps

1. **Review this design doc** with stakeholders
2. **Implement Phase 1** (Critical CRUD) immediately
3. **Implement Phase 2** (Bulk operations) for production readiness
4. **Evaluate Phases 3-6** based on actual usage patterns and API capabilities
5. **Update CLAUDE.md** with approved patterns for AI-assisted development

---

**Document Status**: Draft for Review
**Last Updated**: 2025-01-02
**Author**: Claude Code
**Reviewers**: [To be determined]
