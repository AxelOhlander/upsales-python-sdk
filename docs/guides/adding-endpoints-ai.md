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

**⚠️ CRITICAL ORDER CHANGE** (2025-11-08): Steps 2-4 create/register the resource BEFORE
recording VCR in Step 5. This unblocks the workflow - you cannot record VCR without the
resource being registered first!

**Resource-first approach**:
1. Consult api_endpoints_with_fields.json for expected fields
2. Generate model
3. **Create and register resource immediately** (Steps 2-4)
4. **Record VCR cassette** (Step 5) - now unblocked
5. **Run full CRUD validation** (Step 6) - 15 min of real API testing
6. **Apply validation results** (Step 8) - use verified data, not guesses
7. All subsequent work uses VCR, NOT live API!

### STEP 0: Consult API Endpoints Reference (2 min) ⭐ **NEW**
```bash
# Check expected required fields for CREATE
cat api_endpoints_with_fields.json | jq '.endpoints.{endpoint}.methods.POST.required'

# Check updatable fields for UPDATE
cat api_endpoints_with_fields.json | jq '.endpoints.{endpoint}.methods.PUT.allowed'

# Check read-only fields
cat api_endpoints_with_fields.json | jq '.endpoints.{endpoint}.methods.PUT.readOnly'
```
Use this as a **starting point** (verify with real testing).

### STEP 0a: Environment Check (1 min) ⭐ **NEW**
Ensure your environment can initialize the client safely (no network calls yet).

```bash
# Verify .env has required settings (do not commit this file)
cat .env | sed -E 's/(UPSALES_TOKEN=).*/\1REDACTED/'
```

```python
# Quick no-op sanity check (no API call)
import asyncio
from upsales import Upsales

async def main():
    async with Upsales.from_env():
        pass  # Ensures settings parse and client initializes

asyncio.run(main())
```

Security:
- Never print real tokens or credentials to console/logs.
- .env is already gitignored; keep secrets out of code and cassettes.

### STEP 1: Generate Model (5 min)
```bash
uv run upsales generate-model {endpoint} --partial
```
Creates `upsales/models/{endpoint}.py` with TypedDict.

### STEP 2: Create Resource (2 min) ⭐ **ENABLE VCR TESTING**
```bash
uv run upsales init-resource {endpoint}
```
Creates `upsales/resources/{endpoint}.py` with BaseResource inheritance.
Verify endpoint path matches actual API (e.g., `/accounts` not `/companies`).

**Why Now?** VCR testing (Step 5) requires the resource to be registered in the client.
Creating it early unblocks the entire workflow.

### STEP 3: Register in Client (2 min)
Edit `upsales/client.py`:
```python
from upsales.resources.{endpoint} import {Model}sResource

self.{endpoint} = {Model}sResource(self.http)
```
Update class docstring to add resource to the Attributes list.

### STEP 4: Update Exports (2 min)
Edit `upsales/models/__init__.py`:
```python
from upsales.models.{endpoint} import {Model}, {Model}UpdateFields, Partial{Model}

__all__ = [..., "{Model}", "{Model}UpdateFields", "Partial{Model}"]
```

Registration & Exports (Resources): Also update `upsales/resources/__init__.py` to export
the new resource so imports and docs stay consistent:
```python
from upsales.resources.{endpoint} import {Model}sResource

__all__ = [..., "{Model}sResource"]
```

Forward References (optional): If the new model has forward references, add a
`{Model}.model_rebuild()` call in `upsales/models/__init__.py` after imports to resolve
Pydantic v2 forward refs.

### STEP 5: Record VCR Cassette (5 min) ⭐ **CAPTURE API NOW**
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
    filter_headers=[
        ("cookie", "REDACTED"),
        ("set-cookie", "REDACTED"),  # Safety: redact tokens from responses
    ],
    filter_query_parameters=[
        ("token", "REDACTED"),  # Safety: redact token in query if ever present
    ],
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

VCR Hygiene & Safety:
- Keep `record_mode="once"`; do not switch to `"all"` unless intentionally re-recording.
- Always scrub credentials: redact `cookie` and `set-cookie` headers, query `token`, and
  any sensitive body fields (e.g., `password`).

### STEP 6: Run Full CRUD Validation (15 min) ⭐ **VERIFY ALL OPERATIONS**

**CRITICAL**: This step validates all CRUD operations against the real API and provides
authoritative results. Skip this and you'll guess which fields are required/editable!

```bash
# Run comprehensive validation (makes real API calls - creates/updates/deletes test records)
python scripts/test_full_crud_lifecycle.py {endpoint} --full

# Or run individual validators:
python scripts/test_required_create_fields.py {endpoint}    # POST: required fields
python scripts/test_required_update_fields.py {endpoint}    # PUT: updatable fields
python scripts/test_field_editability_bulk.py {endpoint}    # PUT: read-only detection
python scripts/test_search_validation.py {endpoint}         # GET: searchable fields
python scripts/test_sort_validation.py {endpoint}           # GET: sortable fields & order
python scripts/test_pagination.py {endpoint}                # GET: limit/offset behavior
python scripts/test_delete_operation.py {endpoint}          # DELETE: can delete?
```

**What This Tests**:
1. **POST (Create)**: Discovers actual required vs optional fields
2. **PUT (Update)**: Tests which fields can be edited, which are read-only
3. **GET (Search)**: Validates search() works with various field filters
4. **GET (Sort)**: Verifies sortable fields and sort order (asc/desc)
5. **GET (Pagination)**: Validates limit/offset behavior and page stitching
6. **DELETE**: Tests if records can be deleted

**Expected Output**:
```
✅ POST Validation:
   Required fields: year, month, value, user.id
   Optional fields: currency, currencyRate

✅ PUT Validation:
   Editable: year, month, value, currencyRate, currency
   Read-only: id, date, valueInMasterCurrency, user

✅ Search Validation:
   Searchable: year, month, user.id
   Not searchable: currency, currencyRate

✅ DELETE Validation:
   Can delete: Yes
```

**Apply Results Immediately**:
1. Update `{Model}CreateFields` TypedDict with discovered required fields
2. Mark read-only fields as `frozen=True` in model
3. Update `{Model}UpdateFields` to exclude read-only fields
4. Document search limitations in model docstring

**Time**: 15 minutes (but saves 60+ minutes of manual trial-and-error testing!)

### STEP 7: Analyze Cassette (5 min) ⭐ **VALIDATE MODEL STRUCTURE**
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

### STEP 8: Apply Validation Results to Model (10 min) ⭐ **USE VERIFIED DATA**
**Use STEP 6 validation results and cassette as source of truth.**

**Apply CRUD validation results from STEP 6**:
1. Add `{Model}CreateFields` TypedDict with discovered required fields
2. Mark read-only fields as `frozen=True` (from PUT validation)
3. Update `{Model}UpdateFields` to exclude read-only fields
4. Add CREATE examples to model docstring with actual required fields
5. Document search limitations if any fields are not searchable

**Example**:
```python
# From test_required_create_fields.py output:
class ContactCreateFields(TypedDict, total=False):
    """Required: client.id only (verified 2025-11-07)"""
    client: dict[str, int]  # Required
    email: str  # Optional (API file was wrong!)
    name: str
    # ... other optional fields

# From test_field_editability_bulk.py output:
# Mark these as frozen=True:
regDate: str = Field(frozen=True, description="...")
score: int = Field(frozen=True, description="...")  # Calculated
numberOfContacts: int = Field(frozen=True, description="...")  # Calculated
```

### STEP 9: Document Always-Returned Fields (5 min)

**Note**: Frozen fields should already be marked in STEP 8 based on validation results.

**Document always-returned fields** (from field selection test):
Run `test_field_selection.py` or check raw HTTP responses to discover which
fields are always returned even with field selection.

**Documentation Pattern** (3 levels):

1. **Model Docstring** - Complete list in class docstring:
```python
class Contact(BaseModel):
    """
    Contact model from /api/v2/contacts.

    Field Selection (Performance Optimization):
        When using fields=["id", "name"], these 12 fields are ALWAYS returned
        regardless of field selection (verified YYYY-MM-DD):

        - id (primary key)
        - userEditable, userRemovable (permissions)
        - has*, had* tracking fields (8 fields)
        - score (lead score)

        All other fields can be excluded for bandwidth reduction.

        Example:
            >>> contacts = await upsales.contacts.list(
            ...     fields=["id", "name", "email"],
            ...     limit=100
            ... )
            >>> # Returns: requested fields + always-returned fields
    """
```

2. **Section Comments** - Group related always-returned fields:
```python
# NOTE: These tracking fields are ALWAYS returned even with field selection (verified YYYY-MM-DD)
hasActivity: str | None = Field(None, description="Has activity (always returned)")
hadActivity: str | None = Field(None, description="Had activity (always returned)")
```

3. **Field Descriptions** - Mark individual fields:
```python
# NOTE: 'id' is ALWAYS returned even with field selection
id: int = Field(frozen=True, strict=True, description="Unique ID")

dunsNo: str | None = Field(None, description="DUNS number (always returned)")
prospectingId: str | None = Field(None, description="Prospecting ID (always returned)")
```

**Why document at 3 levels**:
- Model docstring: Complete overview with example
- Section comments: Quick scanning for developers
- Field descriptions: IDE tooltips, generated docs

**Example from Company model**:
- 17 always-returned fields documented
- Docstring explains 80% bandwidth reduction possible
- Comments mark each group of related fields
- Descriptions show "(always returned)" for discoverability

### STEP 10: Add Validators (10 min)
Replace primitive types with BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr, PositiveInt, Percentage

### STEP 11: Add Computed Fields (10 min)
- custom_fields property (if custom field exists)
- is_active property (if active field exists)
- Domain-specific helpers

Order: @computed_field THEN @property

### STEP 12: Add Field Serializer (5 min)
If custom field exists, add serializer.

### STEP 13: Verify TypedDict (5 min)
Count: model fields - frozen fields = TypedDict fields

### STEP 14: Implement edit() (5 min)
Use pattern from Pattern 5. Use to_api_dict(**kwargs).

### STEP 15: Enhance PartialModel (5 min)
Add fetch_full() and edit() methods.

### STEP 16: Add Custom Methods (10 min - optional)
Common patterns:
- get_by_email(email)
- get_by_company(company_id)
- get_active()
Use inherited list_all(), don't reimplement.

### STEP 17: Copy Test Template (15 min)
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

### STEP 18: Run Unit Tests (5 min)
```bash
uv run pytest tests/unit/test_contacts_resource.py -v --cov=upsales/resources/contacts.py --cov-report=term-missing
```
MUST achieve 100% resource coverage.

### STEP 19: Expand Integration Tests (10 min)
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

### STEP 20: Verify All Tests Use VCR (2 min)
```bash
# All integration tests should use cassettes (fast!)
uv run pytest tests/integration/test_contacts_integration.py -v
# Should complete in < 2 seconds (VCR replay)
```

### STEP 21: Quality Checks (5 min)
ALL must pass:
```bash
uv run interrogate upsales  # MUST be 100%
uv run mypy upsales  # MUST pass strict
uv run ruff format .  # MUST format
uv run ruff check .  # MUST pass (N999 warnings acceptable)
uv run pytest tests/unit/test_contacts_resource.py --cov=upsales/resources/contacts.py  # MUST be 100%
```

### STEP 22: Update Documentation (5 min) ⭐ **RECORD YOUR WORK**

**CRITICAL**: Update tracking files to record verification status and share knowledge with the team.

**A. Update `docs/endpoint-map.md`**:

Mark endpoint as verified with complete CRUD status:

```markdown
### {endpoint}
**Status**: ✅ VERIFIED
**Verification Date**: YYYY-MM-DD
**Endpoint**: /api/v2/{endpoint}

**CRUD Operations**:
- CREATE: ✅ Verified (required: field1, field2, field3)
- READ: ✅ Verified
- UPDATE: ✅ Verified (editable: field1, field2; read-only: id, date)
- DELETE: ✅ Verified
- SEARCH: ✅ Verified (searchable: field1, field2)

**Discrepancies from API File**:
- Field X was listed as required but is actually optional
- Field Y is read-only but API file didn't document it

**Notes**:
- Nested required field pattern: client.id, user.id
- Special validation: probability must be 1-99
```

**B. Update `docs/endpoint-map.md`**:

Update the endpoint's entry to show verified status with CRUD details.

**Time**: 5 minutes

**D. Update API Reference (docs coverage)**:

Add the new resource and models to the API reference pages so MkDocs includes
them in the published docs.

- Edit `docs/api-reference/resources.md` and add:
  ```markdown
  ::: upsales.resources.{endpoint}.{Model}sResource
      options:
        show_root_heading: true
        show_source: false
  ```

- Edit `docs/api-reference/models.md` and add both full and partial models:
  ```markdown
  ::: upsales.models.{endpoint}.{Model}
      options:
        show_root_heading: true
        show_source: false
        members_order: source

  ::: upsales.models.{endpoint}.Partial{Model}
      options:
        show_root_heading: true
        show_source: false
  ```

**E. Build Docs**:
```bash
uv run mkdocs build
```
Ensures reference pages render and import paths are correct.

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
11. **Field selection not documented**: Mark always-returned fields (see STEP 9)
12. **Missing None defaults**: Fields need `| None` defaults for field selection support
13. **Skipping CRUD validation**: Always run STEP 6 validation - guessing requirements leads to bugs
14. **Skipping documentation**: Always update STEP 22 docs - undocumented work is invisible to the team
15. **Resources exports not updated**: Add import + `__all__` entry in `upsales/resources/__init__.py`.
16. **Docstrings missing on helper types**: Ensure TypedDict classes and PartialModel helpers have docstrings to satisfy `interrogate` 100%.
17. **Insufficient VCR scrubbing**: Redact `set-cookie`, `cookie`, query `token`, and any sensitive body fields.
18. **API reference not updated**: Add new resource/model entries to `docs/api-reference/*.md` and run `mkdocs build`.

## Reference Files

### Models & Resources
- Models: `upsales/models/user.py`, `upsales/models/company.py`, `upsales/models/contacts.py`
- Resources: `upsales/resources/users.py`, `upsales/resources/base.py`
- Tests: `tests/templates/resource_template.py`, `tests/integration/test_users_integration.py`
- Validators: `upsales/validators.py`

### Automation Scripts ⭐ **TIME SAVERS**
- **API Reference**: `api_endpoints_with_fields.json` (167 endpoints documented)
- **CREATE Validator**: `scripts/test_required_create_fields.py` (discovers required fields + DELETE)
- **UPDATE Validator**: `scripts/test_required_update_fields.py` (discovers required update fields)
- **Editability Tester**: `scripts/test_field_editability_bulk.py` (bulk update, discovers read-only fields)
- **Search Validator**: `scripts/test_search_validation.py` (validates searchable fields + results)
- **Sort Validator**: `scripts/test_sort_validation.py` (validates sorting + actual order)
- **Field Selection**: `scripts/test_field_selection.py` (discovers always-returned fields)
- **Pagination Test**: `scripts/test_pagination.py` (validates limit/offset, run once)
- **DELETE Validator**: `scripts/test_delete_operation.py` (standalone DELETE verification)
- **Full CRUD Lifecycle**: `scripts/test_full_crud_lifecycle.py` (orchestrator, runs all validators)
- **Field Analyzer**: `ai_temp_files/find_unmapped_fields.py` (compare cassette vs model)

**Time Savings**: ~45-60 minutes per endpoint with automation vs manual testing

**Comprehensive Testing**: Run all validators with:
```bash
python scripts/test_full_crud_lifecycle.py {endpoint} --full
```

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
- [ ] **STEP 6: Full CRUD validation completed** ⭐ CRITICAL
  - [ ] CREATE requirements verified with `test_required_create_fields.py`
  - [ ] UPDATE requirements verified with `test_required_update_fields.py`
  - [ ] Field editability verified with `test_field_editability_bulk.py`
  - [ ] Search validation completed with `test_search_validation.py`
  - [ ] DELETE operation verified with `test_delete_operation.py`
- [ ] Frozen fields marked based on validation results
- [ ] {Model}CreateFields TypedDict added
- [ ] {Model}UpdateFields includes only editable fields
- [ ] 100% resource coverage
- [ ] 100% docstrings (interrogate)
- [ ] mypy strict passing
- [ ] ruff passing
- [ ] VCR cassettes recorded (3+)
- [ ] Client registered
- [ ] Exports updated
- [ ] Integration tests passing
- [ ] **STEP 22: Documentation updated** ⭐ REQUIRED
  - [ ] docs/endpoint-map.md updated with verified status
  - [ ] CRUD operation results documented
  - [ ] Discrepancies from API file noted

Time budget: 65 minutes with automation (was 90+ manual). Do not skip steps.

## Automation Workflow Summary

**Old Manual Way** (90-120 min):
```
Generate → VCR → Analyze → Trial-and-error CREATE testing →
Trial-and-error UPDATE testing → Guess frozen fields → Document
```

**New Automated Way** (45-60 min):
```
Check API file → Generate → Create Resource → Register → Export →
VCR → Full CRUD Validation (STEP 6 - 15 min) →
Apply Results → Analyze Cassette → Enhance Model → Test → Quality Checks
```

**STEP 6 CRUD Validation Runs**:
- test_required_create_fields.py (POST: required fields)
- test_required_update_fields.py (PUT: updatable fields)
- test_field_editability_bulk.py (PUT: read-only detection)
- test_search_validation.py (GET: searchable fields)
- test_delete_operation.py (DELETE: can delete?)

**Why Resource Early?** VCR testing (Step 5) requires the resource to be registered in the
client. Creating and registering it immediately (Steps 2-4) unblocks the workflow.

**Why CRUD Validation?** STEP 6 provides authoritative results from real API testing, eliminating
guesswork about which fields are required, editable, or searchable.

**Time Saved**: 30-60 minutes per endpoint
**Accuracy**: Higher (no guessing, real API testing)
**Confidence**: Verified with actual API responses
