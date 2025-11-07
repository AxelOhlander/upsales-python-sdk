# Pydantic v2 Features Guide

This guide covers the advanced Pydantic v2 features used throughout the Upsales SDK for validation, serialization, and developer experience.

## Overview

The SDK leverages Pydantic v2's advanced features for:
- **Reusable validators** - DRY validation patterns
- **Computed fields** - Derived properties with automatic serialization
- **Field serializers** - Custom serialization logic
- **Field aliases** - API name to Python name mapping
- **Optimized serialization** - 5-50x faster with Rust core
- **Model validators** - Cross-field validation rules

---

## 1. Reusable Validators

### Location
`upsales/validators.py`

### Available Validators

| Validator | Purpose | Example |
|-----------|---------|---------|
| `BinaryFlag` | Validates 0 or 1 (rejects bool) | `active: BinaryFlag = 1` |
| `EmailStr` | Validates & normalizes email | `email: EmailStr` |
| `CustomFieldsList` | Validates Upsales custom fields | `custom: CustomFieldsList = []` |
| `NonEmptyStr` | Validates & strips strings | `name: NonEmptyStr` |
| `PositiveInt` | Validates non-negative int | `count: PositiveInt = 0` |

### Usage

```python
from upsales.validators import BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr
from upsales.models.base import BaseModel

class User(BaseModel):
    # Binary flags (0 or 1)
    active: BinaryFlag = 1
    administrator: BinaryFlag = 0

    # Email (normalized to lowercase)
    email: EmailStr

    # Non-empty string (whitespace stripped)
    name: NonEmptyStr

    # Custom fields (validated structure)
    custom: CustomFieldsList = []
```

### Benefits

✅ **DRY Principle** - Define once, use everywhere
✅ **Consistency** - Same validation across all models
✅ **Better Errors** - Clear, descriptive error messages
✅ **Type Safe** - Full IDE autocomplete and type checking

### Creating Custom Validators

```python
from typing import Annotated, Any
from pydantic import BeforeValidator

def validate_phone_number(v: Any) -> str:
    """Validate and format phone number."""
    if not isinstance(v, str):
        raise ValueError("Phone must be string")
    # Remove non-digits
    digits = ''.join(c for c in v if c.isdigit())
    if len(digits) < 10:
        raise ValueError("Phone must have at least 10 digits")
    return digits

PhoneNumber = Annotated[str, BeforeValidator(validate_phone_number)]

# Usage
class Contact(BaseModel):
    phone: PhoneNumber
```

---

## 2. Computed Fields

### Purpose
Derive properties from model data with automatic serialization.

### Basic Example

```python
from pydantic import computed_field
from upsales.models.base import BaseModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import BinaryFlag, CustomFieldsList

class User(BaseModel):
    administrator: BinaryFlag = 0
    custom: CustomFieldsList = []

    @computed_field
    @property
    def is_admin(self) -> bool:
        """Check if user is administrator."""
        return self.administrator == 1

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface."""
        return CustomFields(self.custom)
```

### Usage

```python
user = await upsales.users.get(1)

# Access computed properties
if user.is_admin:
    print(f"Admin user: {user.name}")

# Access custom fields
value = user.custom_fields[11]  # By field ID
user.custom_fields["FIELD_ALIAS"] = "new value"  # By alias
```

### Advanced Example

```python
class User(BaseModel):
    name: str
    administrator: BinaryFlag
    active: BinaryFlag

    @computed_field
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        suffix = []
        if self.administrator == 1:
            suffix.append("ADMIN")
        if self.active == 0:
            suffix.append("INACTIVE")

        if suffix:
            return f"{self.name} [{', '.join(suffix)}]"
        return self.name

    @computed_field
    @property
    def status(self) -> str:
        """Get user status."""
        if self.active == 0:
            return "inactive"
        return "admin" if self.administrator == 1 else "user"
```

### Benefits

✅ **Automatic Serialization** - Included in `model_dump()` output
✅ **IDE Support** - Full autocomplete and type hints
✅ **Cleaner API** - No need for manual property management
✅ **Cacheable** - Can use `@cached_property` for expensive computations

---

## 3. Field Serializers

### Purpose
Customize how fields are serialized for API requests.

### Custom Fields Example

```python
from pydantic import field_serializer
from upsales.validators import CustomFieldsList

class User(BaseModel):
    custom: CustomFieldsList = []

    @field_serializer('custom', when_used='json')
    def serialize_custom_fields(self, custom: list[dict]) -> list[dict]:
        """
        Clean custom fields for API requests.

        Removes fields without values and extracts only necessary data.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]
```

### Multiple Fields Example

```python
class Product(BaseModel):
    price: float
    discount: float | None = None

    @field_serializer('price', 'discount', when_used='json')
    def serialize_currency(self, value: float | None) -> str | None:
        """Format currency values for API."""
        if value is None:
            return None
        return f"{value:.2f}"
```

### Benefits

✅ **Control** - Full control over serialization
✅ **Cleaner Payloads** - Remove unnecessary data
✅ **Performance** - Optimized serialization path
✅ **Type Safe** - Validated input, controlled output

---

## 4. Field Aliases

### Purpose
Map API field names to Pythonic names.

### Basic Example

```python
from pydantic import Field
from upsales.models.base import BaseModel, PartialModel

class Contact(BaseModel):
    id: int = Field(frozen=True, strict=True)
    name: str

    # API sends "client", Python uses "company"
    company: PartialCompany | None = Field(
        None,
        alias="client",
        description="Contact's company"
    )
```

### How It Works

```python
# Reading from API (deserialization)
# API sends: {"id": 1, "name": "John", "client": {"id": 10, "name": "ACME"}}
contact = Contact(**api_data)
print(contact.company.name)  # "ACME" - use Python name

# Writing to API (serialization)
data = contact.model_dump(by_alias=True)
# Returns: {"id": 1, "name": "John", "client": {...}}
# Field sent as "client" to match API
```

### Multiple Aliases

```python
class User(BaseModel):
    # Configure to accept both names
    model_config = ConfigDict(populate_by_name=True)

    email_address: str = Field(alias="email")
    phone_number: str | None = Field(None, alias="phone")
```

**Note**: `BaseModel` already has `populate_by_name=True`, so both names work for input.

### Benefits

✅ **Pythonic Code** - Use Python naming conventions
✅ **API Compatible** - Automatic conversion to API names
✅ **No Manual Mapping** - Pydantic handles it
✅ **Both Names Work** - Accept both Python and API names

---

## 5. Optimized Serialization

### to_api_dict() Method

The SDK provides `to_api_dict()` with Pydantic v2's Rust-based serialization.

```python
class User(BaseModel):
    id: int = Field(frozen=True, strict=True)
    name: str
    email: str
    active: BinaryFlag = 1

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit this user."""
        if not self._client:
            raise RuntimeError("No client available")
        # Uses optimized serialization
        return await self._client.users.update(
            self.id,
            **self.to_api_dict(**kwargs)
        )
```

### How It Works

```python
user = await upsales.users.get(1)
user.name = "Jane"

# Optimized serialization (5-50x faster than v1)
api_data = user.to_api_dict()
# Automatically:
# - Excludes frozen fields (id, created_at, etc.)
# - Uses field aliases (company → client)
# - Filters overrides to exclude frozen fields
# - Leverages Pydantic v2 Rust core

# Or with overrides
api_data = user.to_api_dict(active=0)
```

### Implementation

```python
def to_api_dict(self, **overrides: Any) -> dict[str, Any]:
    """Serialize for API using Pydantic v2 optimized serialization."""
    # Build set of frozen fields
    frozen_fields = {
        field_name
        for field_name, field_info in self.__class__.model_fields.items()
        if field_info.frozen
    }

    # Use Pydantic's optimized serialization
    data = self.model_dump(
        mode="json",
        exclude=frozen_fields | {"_client"},
        by_alias=True,  # Use field aliases
    )

    # Apply overrides, excluding frozen fields
    for key, value in overrides.items():
        if key not in frozen_fields:
            data[key] = value

    return data
```

### Performance

| Operation | Pydantic v1 | Pydantic v2 | Speedup |
|-----------|-------------|-------------|---------|
| Serialization | 1.0x | 5-50x | ⬆️ 5-50x |
| Validation | 1.0x | 5-10x | ⬆️ 5-10x |
| Model creation | 1.0x | 2-5x | ⬆️ 2-5x |

### Free-Threaded Mode

With Python 3.13 free-threaded mode:

```bash
python -X gil=0 your_script.py
```

Bulk operations can achieve true parallelism:

```python
# All updates run in parallel without GIL contention
results = await upsales.users.bulk_update(
    ids=[1, 2, 3, 4, 5],
    data={"active": 1},
    max_concurrent=5
)
```

### Benefits

✅ **5-50x Faster** - Pydantic v2 Rust core
✅ **Automatic** - Frozen fields excluded
✅ **Alias Support** - Uses field aliases
✅ **Free-Threaded Ready** - True parallelism

---

## 6. Model Validators

### Purpose
Validate relationships between fields (cross-field validation).

### Basic Example

```python
from pydantic import model_validator
from upsales.validators import BinaryFlag

class User(BaseModel):
    administrator: BinaryFlag
    role: dict | None

    @model_validator(mode='after')
    def validate_admin_has_role(self) -> 'User':
        """Ensure administrators have a role assigned."""
        if self.administrator == 1 and not self.role:
            raise ValueError("Administrator users must have a role")
        return self
```

### Advanced Example

```python
class Order(BaseModel):
    total: float
    discount: float = 0.0
    tax: float = 0.0

    @model_validator(mode='after')
    def validate_amounts(self) -> 'Order':
        """Validate order amounts make sense."""
        if self.discount < 0:
            raise ValueError("Discount cannot be negative")

        if self.discount > self.total:
            raise ValueError("Discount cannot exceed total")

        if self.tax < 0:
            raise ValueError("Tax cannot be negative")

        return self
```

### Before vs After

```python
class User(BaseModel):
    email: str
    backup_email: str | None = None

    @model_validator(mode='before')
    @classmethod
    def set_backup_email(cls, data: dict) -> dict:
        """Set backup_email if not provided."""
        if 'backup_email' not in data and 'email' in data:
            data['backup_email'] = data['email']
        return data

    @model_validator(mode='after')
    def validate_emails_different(self) -> 'User':
        """Ensure emails are different if both provided."""
        if self.backup_email and self.email == self.backup_email:
            raise ValueError("Backup email must differ from primary email")
        return self
```

### Benefits

✅ **Business Logic** - Enforce domain rules
✅ **Data Integrity** - Catch invalid combinations
✅ **Self-Documenting** - Rules visible in code
✅ **Automatic** - Runs on model creation and assignment

---

## 7. Complete Model Pattern

### Reference Implementation

See `ai_temp_files/users_enhanced.py` for a complete example combining all patterns.

### Template

```python
"""
{Model} models for Upsales API.

Generated from /api/v2/{endpoint} endpoint.
"""

from typing import TYPE_CHECKING, Unpack, TypedDict, Any

from pydantic import Field, computed_field, field_serializer, model_validator

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr

if TYPE_CHECKING:
    from upsales import Upsales


class {Model}UpdateFields(TypedDict, total=False):
    """Available fields for updating a {Model}."""
    # List all updatable fields here
    name: str
    active: int


class {Model}(BaseModel):
    """
    {Model} model from /api/v2/{endpoint}.

    Example:
        >>> model = await upsales.{resource}.get(1)
        >>> model.name
        'Example'
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique ID")
    created_at: str | None = Field(None, frozen=True, description="Creation date")

    # Required fields with validators
    name: NonEmptyStr = Field(description="Name")
    email: EmailStr = Field(description="Email address")

    # Binary flags
    active: BinaryFlag = Field(default=1, description="Active status")

    # Custom fields
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    # Computed fields
    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields."""
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if active."""
        return self.active == 1

    # Field serializers
    @field_serializer('custom', when_used='json')
    def serialize_custom_fields(self, custom: list[dict]) -> list[dict]:
        """Clean custom fields for API."""
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    # Model validators
    @model_validator(mode='after')
    def validate_business_rules(self) -> '{Model}':
        """Validate business rules."""
        # Add cross-field validation here
        return self

    # Edit method
    async def edit(self, **kwargs: Unpack[{Model}UpdateFields]) -> "{Model}":
        """
        Edit this {model}.

        Args:
            **kwargs: Fields to update (full IDE autocomplete).

        Returns:
            Updated {model}.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{resource}.update(
            self.id,
            **self.to_api_dict(**kwargs)
        )


class Partial{Model}(PartialModel):
    """
    Partial {Model} for nested responses.
    """

    id: int = Field(frozen=True, strict=True)
    name: NonEmptyStr

    async def fetch_full(self) -> {Model}:
        """Fetch full {model} data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{resource}.get(self.id)

    async def edit(self, **kwargs: Unpack[{Model}UpdateFields]) -> {Model}:
        """Edit this {model}."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{resource}.update(self.id, **kwargs)
```

---

## Best Practices

### 1. Always Use Reusable Validators

❌ **Don't:**
```python
custom: list[dict] = []
```

✅ **Do:**
```python
from upsales.validators import CustomFieldsList

custom: CustomFieldsList = []
```

### 2. Add Computed Fields for Convenience

❌ **Don't:**
```python
# User code has to check manually
if user.administrator == 1:
    ...
```

✅ **Do:**
```python
@computed_field
@property
def is_admin(self) -> bool:
    return self.administrator == 1

# Clean user code
if user.is_admin:
    ...
```

### 3. Use to_api_dict() in edit()

❌ **Don't:**
```python
async def edit(self, **kwargs) -> "User":
    return await self._client.users.update(
        self.id,
        **self.to_update_dict(**kwargs)  # Slower
    )
```

✅ **Do:**
```python
async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
    return await self._client.users.update(
        self.id,
        **self.to_api_dict(**kwargs)  # 5-50x faster
    )
```

### 4. Always Add Field Descriptions

❌ **Don't:**
```python
name: str
```

✅ **Do:**
```python
name: NonEmptyStr = Field(description="User's full name")
```

### 5. Mark Read-Only Fields Properly

❌ **Don't:**
```python
id: int
```

✅ **Do:**
```python
id: int = Field(frozen=True, strict=True, description="Unique user ID")
```

---

## See Also

- [Creating Models](creating-models.md) - Model creation guide
- [Type-Safe Updates](type-safe-updates.md) - TypedDict patterns
- [Custom Fields](custom-fields.md) - Custom fields usage
- [Field Types](field-types.md) - Field type patterns
- `ai_temp_files/users_enhanced.py` - Complete reference implementation
- `upsales/validators.py` - Validator source code
- `upsales/models/base.py` - BaseModel implementation
