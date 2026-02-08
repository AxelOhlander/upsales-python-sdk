# Creating Models

Guide for creating Pydantic models for Upsales API objects using Python 3.13 syntax.

## Overview

Models represent API data as Python objects. This SDK uses two types:

1. **BaseModel**: Full objects with all fields (from GET /resource/:id)
2. **PartialModel**: Minimal objects for nested data (e.g., user.role)

## Python 3.13 Type Hints

**CRITICAL**: Use native type hints, NOT typing imports.

### ✅ Correct Usage

```python
# No typing imports needed!
class User(BaseModel):
    id: int
    name: str
    email: str | None = None  # Use | for unions
    tags: list[str] = []  # Use list, not List
    metadata: dict[str, any] = {}  # Use dict, not Dict
    role: PartialRole | None = None
```

### ❌ Incorrect Usage

```python
# DON'T DO THIS
from typing import Optional, List, Dict, Union

class User(BaseModel):
    email: Optional[str] = None  # Wrong
    tags: List[str] = []  # Wrong
    metadata: Dict[str, any] = {}  # Wrong
```

## Basic Model Structure

### Full Model (with Pydantic v2 Features)

```python
"""
User models for Upsales API.

Uses Python 3.13 native type hints and Pydantic v2 advanced features.
"""

from typing import TYPE_CHECKING, Unpack, TypedDict, Any
from pydantic import Field, computed_field, field_serializer
from upsales.models.base import BaseModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr

if TYPE_CHECKING:
    from upsales import Upsales


# TypedDict for IDE autocomplete
class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    Only updatable fields - excludes frozen fields like id.
    """
    name: str
    email: str
    administrator: int
    active: int
    custom: list[Any]


class User(BaseModel):
    """
    Full User model from Upsales API.

    All fields are guaranteed to be present when retrieved via GET /users/:id.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Example:
        >>> user = await upsales.users.get(1)
        >>> user.name
        'John Doe'
        >>> user.is_admin  # Computed property
        True
        >>> user.custom_fields[11]  # Dict-like access
        'value'
    """

    # Read-only fields - frozen=True, strict=True
    id: int = Field(frozen=True, strict=True, description="Unique user ID")
    regDate: str = Field(frozen=True, description="Registration date")

    # Required fields with Pydantic v2 validators
    name: NonEmptyStr = Field(description="User's full name")
    email: EmailStr = Field(description="User's email (normalized)")

    # Binary flags with validation
    administrator: BinaryFlag = Field(default=0, description="Admin flag (0=no, 1=yes)")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

    # Custom fields with structure validation
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    # Optional fields
    role: dict[str, Any] | None = Field(None, description="User's role")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access.

        Example:
            >>> user.custom_fields[11]  # By field ID
            'value'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_admin(self) -> bool:
        """Check if user is administrator."""
        return self.administrator == 1

    @field_serializer('custom', when_used='json')
    def serialize_custom_fields(self, custom: list[dict]) -> list[dict]:
        """Clean custom fields for API requests."""
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """
        Edit this user via the API with type-safe autocomplete.

        Uses Pydantic v2's optimized serialization (5-50x faster).

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated user with fresh data from API.

        Example:
            >>> user = await upsales.users.get(1)
            >>> updated = await user.edit(name="Jane Doe", administrator=1)

        Note:
            This method uses to_update_dict_minimal() which only sends
            changed fields plus required fields, reducing API payload size.
            Alternative: to_api_dict() sends all non-frozen fields.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict_minimal(**kwargs)  # Preferred: only changed + required fields
        )
```

**Key Pydantic v2 Features Used:**
- ✅ **Reusable Validators**: `BinaryFlag`, `EmailStr`, `CustomFieldsList`, `NonEmptyStr`
- ✅ **Computed Fields**: `@computed_field` for derived properties
- ✅ **Field Serializers**: `@field_serializer` for custom serialization
- ✅ **Strict Type Checking**: `strict=True` on critical fields
- ✅ **Field Descriptions**: `description=` on all fields
- ✅ **Optimized Serialization**: `to_api_dict()` method (5-50x faster)

### Partial Model (with Pydantic v2 Features)

```python
class PartialUser(PartialModel):
    """
    Partial User model for nested objects.

    Only minimal fields are guaranteed. Used when user
    appears nested in other responses.

    Example:
        >>> # User appears nested in company response
        >>> company = await upsales.companies.get(1)
        >>> owner: PartialUser = company.owner
        >>> full_owner: User = await owner.fetch_full()
    """

    # Use validators even in partial models
    id: int = Field(frozen=True, strict=True, description="Unique user ID")
    name: NonEmptyStr = Field(description="User's name")
    email: EmailStr = Field(description="User's email")

    async def fetch_full(self) -> User:
        """
        Fetch full user data from API.

        Returns:
            Full User object with all fields.

        Example:
            >>> partial = PartialUser(id=1, name="John", email="john@example.com")
            >>> full = await partial.fetch_full()
            >>> full.administrator  # Now available
            1
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.get(self.id)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> User:
        """
        Edit this user via the API.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full User object.

        Example:
            >>> partial = company.owner  # PartialUser
            >>> updated = await partial.edit(name="Jane")  # Returns User
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(self.id, **kwargs)
```

**Pydantic v2 in Partial Models:**
- ✅ Use validators (`NonEmptyStr`, `EmailStr`) for consistency
- ✅ Add `strict=True` to ID fields
- ✅ Add field descriptions
- ✅ Use TypedDict in `edit()` for autocomplete

## Field Types Guide

### Read-Only Fields (Frozen)

Mark fields that should never be updated with `Field(frozen=True)`:

```python
from pydantic import Field

class MyModel(BaseModel):
    # Read-only fields - never sent in updates
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Updatable fields
    name: str
    active: int
```

**Benefits**:
- Fields marked `frozen=True` are excluded from `to_update_dict()`
- Pydantic prevents direct modification: `user.id = 2` raises error
- TypedDict excludes these from autocomplete

### Primitives

```python
class MyModel(BaseModel):
    # Integers
    count: int
    optional_count: int | None = None

    # Strings
    name: str
    optional_name: str | None = None

    # Floats
    price: float
    optional_price: float | None = None

    # Booleans (Note: Upsales uses 0/1 integers)
    active: int  # 0 or 1, not bool!
```

### Collections

```python
class MyModel(BaseModel):
    # Lists (use list, not List)
    tags: list[str] = []
    ids: list[int] = []
    items: list[dict] = []

    # Dicts (use dict, not Dict)
    metadata: dict[str, any] = {}
    settings: dict[str, str | int] = {}
```

### Nested Objects

```python
class Company(BaseModel):
    id: int
    name: str

    # Single nested object
    owner: PartialUser | None = None

    # List of nested objects
    contacts: list[PartialContact] = []
```

### Unions (use |)

```python
class MyModel(BaseModel):
    # Use | for unions (Python 3.10+)
    value: str | int | None = None
    data: dict | list = {}

    # Multiple types
    response: User | PartialUser | None = None
```

### Custom Fields

```python
class MyModel(BaseModel):
    # Always include custom fields
    custom: list[dict] = []

    @property
    def custom_fields(self) -> CustomFields:
        """Get custom fields helper."""
        return CustomFields(self.custom)
```

## Docstring Requirements

All models need **90%+ docstring coverage**.

### Class Docstring

```python
class User(BaseModel):
    """
    Full User model from Upsales API.

    Brief description of what this model represents.
    Include when/how it's used.

    Attributes:
        id: Description of id field.
        name: Description of name field.
        # ... list all important fields

    Example:
        >>> # Show common usage
        >>> user = User(id=1, name="John")
        >>> print(user.name)
    """
```

### Method Docstrings

```python
async def edit(self, **kwargs) -> "User":
    """
    Edit this user via the API.

    Detailed description of what this method does.

    Args:
        **kwargs: Description of what kwargs are accepted.

    Returns:
        Description of return value.

    Raises:
        RuntimeError: When client not available.

    Example:
        >>> user = await upsales.users.get(1)
        >>> updated = await user.edit(name="New")
    """
```

## Pattern Matching for Type Handling

Use pattern matching for complex field parsing:

```python
from typing import Any

class MyModel(BaseModel):
    value: str | int | None = None

    @classmethod
    def parse_value(cls, data: dict[str, Any]) -> str | int | None:
        """Parse value field using pattern matching."""
        raw_value = data.get("value")

        match raw_value:
            case str() as s:
                return s
            case int() as i:
                return i
            case None:
                return None
            case _:
                raise ValueError(f"Unexpected value type: {type(raw_value)}")
```

## Complex Example

Complete example with all patterns:

```python
"""
Product models for Upsales API.

Uses Python 3.13 native type hints.
"""

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields


class Product(BaseModel):
    """
    Full Product model from Upsales API.

    Represents a product in the Upsales catalog with pricing,
    categories, and custom fields.

    Attributes:
        id: Unique product identifier.
        name: Product name.
        description: Optional product description.
        price: Product price.
        active: Active status (0 or 1).
        category: Product category (partial object).
        tags: List of tag strings.
        custom: Custom fields list.

    Example:
        >>> product = Product(
        ...     id=1,
        ...     name="Widget",
        ...     price=99.99,
        ...     active=1,
        ... )
        >>> print(f"{product.name}: ${product.price}")
    """

    id: int
    name: str
    description: str | None = None
    price: float
    active: int  # 0 or 1
    category: PartialCategory | None = None
    tags: list[str] = []
    custom: list[dict] = []
    metadata: dict[str, any] = {}

    @property
    def custom_fields(self) -> CustomFields:
        """Get custom fields helper."""
        return CustomFields(self.custom)

    @property
    def is_active(self) -> bool:
        """Check if product is active."""
        return self.active == 1

    async def edit(self, **kwargs) -> "Product":
        """Edit this product."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.update(self.id, **kwargs)

    async def deactivate(self) -> "Product":
        """
        Deactivate this product.

        Returns:
            Updated product with active=0.
        """
        return await self.edit(active=0)


class PartialProduct(PartialModel):
    """
    Partial Product model for nested objects.

    Example:
        >>> order = await upsales.orders.get(1)
        >>> product: PartialProduct = order.product
        >>> full: Product = await product.fetch_full()
    """

    id: int
    name: str
    price: float | None = None

    async def fetch_full(self) -> Product:
        """Fetch full product data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.get(self.id)

    async def edit(self, **kwargs) -> Product:
        """Edit this product."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.products.update(self.id, **kwargs)
```

## Type-Safe Updates

The SDK uses **TypedDict with Unpack** to provide full IDE autocomplete and type checking for model updates. This pattern was chosen after evaluating multiple approaches for the best developer experience.

### Why TypedDict + Unpack?

**The Problem** with `**kwargs: Any`:
- No IDE autocomplete
- No type checking
- User must read docs to discover available fields

**The Solution**:
```python
from typing import Unpack, TypedDict

class UserUpdateFields(TypedDict, total=False):
    """Available fields for updating a User."""
    name: str
    email: str
    administrator: int

class User(BaseModel):
    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit with full IDE autocomplete."""
        ...
```

### Comparison of Approaches

| Approach | IDE Autocomplete | Type Checking | Flexibility | Maintenance |
|----------|-----------------|---------------|-------------|-------------|
| **TypedDict + Unpack** ✅ | Perfect | Full | High | Medium |
| Explicit Parameters | Perfect | Full | Limited | High |
| Hybrid (overload) | Good | Good | High | Medium |
| **kwargs: Any | None | None | High | Low |

**TypedDict + Unpack** provides the best balance of developer experience and maintainability for our template-driven architecture.

### Testing Type Safety

Verify TypedDict correctness in tests:

```python
from upsales.models.user import User, UserUpdateFields

def test_typeddict_structure():
    """Verify TypedDict has correct fields."""
    expected_fields = {"name", "email", "administrator", "active", "custom"}
    actual_fields = set(UserUpdateFields.__annotations__.keys())
    assert actual_fields == expected_fields

def test_typeddict_types():
    """Verify TypedDict has correct types."""
    assert UserUpdateFields.__annotations__["name"] == str
    assert UserUpdateFields.__annotations__["administrator"] == int
```

### Key Guidelines

1. **Define TypedDict** for every model with updatable fields
2. **Use `total=False`** to make all fields optional
3. **Exclude frozen fields** (id, timestamps) from TypedDict
4. **Document fields** in TypedDict docstring
5. **Use `Unpack`** in `edit()` signature for autocomplete

## Checklist

Before submitting models:

- [ ] Uses Python 3.13 native type hints (no typing imports except `Unpack`, `TypedDict`)
- [ ] All unions use `|` operator
- [ ] All collections use lowercase (`list`, `dict`)
- [ ] Read-only fields marked with `Field(frozen=True)`
- [ ] TypedDict created for `edit()` with only updatable fields
- [ ] `edit()` uses `Unpack[{Model}UpdateFields]` signature
- [ ] `edit()` calls `to_update_dict_minimal(**kwargs)` (preferred) or `to_api_dict(**kwargs)`
- [ ] Includes both BaseModel and PartialModel versions
- [ ] 90%+ docstring coverage
- [ ] Examples in docstrings
- [ ] Custom fields support with `custom_fields` property
- [ ] `edit()` and `fetch_full()` methods implemented
- [ ] Passes mypy strict mode
- [ ] Passes ruff linting
