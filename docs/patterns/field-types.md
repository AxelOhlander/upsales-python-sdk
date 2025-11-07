# Field Types and CRUD Operations

Guide for handling different field requirements across CRUD operations.

## The Problem

APIs have different field requirements for different operations:
- **GET**: Returns all fields including `id`
- **POST/CREATE**: No `id` (server generates it)
- **PUT/UPDATE**: `id` in URL path, not in body; some fields read-only
- **PATCH**: Partial updates with optional fields

## Solution: Field Metadata with Pydantic

Use Pydantic's `Field` configuration to mark field types:

```python
from pydantic import Field
from upsales.models.base import BaseModel

class User(BaseModel):
    # Read-only fields (never sent in updates)
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Normal fields (can be updated)
    name: str
    email: str
    administrator: int

    # Optional fields
    description: str | None = None
    custom: list[dict] = Field(default_factory=list)
```

## Approach 1: Smart Serialization (Recommended)

Add helper methods to models for different operations:

```python
from typing import Any
from pydantic import Field
from upsales.models.base import BaseModel

class User(BaseModel):
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)
    name: str
    email: str
    administrator: int
    custom: list[dict] = Field(default_factory=list)

    def to_update_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize for PUT/PATCH requests.

        Excludes read-only fields (id, timestamps) and private fields (_client).

        Args:
            **overrides: Additional fields to override.

        Returns:
            Dict suitable for API update requests.

        Example:
            >>> user = await client.users.get(1)
            >>> user.name = "New Name"
            >>> update_data = user.to_update_dict()
            >>> # {'name': 'New Name', 'email': '...', 'administrator': 0, ...}
        """
        # Get all fields that aren't frozen (read-only)
        data = self.model_dump(
            exclude={"_client"},  # Private fields
            exclude_none=False,  # Keep None values
        )

        # Remove frozen (read-only) fields
        for field_name, field_info in self.__class__.model_fields.items():
            if field_info.frozen:
                data.pop(field_name, None)

        # Apply overrides
        data.update(overrides)

        return data

    async def edit(self, **kwargs: Any) -> "User":
        """
        Edit this user via the API.

        Only sends updatable fields to the API. Read-only fields like
        `id` and timestamps are automatically excluded.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated user with fresh data from API.

        Example:
            >>> user = await client.users.get(1)
            >>> updated = await user.edit(name="Jane Doe")
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Use to_update_dict to exclude read-only fields
        update_data = self.to_update_dict(**kwargs)

        return await self._client.users.update(self.id, **update_data)
```

## Approach 2: Validation in Resource Manager

Add validation to prevent updating read-only fields:

```python
from typing import Any
from upsales.resources.base import BaseResource
from upsales.models.user import User, PartialUser

class UsersResource(BaseResource[User, PartialUser]):
    # Define read-only fields for this resource
    READ_ONLY_FIELDS = {"id", "created_at", "updated_at"}

    async def update(self, id: int, **data: Any) -> User:
        """
        Update a user.

        Validates that read-only fields are not included in update.

        Args:
            id: User ID.
            **data: Fields to update.

        Returns:
            Updated user.

        Raises:
            ValueError: If attempting to update read-only fields.

        Example:
            >>> user = await client.users.update(1, name="New Name")
        """
        # Validate no read-only fields
        read_only_attempted = self.READ_ONLY_FIELDS & data.keys()
        if read_only_attempted:
            raise ValueError(
                f"Cannot update read-only fields: {', '.join(read_only_attempted)}"
            )

        response = await self._http.put(f"{self._endpoint}/{id}", **data)
        return self._model_class(**response["data"], _client=self._http._client)
```

## Approach 3: Separate Update Models (Type-Safe)

For strict type safety, create separate models for updates:

```python
from pydantic import Field
from upsales.models.base import BaseModel

class User(BaseModel):
    """Full user model from GET requests."""
    id: int
    created_at: str | None = None
    updated_at: str | None = None
    name: str
    email: str
    administrator: int
    custom: list[dict] = Field(default_factory=list)

class UserUpdate(BaseModel):
    """
    User update model for PUT/PATCH requests.

    All fields optional except those required by API.
    No read-only fields included.

    Example:
        >>> update = UserUpdate(name="New Name", email="new@example.com")
        >>> user = await client.users.update(1, update)
    """
    name: str | None = None
    email: str | None = None
    administrator: int | None = None
    custom: list[dict] | None = None

class UserCreate(BaseModel):
    """
    User creation model for POST requests.

    No id or timestamps - server generates these.

    Example:
        >>> create = UserCreate(
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     administrator=0
        ... )
        >>> user = await client.users.create(create)
    """
    name: str
    email: str
    administrator: int = 0
    custom: list[dict] = Field(default_factory=list)
```

Then update resource manager:

```python
class UsersResource(BaseResource[User, PartialUser]):
    async def update(
        self,
        id: int,
        data: UserUpdate | dict[str, Any]
    ) -> User:
        """
        Update a user.

        Args:
            id: User ID.
            data: UserUpdate model or dict of fields to update.

        Returns:
            Updated user.

        Example:
            >>> # Type-safe with model
            >>> update = UserUpdate(name="New Name")
            >>> user = await client.users.update(1, update)
            >>>
            >>> # Flexible with dict
            >>> user = await client.users.update(1, {"name": "New Name"})
        """
        if isinstance(data, UserUpdate):
            update_dict = data.model_dump(exclude_unset=True)
        else:
            update_dict = data

        response = await self._http.put(f"{self._endpoint}/{id}", **update_dict)
        return self._model_class(**response["data"], _client=self._http._client)

    async def create(self, data: UserCreate | dict[str, Any]) -> User:
        """
        Create a new user.

        Args:
            data: UserCreate model or dict.

        Returns:
            Created user.
        """
        if isinstance(data, UserCreate):
            create_dict = data.model_dump()
        else:
            create_dict = data

        response = await self._http.post(self._endpoint, **create_dict)
        return self._model_class(**response["data"], _client=self._http._client)
```

## Approach 4: Pydantic exclude_unset

For partial updates (PATCH-style), use `exclude_unset`:

```python
class User(BaseModel):
    id: int
    name: str
    email: str
    administrator: int

    async def save(self) -> "User":
        """
        Save changes to this user.

        Only sends fields that have been modified since creation/load.

        Example:
            >>> user = await client.users.get(1)
            >>> user.name = "New Name"  # Only this changed
            >>> await user.save()  # Only sends {'name': 'New Name'}
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Only send changed fields
        update_data = self.model_dump(
            exclude={"id", "_client"},
            exclude_unset=True  # Only include explicitly set fields
        )

        return await self._client.users.update(self.id, **update_data)
```

## Recommended Pattern for This SDK

Use **Approach 1 (Smart Serialization)** as the base pattern:

```python
from typing import Any
from pydantic import Field
from upsales.models.base import BaseModel

class User(BaseModel):
    # Mark read-only fields with frozen=True
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)

    # Normal updatable fields
    name: str
    email: str

    def to_update_dict(self, **overrides: Any) -> dict[str, Any]:
        """Get dict for updates, excluding read-only fields."""
        data = self.model_dump(exclude={"_client"})

        # Remove frozen fields
        for field_name, field_info in self.__class__.model_fields.items():
            if field_info.frozen:
                data.pop(field_name, None)

        data.update(overrides)
        return data

    async def edit(self, **kwargs: Any) -> "User":
        """Edit user, automatically excluding read-only fields."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
```

**Benefits**:
- Simple API: `await user.edit(name="New Name")`
- Type-safe: Pydantic validates field types
- Safe: Read-only fields automatically excluded
- Flexible: Can still use dict kwargs
- Pythonic: Follows Python 3.13+ patterns

## Complete Example

```python
# upsales/models/user.py
from typing import Any
from pydantic import Field
from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields


class User(BaseModel):
    """Full User model with read-only field handling."""

    # Read-only fields - marked with frozen=True
    id: int = Field(frozen=True, description="Unique user identifier")
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Updatable fields
    name: str
    email: str
    administrator: int
    active: int = 1
    custom: list[dict] = Field(default_factory=list)

    @property
    def custom_fields(self) -> CustomFields:
        """Get custom fields helper."""
        return CustomFields(self.custom)

    def to_update_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize for update requests.

        Excludes read-only fields (frozen=True) and private fields.

        Args:
            **overrides: Additional fields to override.

        Returns:
            Dict for API update request.
        """
        data = self.model_dump(exclude={"_client"})

        # Remove frozen (read-only) fields
        for field_name, field_info in self.__class__.model_fields.items():
            if field_info.frozen:
                data.pop(field_name, None)

        data.update(overrides)
        return data

    async def edit(self, **kwargs: Any) -> "User":
        """
        Edit this user.

        Automatically excludes read-only fields like id and timestamps.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated user.

        Example:
            >>> user = await client.users.get(1)
            >>> user.name = "Jane"
            >>> updated = await user.edit()  # Sends all non-readonly fields
            >>>
            >>> # Or update specific fields
            >>> updated = await user.edit(name="Jane", email="jane@example.com")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )


class PartialUser(PartialModel):
    """Partial User model for nested objects."""

    id: int
    name: str
    email: str | None = None

    async def fetch_full(self) -> User:
        """Fetch full user data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.get(self.id)

    async def edit(self, **kwargs: Any) -> User:
        """Edit this user."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(self.id, **kwargs)
```

## Testing Updates

```python
# tests/unit/test_user_updates.py
import pytest
from upsales.models.user import User

def test_to_update_dict_excludes_readonly():
    """Test that to_update_dict excludes read-only fields."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        administrator=0,
        created_at="2024-01-01",
        updated_at="2024-01-02"
    )

    update_dict = user.to_update_dict()

    # Read-only fields should be excluded
    assert "id" not in update_dict
    assert "created_at" not in update_dict
    assert "updated_at" not in update_dict

    # Updatable fields should be included
    assert update_dict["name"] == "John"
    assert update_dict["email"] == "john@example.com"

def test_to_update_dict_with_overrides():
    """Test overriding fields in to_update_dict."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        administrator=0
    )

    update_dict = user.to_update_dict(name="Jane", active=0)

    assert update_dict["name"] == "Jane"
    assert update_dict["active"] == 0

def test_frozen_fields_cannot_be_modified():
    """Test that frozen fields raise error when modified."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        administrator=0
    )

    with pytest.raises(ValueError, match="frozen"):
        user.id = 2
```

## Summary

**Recommended approach**: Use Pydantic's `frozen=True` to mark read-only fields and add `to_update_dict()` method to models.

**Benefits**:
- ✅ Simple, Pythonic API
- ✅ Type-safe with Pydantic validation
- ✅ Automatic exclusion of read-only fields
- ✅ Flexible (supports both model instances and dicts)
- ✅ Fits template-driven design
- ✅ Uses Python 3.13+ syntax throughout
