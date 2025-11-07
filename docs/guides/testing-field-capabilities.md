# Testing Field Capabilities for Endpoints

**Purpose**: Document which fields support sorting, filtering, and search operators
**When to use**: When adding a new endpoint or discovering API capabilities
**Time**: 15-30 minutes per endpoint

---

## 🎯 Why Test Field Capabilities

Not all fields support all operations in the Upsales API:
- Some fields are sortable, some are not
- Some fields support comparison operators (>, <, etc.)
- Some fields support substring search (*)
- This varies by endpoint!

**Benefits of testing**:
- ✅ Know which features work before documenting
- ✅ Provide accurate examples in docstrings
- ✅ Avoid user errors (trying to sort on unsupported field)
- ✅ Optimize queries (use sortable fields)

---

## 🧪 Manual Testing Process

### Step 1: Test Sorting (10 minutes)

**Use Postman, curl, or Python REPL**:

```python
# In Python REPL or temp script
from upsales import Upsales
import asyncio

async def test_sorting():
    async with Upsales.from_env() as upsales:
        # Test common fields
        fields_to_test = ["id", "name", "regDate", "modDate", "active"]

        for field in fields_to_test:
            try:
                # Test ascending
                results = await upsales.contacts.list(limit=5, sort=field)
                print(f"✅ {field}: Sortable (ascending)")

                # Test descending
                results = await upsales.contacts.list(limit=5, sort=f"-{field}")
                print(f"✅ {field}: Sortable (descending)")

            except Exception as e:
                print(f"❌ {field}: Not sortable - {e}")

asyncio.run(test_sorting())
```

**Document results**:
```
Sortable fields for contacts:
  ✅ id (asc/desc)
  ✅ name (asc/desc)
  ✅ regDate (asc/desc)
  ✅ modDate (asc/desc)
  ❌ active (not sortable)
```

---

### Step 2: Test Search Operators (10 minutes)

```python
async def test_operators():
    async with Upsales.from_env() as upsales:
        field = "regDate"  # Test date field

        try:
            # Greater than
            await upsales.contacts.search(**{field: ">2024-01-01"})
            print(f"✅ {field}: Supports >")
        except:
            print(f"❌ {field}: No >")

        try:
            # Substring
            await upsales.contacts.search(name="*test")
            print(f"✅ name: Supports *")
        except:
            print(f"❌ name: No *")

asyncio.run(test_operators())
```

---

### Step 3: Test Field Selection (5 minutes)

```python
async def test_field_selection():
    async with Upsales.from_env() as upsales:
        # Test if specific fields can be selected
        results = await upsales.contacts.list(
            limit=1,
            fields=["id", "name", "email"]
        )

        # Verify only those fields returned
        if results:
            contact = results[0]
            print(f"Fields returned: {list(contact.model_dump().keys())}")

asyncio.run(test_field_selection())
```

---

## 📝 Document Results

### Create Capability Matrix

**For each endpoint, document**:

```markdown
## Contacts Endpoint Capabilities

### Sortable Fields
- ✅ id (numeric)
- ✅ name (alphabetic)
- ✅ regDate (date)
- ✅ modDate (date)
- ❌ active (binary, not sortable)
- ❌ custom (array, not sortable)

### Fields Supporting Comparison Operators
- ✅ id: >, >=, <, <=, =, !=
- ✅ regDate: >, >=, <, <=, =, !=
- ✅ modDate: >, >=, <, <=, =, !=
- ⚠️ active: =, != only (binary)

### Fields Supporting Substring Search
- ✅ name: * (contains)
- ✅ email: * (contains)
- ✅ phone: * (contains)
- ❌ id: No (numeric)
- ❌ active: No (binary)

### Field Selection
- ✅ All fields support selection
- ✅ Nested fields work: "company.name", "users.id"
```

**Save as**: `docs/capabilities/{endpoint}-capabilities.md`

---

## 🔍 Automated Testing Script

**Create**: `scripts/test_field_capabilities.py`

```python
"""
Script to test field capabilities for an endpoint.

Usage:
    python scripts/test_field_capabilities.py contacts
    python scripts/test_field_capabilities.py companies
"""

import asyncio
import sys
from upsales import Upsales


async def test_endpoint_capabilities(endpoint_name: str):
    """Test which fields support sorting, operators, etc."""

    async with Upsales.from_env() as upsales:
        resource = getattr(upsales, endpoint_name)

        # Get sample object to find available fields
        print(f"Testing {endpoint_name} endpoint...")
        objects = await resource.list(limit=1)

        if not objects:
            print("❌ No objects found to test")
            return

        obj = objects[0]
        fields = list(obj.model_fields.keys())
        print(f"Found {len(fields)} fields to test")

        sortable = []
        comparable = []
        searchable = []

        for field in fields:
            # Skip complex fields
            if field in ["custom", "_client"]:
                continue

            # Test sorting
            try:
                await resource.list(limit=1, sort=field)
                sortable.append(field)
                print(f"  ✅ {field}: Sortable")
            except:
                print(f"  ❌ {field}: Not sortable")

        print(f"\nSummary:")
        print(f"  Sortable: {len(sortable)}/{len(fields)}")
        print(f"  Fields: {', '.join(sortable)}")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "users"
    asyncio.run(test_endpoint_capabilities(endpoint))
```

**Usage**:
```bash
python scripts/test_field_capabilities.py users
python scripts/test_field_capabilities.py companies
python scripts/test_field_capabilities.py products
```

---

## 📊 Expected Results by Field Type

### Typically Sortable
- ✅ `id` - Numeric primary key
- ✅ `name` - String field
- ✅ `regDate` - Date field
- ✅ `modDate` - Date field
- ✅ `score` - Numeric field
- ✅ `value` - Numeric field

### Typically NOT Sortable
- ❌ `active` - Binary flag (0/1)
- ❌ `custom` - Array/object field
- ❌ `addresses` - Array field
- ❌ Boolean fields

### Comparison Operators by Field Type
- **Numeric** (id, score, value): All operators (>, >=, <, <=, =, !=)
- **Date** (regDate, modDate): All operators
- **Binary** (active, administrator): = and != only
- **String** (name, email): = and != (plus * for substring)

---

## 🎯 Best Practices

### When Adding New Endpoint

1. **Generate model** first
2. **Test field capabilities** (15-30 min)
3. **Document findings** in model docstring
4. **Add examples** using confirmed sortable fields
5. **Avoid assumptions** - test first!

### Docstring Pattern

```python
class Contact(BaseModel):
    """
    Contact model from /api/v2/contacts.

    Sortable fields: id, name, regDate, modDate, email
    Searchable (*): name, email, phone
    Comparison ops: id, regDate, modDate (all), active (= and != only)

    Example:
        >>> # Sorted by name
        >>> contacts = await upsales.contacts.list(sort="name")
        >>>
        >>> # Search with substring
        >>> results = await upsales.contacts.search(phone="*555")
    """
```

---

## 📋 Testing Checklist

**For each new endpoint**:

- [ ] Test 5-10 common fields for sorting
- [ ] Test numeric fields for comparison operators
- [ ] Test string fields for substring search (*)
- [ ] Test field selection works
- [ ] Document sortable fields in model docstring
- [ ] Add sorting examples to resource docstring
- [ ] Test multi-field sort if needed

**Time**: 15-30 minutes per endpoint

---

## 🔍 Known Limitations

### From Testing
- Binary flags (0/1) typically not sortable
- Array fields (custom, addresses) not sortable
- Nested objects may not be sortable directly
- Some endpoints may have restricted sorting

### Fallback
If sorting fails on a field:
- ✅ Fetch data unsorted
- ✅ Sort client-side in Python
- ✅ Document limitation

---

## 📖 Reference

**Current tested endpoints**:
- users: Documented in model
- companies: Documented in model
- products: Documented in model

**Next endpoints to test**:
- contacts
- opportunities
- activities
- appointments

**Save results**: Document in model docstrings and capability matrix

---

## 🧪 Testing Field Editability

### Why Test Editability

**Problem**: We mark fields as `frozen=True` based on assumptions, but haven't verified with real API.

**Risks**:
- Field marked frozen but API actually allows updates
- Field in TypedDict but API rejects/ignores updates
- Missing frozen fields that should be read-only

**Solution**: Test each field systematically

---

### Using the Test Script

**Script**: `scripts/test_field_editability.py`

**Usage**:
```bash
# Test which fields are editable
python scripts/test_field_editability.py users

# Test specific object ID
python scripts/test_field_editability.py companies 123

# ⚠️ WARNING: Uses real API updates! Use test environment!
```

**What it does**:
1. Fetches a test object
2. Tries to update each field one-by-one
3. Checks if API accepts the update
4. Checks if field value changed
5. Reports editable vs read-only fields
6. Warns about model mismatches

---

### Manual Testing Process

```python
# In Python REPL or temp script
from upsales import Upsales
import asyncio

async def test_field(resource, obj_id: int, field: str, value):
    """Test if a specific field is editable."""
    original = await resource.get(obj_id)
    current = getattr(original, field)

    try:
        # Try to update just this field
        updated = await resource.update(obj_id, **{field: value})
        new_value = getattr(updated, field)

        if new_value == value:
            print(f"✅ {field}: Editable (value changed)")
            return "editable"
        elif new_value == current:
            print(f"❌ {field}: Read-only (API ignored update)")
            return "ignored"
        else:
            print(f"⚠️ {field}: Unexpected value")
            return "unexpected"
    except Exception as e:
        print(f"❌ {field}: Error - {e}")
        return "error"

# Test all fields
async def test_all():
    async with Upsales.from_env() as upsales:
        # Test field
        await test_field(upsales.users, 1, "name", "Test Name")
        await test_field(upsales.users, 1, "id", 999)  # Should fail
        await test_field(upsales.users, 1, "regDate", "2099-01-01")  # Should fail

asyncio.run(test_all())
```

---

### Interpreting Results

**✅ Editable**: API accepted update and value changed
- Should NOT be marked frozen
- Should be in TypedDict

**❌ Read-Only (Ignored)**: API didn't error but ignored the update
- Should be marked `frozen=True`
- Should NOT be in TypedDict

**❌ Error**: API returned error (validation, permission, etc.)
- Should be marked `frozen=True`
- Should NOT be in TypedDict

**⚠️ Warnings**:
- "Marked frozen but editable" → Remove frozen=True
- "Not frozen but ignored" → Add frozen=True
- "In TypedDict but not editable" → Remove from TypedDict

---

### Expected Results

**Typically Read-Only** (should be frozen):
- `id` - Primary key (never editable)
- `regDate` - Registration/creation date (set once)
- `modDate` - Modification date (auto-updated by API)
- `created` - Timestamp (set once)
- `updated` - Timestamp (auto-updated)
- `createdAt` - Timestamp (set once)
- `updatedAt` - Timestamp (auto-updated)

**Typically Editable** (should NOT be frozen):
- `name` - Object name
- `email` - Email address
- `active` - Active status flag
- `phone` - Phone number
- `notes` - Notes/description
- `custom` - Custom fields (array)
- Most user-facing fields

---

### After Testing

**Update model if needed**:
```python
# If test shows "name" is read-only but not marked frozen:
name: str = Field(frozen=True, description="...")  # Add frozen

# If test shows "id" is editable but marked frozen:
id: int = Field(frozen=True, strict=True, description="...")  # Keep frozen (API bug?)

# Always trust what the test shows!
```

**Update TypedDict**:
```python
class UserUpdateFields(TypedDict, total=False):
    # Only include fields that tested as editable
    name: str  # ✅ If editable
    email: str  # ✅ If editable
    # Don't include fields that tested as read-only
```

**Re-record VCR cassettes** if model changed:
```bash
rm -rf tests/cassettes/integration/test_users_integration/
uv run pytest tests/integration/test_users_integration.py -v
```

---

**Created**: 2025-11-02
**Status**: Testing guide for field capabilities
**Use**: When adding new endpoints or validating models
**Goal**: Know what works before documenting

