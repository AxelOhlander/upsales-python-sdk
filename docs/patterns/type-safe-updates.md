# Type-Safe Updates with IDE Autocomplete

Guide for making `.edit()` methods discoverable with IDE autocomplete.

## The Problem

Current signature uses `**kwargs: Any`:

```python
async def edit(self, **kwargs: Any) -> "User":
    ...
```

**Issues**:
- ❌ No IDE autocomplete
- ❌ No type checking
- ❌ User must read docs/code to know available fields

## Solution 1: TypedDict with Unpack (Recommended) ✅

Use Python 3.12+ `TypedDict` with `Unpack` for full type safety:

```python
from typing import Unpack, TypedDict

class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    All fields are optional (total=False).
    """
    name: str
    email: str
    administrator: int
    active: int
    custom: list[dict]


class User(BaseModel):
    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int
    active: int = 1
    custom: list[dict] = Field(default_factory=list)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """
        Edit this user.

        Args:
            **kwargs: Fields to update. See UserUpdateFields for available fields.

        Returns:
            Updated user.

        Example:
            >>> user = await client.users.get(1)
            >>>
            >>> # IDE provides autocomplete for name, email, administrator, etc.
            >>> updated = await user.edit(
            ...     name="Jane",
            ...     email="jane@example.com"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
```

**Benefits**:
- ✅ Full IDE autocomplete
- ✅ Type checking (mypy, pyright)
- ✅ Flexible (any subset of fields)
- ✅ Minimal runtime overhead
- ✅ Fits template pattern

**IDE Experience**:
```python
user = await client.users.get(1)

# When typing user.edit(
# IDE shows: name: str, email: str, administrator: int, active: int, custom: list[dict]

await user.edit(
    name="Jane",  # ✅ Autocomplete suggests this
    email="jane@example.com",  # ✅ Type checked
    administrator=1,  # ✅ IDE knows this is int
)
```

## Solution 2: Explicit Parameters

Use explicit parameters with `None` defaults:

```python
class User(BaseModel):
    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int

    async def edit(
        self,
        *,  # Force keyword-only arguments
        name: str | None = None,
        email: str | None = None,
        administrator: int | None = None,
        active: int | None = None,
        custom: list[dict] | None = None,
    ) -> "User":
        """
        Edit this user.

        Args:
            name: New name.
            email: New email.
            administrator: Admin flag (0 or 1).
            active: Active flag (0 or 1).
            custom: Custom fields.

        Returns:
            Updated user.

        Example:
            >>> await user.edit(name="Jane", email="jane@example.com")
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Build update dict from provided arguments
        updates = {
            k: v for k, v in {
                "name": name,
                "email": email,
                "administrator": administrator,
                "active": active,
                "custom": custom,
            }.items()
            if v is not None
        }

        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**updates)
        )
```

**Benefits**:
- ✅ Perfect IDE autocomplete
- ✅ Self-documenting
- ✅ Type checked

**Drawbacks**:
- ❌ Verbose (signature must match all fields)
- ❌ Harder to maintain (change model = change signature)
- ❌ Can't easily pass dict of updates

## Solution 3: Hybrid Approach

Combine TypedDict with overload for flexibility:

```python
from typing import Unpack, TypedDict, overload

class UserUpdateFields(TypedDict, total=False):
    name: str
    email: str
    administrator: int


class User(BaseModel):
    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int

    @overload
    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Type-safe kwargs."""
        ...

    @overload
    async def edit(self, **kwargs: Any) -> "User":
        """Fallback for dynamic usage."""
        ...

    async def edit(self, **kwargs: Any) -> "User":
        """
        Edit this user.

        IDE provides autocomplete for known fields, but also accepts any kwargs
        for dynamic usage (e.g., from API responses, config files).

        Example:
            >>> # Type-safe (autocomplete works)
            >>> await user.edit(name="Jane", email="jane@example.com")
            >>>
            >>> # Dynamic (also works)
            >>> fields = {"name": "Jane", "active": 0}
            >>> await user.edit(**fields)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
```

## Solution 4: Resource Manager Method

Add typed update method to resource manager:

```python
class UsersResource(BaseResource[User, PartialUser]):
    async def update_user(
        self,
        id: int,
        *,
        name: str | None = None,
        email: str | None = None,
        administrator: int | None = None,
    ) -> User:
        """
        Update a user with typed parameters.

        Args:
            id: User ID.
            name: New name.
            email: New email.
            administrator: Admin flag.

        Returns:
            Updated user.

        Example:
            >>> # Full autocomplete!
            >>> user = await client.users.update_user(
            ...     id=1,
            ...     name="Jane",
            ...     email="jane@example.com"
            ... )
        """
        updates = {
            k: v for k, v in {
                "name": name,
                "email": email,
                "administrator": administrator,
            }.items()
            if v is not None
        }

        return await self.update(id, **updates)
```

## Recommended Pattern: TypedDict

For the template-driven SDK, use **TypedDict with Unpack**:

### Step 1: Define UpdateFields TypedDict

```python
# upsales/models/user.py
from typing import Unpack, TypedDict
from pydantic import Field
from upsales.models.base import BaseModel

class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    Only includes updatable fields (no id, timestamps, etc.).
    All fields are optional.

    Attributes:
        name: User's full name.
        email: Email address.
        administrator: Admin flag (0 or 1).
        active: Active status (0 or 1).
        custom: Custom fields list.
    """
    name: str
    email: str
    administrator: int
    active: int
    custom: list[dict]


class User(BaseModel):
    """Full User model with type-safe updates."""

    # Read-only
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)

    # Updatable
    name: str
    email: str
    administrator: int
    active: int = 1
    custom: list[dict] = Field(default_factory=list)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """
        Edit this user with type-safe parameters.

        IDE provides autocomplete and type checking for all fields.

        Args:
            **kwargs: Fields to update. See UserUpdateFields for available options.

        Returns:
            Updated user.

        Example:
            >>> user = await client.users.get(1)
            >>> updated = await user.edit(
            ...     name="Jane Doe",
            ...     administrator=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
```

### Step 2: Update Template in BaseModel

```python
# upsales/models/base.py
from typing import Any

class BaseModel(PydanticBase):
    """
    Base model with type-safe updates.

    Subclasses should define a TypedDict for updatable fields:

    Example:
        >>> class UserUpdateFields(TypedDict, total=False):
        ...     name: str
        ...     email: str
        ...
        >>> class User(BaseModel):
        ...     async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        ...         ...
    """

    # ... existing implementation ...
```

## Comparison Table

| Approach | IDE Autocomplete | Type Checking | Flexibility | Maintenance |
|----------|-----------------|---------------|-------------|-------------|
| TypedDict + Unpack | ✅ Perfect | ✅ Full | ✅ High | ⚠️ Medium |
| Explicit Parameters | ✅ Perfect | ✅ Full | ❌ Limited | ❌ High |
| Hybrid (overload) | ✅ Good | ✅ Good | ✅ High | ⚠️ Medium |
| **kwargs: Any | ❌ None | ❌ None | ✅ High | ✅ Low |

## Testing Type Safety

```python
# tests/test_type_safety.py
from upsales.models.user import User, UserUpdateFields

def test_typeddict_structure():
    """Verify TypedDict has correct fields."""
    expected_fields = {"name", "email", "administrator", "active", "custom"}
    actual_fields = set(UserUpdateFields.__annotations__.keys())
    assert actual_fields == expected_fields

def test_typeddict_types():
    """Verify TypedDict has correct types."""
    assert UserUpdateFields.__annotations__["name"] == str
    assert UserUpdateFields.__annotations__["email"] == str
    assert UserUpdateFields.__annotations__["administrator"] == int
```

## Mypy Configuration

Ensure mypy checks TypedDict usage:

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
# TypedDict checking
check_untyped_defs = true
disallow_untyped_decorators = false
```

## Summary

**Use TypedDict with Unpack** for:
- ✅ Full IDE autocomplete
- ✅ Type checking with mypy/pyright
- ✅ Flexibility (any subset of fields)
- ✅ Python 3.13+ native syntax
- ✅ Fits template-driven design

**Pattern**:
1. Define `{Model}UpdateFields` TypedDict
2. Use `**kwargs: Unpack[{Model}UpdateFields]` in `edit()`
3. Mark fields `total=False` for optional updates
4. Document in TypedDict docstring
