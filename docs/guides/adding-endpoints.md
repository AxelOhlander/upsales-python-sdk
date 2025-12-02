# Complete Guide: Adding Endpoints to Upsales SDK
## 🤖 AUTONOMOUS AGENT BLUEPRINT

**Version**: 2.0 (Enhanced for autonomous agents)
**Date**: 2025-11-02
**Estimated Time**: 30-60 minutes per endpoint
**Prerequisites**: Foundation complete, test template ready

---

## 🎯 FOR AUTONOMOUS AGENTS: READ THIS FIRST

**This guide is self-contained for autonomous endpoint addition.**

You are an autonomous agent tasked with adding a new endpoint to the Upsales Python SDK. This guide contains ALL necessary context and patterns. Follow it exactly, and you will create production-ready, fully-tested code with minimal human intervention.

### Critical Success Criteria

Your work will be considered complete when:
1. ✅ Model generated with ALL Pydantic v2 features
2. ✅ Resource manager created with proper inheritance
3. ✅ ALL tests passing (unit + integration) with 100% resource coverage
4. ✅ VCR cassette recorded with real API data
5. ✅ ALL quality checks pass (ruff, mypy, interrogate)
6. ✅ ALL exports updated
7. ✅ Registered in client
8. ✅ 100% docstrings on all new code

**DO NOT skip any steps. DO NOT cut corners. Quality is non-negotiable.**

---

### 🔧 Field Discovery Scripts (AI Agent Optimized)

Use these scripts with `--compact` flag for minimal token output:

```bash
# Discover required fields for CREATE (POST)
python scripts/test_required_create_fields.py {endpoint} --compact

# Discover editable vs read-only fields for UPDATE (PUT)
python scripts/test_field_editability_bulk.py {endpoint} --compact
```

**Compact mode outputs JSON** with exactly what you need:
- `required_fields` / `optional_fields` for CREATE
- `editable_fields` / `frozen_recommendations` for UPDATE

**Token savings**: ~90% compared to verbose output.

---

## 📚 REQUIRED READING: Critical Documents

Before starting, understand these key documents contain essential patterns:

### 1. CLAUDE.md (Project Master Guide)
**Location**: `/CLAUDE.md`
**Critical sections**:
- **Pydantic v2 Patterns** (lines 90-200) - Validators, computed fields, serializers
- **Common Pitfalls** (lines 400-450) - Decorator order, TypedDict, field descriptions
- **Model Pattern** (lines 150-250) - Complete reference pattern

**Key takeaways**:
- Decorator order MUST be `@computed_field` then `@property` (NOT reversed!)
- All fields MUST have `description=` parameter
- TypedDict MUST include ALL updatable fields (not frozen ones)
- Always use reusable validators from `upsales/validators.py`

### 2. Reference Model Implementations
**Locations**:
- `upsales/models/user.py` - Complete reference (24 fields, all features)
- `upsales/models/company.py` - Complex model (87 fields, many PartialModels)
- `upsales/models/product.py` - Computed fields example

**Study these for**:
- Correct decorator patterns
- Field validation usage
- TypedDict structure
- edit() method implementation
- Computed field patterns

### 3. Resource Manager Examples
**Locations**:
- `upsales/resources/users.py` - Custom methods (get_by_email, get_active, etc.)
- `upsales/resources/products.py` - Bulk operations (bulk_deactivate)
- `upsales/resources/base.py` - BaseResource inheritance pattern

**Key pattern**: Inherit from `BaseResource[Model, PartialModel]` and call `super().__init__()`

### 4. Test Template
**Location**: `tests/templates/resource_template.py` (350 lines)
**MUST copy this** - Don't write tests from scratch!

### 5. Integration Test Pattern
**Location**: `tests/integration/test_users_integration.py`
**Critical**: Shows VCR configuration and cassette pattern

---

## 🔑 CRITICAL KNOWLEDGE: Core Patterns

### Pattern 1: Pydantic v2 Computed Fields (CRITICAL!)

**CORRECT decorator order** (MEMORIZE THIS!):
```python
@computed_field  # ✅ FIRST
@property        # ✅ SECOND
def is_active(self) -> bool:
    return self.active == 1
```

**WRONG decorator order** (causes TypeError):
```python
@property        # ❌ WRONG ORDER
@computed_field  # ❌ WRONG ORDER
def is_active(self) -> bool:
    return self.active == 1
# TypeError: 'PydanticDescriptorProxy' object is not callable
```

**This is THE #1 bug that was found and fixed. DO NOT make this mistake!**

---

### Pattern 2: Reusable Validators (REQUIRED)

**Location**: `upsales/validators.py`

**ALWAYS use these instead of primitive types**:

```python
from upsales.validators import (
    BinaryFlag,       # For 0 or 1 (NOT bool!)
    EmailStr,         # For emails (normalizes to lowercase)
    CustomFieldsList, # For custom field arrays
    NonEmptyStr,      # For required strings
    PositiveInt,      # For non-negative integers
)

# ✅ CORRECT
active: BinaryFlag = Field(default=1, description="Active status (0=no, 1=yes)")
email: EmailStr = Field(description="Email address")
custom: CustomFieldsList = Field(default=[], description="Custom fields")

# ❌ WRONG - Don't use primitive types
active: int = Field(default=1, description="Active status")
email: str = Field(description="Email")
custom: list[dict] = Field(default=[], description="Custom fields")
```

**Why**: Validators provide consistent validation, error messages, and behavior across all models.

---

### Pattern 3: Field Serializer (REQUIRED for models with custom fields)

**ALWAYS add this to models with `custom` field**:

```python
from pydantic import field_serializer

@field_serializer('custom', when_used='json')
def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Serialize custom fields for API requests.

    Removes fields without values to keep payloads clean.
    """
    return [
        {"fieldId": item["fieldId"], "value": item.get("value")}
        for item in custom
        if "value" in item and item.get("value") is not None
    ]
```

**Why**: Cleans custom field data before sending to API.

---

### Pattern 4: TypedDict for IDE Autocomplete (REQUIRED)

**MUST create for EVERY model**:

```python
from typing import TypedDict, Unpack

class ContactUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Contact.

    All fields are optional (total=False).
    """
    name: str
    email: str
    active: int
    phone: str
    # ... EVERY updatable field (not frozen ones!)
```

**Rules**:
- Include EVERY field that's not marked `frozen=True`
- Use plain Python types (str, int, not Field())
- Set `total=False` (all fields optional)
- Count: Model fields - frozen fields = TypedDict fields

**Verification**:
```python
# Check: Count non-frozen fields in model
# Should equal count of fields in TypedDict
```

---

### Pattern 5: edit() Method (REQUIRED)

**MUST implement in every BaseModel and PartialModel**:

```python
async def edit(self, **kwargs: Unpack[ContactUpdateFields]) -> "Contact":
    """
    Edit this contact.

    Args:
        **kwargs: Fields to update (from ContactUpdateFields).

    Returns:
        Updated Contact object from API.

    Raises:
        RuntimeError: If no client reference available.

    Example:
        >>> contact = await upsales.contacts.get(1)
        >>> updated = await contact.edit(name="New Name", email="new@example.com")
    """
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.contacts.update(
        self.id,
        **self.to_api_dict(**kwargs)  # Uses Pydantic v2 optimized serialization
    )
```

**Important**: Use `self.to_api_dict(**kwargs)` NOT `self.to_update_dict(**kwargs)`

---

### Pattern 6: Frozen Fields (REQUIRED)

**ALWAYS mark these as frozen**:

```python
from pydantic import Field

# Read-only fields from API (never send in updates)
id: int = Field(frozen=True, strict=True, description="Unique ID")
regDate: str = Field(frozen=True, description="Registration date")
modDate: str = Field(frozen=True, description="Last modification date")
createdAt: str | None = Field(None, frozen=True, description="Created timestamp")
updatedAt: str | None = Field(None, frozen=True, description="Updated timestamp")
```

**Why**:
- `frozen=True` prevents modification
- `strict=True` prevents type coercion
- Excluded from `to_api_dict()` automatically

---

### Pattern 7: Field Descriptions (REQUIRED - 100%)

**EVERY field MUST have description**:

```python
# ✅ CORRECT - Every field has description
name: str = Field(description="Contact name")
email: EmailStr = Field(description="Email address")
active: BinaryFlag = Field(default=1, description="Active status (0=no, 1=yes)")

# ❌ WRONG - Missing descriptions fails interrogate check
name: str
email: str = Field(default="")
```

**This is enforced by `uv run interrogate upsales` - must be 100%!**

---

### Pattern 8: PartialModel for Nested Objects

**When API returns nested objects like**:
```json
{
  "id": 1,
  "name": "Contact",
  "company": {"id": 5, "name": "ACME Corp"}
}
```

**Create PartialModel**:
```python
from upsales.models.company import PartialCompany

company: PartialCompany | None = Field(None, description="Contact's company")
```

**BUT if structure varies or is complex, use dict**:
```python
# API sometimes returns [], sometimes {}, sometimes null
assigned: dict[str, Any] | list[Any] | None = Field(
    None, description="Assigned user (structure varies)"
)
```

**Rule**: Trust real API data (VCR cassettes) over assumptions!

---

### Pattern 9: Field Selection (Performance Optimization)

**Use `fields` parameter** to reduce bandwidth and improve query speed (confirmed by testing).

**When to use**:
- Mobile apps (reduce data transfer)
- Dashboards (only need specific fields)
- Large datasets (faster queries)
- Frequent polling (optimize repeated queries)

**Examples**:
```python
# Return only needed fields
users = await upsales.users.list(
    limit=100,
    fields=["id", "name", "email"]  # 50-90% smaller response
)

# With search
results = await upsales.companies.search(
    active=1,
    name="*Tech",
    fields=["id", "name", "phone"]  # Optimized
)

# With list_all (reduces bandwidth significantly for large datasets)
all_contacts = await upsales.contacts.list_all(
    fields=["id", "name"]  # Much faster than all fields
)
```

**Benefits**:
- ✅ Faster queries (confirmed by testing)
- ✅ Reduced bandwidth (50-90% depending on field count)
- ✅ Smaller JSON to parse (faster client-side)

---

### Pattern 10: Sorting

**Use `sort` parameter** to order results by field(s).

**Syntax**:
- `sort="field"` - Ascending order
- `sort="-field"` - Descending order (minus prefix)
- `sort=["field1", "-field2"]` - Multi-field sort

**Examples**:
```python
# Ascending sort
users = await upsales.users.list(sort="name")

# Descending sort (newest first)
users = await upsales.users.list(sort="-regDate")

# Multi-field sort
users = await upsales.users.list(sort=["name", "-id"])

# With search and filters
results = await upsales.companies.search(
    active=1,
    employees=">10",
    sort="-regDate"  # Newest companies with 10+ employees
)
```

**Note**: Not all fields support sorting. Common sortable fields:
- ✅ id, name, regDate, modDate (usually sortable)
- ❌ active, custom, arrays (usually not sortable)

**Test before documenting**: Use `docs/guides/testing-field-capabilities.md`

---

### Pattern 11: Minimal Updates (Conflict Reduction)

**Use to_update_dict_minimal()** to send only changed + required fields, reducing edit conflicts.

**Define required fields** (discovered via testing):
```python
class OrderStage(BaseModel):
    _required_update_fields = {"probability"}  # From test_required_update_fields.py
```

**In edit() method**:
```python
async def edit(self, **kwargs: Unpack[OrderStageUpdateFields]) -> "OrderStage":
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.order_stages.update(
        self.id,
        **self.to_update_dict_minimal(**kwargs)  # Minimal payload!
    )
```

**Benefits**:
- ✅ Reduces edit conflicts (concurrent updates safer)
- ✅ Smaller payloads (50-97% reduction)
- ✅ Won't overwrite unchanged fields

**Discover required fields**:
```bash
python scripts/test_required_update_fields.py {endpoint}
# Tests each field by omission
# Reports which are required vs optional
```

**Example**: orderStages requires `probability` in every update, even if not changing it.

---

### Pattern 12: API Key Handling (User-Specific)

**User types** in Upsales (ghost + active flags):
- **Active users**: ghost=0, active=1 (regular users)
- **API keys**: ghost=1, active=1 (service accounts)
- **Inactive**: ghost=0, active=0
- **Invalid**: ghost=1, active=0 (shouldn't exist)

**get_active() with filtering**:
```python
from upsales.resources.users import UsersResource

# Exclude API keys (default - most common)
users = await upsales.users.get_active()
# Returns: Only regular users (ghost=0, active=1)

# Include API keys
all_active = await upsales.users.get_active(include_api_keys=True)
# Returns: Regular users + API keys (all active=1)
```

**Computed fields for user types**:
```python
@computed_field
@property
def is_api_key(self) -> bool:
    """Check if user is API key."""
    return self.ghost == 1 and self.active == 1

@computed_field
@property
def user_type(self) -> str:
    """Get user type: 'api_key', 'active', 'inactive', or 'invalid'."""
    if self.ghost == 1 and self.active == 1:
        return "api_key"
    elif self.ghost == 0 and self.active == 1:
        return "active"
    # ... etc
```

**Usage**:
```python
for user in users:
    if user.is_api_key:
        print(f"Service account: {user.name}")
    elif user.user_type == "active":
        print(f"Regular user: {user.name}")
```

**Note**: Only applicable to User model (ghost flag specific to users).

---

## 🔧 Custom Fields Infrastructure

**Available**: `upsales.custom_fields` resource (entity-specific operations)

### Entities Supporting Custom Fields
- account, order, orderrow, product, contact
- agreement, activity, todo, appointment, project, projectPlan, ticket, user

### 16 Custom Field Types
String, Text, Integer, Currency, Percent, Boolean, Date, Time, Email, Phone, Link, Select, MultiSelect, User, Discount, Calculation

### Working with Custom Fields

**List custom fields for an entity**:
```python
fields = await upsales.custom_fields.list_for_entity("account")

for field in fields:
    print(f"{field.name} ({field.datatype}): {field.alias}")
```

**Create String field**:
```python
field = await upsales.custom_fields.create_for_entity(
    entity="account",
    name="Customer Code",
    datatype="String",
    alias="CUSTOMER_CODE",
    visible=1,
    editable=1
)
```

**Create Select field with options**:
```python
select = await upsales.custom_fields.create_for_entity(
    entity="account",
    name="Priority",
    datatype="Select",
    alias="PRIORITY",
    default=["Low", "Medium", "High"]  # Options in default field!
)
```

**Create Calculation field** (order/orderrow only):
```python
calc = await upsales.custom_fields.create_for_entity(
    entity="order",
    name="Total with Tax",
    datatype="Calculation",
    alias="TOTAL_TAX",
    formula="{Order.value} * 1.25"  # Formula field!
)
```

**In models** (use CustomFieldsList validator):
```python
from upsales.validators import CustomFieldsList

custom: CustomFieldsList = Field(
    default=[],
    description="Custom fields (see upsales.custom_fields for definitions)"
)
```

**Key insights**:
- ✅ ONE unified CustomField model for all entities
- ✅ Select options: Stored in `default` field (array of strings)
- ✅ Calculation formulas: Stored in `formula` field
- ✅ Required for create: name, datatype, alias
- ✅ Updates: Partial payloads work

**Reference**: See `upsales/models/custom_field.py` for complete structure.

---

## 📋 COMPLETE AUTONOMOUS WORKFLOW

Follow this workflow EXACTLY for autonomous endpoint addition.

**CRITICAL**: This workflow uses **VCR-first** approach:
1. Generate model
2. **Record VCR cassette immediately** (Step 2)
3. All subsequent development uses VCR, NOT live API
4. Fast, offline, no rate limits!

---

## 🚀 STEP-BY-STEP: Adding a New Endpoint

### STEP 1: Generate the Model (5 minutes)

**Command**:
```bash
uv run upsales generate-model {endpoint} --partial
```

**Example**:
```bash
uv run upsales generate-model contacts --partial
# Creates: upsales/models/contacts.py
```

**What it does**:
- Fetches up to 2000 real objects from Upsales API
- Analyzes which fields are required vs optional
- Generates Python 3.13 model with type hints
- Creates TypedDict for updates
- Includes PartialModel if --partial flag used

**Expected output** (with Rich enhancements):
```
━━━━━━━━━━━━ Step 1: Fetching Data ━━━━━━━━━━━━

⠹ Fetching objects from API (up to 2000)...

✅ Success! Fetched 247 objects

━━━━━━━━━━━━ Step 2: Analyzing Fields ━━━━━━━━━━━━

⠋ Analyzing 247 objects for field requirements...

✅ Analysis complete!
   • Fields: 15 total
   • Required: 10
   • Optional: 5

━━━━━━━━━━━━ Complete ━━━━━━━━━━━━

✅ Model generated successfully!
```

**Verify**: Check that file was created at `upsales/models/{endpoint}.py`

---

### STEP 2: Record VCR Cassette (5 minutes) ⭐ **CAPTURE REAL API STRUCTURE**

**CRITICAL**: Record real API responses NOW. All subsequent work uses VCR, not live API!

**Why record now**:
- ✅ Capture real API structure immediately
- ✅ Develop offline (no more API calls!)
- ✅ Avoid rate limits during development
- ✅ Validate model against real data
- ✅ Fast iteration (instant replay)

**Create minimal integration test**:

```bash
# Create test file
cat > tests/integration/test_contacts_integration.py << 'EOF'
"""
Integration tests for Contact model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
This file was created in Step 2 to capture real API structure early.
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.contact import Contact

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_record_api_structure.yaml")
async def test_record_api_structure():
    """
    Record real API structure for offline development.

    This test runs ONCE to capture real API responses, then all
    subsequent development uses the recorded cassettes (fast, offline).
    """
    async with Upsales.from_env() as upsales:
        # Record GET single contact
        contacts = await upsales.contacts.list(limit=1)
        assert len(contacts) > 0, "Should have at least one contact"

        contact = contacts[0]
        assert isinstance(contact, Contact)
        assert contact.id > 0

        print(f"✅ Recorded structure for: {contact.name} (ID: {contact.id})")

        # Record LIST contacts
        more_contacts = await upsales.contacts.list(limit=5)
        assert isinstance(more_contacts, list)

        print(f"✅ Recorded list of {len(more_contacts)} contacts")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_record_search.yaml")
async def test_record_search_structure():
    """Record search/filter API responses."""
    async with Upsales.from_env() as upsales:
        # Record search with filters
        active_contacts = await upsales.contacts.search(active=1)
        assert isinstance(active_contacts, list)

        print(f"✅ Recorded search: {len(active_contacts)} active contacts")
EOF
```

**Run once to record**:

```bash
# Ensure .env has valid credentials
# UPSALES_TOKEN=your_token
# UPSALES_EMAIL=your_email
# UPSALES_PASSWORD=your_password

# Record cassettes (makes real API calls)
uv run pytest tests/integration/test_contacts_integration.py -v

# Expected output:
# test_record_api_structure PASSED
# test_record_search_structure PASSED
# ✅ Cassettes saved in tests/cassettes/integration/test_contacts_integration/
```

**Verify cassettes created**:

```bash
ls tests/cassettes/integration/test_contacts_integration/

# Should see:
# test_record_api_structure.yaml
# test_record_search_structure.yaml
```

**From this point forward**: All development uses VCR, NOT live API!

---

### STEP 3: Analyze Cassette for Real API Structure (5 minutes) ⭐ **VALIDATE MODEL**

**Now that you have real API responses recorded, analyze them!**

**Quick analysis script**:

```python
# ai_temp_files/analyze_cassette.py
import yaml
import json
from pathlib import Path

cassette_path = "tests/cassettes/integration/test_contacts_integration/test_record_api_structure.yaml"

with open(cassette_path) as f:
    cassette = yaml.safe_load(f)

# Get first interaction
interaction = cassette["interactions"][0]
response_str = interaction["response"]["body"]["string"]
response = json.loads(response_str)

# Extract data
data = response["data"]
if isinstance(data, list):
    item = data[0]
else:
    item = data

print("🔍 Real API Fields:")
print("=" * 60)
for field, value in item.items():
    value_type = type(value).__name__
    # Truncate long values
    value_str = str(value)[:50]
    if len(str(value)) > 50:
        value_str += "..."
    print(f"  {field:20} {value_type:10} = {value_str}")

print("\n📊 Field Analysis:")
print(f"  Total fields: {len(item)}")

# Compare against generated model
from upsales.models.contact import Contact

model_fields = set(Contact.model_fields.keys())
api_fields = set(item.keys())

missing = api_fields - model_fields
extra = model_fields - api_fields

if missing:
    print(f"\n❌ Fields in API but NOT in model: {len(missing)}")
    for field in sorted(missing):
        print(f"    - {field}")

if extra:
    print(f"\n⚠️  Fields in model but NOT in API: {len(extra)}")
    for field in sorted(extra):
        print(f"    - {field}")

if not missing and not extra:
    print("\n✅ Perfect match! Model has all API fields.")
```

**Run analysis**:

```bash
python ai_temp_files/analyze_cassette.py

# Expected output:
# 🔍 Real API Fields:
# ============================================================
#   id                   int        = 1
#   name                 str        = John Doe
#   email                str        = john@example.com
#   active               int        = 1
#   regDate              str        = 2025-01-01T00:00:00.000Z
#   ...
#
# 📊 Field Analysis:
#   Total fields: 15
#
# ✅ Perfect match! Model has all API fields.
```

**If mismatches found**:
1. **Missing in model**: Add to generated model
2. **Extra in model**: Remove or mark as optional
3. **Wrong types**: Fix based on real API data
4. **Trust the cassette** - it's the source of truth!

**Reference**: See `ai_temp_files/find_unmapped_fields.py` for automated comparison.

---

### STEP 4: Review Generated Code Against Cassette (5 minutes)

**Open**: `upsales/models/{endpoint}.py`

**Check for TODOs** - The generator marks these for review:
```python
# TODO: Review and customize the generated models:
# 1. Mark read-only fields with Field(frozen=True)
# 2. Update field types if needed
# 3. Add custom_fields property if 'custom' field exists
# 4. Update docstrings with detailed descriptions
# 5. Add any custom methods
```

**Use cassette as source of truth**: If generated model doesn't match cassette, fix the model!

**Action**: Address each TODO in the following steps.

---

### STEP 5: Mark Frozen Fields (2 minutes)

**Find these fields and mark as frozen**:

```python
# ALWAYS frozen (read-only from API):
id: int = Field(frozen=True, strict=True, description="...")
regDate: str = Field(frozen=True, description="...")
modDate: str = Field(frozen=True, description="...")
createdAt: str | None = Field(None, frozen=True, description="...")
updatedAt: str | None = Field(None, frozen=True, description="...")

# Sometimes frozen (depends on endpoint):
created: str | None = Field(None, frozen=True, description="...")
updated: str | None = Field(None, frozen=True, description="...")
```

**Why frozen**: These are set by the API and should never be modified by client.

**Discover frozen fields automatically** (optional but recommended):
```bash
# Run with --compact for minimal output (for AI agents)
python scripts/test_field_editability_bulk.py {endpoint} --compact
```

This outputs JSON with `frozen_recommendations` listing fields that should be `Field(frozen=True)`.

**Reference**: See `upsales/models/user.py:78-79` for example.

---

### STEP 6: Add Reusable Validators (10 minutes)

**CRITICAL**: Replace primitive types with validators from `upsales/validators.py`

**Import validators**:
```python
from upsales.validators import (
    BinaryFlag,       # For 0/1 flags (NOT bool!)
    EmailStr,         # For email addresses
    CustomFieldsList, # For custom field arrays
    NonEmptyStr,      # For required non-empty strings
    PositiveInt,      # For non-negative integers
    Percentage,       # For 1-100 range (probabilities, percentages) ⭐ NEW!
)
```

**Replace types**:

```python
# Generated code might have:
active: int = Field(default=1, description="Active status")
email: str = Field(description="Email")
custom: list[dict] = Field(default=[], description="Custom fields")
name: str = Field(description="Name")

# CHANGE TO:
active: BinaryFlag = Field(default=1, description="Active status (0=no, 1=yes)")
email: EmailStr = Field(description="Email address")
custom: CustomFieldsList = Field(default=[], description="Custom fields")
name: NonEmptyStr = Field(description="Name")
```

**Rules for validator selection**:
- `active`, `administrator`, `isExternal`, any 0/1 flag → `BinaryFlag`
- `email`, `userEmail`, `contactEmail` → `EmailStr`
- `custom`, `customFields` → `CustomFieldsList`
- `name`, `title`, required strings → `NonEmptyStr`
- `id`, `count`, `number` fields → `PositiveInt` (if can't be negative)
- `probability`, `completion`, `progress` (1-100) → `Percentage` ⭐ NEW!

**Reference**: See `upsales/models/user.py:82-110` for complete example.

---

### STEP 7: Add Computed Fields (10 minutes)

**REQUIRED**: Add these standard computed fields:

#### 5a. custom_fields Property (if model has `custom` field)

```python
from pydantic import computed_field
from upsales.models.custom_fields import CustomFields

@computed_field
@property
def custom_fields(self) -> CustomFields:
    """
    Access custom fields with dict-like interface.

    Returns:
        CustomFields helper for easy access by ID or alias.

    Example:
        >>> contact.custom_fields[11]  # By field ID
        'value'
        >>> contact.custom_fields.get(11, "default")
        'value'
    """
    return CustomFields(self.custom)
```

**CRITICAL**: Order MUST be `@computed_field` THEN `@property`!

---

#### 5b. is_active Property (if model has `active` field)

```python
@computed_field
@property
def is_active(self) -> bool:
    """
    Check if resource is active.

    Returns:
        True if active flag is 1, False otherwise.

    Example:
        >>> contact.is_active
        True
    """
    return self.active == 1
```

---

#### 5c. Domain-Specific Computed Fields (optional)

Add computed fields that make sense for the domain:

```python
# For contacts with firstName/lastName
@computed_field
@property
def full_name(self) -> str:
    """
    Get full name from first and last name.

    Returns:
        Combined first and last name.

    Example:
        >>> contact.full_name
        'John Doe'
    """
    if self.firstName and self.lastName:
        return f"{self.firstName} {self.lastName}"
    return self.name

# For opportunities with value/probability
@computed_field
@property
def expected_value(self) -> float:
    """
    Calculate expected value based on probability.

    Returns:
        Value multiplied by probability percentage.

    Example:
        >>> opportunity.expected_value
        45000.0  # $100k * 45% probability
    """
    return (self.value * self.probability) / 100 if self.value and self.probability else 0.0
```

**Reference**: See `upsales/models/product.py:196-211` for profit_margin example.

---

### STEP 8: Add Field Serializer (5 minutes)

**If model has `custom` field, MUST add serializer**:

```python
from pydantic import field_serializer

@field_serializer('custom', when_used='json')
def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Serialize custom fields for API requests.

    Removes fields without values to keep API payloads clean.

    Args:
        custom: List of custom field dicts from model.

    Returns:
        Cleaned list with only fields that have values.

    Example:
        >>> # Removes items without 'value' key
        >>> [{"fieldId": 11, "value": "data"}]  # Kept
        >>> [{"fieldId": 12}]  # Removed (no value)
    """
    return [
        {"fieldId": item["fieldId"], "value": item.get("value")}
        for item in custom
        if "value" in item and item.get("value") is not None
    ]
```

**Reference**: See `upsales/models/user.py:185-203` for exact pattern.

---

### STEP 9: Verify TypedDict Completeness (5 minutes)

**CRITICAL CHECK**: TypedDict MUST include ALL updatable fields.

**How to verify**:
1. Count non-frozen fields in model
2. Count fields in TypedDict
3. Numbers MUST match!

```python
# Example verification:
# Model has: id (frozen), name, email, active, phone, custom
# Frozen: 1 (id)
# Updatable: 5 (name, email, active, phone, custom)
# TypedDict MUST have: 5 fields

class ContactUpdateFields(TypedDict, total=False):
    """Must have ALL 5 updatable fields."""
    name: str        # ✅
    email: str       # ✅
    active: int      # ✅
    phone: str       # ✅
    custom: list[Any]  # ✅
    # Total: 5 ✅ Matches!
```

**If generator missed fields, ADD them manually!**

**Verify with script** (optional but recommended):
```bash
python scripts/test_field_editability_bulk.py {endpoint} --compact
```
The `editable_fields` list in the output shows exactly which fields should be in your TypedDict.

**Reference**: See `upsales/models/company.py:32-146` for complete TypedDict with 84 fields.

---

### STEP 10: Implement edit() Method (5 minutes)

**Copy this pattern EXACTLY**:

```python
from typing import Unpack

async def edit(self, **kwargs: Unpack[ContactUpdateFields]) -> "Contact":
    """
    Edit this contact via the API.

    Args:
        **kwargs: Fields to update (from ContactUpdateFields TypedDict).

    Returns:
        Updated Contact object with fresh data from API.

    Raises:
        RuntimeError: If no client reference available.

    Example:
        >>> contact = await upsales.contacts.get(1)
        >>> updated = await contact.edit(
        ...     name="New Name",
        ...     email="new@example.com",
        ...     active=1
        ... )
        >>> print(updated.name)  # Fresh from API
        'New Name'
    """
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.contacts.update(
        self.id,
        **self.to_api_dict(**kwargs)
    )
```

**IMPORTANT**:
- Use `Unpack[ContactUpdateFields]` for type safety
- Use `self.to_api_dict(**kwargs)` NOT `self.to_update_dict(**kwargs)`
- Check `if not self._client` before using it

**Reference**: See `upsales/models/user.py:204-228` for exact pattern.

---

### STEP 11: Enhance PartialModel (5 minutes)

**If generator created PartialModel, enhance it**:

```python
from upsales.validators import NonEmptyStr, EmailStr

class PartialContact(PartialModel):
    """
    Partial Contact for nested responses.

    Contains minimal fields for when Contact appears nested in other
    API responses (e.g., as opportunity owner, company contact, etc.).

    Use fetch_full() to get complete Contact object with all fields.

    Example:
        >>> opportunity = await upsales.opportunities.get(1)
        >>> owner = opportunity.owner  # PartialContact
        >>> full = await owner.fetch_full()  # Now Contact
    """

    # Minimum fields (usually id + name + email)
    id: int = Field(frozen=True, strict=True, description="Unique contact ID")
    name: NonEmptyStr = Field(description="Contact name")
    email: EmailStr = Field(description="Contact email")

    async def fetch_full(self) -> Contact:
        """
        Fetch complete contact data from API.

        Returns:
            Full Contact object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.owner  # PartialContact
            >>> full = await partial.fetch_full()  # Contact
            >>> full.phone  # Now available
            '+1-555-0123'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.get(self.id)

    async def edit(self, **kwargs: Any) -> Contact:
        """
        Edit contact via partial reference.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Contact object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.owner  # PartialContact
            >>> updated = await partial.edit(name="New Name")  # Returns Contact
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.update(self.id, **kwargs)
```

**Reference**: See `upsales/models/user.py:236-296` for PartialUser example.

---

### STEP 12: Add Model Docstring Example (3 minutes)

**Update the main model docstring with usage example**:

```python
class Contact(BaseModel):
    """
    Contact model from /api/v2/contacts.

    Represents a contact in the Upsales system with full data.
    Enhanced with Pydantic v2 validators, computed fields, and
    optimized serialization.

    Example:
        >>> # Get contact
        >>> contact = await upsales.contacts.get(1)
        >>> contact.name
        'John Doe'
        >>>
        >>> # Use computed fields
        >>> contact.is_active
        True
        >>> contact.full_name
        'John Doe'
        >>>
        >>> # Access custom fields
        >>> contact.custom_fields[11]
        'value'
        >>>
        >>> # Edit contact (IDE autocomplete!)
        >>> await contact.edit(
        ...     name="Jane Doe",
        ...     email="jane@example.com",
        ...     active=1
        ... )
    """
```

**Reference**: See `upsales/models/user.py:57-76` for complete example.

---

### STEP 13: Create Resource Manager (2 minutes)

**Command**:
```bash
uv run upsales init-resource contacts
```

**What it creates**:
- `upsales/resources/contacts.py` - Resource manager boilerplate
- Updates `upsales/resources/__init__.py` - Adds export

**Expected output**:
```
━━━━━━━━━━━━ Initializing Resource: contacts ━━━━━━━━━━━━

⠋ Creating contacts resource manager...

✅ Created upsales/resources/contacts.py
✅ Updated upsales/resources/__init__.py

Next steps: [shows next steps]
```

**Verify**: Check files were created.

---

### STEP 14: Review Resource and Add Custom Methods (10 minutes)

**Open**: `upsales/resources/contacts.py`

#### 12a. Verify Basic Structure

**MUST have this structure**:
```python
from upsales.http import HTTPClient
from upsales.models.contact import Contact, PartialContact
from upsales.resources.base import BaseResource


class ContactsResource(BaseResource[Contact, PartialContact]):
    """
    Resource manager for Contact endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new contact
    - get(id) - Get single contact
    - list(limit, offset, **params) - List contacts with pagination
    - list_all(**params) - Auto-paginated list of all contacts
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update contact
    - delete(id) - Delete contact
    - bulk_update(ids, data) - Parallel updates
    - bulk_delete(ids) - Parallel deletes

    Example:
        >>> contacts = ContactsResource(http_client)
        >>> contact = await contacts.get(1)
        >>> all_active = await contacts.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize contacts resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/contacts",  # ⚠️ VERIFY this matches actual API endpoint!
            model_class=Contact,
            partial_class=PartialContact,
        )
```

**CRITICAL**: Verify the `endpoint="/contacts"` matches actual Upsales API endpoint!
- Check `ai_temp_files/postman_api_analysis.md` for endpoint list
- Upsales sometimes uses different naming (e.g., `/accounts` for companies)

---

#### 12b. Add Custom Methods (Optional but Recommended)

**Common useful methods**:

```python
    async def get_by_email(self, email: str) -> Contact | None:
        """
        Get contact by email address.

        Args:
            email: Email address to search for.

        Returns:
            Contact if found, None otherwise.

        Example:
            >>> contact = await upsales.contacts.get_by_email("john@example.com")
            >>> if contact:
            ...     print(contact.name)
        """
        all_contacts = await self.list_all()
        for contact in all_contacts:
            if contact.email.lower() == email.lower():
                return contact
        return None

    async def get_by_company(self, company_id: int) -> list[Contact]:
        """
        Get all contacts for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of contacts belonging to the company.

        Example:
            >>> contacts = await upsales.contacts.get_by_company(123)
            >>> len(contacts)
            5
        """
        # Note: Assumes API supports filtering by company/client
        # Adjust field name based on actual API (might be 'client', 'account', etc.)
        return await self.list_all(client=company_id)

    async def get_active(self) -> list[Contact]:
        """
        Get all active contacts.

        Returns:
            List of contacts with active=1.

        Example:
            >>> active = await upsales.contacts.get_active()
            >>> all(c.is_active for c in active)
            True
        """
        return await self.list_all(active=1)
```

**Pattern**: Custom methods should use `list_all()` or other inherited methods, NOT reimplement logic.

**Reference**:
- See `upsales/resources/users.py:66-115` for 3 custom method examples
- See `upsales/resources/products.py:66-119` for bulk operations

---

### STEP 12c: Understanding search() Method (IMPORTANT!)

**ALL resources inherit search() from BaseResource** - you don't need to implement it!

**Location**: `upsales/resources/base.py:258-321`

**What it does**: Wrapper around `list_all()` with powerful filter operators

#### Basic Search (Equality)
```python
# Simple equality filter
active_contacts = await upsales.contacts.search(active=1)
# Same as: await upsales.contacts.list_all(active=1)
```

#### Advanced Search with Comparison Operators

**Natural operator syntax** (recommended, more intuitive):
- `>=value` - Greater than or equals
- `>value` - Greater than
- `<=value` - Less than or equals
- `<value` - Less than
- `=value` - Equals (explicit)
- `!=value` - Not equals
- `=1,2,3` - In list (multiple values)
- `*value` - Substring search (contains) ⭐ **NEW!**

**API operator syntax** (also supported for backward compatibility):
- `gte:value` - Greater than or equals
- `gt:value` - Greater than
- `lte:value` - Less than or equals
- `lt:value` - Less than
- `eq:value` - Equals
- `ne:value` - Not equals
- `src:value` - Substring search ⭐ **NEW!**

**Both syntaxes work!** Use natural operators for cleaner code:

```python
# Date range search (natural operators)
recent_contacts = await upsales.contacts.search(
    active=1,
    regDate=">=2024-01-01"  # Natural syntax ✅
)

# Numeric range (natural operators)
high_value_opportunities = await upsales.opportunities.search(
    value=">50000",      # > $50k
    value="<100000",     # AND < $100k
    active=1
)

# Multiple values with IN operator
specific_contacts = await upsales.contacts.search(
    id="=1,2,3,4,5"  # Natural IN syntax ✅
)

# Custom field filtering (natural)
tech_companies = await upsales.companies.search(
    active=1,
    custom="=11:Technology"  # Natural syntax ✅
)

# Nested field search (use dict unpacking)
contacts_of_company = await upsales.contacts.search(
    **{"client.id": 123}  # company.id = 123
)

# Backward compatibility - old syntax still works!
legacy_search = await upsales.users.search(
    regDate="gte:2024-01-01"  # API syntax still works ✅
)

# Substring search (wildcard) ⭐ NEW!
contacts = await upsales.contacts.search(
    phone="*555",        # Contains "555"
    name="*John"         # Name contains "John"
)

# Field selection (performance optimization) ⭐ NEW!
users = await upsales.users.search(
    active=1,
    fields=["id", "name", "email"]  # Only return these (faster!)
)

# Sorting ⭐ NEW!
users = await upsales.users.search(
    active=1,
    sort="-regDate"  # Newest first
)

# Everything combined! ⭐
results = await upsales.companies.search(
    name="*Technology",              # Substring
    employees=">10",                 # Natural operator
    active=1,                        # Filter
    fields=["id", "name", "phone"],  # Optimize (faster!)
    sort="-regDate"                  # Newest first
)
```

**Important Notes**:
- search() is just a wrapper around list_all() - it passes filters through
- Not all fields support all operators (binary flags usually only eq/ne)
- Date fields support full range (gt, gte, lt, lte)
- Numeric fields support full range
- String fields support substring search (*) and equality
- Field selection reduces bandwidth 50-90% (confirmed faster!)
- Sorting: Use `-field` for descending, `field` for ascending

**You don't need to add search() - it's already inherited!**

**But you CAN add convenience methods**:
```python
# Instead of exposing raw search, provide domain methods
async def get_by_date_range(self, start: str, end: str) -> list[Contact]:
    """Get contacts registered in date range."""
    return await self.search(
        regDate=f">={start}",  # Natural operator
        regDate=f"<={end}",
        sort="-regDate"        # Newest first
    )

async def get_high_priority(self) -> list[Contact]:
    """Get high priority contacts."""
    return await self.search(
        priority=">7",
        fields=["id", "name", "priority"],  # Optimize
        sort="-priority"
    )

async def search_by_name(self, name_fragment: str) -> list[Contact]:
    """Search contacts by partial name match."""
    return await self.search(
        name=f"*{name_fragment}",  # Substring search
        fields=["id", "name", "email", "phone"],
        sort="name"
    )
```

---

### STEP 12d: Using Field Selection and Sorting (IMPORTANT!)

**Field selection** reduces bandwidth and improves performance (confirmed by testing).

**When to use**:
- ✅ Mobile apps (reduce data transfer)
- ✅ Dashboards (only need specific fields)
- ✅ Large datasets (faster queries)
- ✅ Frequent polling (optimize repeated queries)

**Examples**:
```python
# In your custom methods, use fields parameter
async def get_for_dashboard(self) -> list[Contact]:
    """Get contacts for dashboard display (optimized)."""
    return await self.list_all(
        active=1,
        fields=["id", "name", "email", "phone"],  # Only what dashboard shows
        sort="-regDate"  # Newest first
    )

async def get_name_list(self) -> list[Contact]:
    """Get minimal contact list (very fast)."""
    return await self.list_all(
        fields=["id", "name"]  # Ultra-fast, minimal payload
    )
```

**Sorting syntax**:
- `sort="name"` - Ascending
- `sort="-regDate"` - Descending (minus prefix)
- `sort=["name", "-id"]` - Multi-field (name asc, id desc)

**Note**: Not all fields support sorting. Test with your endpoint using `docs/guides/testing-field-capabilities.md`.

---

### STEP 15: Register in Client (2 minutes)

**Edit**: `upsales/client.py`

#### 13a. Add Import (top of file)

```python
# Add with other resource imports
from upsales.resources.contacts import ContactsResource
```

#### 13b. Add to __init__ (in Upsales class)

```python
def __init__(
    self,
    token: str,
    base_url: str = "https://power.upsales.com/api/v2",
    max_concurrent: int = 50,
    auth_manager: AuthenticationManager | None = None,
) -> None:
    """Initialize Upsales client."""
    # ... existing code ...

    # Initialize HTTP client
    self.http = HTTPClient(
        token=token,
        base_url=base_url,
        max_concurrent=max_concurrent,
        auth_manager=auth_manager,
        upsales_client=self,
    )

    # Register resource managers
    self.users = UsersResource(self.http)
    self.companies = CompaniesResource(self.http)
    self.products = ProductsResource(self.http)
    self.contacts = ContactsResource(self.http)  # ✅ ADD THIS LINE
```

#### 13c. Update Client Docstring

```python
class Upsales:
    """
    Async client for Upsales CRM API.

    Provides access to all Upsales API resources with Pydantic v2 models,
    type safety, and async/await support.

    Attributes:
        users: User resource manager.
        companies: Company resource manager.
        products: Product resource manager.
        contacts: Contact resource manager.  # ✅ ADD THIS

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Users
        ...     user = await upsales.users.get(1)
        ...
        ...     # Contacts (NEW!)
        ...     contact = await upsales.contacts.get(1)  # ✅ ADD EXAMPLE
        ...     contacts = await upsales.contacts.get_active()
    """
```

**Reference**: See `upsales/client.py:30-80` for complete pattern.

---

### STEP 16: Update Model Exports (2 minutes)

**Edit**: `upsales/models/__init__.py`

```python
# Add imports
from upsales.models.contact import (
    Contact,
    ContactUpdateFields,
    PartialContact,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "Contact",
    "ContactUpdateFields",
    "PartialContact",
]
```

**Verify**: All three items exported (Model, UpdateFields, PartialModel)

**Reference**: See `upsales/models/__init__.py:23-36` for current exports.

---

### STEP 17: Copy and Customize Test Template (15 minutes)

#### 15a. Copy Template

```bash
cp tests/templates/resource_template.py tests/unit/test_contacts_resource.py
```

---

#### 15b. Global Find/Replace

**In your editor, find and replace** (case-sensitive):

| Find | Replace |
|------|---------|
| `{ResourceName}` | `ContactsResource` |
| `{ModelName}` | `Contact` |
| `{PartialModelName}` | `PartialContact` |
| `{endpoint}` | `/contacts` |
| `{resource_name}` | `contacts` |
| `{model_name}` | `contact` |
| `{singular}` | `contact` |

**After replace, verify**:
- Class names: `TestContactsResourceCRUD`, `TestContactsResourceCustomMethods`
- URLs: `https://power.upsales.com/api/v2/contacts`
- Variable names: `contact`, `contacts`

---

#### 15c. Update Imports

```python
import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.http import HTTPClient
from upsales.models.contact import Contact  # ✅ Update this
from upsales.resources.contacts import ContactsResource  # ✅ Update this
```

---

#### 15d. Create Sample Data Fixture

**CRITICAL**: Sample data MUST match your model's required fields!

```python
@pytest.fixture
def sample_contact(self):
    """Sample contact data for testing."""
    return {
        # Required fields (check your Contact model!)
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "active": 1,
        "regDate": "2025-01-01T00:00:00Z",
        "custom": [],

        # Add any other REQUIRED fields from your model
        # Check: Fields without default values are required
        # "phone": "+1-555-0123",  # Add if required
        # "company": {"id": 1, "name": "ACME"},  # Add if required
    }
```

**How to know what's required**:
1. Open `upsales/models/contact.py`
2. Find fields WITHOUT `= Field(default=...)`
3. Those are required - add them to sample_contact!

---

#### 15e. Uncomment Test Bodies

**The template has commented-out code. Uncomment and verify**:

```python
@pytest.mark.asyncio
async def test_create(self, httpx_mock: HTTPXMock, sample_contact):
    """Test creating a contact."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/contacts",  # ✅ Verify URL
        method="POST",
        json={"error": None, "data": sample_contact},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = ContactsResource(http)
        result = await resource.create(
            name="John Doe",
            email="john@example.com",
            active=1,
        )

        assert isinstance(result, Contact)
        assert result.id == 1
        assert result.name == "John Doe"
```

**Do this for ALL test methods in the template!**

---

#### 15f. Verify search() Test is Uncommented

**The template includes a search() test** - make sure to uncomment it:

```python
@pytest.mark.asyncio
async def test_search(self, httpx_mock: HTTPXMock, sample_contact):
    """Test search() with filters."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/contacts?active=1&limit=100&offset=0",
        json={"error": None, "data": [sample_contact]},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = ContactsResource(http)
        results = await resource.search(active=1)

        assert len(results) == 1
        assert results[0].active == 1
```

**Testing advanced search with operators**:
```python
@pytest.mark.asyncio
async def test_search_with_operators(self, httpx_mock: HTTPXMock, sample_contact):
    """Test search() with comparison operators."""
    # API receives the operator string as-is
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/contacts?regDate=gte%3A2024-01-01&limit=100&offset=0",
        json={"error": None, "data": [sample_contact]},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = ContactsResource(http)
        results = await resource.search(regDate="gte:2024-01-01")

        assert len(results) == 1

@pytest.mark.asyncio
async def test_search_multiple_filters(self, httpx_mock: HTTPXMock, sample_contact):
    """Test search() with multiple filter criteria."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/contacts?active=1&verified=1&limit=100&offset=0",
        json={"error": None, "data": [sample_contact]},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = ContactsResource(http)
        results = await resource.search(active=1, verified=1)

        assert len(results) == 1
```

**Note**: search() is inherited from BaseResource - you're testing it works with your endpoint!

**Reference for search() testing**:
- `tests/unit/test_base_resource.py:343-404` - Complete search test examples
  - test_search_simple_filter (line 360)
  - test_search_multiple_filters (line 375)
  - test_search_no_results (line 389)
  - test_search_substring_operator (line 568) - Wildcard test
  - test_search_with_field_selection (line 652) - Performance test
  - test_search_with_sort (line 762) - Sorting test

**These BaseResource tests already validate search() works** - you're adding endpoint-specific tests to ensure it works with your model's fields.

**Also test new features**:
```python
@pytest.mark.asyncio
async def test_search_with_all_features(self, httpx_mock: HTTPXMock, sample_contact):
    """Test search with substring, fields, and sorting."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/contacts?name=src%3AJohn&limit=100&offset=0&f%5B%5D=id&f%5B%5D=name&sort=-regDate",
        json={"error": None, "data": [sample_contact]},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = ContactsResource(http)
        results = await resource.search(
            name="*John",               # Substring
            fields=["id", "name"],      # Field selection
            sort="-regDate"             # Sorting
        )

        assert len(results) == 1
```

---

#### 15g. Add Custom Method Tests

**If you added custom methods in Step 12, add tests**:

```python
class TestContactsResourceCustomMethods:
    """Test custom methods specific to ContactsResource."""

    @pytest.mark.asyncio
    async def test_get_by_email(self, httpx_mock: HTTPXMock):
        """Test get_by_email() finds contact."""
        sample = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": 1,
            "regDate": "2025-01-01",
            "custom": [],
        }

        # get_by_email calls list_all() internally
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?limit=100&offset=0",
            json={"error": None, "data": [sample]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ContactsResource(http)
            result = await resource.get_by_email("john@example.com")

            assert isinstance(result, Contact)
            assert result.email == "john@example.com"
```

**Pattern**:
- Mock the underlying BaseResource method the custom method uses
- get_by_email uses list_all() → mock list() with pagination
- get_active uses list_all() → mock list() with active=1 filter

**Reference**: See `tests/unit/test_users_resource.py` for 4 custom method test examples.

---

### STEP 18: Run Unit Tests (5 minutes)

```bash
# Run your new tests
uv run pytest tests/unit/test_contacts_resource.py -v

# Check coverage (MUST be 100% for resource)
uv run pytest tests/unit/test_contacts_resource.py -v \
    --cov=upsales/resources/contacts.py \
    --cov-report=term-missing
```

**Expected**:
```
tests/unit/test_contacts_resource.py::TestContactsResourceCRUD::test_create PASSED
tests/unit/test_contacts_resource.py::TestContactsResourceCRUD::test_get PASSED
...
tests/unit/test_contacts_resource.py::TestContactsResourceCustomMethods::test_get_by_email PASSED

======================== 22 passed in 2.35s ========================

upsales/resources/contacts.py    100%    ✅ REQUIRED!
```

**If not 100% coverage**: Add missing tests for uncovered lines.

**If tests fail**:
1. Check error message
2. Fix sample_contact data (missing required fields?)
3. Fix URL (wrong endpoint?)
4. Fix assertions (wrong field names?)

---

### STEP 19: Expand Integration Tests (10 minutes)

**Create**: `tests/integration/test_contacts_integration.py`

**Copy this EXACT pattern**:

```python
"""
Integration tests for Contact model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that Contact model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_contacts_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.contact import Contact
from upsales.models.custom_fields import CustomFields

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_get_contact_real_response.yaml")
async def test_get_contact_real_response():
    """
    Test getting contact with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our Contact
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get contacts to find a valid ID
        contacts = await upsales.contacts.list(limit=1)

        assert len(contacts) > 0, "Should have at least one contact"
        contact = contacts[0]

        # Validate Contact model with Pydantic v2 features
        assert isinstance(contact, Contact)
        assert isinstance(contact.id, int)
        assert isinstance(contact.name, str)
        assert len(contact.name) > 0  # NonEmptyStr validator

        # If email field exists, validate EmailStr normalization
        if hasattr(contact, 'email') and contact.email:
            assert contact.email == contact.email.lower()  # EmailStr normalizes

        # Validate BinaryFlag fields (should be 0 or 1)
        if hasattr(contact, 'active'):
            assert contact.active in (0, 1)

        # Validate computed fields work
        if hasattr(contact, 'is_active'):
            assert isinstance(contact.is_active, bool)

        if hasattr(contact, 'custom_fields'):
            assert isinstance(contact.custom_fields, CustomFields)

        print(f"[OK] Contact parsed successfully: {contact.name} (ID: {contact.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_list_contacts_real_response.yaml")
async def test_list_contacts_real_response():
    """Test listing contacts with real API response structure."""
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=5)

        assert isinstance(contacts, list)
        assert len(contacts) <= 5

        for contact in contacts:
            assert isinstance(contact, Contact)
            assert contact.id > 0
            assert len(contact.name) > 0

        print(f"[OK] Listed {len(contacts)} contacts successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_search_contacts_real_data.yaml")
async def test_search_contacts_real_data():
    """
    Test search() method with real API filtering.

    Validates that inherited search() method works correctly with
    the contacts endpoint and real filter parameters.
    """
    async with Upsales.from_env() as upsales:
        # Test simple search
        active_contacts = await upsales.contacts.search(active=1)

        assert isinstance(active_contacts, list)
        # All should be active
        for contact in active_contacts:
            assert contact.active == 1

        print(f"[OK] Search found {len(active_contacts)} active contacts")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_advanced_query_features.yaml")
async def test_advanced_query_features():
    """
    Test advanced query features: substring, field selection, sorting.

    Validates that substring search (*), field selection, and sorting
    all work with the contacts endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Test with all features combined
        results = await upsales.contacts.search(
            active=1,
            fields=["id", "name", "email"],  # Field selection
            sort="-regDate"                  # Sorting (newest first)
        )

        assert isinstance(results, list)
        # Verify we got results
        if len(results) > 0:
            # Should only have requested fields (though model allows all)
            print(f"[OK] Advanced query returned {len(results)} contacts")

        print("[OK] Advanced features (field selection + sorting) work")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_contact_serialization.yaml")
async def test_contact_serialization_real_data():
    """
    Test to_api_dict() serialization with real contact data.

    Validates that serialization excludes frozen and computed fields.
    """
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=1)
        contact = contacts[0]

        # Get API dict
        api_dict = contact.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict
        if hasattr(contact, 'regDate'):
            assert "regDate" not in api_dict

        # Validate computed fields excluded
        assert "is_active" not in api_dict
        assert "custom_fields" not in api_dict

        # Validate updatable fields included
        assert "name" in api_dict
        if hasattr(contact, 'active'):
            assert "active" in api_dict

        # Validate it's JSON serializable
        import json
        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {contact.name}")
```

**CRITICAL NOTES**:
- Use `my_vcr.use_cassette()` decorator (NOT `@pytest.mark.vcr()`)
- Cassette path: `"test_contacts_integration/test_name.yaml"`
- Use `hasattr()` checks for optional fields
- VCR configuration MUST match this exact pattern

**Reference**: Copy from `tests/integration/test_users_integration.py` - DO NOT deviate from this pattern!

---

### STEP 20: Add More Integration Tests (5 minutes)

**CRITICAL**: Ensure `.env` file has valid credentials!

**Required .env vars**:
```bash
UPSALES_TOKEN=your_token_here
UPSALES_EMAIL=your_email@example.com  # For token refresh if needed
UPSALES_PASSWORD=your_password  # For token refresh if needed
```

**Run integration tests**:
```bash
# First run: Records cassettes from real API
uv run pytest tests/integration/test_contacts_integration.py -v
```

**What happens**:
1. Makes real API requests
2. Records responses to YAML cassettes
3. Tests should PASS (if model matches API)
4. Cassettes saved in `tests/cassettes/integration/test_contacts_integration/`

**If tests FAIL**:
- **ValidationError**: Model doesn't match real API!
  - Check error message for which field failed
  - Update model field type to match real API data
  - Trust the real API data, not assumptions!

- **TypeError with computed fields**: Wrong decorator order
  - Fix: `@computed_field` THEN `@property`

- **JSON serialization error**: Computed fields in to_api_dict()
  - Should not happen (BaseModel excludes them)
  - If happens, check BaseModel.to_api_dict() implementation

**Examples of real bugs found by VCR**:
- `cfar` field typed as `BinaryFlag` but API returned `45084548` (int)
- `assigned` field typed as `PartialUser` but API returned `[]` (empty list)
- Decorator order wrong on 17 computed fields

**Reference**: See `ai_temp_files/FOUNDATION_COMPLETE.md` for bug examples.

---

### STEP 21: Verify All Tests Use VCR Created (1 minute)

```bash
ls tests/cassettes/integration/test_contacts_integration/

# Should see:
# test_get_contact_real_response.yaml
# test_list_contacts_real_response.yaml
# test_contact_serialization.yaml
```

**Verify cassettes work offline**:
```bash
# Run again (should use cassettes, no API calls)
uv run pytest tests/integration/test_contacts_integration.py -v

# Should be MUCH faster (< 2 seconds)
# Should still pass
```

---

### STEP 22: Run Full Test Suite (2 minutes)

```bash
# Run ALL tests (unit + integration)
uv run pytest tests/ -q

# Should see increased count
# Example: 231 passed, 7 skipped (was 212 passed)
```

**Expected**: All tests pass, including new ones.

**If any tests fail**: Fix before proceeding!

---

### STEP 23: Quality Checks (5 minutes)

**Run ALL quality gates** (MUST all pass):

#### 21a. Docstring Coverage (MUST be 100%)

```bash
uv run interrogate upsales

# MUST show: RESULT: PASSED (100.0%)
# If not 100%: Add missing docstrings to Contact model and resource
```

**Common missing docstrings**:
- Model class docstring
- Computed field docstrings
- edit() method docstring
- Resource class docstring
- Custom method docstrings

---

#### 21b. Type Checking (MUST pass strict mode)

```bash
uv run mypy upsales

# MUST show: Success: no issues found in XX source files
```

**Common type errors**:
- Missing type parameters: `list` → `list[Any]`, `dict` → `dict[str, Any]`
- Computed field decorator warnings (suppressed in pyproject.toml)
- Edit method signature (suppressed in pyproject.toml)

---

#### 21c. Linting (MUST pass)

```bash
# Check for issues
uv run ruff check .

# Auto-fix formatting
uv run ruff format .
```

**Common issues**:
- Unused imports (remove them)
- Import order (ruff --fix handles this)
- Line too long (ruff format handles this)

---

#### 21d. Use Validate Command

```bash
uv run upsales validate

# Should show:
# ━━━━━━━━━━━━ Project Validation ━━━━━━━━━━━━
# [Table with all checks]
# ✅ All checks passed - Project structure: EXCELLENT
```

---

### STEP 22: Final Verification (3 minutes)

**Run complete verification**:

```bash
# 1. All tests pass
uv run pytest tests/ -q
# Expect: 231 passed, 7 skipped (or higher)

# 2. Full coverage check
uv run pytest tests/ --cov=upsales --cov-report=term | grep contacts
# Expect: upsales/resources/contacts.py    100%

# 3. All quality gates
uv run ruff check . && uv run mypy upsales && uv run interrogate upsales
# Expect: All pass with no errors
```

**ALL must pass before committing!**

---

### STEP 23: Commit (2 minutes)

```bash
# Add all files
git add upsales/models/contact.py
git add upsales/resources/contacts.py
git add upsales/resources/__init__.py
git add upsales/models/__init__.py
git add upsales/client.py
git add tests/unit/test_contacts_resource.py
git add tests/integration/test_contacts_integration.py
git add tests/cassettes/integration/test_contacts_integration/

# Commit with descriptive message
git commit -m "Add contacts endpoint with full test coverage

- Generated Contact and PartialContact models from 247 API samples
- Added Pydantic v2 validators (BinaryFlag, EmailStr, CustomFieldsList)
- Implemented 4 computed fields (custom_fields, is_active, full_name, display_name)
- Created ContactsResource with 3 custom methods
- Added 22 unit tests achieving 100% resource coverage
- Added 3 integration tests with VCR cassettes
- Validated with real API data
- All quality checks pass (ruff, mypy, interrogate)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## ✅ AUTONOMOUS AGENT CHECKLIST

**Use this checklist to verify completion**:

### Model Enhancement
- [ ] Frozen fields marked (id, regDate, modDate)
- [ ] Reusable validators added (BinaryFlag, EmailStr, etc.)
- [ ] Computed fields added with CORRECT decorator order (`@computed_field` `@property`)
- [ ] Field serializer added (for custom fields)
- [ ] TypedDict is COMPLETE (all updatable fields)
- [ ] edit() method implemented
- [ ] PartialModel enhanced (if generated)
- [ ] ALL fields have description=
- [ ] Model docstring has example

### Resource Manager
- [ ] Endpoint path verified (check postman_api_analysis.md)
- [ ] Custom methods added (get_active, get_by_email, etc.)
- [ ] ALL methods have docstrings with examples
- [ ] Resource registered in client
- [ ] Client docstring updated
- [ ] Exports updated (models/__init__.py)

### Testing
- [ ] Test template copied
- [ ] Placeholders replaced
- [ ] Sample data matches model
- [ ] ALL test methods uncommented and working
- [ ] Custom method tests added
- [ ] Unit tests: 100% resource coverage
- [ ] Integration tests created
- [ ] VCR cassettes recorded (3+ cassettes)
- [ ] Cassettes verified (tests run offline)

### Quality
- [ ] Interrogate: 100% docstrings
- [ ] Mypy: No errors
- [ ] Ruff: All checks pass
- [ ] All tests pass (unit + integration)
- [ ] Coverage: 100% for new resource

### Commit
- [ ] All files added to git
- [ ] Descriptive commit message
- [ ] Includes file list and metrics

**Total**: 25 items - ALL must be checked before declaring success!

---

## 🔍 VALIDATION CRITERIA FOR SUB-AGENTS

**An endpoint is considered "complete" when**:

### 1. Code Quality ✅
```bash
$ uv run ruff check .
All checks passed! ✅

$ uv run mypy upsales
Success: no issues found ✅

$ uv run interrogate upsales
RESULT: PASSED (100.0%) ✅
```

### 2. Test Coverage ✅
```bash
$ uv run pytest tests/unit/test_contacts_resource.py --cov=upsales/resources/contacts.py
upsales/resources/contacts.py    100%    ✅ REQUIRED

$ uv run pytest tests/integration/test_contacts_integration.py -v
3 passed ✅

$ ls tests/cassettes/integration/test_contacts_integration/
test_get_contact_real_response.yaml ✅
test_list_contacts_real_response.yaml ✅
test_contact_serialization.yaml ✅
```

### 3. Test Pass Rate ✅
```bash
$ uv run pytest tests/ -q
231 passed, 7 skipped ✅  # Increased from 212

# Pass rate should remain 97%+ ✅
```

### 4. Model Features ✅

**Every model MUST have**:
- ✅ Reusable validators (BinaryFlag, EmailStr, etc.) - Check at least 1
- ✅ Computed fields - At least custom_fields and is_active
- ✅ Field serializer - If has custom field
- ✅ Complete TypedDict - ALL updatable fields
- ✅ edit() method - With Unpack[UpdateFields]
- ✅ 100% field descriptions - Every Field() has description=

**Verification script**:
```python
# Check model has required features
import ast
with open('upsales/models/contact.py') as f:
    content = f.read()
    assert '@computed_field' in content  # Has computed fields
    assert '@field_serializer' in content  # Has serializer (if custom field)
    assert 'Unpack[' in content  # Has type-safe edit
    assert 'UpdateFields(TypedDict' in content  # Has TypedDict
    assert content.count('description="') >= 10  # Field descriptions
```

### 5. Integration with Real API ✅

**VCR cassettes MUST**:
- Exist (3+ cassette files)
- Contain real API responses
- Not contain "error" in response
- Show model parses without ValidationError

**If cassette recording fails with ValidationError**:
- This means model doesn't match real API!
- Update model based on error message
- Re-record cassette
- Repeat until cassette records successfully

---

## 🎓 KNOWLEDGE BASE: Critical Information

### Upsales API Conventions

**Endpoint naming** (check `postman_api_analysis.md`):
- Users: `/users` ✅
- Companies: `/accounts` ⚠️ (NOT /companies!)
- Products: `/products` ✅
- Contacts: `/contacts` ✅
- Opportunities: `/opportunities` ✅
- **Always verify in API docs!**

**Response format** (ALL endpoints):
```json
{
  "error": null,
  "metadata": {
    "total": 500,
    "limit": 100,
    "offset": 0
  },
  "data": [...] or {...}
}
```

**Common fields** (appear in most models):
- `id`: int (frozen, strict)
- `regDate`: str (frozen) - Registration/creation date
- `modDate`: str (frozen) - Last modification date
- `active`: BinaryFlag (0 or 1, NOT bool)
- `custom`: CustomFieldsList (always optional, default=[])

**Field naming**:
- camelCase in API (regDate, modDate, isExternal)
- Keep camelCase in Python models (matches API)
- NOT snake_case (don't convert)

---

### Python 3.13 Requirements

**Type hints** (MUST use native types):
```python
# ✅ CORRECT (Python 3.13+)
def get_contacts(self) -> list[Contact]:
    users: dict[str, Any] = {}
    result: Contact | None = None

# ❌ WRONG (old style)
from typing import List, Dict, Optional, Union
def get_contacts(self) -> List[Contact]:
```

**Only import from typing**:
- `Any` - For unknown types
- `TYPE_CHECKING` - For forward references
- `TypedDict` - For update field definitions
- `Unpack` - For type-safe **kwargs
- Nothing else!

---

### Pydantic v2 ConfigDict

**ALL models inherit this from BaseModel**:
```python
model_config = ConfigDict(
    frozen=False,  # Models are mutable
    validate_assignment=True,  # Validate on field assignment
    arbitrary_types_allowed=True,  # Allow Upsales client type
    extra="allow",  # Allow extra fields from API
    populate_by_name=True,  # Allow both field name and alias
)
```

**You don't add this** - it's inherited from `upsales.models.base.BaseModel`

---

### Test Pattern: Mock HTTP Responses

**Structure for all mock responses**:
```python
httpx_mock.add_response(
    url="https://power.upsales.com/api/v2/{endpoint}",
    method="POST",  # or "GET", "PUT", "DELETE"
    json={
        "error": None,  # ✅ Always None for success
        "data": {...}   # ✅ The actual object or array
    },
)
```

**For lists, include metadata**:
```python
json={
    "error": None,
    "metadata": {"total": 10, "limit": 100, "offset": 0},
    "data": [...]
}
```

---

## 🚨 COMMON PITFALLS (Learn from our mistakes!)

### Pitfall 1: Wrong Decorator Order (MOST COMMON!)

**Bug**: `TypeError: 'PydanticDescriptorProxy' object is not callable`

**Cause**: Decorators in wrong order

**Fix**:
```python
# ✅ CORRECT
@computed_field
@property
def is_active(self) -> bool:
    return self.active == 1

# ❌ WRONG (causes TypeError)
@property
@computed_field
def is_active(self) -> bool:
    return self.active == 1
```

**We fixed this on 17 fields across 6 models!**

---

### Pitfall 2: Incomplete TypedDict

**Bug**: IDE doesn't show all fields in autocomplete for edit()

**Cause**: TypedDict missing fields

**Fix**: Count fields!
```python
# Model has 10 fields, 3 are frozen
# TypedDict MUST have 7 fields (10 - 3)

# If TypedDict only has 5, find the missing 2 and add them!
```

---

### Pitfall 3: Wrong Field Types from Assumptions

**Bug**: `ValidationError` when recording VCR cassette

**Cause**: Assumed type doesn't match real API

**Example**:
```python
# Assumed:
cfar: BinaryFlag = Field(...)  # Thought it was 0/1

# Real API returned:
cfar: 45084548  # Actually a large int!

# Fix:
cfar: int | None = Field(None, description="CFAR identifier code")
```

**ALWAYS trust VCR cassette errors over assumptions!**

---

### Pitfall 4: Computed Fields in Serialization

**Bug**: `TypeError: Object of type CustomFields is not JSON serializable`

**Cause**: to_api_dict() included computed fields

**Fix**: Should be automatic! BaseModel excludes them:
```python
# BaseModel.to_api_dict() line 186-189
computed_fields = set(self.__class__.model_computed_fields.keys())
exclude_fields = frozen_fields | computed_fields | {"_client"}
```

**If you see this error**: BaseModel might not be excluding computed fields properly.

---

### Pitfall 5: Missing Field Descriptions

**Bug**: `interrogate` fails with <100%

**Cause**: Forgot `description=` on some fields

**Fix**: EVERY Field() MUST have description:
```python
# ✅ CORRECT
name: str = Field(description="Contact name")

# ❌ WRONG (fails interrogate)
name: str
name: str = Field(default="")
```

---

## 📊 QUALITY STANDARDS (Non-Negotiable)

### Docstring Standards

**MUST have docstrings on**:
- Model class
- PartialModel class
- Every computed field
- edit() method
- fetch_full() method
- Resource class
- Every custom method
- Every property

**Docstring format** (Google style):
```python
def method(self, arg: str) -> str:
    """
    Brief description (one line).

    Detailed description (optional, if needed).

    Args:
        arg: Description of argument.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this exception occurs.

    Example:
        >>> result = method("input")
        >>> print(result)
        'output'
    """
```

**Verification**: `uv run interrogate upsales` MUST show 100.0%

---

### Test Coverage Standards

**Resource managers**: MUST be 100%
```bash
uv run pytest tests/unit/test_contacts_resource.py \
    --cov=upsales/resources/contacts.py \
    --cov-report=term-missing

# MUST show: 100%
# If not, add tests for uncovered lines
```

**Models**: Should be 75%+
- Computed fields covered by integration tests
- edit() covered by integration tests
- Main fields covered by unit tests

**Overall**: Should maintain or improve 71%+

---

### Code Style Standards

**Ruff configuration** (`pyproject.toml`):
- Line length: 100 characters
- Target: Python 3.13
- All checks enabled
- camelCase allowed in models (matches API)

**Mypy configuration** (`pyproject.toml`):
- Strict mode enabled
- Type checking enforced
- Computed field warnings suppressed (known Pydantic limitation)

---

## 📖 COMPLETE REFERENCE: File Locations

### Source Code Locations
```
upsales/
├── models/
│   ├── base.py              # BaseModel, PartialModel (inherit from these)
│   ├── custom_fields.py     # CustomFields helper
│   ├── user.py              # ⭐ Complete reference (24 fields)
│   ├── company.py           # ⭐ Complex example (87 fields)
│   ├── product.py           # ⭐ Computed field example
│   └── {new_endpoint}.py    # ← Your new model here
├── resources/
│   ├── base.py              # BaseResource[T, P] (inherit from this)
│   ├── users.py             # ⭐ Custom methods example
│   ├── products.py          # ⭐ Bulk operations example
│   └── {new_endpoint}.py    # ← Your new resource here
├── validators.py            # ⭐ Reusable validators (ALWAYS use these)
├── client.py                # Register new resource here
└── cli.py                   # CLI tools (generate-model, init-resource)
```

### Test Locations
```
tests/
├── templates/
│   └── resource_template.py      # ⭐ Copy this for every endpoint
├── unit/
│   ├── test_base_resource.py     # BaseResource tests (18 tests)
│   ├── test_users_resource.py    # ⭐ Custom method test example
│   └── test_{endpoint}_resource.py  # ← Your tests here
├── integration/
│   ├── test_users_integration.py  # ⭐ VCR pattern example
│   └── test_{endpoint}_integration.py  # ← Your integration tests
└── cassettes/integration/
    └── test_{endpoint}_integration/  # ← VCR cassettes stored here
```

### Documentation Locations
```
docs/
├── guides/
│   └── adding-endpoints.md       # ⭐ This file
├── patterns/
│   ├── creating-models.md        # Model creation patterns
│   ├── adding-resources.md       # Resource manager patterns
│   ├── pydantic-v2-features.md   # Complete Pydantic v2 guide
│   └── vcr-testing.md            # VCR integration testing
└── api-reference/
    └── ...                       # Auto-generated from docstrings

CLAUDE.md                          # ⭐ Master project guide
ai_temp_files/
├── PROJECT_STATUS.md              # Current project state
├── postman_api_analysis.md        # ⭐ API endpoint reference
└── FOUNDATION_COMPLETE.md         # Foundation work summary
```

---

## 🎯 FOR SUB-AGENTS: Execution Strategy

### Phase 1: Code Generation (20 min)
1. Run generate-model CLI
2. Review generated code
3. Mark frozen fields
4. Add validators
5. Add computed fields (CORRECT decorator order!)
6. Add field serializer
7. Verify TypedDict completeness
8. Implement edit() method
9. Enhance PartialModel

**Validation**: Model has all features, interrogate passes

---

### Phase 2: Resource Creation (15 min)
1. Run init-resource CLI
2. Review generated resource
3. Verify endpoint path
4. Add custom methods
5. Register in client
6. Update exports

**Validation**: Resource inherits BaseResource, custom methods added

---

### Phase 3: Testing (20 min)
1. Copy test template
2. Replace placeholders
3. Update imports
4. Create sample data
5. Uncomment test bodies
6. Add custom method tests
7. Run unit tests
8. Fix until 100% coverage

**Validation**: 22+ tests, 100% resource coverage

---

### Phase 4: Integration (10 min)
1. Create integration test file
2. Copy VCR pattern
3. Add 3+ test methods
4. Record cassettes
5. Verify cassettes work offline

**Validation**: 3+ cassettes, all tests pass

---

### Phase 5: Quality Assurance (5 min)
1. Run interrogate (must be 100%)
2. Run mypy (must pass)
3. Run ruff (must pass)
4. Run full test suite
5. Verify coverage maintained

**Validation**: All quality gates pass

---

### Phase 6: Commit (2 min)
1. Add all files
2. Write descriptive commit
3. Include metrics

**Validation**: Clean git commit

---

## 🤖 AUTONOMOUS AGENT INSTRUCTIONS

When tasked with adding an endpoint, follow this protocol:

### 1. Understand the Endpoint

**Read**: `ai_temp_files/postman_api_analysis.md`
- Find the endpoint path (might not match model name!)
- Understand response structure
- Note any special fields

### 2. Execute Workflow Exactly

**Follow Steps 1-23** in this guide without deviation.

**DO NOT**:
- Skip steps
- Cut corners
- Assume patterns
- Use primitive types instead of validators
- Forget docstrings
- Commit without 100% coverage

**DO**:
- Follow patterns exactly
- Copy from reference implementations
- Trust VCR cassette errors
- Verify each step
- Run all quality checks

### 3. Handle Errors Properly

**If VCR cassette fails**:
1. Read the ValidationError message carefully
2. It tells you EXACTLY which field and what type mismatch
3. Update model to match real API data
4. Re-record cassette
5. Repeat until all tests pass

**Example**:
```
ValidationError: 1 validation error for Contact
cfar
  Value error, Binary flag must be 0 or 1, got 45084548
```

**Fix**: Change `cfar: BinaryFlag` to `cfar: int | None`

### 4. Quality Gate Requirements

**Before considering task complete**:
```bash
# ALL of these MUST pass:
✅ uv run interrogate upsales  # 100.0%
✅ uv run mypy upsales          # Success: no issues found
✅ uv run ruff check .          # All checks passed!
✅ uv run pytest tests/ -q     # 97%+ pass rate
✅ Coverage: 100% for new resource
✅ VCR: 3+ cassettes recorded
✅ Exports: All updated
✅ Client: Resource registered
```

**If ANY fail**: Fix before declaring complete!

### 5. Ask for Help When Needed

**Ask human for help if**:
- VCR cassette fails repeatedly after multiple fix attempts
- API endpoint structure is unclear
- Unsure about domain-specific computed fields
- Quality check fails and cause is unclear

**DO NOT** guess or make assumptions. Ask!

---

## 📚 COMPLETE CODE EXAMPLES

### Example 1: Complete Model Implementation

**See**: `upsales/models/user.py` (complete reference)

**Key sections**:
- Lines 26-55: Complete TypedDict (22 fields)
- Lines 77-121: Field definitions with validators
- Lines 123-183: Computed fields (4 total, CORRECT decorator order)
- Lines 185-203: Field serializer
- Lines 204-228: edit() method with Unpack

**Copy this structure for every model!**

---

### Example 2: Resource with Custom Methods

**See**: `upsales/resources/users.py`

```python
class UsersResource(BaseResource[User, PartialUser]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/users",
            model_class=User,
            partial_class=PartialUser,
        )

    async def get_by_email(self, email: str) -> User | None:
        """Custom method implementation."""
        all_users = await self.list_all()  # ✅ Use inherited methods
        for user in all_users:
            if user.email.lower() == email.lower():
                return user
        return None
```

**Pattern**: Use `list_all()`, `list()`, etc. Don't reimplement!

---

### Example 3: Integration Test with VCR

**See**: `tests/integration/test_users_integration.py:22-76`

**Exact pattern**:
```python
# VCR config
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)

# Test with cassette
@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_name.yaml")
async def test_name():
    async with Upsales.from_env() as upsales:
        # Test implementation
```

**Copy this EXACTLY!**

---

## 🎓 LEARNING FROM REAL BUGS

**We discovered 5 critical bugs during foundation work. Learn from them:**

### Bug 1: Decorator Order (17 fields affected)
**What happened**: All computed fields had `@property @computed_field` (wrong order)
**Impact**: TypeError on access
**Fix**: Reversed to `@computed_field @property`
**Lesson**: ALWAYS check decorator order!

### Bug 2: Field Type Assumptions (Company.cfar)
**What happened**: Assumed cfar was 0/1, API returned 45084548
**Impact**: ValidationError
**Fix**: Changed to `int | None`
**Lesson**: Trust VCR cassettes, not assumptions!

### Bug 3: PartialModel Structure (Company.assigned)
**What happened**: Typed as PartialUser, API returned `[]`
**Impact**: ValidationError
**Fix**: Changed to `dict[str, Any] | list[Any] | None`
**Lesson**: API structure can vary, be flexible!

### Bug 4: Computed Fields in Serialization
**What happened**: to_api_dict() included CustomFields object
**Impact**: JSON serialization error
**Fix**: Exclude computed fields from serialization
**Lesson**: Already fixed in BaseModel! Use to_api_dict()

### Bug 5: Missing Type Parameters
**What happened**: Used `list` instead of `list[Any]`
**Impact**: Mypy error
**Fix**: Always specify type parameters
**Lesson**: Python 3.13 still needs generic type parameters!

**Reference**: See `ai_temp_files/FOUNDATION_COMPLETE.md` for complete bug analysis.

---

## 🔄 Advanced: Adding PartialModels to Existing Endpoints

### When to Add PartialModel

**Scenario**: You added Opportunity model and see:
```python
stage: dict[str, Any] | None = Field(None, description="Stage")
```

**But want**:
```python
stage: PartialStage | None = Field(None, description="Stage")
```

**When to do this**:
- ✅ Object has clear structure (id, name, etc.)
- ✅ Represents an entity (Stage, Category, etc.)
- ✅ Used in multiple places
- ✅ Want IDE autocomplete

**When NOT to**:
- ❌ Structure varies a lot
- ❌ Complex nested data
- ❌ Rarely used
- ❌ Already have full model

---

### Steps to Add PartialModel

**1. Create PartialModel file** (10 min)

**Create**: `upsales/models/stage.py`

```python
"""Stage models for Upsales API."""

from typing import Any

from pydantic import Field

from upsales.models.base import PartialModel
from upsales.validators import NonEmptyStr


class PartialStage(PartialModel):
    """
    Partial Stage for nested responses.

    Example:
        >>> opportunity = await upsales.opportunities.get(1)
        >>> if opportunity.stage:
        ...     print(opportunity.stage.name)  # ✅ IDE autocomplete!
    """

    id: int = Field(frozen=True, strict=True, description="Stage ID")
    name: NonEmptyStr = Field(description="Stage name")
    # Add other common fields if present in API responses

    async def fetch_full(self) -> "PartialStage":
        """Fetch full stage data (if endpoint exists)."""
        raise NotImplementedError("Full Stage model not yet implemented")

    async def edit(self, **kwargs: Any) -> "PartialStage":
        """Edit stage (if supported)."""
        raise NotImplementedError("Stage editing not yet implemented")
```

**2. Update main model** (2 min)

```python
# In opportunity.py
from upsales.models.stage import PartialStage

# Change field
stage: PartialStage | None = Field(None, description="Stage")
```

**3. Export PartialModel** (1 min)

```python
# In upsales/models/__init__.py
from upsales.models.stage import PartialStage

__all__ = [..., "PartialStage"]
```

**4. Re-record VCR cassette** (5 min)

**CRITICAL**: Model structure changed, MUST re-record!

```bash
rm -rf tests/cassettes/integration/test_opportunities_integration/
uv run pytest tests/integration/test_opportunities_integration.py -v
```

**If ValidationError**: PartialStage doesn't match real API structure, update it!

**5. Add tests** (5 min)

```python
# In tests/unit/test_partial_models.py
class TestPartialStage:
    def test_create_partial_stage(self):
        stage = PartialStage(id=1, name="Qualified")
        assert stage.id == 1
```

---

## 🎯 SUCCESS CRITERIA FINAL CHECKLIST

**Before declaring endpoint complete, verify ALL**:

### Code (Model)
- [ ] All frozen fields marked
- [ ] All validators from upsales.validators used
- [ ] Computed fields added (minimum: custom_fields, is_active)
- [ ] Decorator order CORRECT (`@computed_field` `@property`)
- [ ] Field serializer added (if custom field)
- [ ] TypedDict COMPLETE (all updatable fields)
- [ ] edit() method implemented
- [ ] PartialModel enhanced (if exists)
- [ ] 100% field descriptions
- [ ] Docstrings on all classes and methods
- [ ] Examples in docstrings

### Code (Resource)
- [ ] Inherits from BaseResource[Model, PartialModel]
- [ ] Endpoint path verified
- [ ] Custom methods added (minimum: get_active)
- [ ] Methods use list_all(), not reimplemented
- [ ] All methods have docstrings with examples
- [ ] Registered in client
- [ ] Client docstring updated

### Tests
- [ ] Template copied and customized
- [ ] All placeholders replaced
- [ ] Sample data matches model
- [ ] ALL test methods implemented
- [ ] Custom method tests added
- [ ] Unit tests: 100% resource coverage
- [ ] Integration tests created (3+ tests)
- [ ] VCR cassettes recorded (3+ files)
- [ ] Tests run offline successfully

### Quality
- [ ] interrogate: 100.0% ✅
- [ ] mypy: Success ✅
- [ ] ruff: All checks pass ✅
- [ ] Full test suite: 97%+ pass rate ✅
- [ ] Coverage: Resource 100%, overall maintained ✅

### Integration
- [ ] Exports updated (models/__init__.py)
- [ ] Resource exports updated (resources/__init__.py)
- [ ] Client registration (client.py)
- [ ] Git files added
- [ ] Commit message written

**Total**: 44 items - ALL must be ✅ for completion!

---

## 🔑 KEY DOCUMENTS TO REFERENCE

**FOR PATTERNS** (copy these exactly):
1. **`upsales/models/user.py`** - Complete model reference
2. **`upsales/resources/users.py`** - Resource with custom methods
3. **`tests/unit/test_users_resource.py`** - Unit test pattern
4. **`tests/integration/test_users_integration.py`** - VCR pattern
5. **`tests/templates/resource_template.py`** - Test template (copy this!)

**FOR KNOWLEDGE**:
1. **`CLAUDE.md`** - Project guide (Pydantic v2 section critical!)
2. **`ai_temp_files/postman_api_analysis.md`** - API endpoints
3. **`docs/patterns/pydantic-v2-features.md`** - Complete Pydantic v2 guide
4. **`ai_temp_files/FOUNDATION_COMPLETE.md`** - Bug examples and learnings

**FOR VALIDATION**:
1. **`pyproject.toml`** - Ruff & mypy configuration
2. **`.pre-commit-config.yaml`** - Pre-commit hooks (if used)

---

## 🚨 CRITICAL RULES FOR AUTONOMOUS AGENTS

### MUST DO:
1. ✅ Follow this guide EXACTLY
2. ✅ Copy patterns from reference implementations
3. ✅ Use test template (don't write from scratch)
4. ✅ Trust VCR cassette errors over assumptions
5. ✅ Achieve 100% resource coverage
6. ✅ Get 100% docstrings
7. ✅ Pass all quality checks
8. ✅ Record VCR cassettes

### MUST NOT:
1. ❌ Skip steps
2. ❌ Use wrong decorator order
3. ❌ Use primitive types (use validators!)
4. ❌ Forget field descriptions
5. ❌ Have incomplete TypedDict
6. ❌ Commit without quality checks
7. ❌ Make assumptions about API structure
8. ❌ Write tests from scratch (use template!)

### IF UNCERTAIN:
1. 🤔 Check reference implementations
2. 🤔 Read CLAUDE.md for patterns
3. 🤔 Look at existing similar endpoint
4. 🤔 Ask human for clarification

**Quality is non-negotiable. Take time to do it right.**

---

## 📊 Expected Outcomes

**After following this guide completely, you will have**:

1. ✅ Production-ready model with ALL Pydantic v2 features
2. ✅ Resource manager with 100% test coverage
3. ✅ 22+ unit tests (all passing)
4. ✅ 3+ integration tests with VCR cassettes
5. ✅ All quality checks passing
6. ✅ Code ready to commit
7. ✅ Documentation complete

**Time**: 60 minutes average
**Quality**: Production-ready, fully tested
**Coverage**: 100% for resource, maintained overall

---

## 🎊 Version History

**v1.0** (2025-11-02): Initial guide
**v2.0** (2025-11-02): Enhanced for autonomous agents
- Added critical context section
- Added complete code examples
- Added validation criteria
- Added common pitfalls
- Added autonomous execution strategy
- Added quality standards
- Self-contained for sub-agents

---

**Guide Status**: ✅ Complete and autonomous-agent-ready
**Last Updated**: 2025-11-02
**Ready for**: Sub-agent blueprint, autonomous endpoint addition
**Expected Success Rate**: 95%+ when followed exactly
