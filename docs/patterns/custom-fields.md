# Working with Custom Fields

Guide for handling Upsales custom fields using the CustomFields helper and Pydantic v2 validators.

## Overview

Upsales allows custom fields on most objects. The API represents them as:

```json
{
  "custom": [
    {
      "fieldId": 11,
      "value": "string_value",
      "valueInteger": null,
      "valueDate": null,
      "valueArray": null
    }
  ]
}
```

The SDK provides two ways to work with custom fields:
1. **CustomFieldsList validator** - Validates structure when creating/updating models
2. **CustomFields helper** - Dict-like access to custom field values

## Pydantic v2 Validator

### Using CustomFieldsList in Models

**RECOMMENDED**: Use the `CustomFieldsList` validator for automatic structure validation:

```python
from upsales.validators import CustomFieldsList
from pydantic import Field

class User(BaseModel):
    # ✅ Validates custom fields structure automatically
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    # ❌ Old way (no validation)
    # custom: list[dict] = []
```

**Benefits:**
- ✅ Validates each field has required `fieldId`
- ✅ Validates `fieldId` is an integer
- ✅ Clear error messages when structure is invalid
- ✅ Consistent across all models

**Example:**
```python
# Valid
user = User(id=1, name="John", email="john@example.com", regDate="2024-01-01",
            custom=[{"fieldId": 11, "value": "test"}])  # ✅ Works

# Invalid - missing fieldId
user = User(id=1, name="John", email="john@example.com", regDate="2024-01-01",
            custom=[{"value": "test"}])  # ❌ Raises validation error
```

The `CustomFields` helper provides dict-like access to validated data.

## Basic Usage

### Accessing Custom Fields

```python
# Get object with custom fields
user = await upsales.users.get(1)

# Get CustomFields helper
custom = user.custom_fields

# Access by field ID
value = custom[11]

# With default fallback
value = custom.get(11, "default")

# Check if field exists
if 11 in custom:
    print(custom[11])
```

### Updating Custom Fields

```python
# Set value by field ID
custom[11] = "new value"

# Set new field
custom[99] = "value for new field"

# Convert to API format and save
await user.edit(custom=custom.to_api_format())
```

## Using Field Schemas

For better readability, use field aliases:

### Step 1: Fetch Field Schema

```python
# Get custom field definitions for users
response = await upsales.http.get("/customFields/User")
schema = {
    field["alias"]: field["id"]
    for field in response["data"]
}

# Example schema:
# {
#     "DEPARTMENT": 11,
#     "EMPLOYEE_ID": 12,
#     "START_DATE": 13,
# }
```

### Step 2: Use Aliases

```python
# Create CustomFields with schema
custom = CustomFields(user.custom, field_schema=schema)

# Access by alias
department = custom["DEPARTMENT"]
employee_id = custom["EMPLOYEE_ID"]

# Set by alias
custom["DEPARTMENT"] = "Engineering"
```

## Data Types

Custom fields support different data types:

```python
# String values
custom[11] = "text value"

# The CustomFields helper currently focuses on 'value' field
# For other types, access raw custom list:
for field in user.custom:
    match field:
        case {"fieldId": 12, "valueInteger": int(i)}:
            print(f"Integer field: {i}")
        case {"fieldId": 13, "valueDate": str(d)}:
            print(f"Date field: {d}")
        case {"fieldId": 14, "valueArray": list(arr)}:
            print(f"Array field: {arr}")
```

## Complete Example

```python
"""Complete custom fields example."""
import asyncio
from upsales import Upsales

async def main():
    async with Upsales(token="YOUR_TOKEN") as upsales:
        # Get user
        user = await upsales.users.get(1)

        # Access custom fields
        custom = user.custom_fields

        # Read values
        print(f"Field 11: {custom.get(11, 'not set')}")

        # Update values
        custom[11] = "updated value"
        custom[12] = "new field value"

        # Save changes
        await user.edit(custom=custom.to_api_format())
        print("Custom fields updated!")

asyncio.run(main())
```

## Pattern for Models

Always include custom fields in models:

```python
from pydantic import Field
from upsales.models.base import BaseModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

class User(BaseModel):
    id: int
    name: str
    email: str
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @property
    def custom_fields(self) -> CustomFields:
        """Get custom fields helper."""
        return CustomFields(self.custom)

# Usage
user = User(id=1, name="John", email="john@example.com")
user.custom_fields[11] = "value"
```

## Advanced: Caching Schemas

For better performance, cache field schemas:

```python
class SchemaCache:
    """Cache for custom field schemas."""

    def __init__(self, client: Upsales):
        self.client = client
        self._cache: dict[str, dict[str, int]] = {}

    async def get_schema(self, object_type: str) -> dict[str, int]:
        """Get schema for object type."""
        if object_type not in self._cache:
            response = await self.client.http.get(
                f"/customFields/{object_type}"
            )
            self._cache[object_type] = {
                field["alias"]: field["id"]
                for field in response["data"]
            }
        return self._cache[object_type]

# Usage
cache = SchemaCache(client)
user_schema = await cache.get_schema("User")

user = await upsales.users.get(1)
custom = CustomFields(user.custom, field_schema=user_schema)
```

## Type-Safe Custom Fields

For critical custom fields, create typed properties:

```python
class User(BaseModel):
    id: int
    name: str
    custom: list[dict] = []

    @property
    def custom_fields(self) -> CustomFields:
        return CustomFields(self.custom)

    @property
    def department(self) -> str | None:
        """Get department custom field (ID 11)."""
        return self.custom_fields.get(11)

    @department.setter
    def department(self, value: str) -> None:
        """Set department custom field."""
        self.custom_fields[11] = value

    @property
    def employee_id(self) -> str | None:
        """Get employee ID custom field (ID 12)."""
        return self.custom_fields.get(12)

    @employee_id.setter
    def employee_id(self, value: str) -> None:
        """Set employee ID custom field."""
        self.custom_fields[12] = value

# Usage - type-safe!
user = await upsales.users.get(1)
user.department = "Engineering"  # Type-checked!
await user.edit(custom=user.custom_fields.to_api_format())
```

## Best Practices

1. **Always include custom fields** in model definitions
2. **Use field schemas** for better readability
3. **Cache schemas** to avoid repeated API calls
4. **Create typed properties** for frequently-used fields
5. **Document field IDs** in model docstrings

## Checklist

- [ ] Model includes `custom: list[dict] = []`
- [ ] Model has `custom_fields` property
- [ ] Critical fields have typed properties
- [ ] Field IDs documented in docstrings
- [ ] Schema caching for multiple objects
