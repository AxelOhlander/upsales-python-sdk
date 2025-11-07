# Enhanced Model Generation - Partial Model Detection

**Updated**: 2025-11-03
**Enhancement**: Automatic Partial model detection in CLI

---

## 🎉 What's New

The `uv run upsales generate-model` command now **automatically detects** when fields should use Partial models instead of generic `dict[str, Any]`.

### Before
```python
# Old behavior
client: dict[str, Any] = Field(...)  # TODO: Create PartialModel
users: list[dict[str, Any]] = Field(...)  # Generic
regBy: dict[str, Any] = Field(...)  # Generic
```

### After
```python
# New behavior
client: PartialCompany | None = None  # TODO: from upsales.models.company import PartialCompany
users: list[PartialUser] = []  # TODO: from upsales.models.user import PartialUser
regBy: PartialUser  # TODO: from upsales.models.user import PartialUser
```

---

## 🔍 Detection Logic

The generator analyzes field names and structure to suggest Partial models:

### Field Name Patterns

| Field Name Contains | Suggests | Requirements |
|---------------------|----------|--------------|
| user, owner, assigned, regBy, modBy | `PartialUser` | has id + (name or email) |
| client, company, account | `PartialCompany` | has id + name |
| contact | `PartialContact` | has id + name |
| product | `PartialProduct` | has id + name |
| order, opportunity | `PartialOrder` | has id |
| role | `PartialRole` | has id + name |
| project | `PartialProject` | has id + name |
| activity | `PartialActivity` | has id |
| appointment | `PartialAppointment` | has id |

### Structure Requirements

**For single entities**:
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"  // Optional but helps confirm
}
```
→ Suggests: `PartialUser`

**For lists**:
```json
[
  {"id": 1, "name": "User 1", "email": "..."},
  {"id": 2, "name": "User 2", "email": "..."}
]
```
→ Suggests: `list[PartialUser]`

---

## 📝 Generated Output

### Example: Activities Endpoint

```bash
uv run upsales generate-model activities --partial
```

**Generated model includes**:

```python
class Activity(BaseModel):
    """
    Activity model from /api/v2/activities.

    Generated from 100 samples.

    TODO: Review and update field types and docstrings.
    TODO: Mark read-only fields with Field(frozen=True).
    TODO: Add custom_fields property if model has 'custom' field.
    # from upsales.models.company import PartialCompany
    # from upsales.models.contacts import PartialContact
    # from upsales.models.user import PartialUser
    TODO: Add the above imports to use Partial models
    """

    # Fields with Partial model suggestions
    client: PartialCompany | None = None  # TODO: from upsales.models.company import PartialCompany
    regBy: PartialUser  # TODO: from upsales.models.user import PartialUser
    contacts: list[PartialContact] = []  # TODO: from upsales.models.contacts import PartialContact
    users: list[PartialUser] = []  # TODO: from upsales.models.user import PartialUser
```

The docstring lists ALL needed imports at the top for easy copy-paste!

---

## 🛠️ How to Use

### Step 1: Generate Model

```bash
uv run upsales generate-model {endpoint} --partial
```

### Step 2: Review Generated Code

Open the generated file and look for:
1. **Docstring TODO section** - Lists all Partial model imports needed
2. **Inline TODO comments** - Shows import for each field
3. **Field types** - Already uses Partial models!

### Step 3: Apply Imports

Copy the imports from the docstring TODO section:

```python
# Add these to imports section
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.user import PartialUser
```

### Step 4: Remove TODO Comments

After adding imports, remove the inline TODO comments:

```python
# Before
client: PartialCompany | None = None  # TODO: from upsales.models.company import PartialCompany

# After
client: PartialCompany | None = None  # ✅ Clean
```

---

## 🎯 Smart Detection Examples

### Example 1: User References

**Field**: `regBy`, `owner`, `assignedTo`, `createdBy`, `modifiedBy`
**API Data**: `{"id": 1, "name": "John", "email": "john@example.com"}`
**Detected**: `PartialUser` ✅

### Example 2: Company References

**Field**: `client`, `company`, `account`
**API Data**: `{"id": 5, "name": "ACME Corp"}`
**Detected**: `PartialCompany` ✅

### Example 3: Contact Lists

**Field**: `contacts`, `attendees`
**API Data**: `[{"id": 10, "name": "Jane", "email": "jane@..."}]`
**Detected**: `list[PartialContact]` ✅

### Example 4: Mixed References

**Field**: `users` (list), `owner` (single)
**Detected**: Both use `PartialUser` ✅
**Import**: Only need one import for both!

---

## 📊 Validation Integration

The **validate_and_update_models.py** script now also checks Partial models:

```bash
# Validate generated model
uv run python scripts/validate_and_update_models.py activities \
    --token YOUR_TOKEN

# Output shows:
Nested Model Issues:
  • regBy (PartialUser):
    Missing in model: role  # Needs to add optional field
```

This catches when:
- Partial model is missing fields that API returns
- Partial model has extra fields not in API
- Helps keep Partial models in sync!

---

## 🔧 Validator Enhancements

The validator script also got smarter:

### Before
```
Type Mismatches:
  • client:
    Existing: PartialCompany
    Inferred: dict[str, Any]
    ❌ False positive
```

### After
```
Nested Model Issues:
  • client (PartialCompany):
    Missing in model: users
    ✅ Real issue - actionable!

(No type mismatch reported)
```

---

## 📝 Best Practices

### 1. Always Generate with --partial

```bash
uv run upsales generate-model {endpoint} --partial
```

This ensures PartialModel is created too!

### 2. Review Suggestions

Not all suggestions are correct:
- ✅ `regBy` with user data → PartialUser (correct)
- ⚠️ `activityType` with id+name → Keep as dict (it's a type definition, not entity)

Use your judgment!

### 3. Validate After Applying

```bash
# After adding imports and updating types
uv run python scripts/validate_and_update_models.py {endpoint}

# Should show:
✓ Model is up to date!
Nested Model Issues: 0
```

### 4. Update Resources

Don't forget to update resource methods:

```python
# Before
if user.get("id") == user_id

# After
if user.id == user_id
```

---

## 🚀 Complete Workflow

### 1. Generate
```bash
uv run upsales generate-model activities --partial
```

### 2. Review Generated File
- Check docstring for import list
- Review each PartialX suggestion
- Decide which to keep

### 3. Add Imports
```python
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.user import PartialUser
```

### 4. Clean Up
- Remove inline TODO comments
- Update field descriptions
- Mark frozen fields

### 5. Validate
```bash
uv run python scripts/validate_and_update_models.py activities
```

### 6. Test
```bash
uv run pytest tests/unit/test_activities_resource.py
```

---

## 💡 Detection Algorithm

```python
def _detect_partial_model(field_name: str, value: dict) -> str | None:
    """Detect Partial model from field name + structure."""

    # Must have 'id' to be entity
    if "id" not in value:
        return None

    field_lower = field_name.lower()

    # Match field name patterns
    if "user" in field_lower and ("name" in value or "email" in value):
        return "PartialUser"

    if "client" in field_lower and "name" in value:
        return "PartialCompany"

    # ... etc for all entity types

    # Generic entity (has id+name but unknown type)
    if "name" in value:
        return "dict[str, Any]  # Has id+name - consider Partial model"

    return None
```

---

## ✅ Quality Checks

| Feature | Status |
|---------|--------|
| **Detects Partial models** | ✅ Working |
| **Suggests imports** | ✅ In TODO comments |
| **Lists all imports** | ✅ In docstring |
| **Handles lists** | ✅ `list[PartialX]` |
| **MyPy compatible** | ✅ Generates valid code |
| **Validation integration** | ✅ Detects nested issues |

---

## 🎓 Examples

### Generated for Orders

```python
class Order(BaseModel):
    """
    # from upsales.models.company import PartialCompany
    # from upsales.models.contacts import PartialContact
    # from upsales.models.user import PartialUser
    TODO: Add the above imports to use Partial models
    """

    client: PartialCompany  # TODO: from upsales.models.company import PartialCompany
    user: PartialUser  # TODO: from upsales.models.user import PartialUser
    contact: PartialContact | None = None  # TODO: from upsales.models.contacts import PartialContact
```

Just copy the 3 imports from the docstring!

---

## 📚 Related Tools

1. **Model Generator**: `uv run upsales generate-model` - Now detects Partial models
2. **Model Validator**: `python scripts/validate_and_update_models.py` - Validates Partial models
3. **Dict Analyzer**: `python ai_temp_files/comprehensive_dict_analysis.py` - Finds all candidates

---

**Status**: ✅ Production Ready
**Benefits**: Saves manual detection work, catches entity references automatically
**Next**: All future model generations will suggest Partial models!

---

**Created**: 2025-11-03
**Enhancement**: CLI + Validator
**Tested**: Activities endpoint (detected 4 Partial fields correctly)
