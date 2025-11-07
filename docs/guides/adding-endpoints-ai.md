# Autonomous Endpoint Addition Guide - AI Version

**Target**: 30-60 minutes per endpoint. Quality non-negotiable.

## Success Criteria
ALL must pass:
- Model with 12 Pydantic v2 patterns
- Resource with BaseResource inheritance
- Tests passing with 100% resource coverage
- VCR cassette recorded
- ruff, mypy, interrogate all pass
- Exports updated
- Client registered
- 100% docstrings

## Critical Patterns (MEMORIZE)

### 1. Decorator Order (CRITICAL - #1 Bug)
```python
@computed_field  # FIRST
@property        # SECOND
def is_active(self) -> bool:
    return self.active == 1
```
WRONG order causes TypeError. This was found in 17 fields.

### 2. Reusable Validators (REQUIRED)
```python
from upsales.validators import BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr, PositiveInt, Percentage

active: BinaryFlag = Field(default=1, description="0=no, 1=yes")
email: EmailStr = Field(description="Email")
custom: CustomFieldsList = Field(default=[], description="Custom fields")
name: NonEmptyStr = Field(description="Name")
probability: Percentage = Field(description="0-100")
```

### 3. Frozen Fields (REQUIRED)
```python
id: int = Field(frozen=True, strict=True, description="ID")
regDate: str = Field(frozen=True, description="Registration")
modDate: str = Field(frozen=True, description="Modified")
```

### 4. TypedDict (REQUIRED)
```python
class ContactUpdateFields(TypedDict, total=False):
    """All updatable fields (NOT frozen ones)."""
    name: str
    email: str
    active: int
    # Count MUST equal: model fields - frozen fields
```

### 5. edit() Method (REQUIRED)
```python
async def edit(self, **kwargs: Unpack[ContactUpdateFields]) -> "Contact":
    """Edit via API."""
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.contacts.update(
        self.id,
        **self.to_api_dict(**kwargs)  # Use to_api_dict NOT to_update_dict
    )
```

### 6. Field Serializer (REQUIRED if custom field exists)
```python
@field_serializer('custom', when_used='json')
def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Clean custom fields for API."""
    return [
        {"fieldId": item["fieldId"], "value": item.get("value")}
        for item in custom
        if "value" in item and item.get("value") is not None
    ]
```

### 7. Computed Fields (REQUIRED if applicable)
```python
from pydantic import computed_field
from upsales.models.custom_fields import CustomFields

@computed_field
@property
def custom_fields(self) -> CustomFields:
    """Dict-like access."""
    return CustomFields(self.custom)

@computed_field
@property
def is_active(self) -> bool:
    """Boolean helper."""
    return self.active == 1
```

### 8. Field Descriptions (REQUIRED - 100%)
```python
# CORRECT
name: str = Field(description="Contact name")

# WRONG - fails interrogate
name: str
```

### 9. PartialModel Pattern
```python
class PartialContact(PartialModel):
    id: int = Field(frozen=True, strict=True, description="ID")
    name: NonEmptyStr = Field(description="Name")

    async def fetch_full(self) -> Contact:
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.get(self.id)

    async def edit(self, **kwargs: Any) -> Contact:
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.update(self.id, **kwargs)
```

### 10. Resource Inheritance
```python
from upsales.resources.base import BaseResource

class ContactsResource(BaseResource[Contact, PartialContact]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/contacts",  # Verify actual API endpoint
            model_class=Contact,
            partial_class=PartialContact,
        )
```

### 11. search() Operators
Inherited from BaseResource. Natural operators:
- `>=value`, `>value`, `<=value`, `<value`, `=value`, `!=value`
- `*value` - substring
- `=1,2,3` - IN list

### 12. Field Selection & Sorting
```python
# Field selection (50-90% faster)
results = await upsales.contacts.search(
    active=1,
    fields=["id", "name"],  # Optimize
    sort="-regDate"  # Descending
)
```

## Workflow Steps

**CRITICAL**: VCR-first approach:
1. Generate model
2. **Record VCR immediately** (Step 2)
3. All subsequent work uses VCR, NOT live API!

### STEP 1: Generate Model (5 min)
```bash
uv run upsales generate-model {endpoint} --partial
```
Creates `upsales/models/{endpoint}.py` with TypedDict.

### STEP 2: Record VCR Cassette (5 min) ⭐ **CAPTURE API NOW**
```bash
# Create minimal test
cat > tests/integration/test_contacts_integration.py << 'EOF'
import pytest
import vcr
from upsales import Upsales
from upsales.models.contact import Contact

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)

@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_record_structure.yaml")
async def test_record_api_structure():
    """Record real API for offline development."""
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=5)
        assert len(contacts) > 0
        print(f"✅ Recorded {len(contacts)} contacts")
EOF

# Record (makes real API call)
uv run pytest tests/integration/test_contacts_integration.py -v
```
From now on: VCR only, no more API calls!

### STEP 3: Analyze Cassette (5 min) ⭐ **VALIDATE MODEL**
```python
# ai_temp_files/analyze_cassette.py
import yaml, json

with open("tests/cassettes/.../test_record_structure.yaml") as f:
    cassette = yaml.safe_load(f)

response = json.loads(cassette["interactions"][0]["response"]["body"]["string"])
item = response["data"][0] if isinstance(response["data"], list) else response["data"]

print("🔍 Real API Fields:")
for field, value in item.items():
    print(f"  {field}: {type(value).__name__}")

# Compare against model
from upsales.models.contact import Contact
api_fields = set(item.keys())
model_fields = set(Contact.model_fields.keys())
missing = api_fields - model_fields
extra = model_fields - api_fields

if missing:
    print(f"❌ Missing in model: {missing}")
if extra:
    print(f"⚠️  Extra in model: {extra}")
```
Trust the cassette! Fix model if mismatch.

### STEP 4: Review Generated Code (5 min)
Use cassette as source of truth for field types.

### STEP 5: Mark Frozen Fields (2 min)
Add `frozen=True` to: id, regDate, modDate, createdAt, updatedAt

### STEP 6: Add Validators (10 min)
Replace primitive types with BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr, PositiveInt, Percentage

### STEP 7: Add Computed Fields (10 min)
- custom_fields property (if custom field exists)
- is_active property (if active field exists)
- Domain-specific helpers

Order: @computed_field THEN @property

### STEP 8: Add Field Serializer (5 min)
If custom field exists, add serializer.

### STEP 9: Verify TypedDict (5 min)
Count: model fields - frozen fields = TypedDict fields

### STEP 10: Implement edit() (5 min)
Use pattern from Pattern 5. Use to_api_dict(**kwargs).

### STEP 11: Enhance PartialModel (5 min)
Add fetch_full() and edit() methods.

### STEP 12: Create Resource (2 min)
```bash
uv run upsales init-resource {endpoint}
```
Verify endpoint path matches actual API.

### STEP 13: Add Custom Methods (10 min - optional)
Common patterns:
- get_by_email(email)
- get_by_company(company_id)
- get_active()
Use inherited list_all(), don't reimplement.

### STEP 14: Register in Client (2 min)
Edit `upsales/client.py`:
```python
from upsales.resources.contacts import ContactsResource

self.contacts = ContactsResource(self.http)
```
Update docstring.

### STEP 15: Update Exports (2 min)
Edit `upsales/models/__init__.py`:
```python
from upsales.models.contact import Contact, ContactUpdateFields, PartialContact

__all__ = [..., "Contact", "ContactUpdateFields", "PartialContact"]
```

### STEP 16: Copy Test Template (15 min)
```bash
cp tests/templates/resource_template.py tests/unit/test_contacts_resource.py
```
Global replace:
- `{ResourceName}` → `ContactsResource`
- `{ModelName}` → `Contact`
- `{PartialModelName}` → `PartialContact`
- `{endpoint}` → `/contacts`
- `{resource_name}` → `contacts`

Update imports, create sample_data fixture with ALL required fields (check model for fields without defaults).

### STEP 17: Run Unit Tests (5 min)
```bash
uv run pytest tests/unit/test_contacts_resource.py -v --cov=upsales/resources/contacts.py --cov-report=term-missing
```
MUST achieve 100% resource coverage.

### STEP 18: Expand Integration Tests (10 min)
Add to existing test file (already has VCR configured):
```python
@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_computed_fields.yaml")
async def test_computed_fields_with_vcr():
    """Test computed fields with recorded data."""
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=1)
        contact = contacts[0]
        assert isinstance(contact.is_active, bool)
        assert isinstance(contact.custom_fields, CustomFields)

@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_serialization.yaml")
async def test_serialization_with_vcr():
    """Test to_api_dict() with recorded data."""
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=1)
        api_dict = contacts[0].to_api_dict()
        assert "id" not in api_dict  # Frozen excluded
        assert "is_active" not in api_dict  # Computed excluded
```
Run to record new cassettes (uses VCR, instant replay after first run).

### STEP 19: Verify All Tests Use VCR (2 min)
```bash
# All integration tests should use cassettes (fast!)
uv run pytest tests/integration/test_contacts_integration.py -v
# Should complete in < 2 seconds (VCR replay)
```

### STEP 20: Quality Checks (5 min)
ALL must pass:
```bash
uv run interrogate upsales  # MUST be 100%
uv run mypy upsales  # MUST pass strict
uv run ruff format .  # MUST format
uv run ruff check .  # MUST pass (N999 warnings acceptable)
uv run pytest tests/unit/test_contacts_resource.py --cov=upsales/resources/contacts.py  # MUST be 100%
```

## Common Issues

1. **Decorator order**: @computed_field THEN @property
2. **Missing frozen**: id, regDate, modDate must be frozen=True
3. **TypedDict incomplete**: Count must match updatable fields
4. **Missing descriptions**: All fields need description=
5. **Wrong serialization**: Use to_api_dict NOT to_update_dict
6. **Primitive types**: Use validators not int/str/list
7. **No field serializer**: Required if custom field exists
8. **Wrong endpoint**: Verify actual API path (e.g., /accounts not /companies)
9. **Sample data missing required fields**: Check model for fields without defaults
10. **Computed fields in serialization**: Should be excluded automatically

## Reference Files
- Models: `upsales/models/user.py`, `upsales/models/company.py`
- Resources: `upsales/resources/users.py`, `upsales/resources/base.py`
- Tests: `tests/templates/resource_template.py`, `tests/integration/test_users_integration.py`
- Validators: `upsales/validators.py`

## Validator Selection Rules
- 0/1 flags → BinaryFlag
- Email → EmailStr
- custom/customFields → CustomFieldsList
- Required strings → NonEmptyStr
- Non-negative integers → PositiveInt
- 0-100 range → Percentage

## API Endpoint Naming
Check actual API:
- Companies → `/accounts` (NOT /companies)
- Contacts → `/contacts`
- Users → `/users`
Verify in `ai_temp_files/postman_api_analysis.md`

## Final Verification
Before marking complete:
- [ ] All 12 patterns applied
- [ ] 100% resource coverage
- [ ] 100% docstrings (interrogate)
- [ ] mypy strict passing
- [ ] ruff passing
- [ ] VCR cassettes recorded (3+)
- [ ] Client registered
- [ ] Exports updated
- [ ] Integration tests passing

Time budget: 60 minutes. Do not skip steps.
