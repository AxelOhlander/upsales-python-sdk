# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an async Python wrapper for the Upsales CRM API, designed as both a production-ready library and a template-driven system for AI-assisted development. The project **requires Python 3.13+** and leverages modern language features exclusively.

## API Endpoints Reference File

**CRITICAL**: The file `api_endpoints_with_fields.json` in the project root contains **comprehensive documentation of all 167 Upsales API endpoints** extracted from the official Upsales codebase on GitHub.

### What This File Contains

```json
{
  "metadata": {
    "total_endpoints_documented": 167,
    "generated": "2025-11-07",
    "version": "v2"
  },
  "endpoints": {
    "endpoint_name": {
      "base_path": "/api/v2/endpoint",
      "description": "...",
      "methods": {
        "GET_list": { "returns": ["field1", "field2", ...] },
        "GET_item": { "returns": ["field1", "field2", ...] },
        "POST": {
          "required": [
            {"field": "name", "type": "string", "structure": {...}, "notes": "..."}
          ],
          "optional": [
            {"field": "name", "type": "string", "default": "...", "notes": "..."}
          ]
        },
        "PUT": {
          "allowed": ["field1", "field2", ...],
          "readOnly": ["id", "regDate", ...]
        },
        "DELETE": { "path": "/api/v2/endpoint/:id" }
      }
    }
  }
}
```

### Critical Information Provided

For **each of 167 endpoints**, the file documents:

1. **GET Operations**:
   - All fields returned by list endpoint
   - All fields returned by single item endpoint
   - Differences between list and item responses

2. **POST Operations** (Create):
   - **Required fields** with:
     - Field name
     - Data type (string, number, object, array, etc.)
     - Structure for nested objects (e.g., `{"id": "number"}`)
     - Format specifications (e.g., "YYYY-MM-DD" for dates)
     - Special notes and constraints
     - Default values
   - **Optional fields** with:
     - Same details as required
     - Default values
     - Conditional requirements

3. **PUT Operations** (Update):
   - **Allowed fields** - Fields that can be updated
   - **Read-only fields** - Fields that cannot be changed
   - Constraints and special rules

4. **DELETE Operations**:
   - Endpoint paths and requirements

5. **Special Patterns**:
   - Nested object structures (e.g., `user: {"id": number}`)
   - Array structures with examples
   - Field dependencies
   - Validation rules

### How to Use This File

#### 1. **Discovering Required Fields for CREATE**

```bash
# Example: Check what's required to create an order
cat api_endpoints_with_fields.json | jq '.endpoints.orders.methods.POST.required'

# Output:
[
  {"field": "client", "type": "object", "structure": {"id": "number"}},
  {"field": "user", "type": "object", "structure": {"id": "number"}},
  {"field": "stage", "type": "object", "structure": {"id": "number"}},
  {"field": "date", "type": "string", "format": "YYYY-MM-DD"},
  {"field": "orderRow", "type": "array", "structure": [{"product": {"id": "number"}}]}
]
```

#### 2. **Discovering Updatable Fields for UPDATE**

```bash
# Example: Check what can be updated on a contact
cat api_endpoints_with_fields.json | jq '.endpoints.contacts.methods.PUT.allowed'

# Output:
["name", "firstName", "lastName", "email", "phone", "cellPhone", "title",
 "active", "custom", "categories", "projects"]
```

#### 3. **Discovering Read-Only Fields**

```bash
# Example: Check read-only fields for accounts
cat api_endpoints_with_fields.json | jq '.endpoints.accounts.methods.PUT.readOnly'

# Output:
["id", "regDate", "totalOrderValue", "userRemovable", "userEditable", "growth"]
```

#### 4. **Discovering All Returned Fields**

```bash
# Example: Check what fields are returned for activities
cat api_endpoints_with_fields.json | jq '.endpoints.activities.methods.GET_list.returns'
```

### Important Caveats

**⚠️ VALIDATION REQUIRED**: While this file provides a **strong foundation**, the field information may be:
- **Incomplete** - Some fields might be missing
- **Incorrect** - Field types or requirements might be wrong
- **Outdated** - API may have changed since extraction
- **Over-specified** - Some "required" fields might actually be optional

**Always validate with real API testing:**
1. Use VCR cassettes to capture actual API responses
2. Test CREATE operations with minimal fields to discover true requirements
3. Verify field structures match actual API responses
4. Document discrepancies found during testing

### Integration with Development Workflow

#### Step 1: Consult API File First

Before implementing an endpoint:
```bash
# Check what the API file says about the endpoint
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name'
```

#### Step 2: Generate Initial Model

Use the field information to guide model generation:
```bash
uv run upsales generate-model endpoint_name --partial
```

#### Step 3: Verify with VCR Testing

Record actual API responses (Step 2 in workflow):
```bash
# This captures REAL field structure
uv run pytest tests/integration/test_endpoint_integration.py -v
```

#### Step 4: Compare and Adjust

Use the analysis script to find discrepancies:
```python
# Compare API file vs VCR cassette vs model
uv run python ai_temp_files/find_unmapped_fields.py
```

#### Step 5: Document Findings

Update the endpoint-map.md with verified information:
- Mark fields as verified
- Note discrepancies from API file
- Document actual requirements

### Current Implementation Status

**As of 2025-11-07:**
- **API File Documents**: 167 endpoints
- **Currently Implemented**: 35 resources (21%)
- **Remaining to Implement**: 132 endpoints (79%)

**High Priority Endpoints in API File** (commonly used):
- ✅ orders (implemented, verified with nested required fields)
- ✅ opportunities (shares model with orders)
- ✅ accounts (companies - implemented)
- ✅ contacts (implemented, needs verification)
- ✅ activities (implemented, needs verification)
- ✅ appointments (implemented, needs verification)
- ✅ products (implemented, verified)
- ✅ users (implemented, verified)
- ❌ agreements (not implemented)
- ❌ projects (partially implemented)
- ❌ tickets (not implemented)
- ❌ quotes (not implemented)

### Finding Endpoints by Category

```bash
# All endpoints
cat api_endpoints_with_fields.json | jq '.endpoints | keys'

# Count by operation support
cat api_endpoints_with_fields.json | jq '.endpoints | to_entries[] |
  select(.value.methods.POST) | .key' | wc -l  # Count create-capable endpoints

cat api_endpoints_with_fields.json | jq '.endpoints | to_entries[] |
  select(.value.methods.PUT) | .key' | wc -l   # Count update-capable endpoints
```

### Example: Using API File for Orders

The Orders endpoint documentation in the API file correctly identified:
- ✅ Required fields: client.id, user.id, stage.id, date, orderRow with product.id
- ✅ Nested structure: `{"id": number}` for related entities
- ✅ Date format: "YYYY-MM-DD"
- ✅ Read-only fields: regDate, modDate, orderValue, weightedValue

This was verified through manual testing and documented in:
- `upsales/models/orders.py` - OrderCreateFields TypedDict
- `docs/patterns/nested-required-fields.md` - Pattern guide
- `docs/endpoint-map.md` - Verification status

### Best Practice

**Always use this file as a starting point, not the final authority.**

1. ✅ **DO**: Use it to guide model generation and understand API structure
2. ✅ **DO**: Use it to identify likely required fields before testing
3. ✅ **DO**: Compare it with VCR cassettes to validate
4. ❌ **DON'T**: Assume all field information is 100% accurate
5. ❌ **DON'T**: Skip VCR testing because "the file has the fields"
6. ❌ **DON'T**: Trust optional/required designations without verification

## Temporary Files and Testing

**IMPORTANT**: All temporary files must be created in the `ai_temp_files\` directory:

- **What goes in `ai_temp_files\`**:
  - Test scripts for exploration or experimentation
  - Temporary analysis documents
  - Debug outputs
  - API response samples for analysis
  - Any file that is NOT part of the production SDK

- **Cleanup Policy**:
  - Delete temporary test scripts after they've been used
  - Keep analysis documents only if they provide ongoing value
  - Never commit unnecessary temporary files to git

- **Examples**:
  ```python
  # ✅ Correct: Temporary test script
  # File: ai_temp_files/test_campaign_api.py

  # ❌ Wrong: Test script in project root
  # File: test_something.py
  ```

**Never create temporary files in**:
- Project root directory
- `upsales/` source directory
- `tests/` directory (only proper test files belong here)
- `docs/` directory (only official documentation)

## Terminology

**IMPORTANT**: This SDK uses user-friendly naming that matches the Upsales UI, not always the API endpoints:

| Concept | Upsales UI | API Endpoint | Nested Field | SDK Naming | Usage |
|---------|------------|--------------|--------------|------------|-------|
| **SDK Instance** | - | - | - | `Upsales` | `upsales = Upsales(token=...)` |
| Customer | Companies | `/accounts` | `"client"` | `Company` | `upsales.companies` |
| User | Users | `/users` | - | `User` | `upsales.users` |
| Product | Products | `/products` | - | `Product` | `upsales.products` |

**Key Decisions**:
1. **`Upsales`** (not `UpsalesClient`) - Clean, simple naming. No collision with data models.
2. **`Company`** (not `Account`) - Matches UI terminology for better user experience.
3. **Field aliases** - API `"client"` → Python `company` using Pydantic `Field(alias="client")`

**Clean Separation**:
```python
# SDK instance
upsales = Upsales(token="...")

# Data model
company: Company = await upsales.companies.get(1)
contact_company: PartialCompany = contact.company

# No naming collisions!
```

**Nested Field Mapping**: When the API returns a field named `"client"` in nested responses (e.g., in contacts), we map it to `company` in Python using Pydantic field aliases:

```python
from pydantic import Field

class Contact(BaseModel):
    id: int
    name: str
    # API sends "client", Python uses "company"
    company: PartialCompany = Field(alias="client")
```

See `docs/terminology.md` for complete rationale.

## Naming Conventions

**CRITICAL**: This project follows strict PEP 8 naming conventions. All files, classes, and identifiers must adhere to these rules.

### File Naming Rules

#### Models (`upsales/models/`)

**Rule**: Always use `snake_case` for file names.

```
✅ CORRECT:
- order_stages.py
- sales_coaches.py
- todo_views.py
- api_keys.py
- project_plan_stages.py
- client_categories.py

❌ WRONG:
- orderStages.py        # camelCase
- salesCoaches.py       # camelCase
- todoViews.py          # camelCase
- apiKeys.py            # camelCase
- projectPlanStages.py  # PascalCase
- clientcategories.py   # no underscores
```

**Conversion Formula**: `camelCase` or `PascalCase` → `snake_case`
- `orderStages` → `order_stages`
- `SalesCoach` → `sales_coaches` (model file, plural)
- `ApiKey` → `api_keys` (model file, plural)

#### Resources (`upsales/resources/`)

**Rule**: Always use `snake_case` for file names, always plural.

```
✅ CORRECT:
- order_stages.py      # Plural, snake_case
- sales_coaches.py     # Plural, snake_case
- todo_views.py        # Plural, snake_case
- api_keys.py          # Plural, snake_case

❌ WRONG:
- order_stage.py       # Singular (should be plural)
- orderStages.py       # camelCase (should be snake_case)
- salesCoach.py        # Singular + camelCase
```

### Class Naming Rules

#### Model Classes

**Rule**: Always use `PascalCase`, always singular.

```
✅ CORRECT:
class OrderStage(BaseModel):        # PascalCase, singular
class SalesCoach(BaseModel):        # PascalCase, singular
class TodoView(BaseModel):          # PascalCase, singular
class ApiKey(BaseModel):            # PascalCase, singular
class ProjectPlanStage(BaseModel):  # PascalCase, singular

❌ WRONG:
class Orderstage(BaseModel):        # Missing capitals
class salesCoach(BaseModel):        # camelCase
class Apikey(BaseModel):            # Wrong capitalization (should be ApiKey)
class Projectplanstage(BaseModel):  # Missing capitals (should be ProjectPlanStage)
class OrderStages(BaseModel):       # Plural (should be singular)
```

#### Partial Model Classes

**Rule**: Prefix with `Partial`, use `PascalCase`, singular.

```
✅ CORRECT:
class PartialOrderStage(PartialModel):
class PartialSalesCoach(PartialModel):
class PartialApiKey(PartialModel):
class PartialProjectPlanStage(PartialModel):

❌ WRONG:
class PartialApikey(PartialModel):         # Wrong capitalization
class PartialProjectplanstage(PartialModel):  # Missing capitals
```

#### Resource Classes

**Rule**: Use `PascalCase` + `Resource` suffix, always plural for the base name.

```
✅ CORRECT:
class OrderStagesResource(BaseResource):     # Plural + Resource
class SalesCoachesResource(BaseResource):    # Plural + Resource
class TodoViewsResource(BaseResource):       # Plural + Resource
class ApiKeysResource(BaseResource):         # Plural + Resource

❌ WRONG:
class OrderStageResource(BaseResource):      # Singular (should be plural)
class Orderstagesresource(BaseResource):     # Wrong capitalization
```

### Client Attribute Naming

**Rule**: Use `snake_case`, always plural.

```python
# In upsales/client.py

class Upsales:
    def __init__(self, token: str, ...):
        self.http = HTTPClient(token, ...)

        # ✅ CORRECT: snake_case, plural
        self.order_stages = OrderStagesResource(self.http)
        self.sales_coaches = SalesCoachesResource(self.http)
        self.todo_views = TodoViewsResource(self.http)
        self.api_keys = ApiKeysResource(self.http)
        self.project_plan_stages = ProjectPlanStagesResource(self.http)

        # ❌ WRONG: camelCase or incorrect plural
        self.orderStages = OrderStagesResource(self.http)    # camelCase
        self.order_stage = OrderStagesResource(self.http)    # Singular
```

### TypedDict Naming

**Rule**: Use `PascalCase` + descriptive suffix.

```python
✅ CORRECT:
class OrderStageUpdateFields(TypedDict, total=False):
class OrderStageCreateFields(TypedDict, total=False):
class SalesCoachUpdateFields(TypedDict, total=False):

❌ WRONG:
class orderStageUpdateFields(TypedDict, total=False):  # camelCase
class UpdateFieldsOrderStage(TypedDict, total=False):  # Wrong order
```

### Special Cases

#### Acronyms and Initialisms

**Rule**: Treat acronyms as words, capitalize only the first letter in PascalCase.

```
✅ CORRECT:
- ApiKey (not APIKey)
- HttpClient (not HTTPClient)
- JsonData (not JSONData)

Exception for well-known short acronyms:
- URL (acceptable)
- ID (acceptable when alone, but use Id in compounds: userId)
```

#### Multi-word API Endpoints

**Rule**: Use underscores to separate all words.

```
API Endpoint         →  File Name              →  Class Name
-----------------------------------------------------------------
/orderStages         →  order_stages.py        →  OrderStage
/salesCoaches        →  sales_coaches.py       →  SalesCoach
/projectPlanStages   →  project_plan_stages.py →  ProjectPlanStage
/clientCategories    →  client_categories.py   →  ClientCategory
/apiKeys             →  api_keys.py            →  ApiKey
```

### Standardization Script

**A refactoring script is provided to fix existing naming inconsistencies**:

```bash
# Preview changes (dry-run mode)
python scripts/standardize_naming.py --dry-run

# Apply changes
python scripts/standardize_naming.py --execute
```

**What it does**:
1. Renames model files from camelCase to snake_case
2. Renames resource files to snake_case
3. Fixes class names to proper PascalCase
4. Updates all imports in __init__.py files
5. Updates client.py attributes
6. Updates test file imports

**When to use**: Only run this once if you're working with legacy code that doesn't follow conventions.

### Quick Reference

| Element | Convention | Example |
|---------|-----------|---------|
| **Model file** | snake_case | `order_stages.py` |
| **Resource file** | snake_case, plural | `order_stages.py` |
| **Model class** | PascalCase, singular | `OrderStage` |
| **Partial class** | Partial + PascalCase, singular | `PartialOrderStage` |
| **Resource class** | PascalCase plural + Resource | `OrderStagesResource` |
| **Client attribute** | snake_case, plural | `upsales.order_stages` |
| **TypedDict** | PascalCase + Fields | `OrderStageUpdateFields` |

### Key Design Principles

1. **Template-Driven Architecture**: `BaseModel`, `PartialModel`, and `BaseResource` are designed as replicable templates for extending the SDK with new endpoints
2. **Python 3.13+ Modern Syntax**: Native type hints (`list`, `dict`, `|`), type parameter syntax (`[T, P]`), pattern matching, and exception groups throughout
3. **Pydantic v2 Features**: Reusable validators, computed fields, optimized serialization, field aliases
4. **90%+ Docstring Coverage**: All public APIs require comprehensive docstrings with examples
5. **Free-Threaded Mode Support**: Bulk operations documented for true parallelism without GIL

## Pydantic v2 Patterns

**CRITICAL**: This SDK uses advanced Pydantic v2 features for validation, serialization, and developer experience. Always follow these patterns when creating or updating models.

### Pydantic Settings (Configuration)

**Use pydantic-settings for type-safe configuration management:**

```python
from upsales.settings import UpsalesSettings, load_settings

# Load with validation
settings = load_settings()  # Validates types, required fields, ranges
print(settings.upsales_token)  # ✅ Type-safe, IDE autocomplete

# Create client
upsales = Upsales(
    token=settings.upsales_token,
    max_concurrent=settings.upsales_max_concurrent  # ✅ Validated 1-200
)

# Or use directly
upsales = Upsales.from_env()  # ✅ Uses pydantic-settings internally
```

**Benefits**:
- ✅ Reuses EmailStr validator for email validation
- ✅ Type checking (max_concurrent must be int, 1-200)
- ✅ URL validation (base_url must be valid URL)
- ✅ Clear errors for missing required vars
- ✅ IDE autocomplete for all settings
- ✅ Supports multiple .env files (.env.development, .env.production)

**See**: `upsales/settings.py` for UpsalesSettings model

### Reusable Validators

**Location**: `upsales/validators.py`

Use pre-built validators for common field types:

```python
from upsales.validators import (
    BinaryFlag,       # Validates 0 or 1 (not bool!)
    EmailStr,         # Validates and normalizes email
    CustomFieldsList, # Validates Upsales custom fields structure
    NonEmptyStr,      # Validates and strips non-empty strings
    PositiveInt,      # Validates non-negative integers
)

class User(BaseModel):
    active: BinaryFlag = 1              # ✅ Validates 0 or 1
    email: EmailStr                      # ✅ Normalizes to lowercase
    custom: CustomFieldsList = []       # ✅ Validates fieldId presence
    name: NonEmptyStr                   # ✅ Strips whitespace
```

**Benefits**:
- DRY principle - define once, use everywhere
- Consistent validation across all models
- Better error messages

### Computed Fields

Use `@computed_field` for derived properties:

```python
from pydantic import computed_field
from upsales.models.custom_fields import CustomFields

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

**Benefits**:
- Automatic serialization
- Better IDE support
- Cleaner API

### Field Serializers

Use `@field_serializer` to customize API output:

```python
from pydantic import field_serializer

class User(BaseModel):
    custom: CustomFieldsList = []

    @field_serializer('custom', when_used='json')
    def serialize_custom_fields(self, custom: list[dict]) -> list[dict]:
        """Clean custom fields for API requests."""
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]
```

**Benefits**:
- Control over serialization
- Cleaner API payloads
- Better performance

### Field Aliases

Use `Field(alias="...")` when API field names differ from Python names:

```python
from pydantic import Field

class Contact(BaseModel):
    # API sends "client", Python uses "company"
    company: PartialCompany | None = Field(
        None,
        alias="client",
        description="Contact's company"
    )
```

**Important**: ConfigDict already has `populate_by_name=True`, so both names work for input.

### Frozen Fields and Serialization

Mark read-only fields with `Field(frozen=True, strict=True)`:

```python
from pydantic import Field

class User(BaseModel):
    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique user ID")
    regDate: str = Field(frozen=True, description="Registration date")

    # Updatable fields
    name: NonEmptyStr
    email: EmailStr
```

Use `to_api_dict()` for Pydantic v2 optimized serialization:

```python
async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
    """Edit this user."""
    if not self._client:
        raise RuntimeError("No client available")
    # to_api_dict() automatically excludes frozen fields and uses aliases
    return await self._client.users.update(
        self.id,
        **self.to_api_dict(**kwargs)
    )
```

**Benefits**:
- 5-50x faster serialization (Pydantic v2 Rust core)
- Automatic frozen field exclusion
- Automatic field alias handling
- Frozen fields protected in overrides

### Model Validators

Use `@model_validator` for cross-field validation:

```python
from pydantic import model_validator

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

### TypedDict for IDE Autocomplete

**ALWAYS** create a TypedDict for updatable fields:

```python
from typing import Unpack, TypedDict

class UserUpdateFields(TypedDict, total=False):
    """Available fields for updating a User."""
    name: str
    email: str
    administrator: int
    active: int

class User(BaseModel):
    # ... field definitions ...

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit with full IDE autocomplete!"""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_api_dict(**kwargs)
        )
```

**Benefits**:
- Full IDE autocomplete
- Type checking
- Self-documenting

### Complete Model Pattern

See `ai_temp_files/users_enhanced.py` for a complete reference implementation showing all patterns together.

## Development Commands

### Setup
```bash
# Install all dependencies including dev tools
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Testing
```bash
# Run all unit tests with coverage
uv run pytest tests/unit/

# Run specific test file
uv run pytest tests/unit/test_custom_fields.py

# Run single test
uv run pytest tests/unit/test_custom_fields.py::test_get_by_id

# With coverage report
uv run pytest --cov=upsales --cov-report=html

# Integration tests with VCR.py (requires .env configuration)
uv run pytest tests/integration/ -v  # First run records real API responses
# Subsequent runs replay from cassettes (no API calls, fast!)

# Re-record cassettes (delete old ones first)
rm -r tests/cassettes/integration/*
uv run pytest tests/integration/ -v
```

**VCR.py Integration Testing**:
- Records real API responses on first run
- Replays from cassettes on subsequent runs (offline, fast)
- Validates models work with actual API structure
- Automatically filters sensitive data (tokens, passwords)
- See `docs/patterns/vcr-testing.md` for complete guide

### Code Quality
```bash
# Format code (always run before commit)
uv run ruff format .

# Lint and auto-fix
uv run ruff check . --fix

# Type checking (strict mode)
uv run mypy upsales

# Check docstring coverage (must be 90%+)
uv run interrogate upsales

# Security check
uv run bandit -c pyproject.toml -r upsales

# Run all pre-commit checks
uv run pre-commit run --all-files
```

### Documentation
```bash
# Serve docs locally at http://127.0.0.1:8000
uv run mkdocs serve

# Build static docs
uv run mkdocs build
```

### CLI Tool
```bash
# Generate models from API (IMPLEMENTED)
uv run upsales generate-model roles
uv run upsales generate-model users --partial
uv run upsales generate-model products --output ai_temp_files/test.py

# Validate project structure (IMPLEMENTED)
uv run upsales validate

# Initialize new resource (IMPLEMENTED)
uv run upsales init-resource orders
```

**generate-model Features**:
- Fetches real data from Upsales API
- Auto-refreshes expired tokens (uses email/password from .env)
- Generates Python 3.13 syntax (native type hints)
- Creates TypedDict for IDE autocomplete automatically
- Optional `--partial` flag generates PartialModel
- Outputs to `upsales/models/{endpoint}.py`
- Marks TODOs for review (frozen fields, nested objects)

**validate Features**:
- Checks docstring coverage (interrogate)
- Verifies TypedDict completeness
- Validates field descriptions
- Checks resources registered in client
- Verifies model exports
- Confirms pydantic-settings configured

**init-resource Features**:
- Creates resource manager boilerplate
- Updates resource exports automatically
- Generates from BaseResource template
- Shows next steps for model generation
- Maintains project patterns and conventions

## Architecture

### Three-Layer Model System

The SDK uses a sophisticated model system to handle full vs. partial API responses:

1. **BaseModel** (`upsales/models/base.py`): Full objects with all fields guaranteed present. Used for direct endpoint responses like `GET /users/:id`. Must implement `async def edit(**kwargs)`.

2. **PartialModel** (`upsales/models/base.py`): Minimal objects for nested data in responses. Used when objects appear nested (e.g., `account.owner`). Must implement `async def fetch_full()` and `async def edit(**kwargs)`.

3. **CustomFields** (`upsales/models/custom_fields.py`): Helper providing dict-like access to Upsales custom fields by ID or alias.

**Critical Pattern**: Models hold optional `_client` reference for instance methods like `await user.edit(name="New")`.

### Resource Manager Pattern

**BaseResource** (`upsales/resources/base.py`) is a generic template using Python 3.13 type parameter syntax `[T: BaseModel, P: PartialModel]`.

Built-in CRUD operations:
- `create(**data)` - Create new resource (returns created object with ID)
- `get(id)` - Single resource
- `list(limit, offset, **params)` - Paginated list
- `list_all(**params)` - Auto-paginated (fetches all)
- `search(**filters)` - Search with comparison operators (eq, ne, gt, gte, lt, lte, in)
- `update(id, **data)` - Update resource
- `delete(id)` - Delete resource
- `bulk_update(ids, data, max_concurrent)` - Parallel updates with exception groups
- `bulk_delete(ids, max_concurrent)` - Parallel deletes

**Subclassing Pattern**: Inherit and add endpoint-specific methods:
```python
class UsersResource(BaseResource[User, PartialUser]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/users",
            model_class=User,
            partial_class=PartialUser,
        )

    # Add custom methods
    async def get_by_email(self, email: str) -> User | None:
        ...
```

### HTTP Client Layer

**HTTPClient** (`upsales/http.py`) handles:
- Authentication via `Cookie: token=...` header
- Pattern matching for HTTP status codes (200/201/400/401/403/404/429/500+)
- Automatic retry with exponential backoff on rate limits (429)
- Tenacity integration (5 retries, 1-60s backoff)
- Upsales API response wrapper parsing (`{"error": ..., "data": ...}`)

**Rate Limiting**: Upsales enforces 200 req/10 sec. Bulk operations use semaphores for concurrency control.

### Exception Hierarchy

All exceptions inherit from `UpsalesError` (`upsales/exceptions.py`):
- `RateLimitError` (429) - Auto-retried by HTTPClient
- `AuthenticationError` (401/403)
- `NotFoundError` (404)
- `ValidationError` (400)
- `ServerError` (500+)

Bulk operations use **ExceptionGroup** (Python 3.11+) to collect multiple failures.

## Python 3.13+ Syntax Requirements

### CRITICAL: Type Hints

**✅ ALWAYS use native types:**
```python
def get_users() -> list[dict[str, str | None]]:
    pass

user: User | None = None
data: dict[str, Any] = {}
```

**❌ NEVER import from typing:**
```python
# DO NOT DO THIS
from typing import List, Dict, Optional, Union
```

**Exception**: Only import `Any` and `TYPE_CHECKING` from typing when needed.

### Type Parameter Syntax (3.12+)

**✅ Use clean syntax:**
```python
class BaseResource[T: BaseModel, P: PartialModel]:
    def get(self, id: int) -> T:
        pass
```

**❌ Old generic syntax forbidden:**
```python
# DO NOT DO THIS
from typing import Generic, TypeVar
class BaseResource(Generic[T, P]):
    pass
```

### Pattern Matching

Use `match/case` for HTTP status codes and complex conditionals:
```python
match response.status_code:
    case 200 | 201:
        return success()
    case 404:
        raise NotFoundError()
    case code if code >= 500:
        raise ServerError(code)
    case _:
        response.raise_for_status()
```

### Exception Groups (3.11+)

For bulk operations, collect errors and raise as group:
```python
results = await asyncio.gather(*tasks, return_exceptions=True)
errors = [r for r in results if isinstance(r, Exception)]
if errors:
    raise ExceptionGroup(f"Failed {len(errors)}/{len(tasks)}", errors)
```

### Dictionary Merge (3.9+)

```python
all_params = defaults | params  # ✅ Use this
all_params = {**defaults, **params}  # ❌ Avoid
```

## Adding New Endpoints

Follow this three-step process (detailed in `docs/patterns/`):

### 1. Create Models

File: `upsales/models/{endpoint}.py`

```python
from typing import Unpack, TypedDict
from pydantic import Field
from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields

# TypedDict for IDE autocomplete and type checking
class UserUpdateFields(TypedDict, total=False):
    """Available fields for updating a User."""
    name: str
    email: str
    administrator: int
    active: int
    custom: list[dict]

class User(BaseModel):
    # Mark read-only fields with frozen=True
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Normal updatable fields
    name: str
    email: str
    administrator: int
    custom: list[dict] = []  # Always include

    @property
    def custom_fields(self) -> CustomFields:
        return CustomFields(self.custom)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit with full IDE autocomplete for available fields."""
        if not self._client:
            raise RuntimeError("No client available")
        # Use to_update_dict() to automatically exclude frozen fields
        return await self._upsales.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )

class PartialUser(PartialModel):
    id: int
    name: str

    async def fetch_full(self) -> User:
        if not self._client:
            raise RuntimeError("No client available")
        return await self._upsales.users.get(self.id)

    async def edit(self, **kwargs) -> User:
        if not self._client:
            raise RuntimeError("No client available")
        return await self._upsales.users.update(self.id, **kwargs)
```

### 2. Create Resource Manager

File: `upsales/resources/{endpoint}.py`

```python
from upsales.resources.base import BaseResource
from upsales.models.{endpoint} import {Model}, Partial{Model}

class {Model}sResource(BaseResource[{Model}, Partial{Model}]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/{api_endpoint}",  # Use actual API endpoint
            model_class={Model},
            partial_class=Partial{Model},
        )

    # Add endpoint-specific methods here
```

**Example** (Companies endpoint):
```python
class CompaniesResource(BaseResource[Company, PartialCompany]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/accounts",  # API endpoint (not /companies!)
            model_class=Company,
            partial_class=PartialCompany,
        )
```

### 3. Register in Client

File: `upsales/client.py`

```python
from upsales.resources.{endpoint} import {Model}sResource

class Upsales:
    def __init__(self, token: str, ...):
        self.http = HTTPClient(token, ...)
        self.{endpoint} = {Model}sResource(self.http)
```

## Upsales API Details

### Authentication
- **Primary Method**: API token passed as `Cookie: token=YOUR_TOKEN`
- **Fallback Method**: Username/password via `/session/` endpoint for automatic token refresh
- Base URL: `https://power.upsales.com/api/v2`

#### Token Refresh (Sandbox Environments)

For sandboxes that reset daily, enable automatic token refresh:

```python
# From .env file
async with Upsales.from_env() as upsales:
    # Automatically refreshes token if expired
    user = await upsales.users.get(1)
```

**Environment Variables**:
- `UPSALES_TOKEN` - API token (required)
- `UPSALES_ENABLE_FALLBACK_AUTH=true` - Enable auto-refresh
- `UPSALES_EMAIL` - Email for fallback auth
- `UPSALES_PASSWORD` - Password for fallback auth

**How it works**:
1. Request fails with 401/403 (token expired)
2. POST to `/session/` with email/password
3. Get new token from response
4. Retry original request with new token
5. Only attempted once per request (prevents infinite loops)

See `docs/authentication.md` and `upsales/auth.py` for details.

### Response Format
```json
{
    "error": null,
    "metadata": {"total": 10, "limit": 100, "offset": 0},  // Lists only
    "data": {...}  // or [...]
}
```

### Rate Limiting
- Limit: 200 requests per 10 seconds per API key
- Error: HTTP 429
- Handling: Automatic retry with exponential backoff (HTTPClient)

### Custom Fields
API format:
```json
{
    "custom": [
        {
            "fieldId": 11,
            "value": "string_value",
            "valueInteger": 123,
            "valueDate": "2020-01-01",
            "valueArray": ["value"]
        }
    ]
}
```

Field schemas available at: `/api/v2/customFields/{object_type}`
```json
{
    "data": [
        {
            "id": 11,
            "name": "Field Name",
            "alias": "FIELD_ALIAS",  // Use for readable access
            "datatype": "String"
        }
    ]
}
```

## Quality Standards

### Docstring Requirements
- **90% minimum coverage** (enforced by interrogate)
- All public classes, methods, functions, properties must have docstrings
- Include Google-style Args, Returns, Raises, Example sections
- Examples must be executable doctest-style

### Type Checking
- **mypy strict mode** must pass
- All functions require type hints
- Use native types only (`list`, `dict`, `str | None`)

### Code Style
- Line length: 100 characters
- Ruff for formatting and linting
- No typing imports except `Any` and `TYPE_CHECKING`

### Testing
- All new features require unit tests
- Use pytest-asyncio for async tests
- Mock HTTP calls with pytest-httpx
- Integration tests use VCR.py for cassettes

## Free-Threaded Mode

Python 3.13 supports running without GIL for true parallelism:

```bash
python -X gil=0 your_script.py
```

**Benefits for this SDK**:
- Bulk operations (`bulk_update`, `bulk_delete`) run in true parallel
- I/O-bound HTTP requests don't block each other
- Can maximize throughput within 200 req/10s rate limit

**Document this** in bulk operation docstrings with note like:
```python
"""
Note:
    With Python 3.13 free-threaded mode, these requests can truly
    run in parallel without GIL contention. Enable with:
    python -X gil=0 script.py
"""
```

## File Locations Reference

**Core Implementation**:
- `upsales/client.py` - Main Upsales
- `upsales/http.py` - HTTP client with retry logic
- `upsales/exceptions.py` - Exception hierarchy
- `upsales/cli.py` - CLI tool (skeleton)

**Templates** (replicate these patterns):
- `upsales/models/base.py` - BaseModel & PartialModel
- `upsales/models/custom_fields.py` - CustomFields helper
- `upsales/resources/base.py` - BaseResource with generics

**Placeholders** (TODO: implement):
- `upsales/models/{account,product,user}.py` - Model definitions
- `upsales/resources/{accounts,products,users}.py` - Resource managers

**Documentation**:
- `docs/patterns/creating-models.md` - Model creation guide
- `docs/patterns/adding-resources.md` - Resource manager guide
- `docs/patterns/custom-fields.md` - Custom fields usage
- `CONTRIBUTING.md` - Full contributing guidelines with ✅/❌ examples

## Handling Read-Only and Updatable Fields

Different CRUD operations have different field requirements:
- **GET**: Returns all fields including `id`, timestamps
- **PUT/PATCH**: `id` in URL path, timestamps read-only, some fields updatable

### Solution: Pydantic Field Metadata

Mark read-only fields with `Field(frozen=True)`:

```python
from pydantic import Field

class User(BaseModel):
    # Read-only - never sent in updates
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Updatable
    name: str
    email: str
```

### Using to_api_dict() (Recommended)

BaseModel provides `to_api_dict()` with Pydantic v2 optimized serialization (5-50x faster):

```python
user = await upsales.users.get(1)
user.name = "Jane"

# Use to_api_dict() for Pydantic v2 optimized serialization
api_data = user.to_api_dict()
# Automatically excludes: id (frozen), uses field aliases, 5-50x faster

# Or with overrides
api_data = user.to_api_dict(active=0)

# Use in edit()
await user.edit(name="Jane")  # Uses to_api_dict() internally
```

### Using to_update_dict() (Legacy)

BaseModel also provides `to_update_dict()` for backward compatibility:

```python
user = await upsales.users.get(1)
user.name = "Jane"

# Only sends updatable fields (name, email, etc.)
# Excludes: id, created_at, updated_at
update_data = user.to_update_dict()

# Or with overrides
update_data = user.to_update_dict(active=0)

# Use in edit()
await user.edit(name="Jane")  # Automatically excludes frozen fields
```

**Pattern in models**:
```python
async def edit(self, **kwargs) -> "User":
    if not self._client:
        raise RuntimeError("No client available")
    return await self._upsales.users.update(
        self.id,
        **self.to_update_dict(**kwargs)  # Excludes frozen fields
    )
```

See `docs/patterns/field-types.md` for complete guide including alternative approaches.

## IDE Autocomplete for Updates

Use **TypedDict with Unpack** for full IDE autocomplete in `.edit()` methods:

```python
from typing import Unpack, TypedDict

# Define updatable fields for IDE autocomplete
class UserUpdateFields(TypedDict, total=False):
    """All fields are optional (total=False)."""
    name: str
    email: str
    administrator: int

class User(BaseModel):
    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """IDE provides autocomplete for name, email, administrator."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._upsales.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
```

**IDE Experience**:
```python
user = await upsales.users.get(1)

# When typing: await user.edit(
# IDE suggests: name, email, administrator with correct types
await user.edit(
    name="Jane",        # ✅ IDE autocompletes
    email="jane@..."    # ✅ Type checked
)
```

**Benefits**:
- Full IDE autocomplete for all updatable fields
- Type checking with mypy/pyright
- Self-documenting (TypedDict shows available fields)
- Still flexible (any subset of fields can be passed)

See `docs/patterns/type-safe-updates.md` for complete guide including alternatives.

## Common Pitfalls

### General
1. **Don't create temp files in wrong locations**: ALL temporary files (test scripts, analysis docs, debug outputs) must go in `ai_temp_files\`. Delete temp scripts after use.
2. **Don't import from typing**: Use `list`, `dict`, `str | None` directly (except `Unpack`, `TypedDict`, `TYPE_CHECKING`)
3. **Don't use old generic syntax**: Use `class Foo[T, P]:` not `Generic[T, P]`
4. **Don't skip docstrings**: 90% coverage required, will fail CI

### Naming & Terminology
5. **Don't use API naming in user code**: Use `Company` (not `Account`), `upsales.companies` (not `client.accounts`)
6. **Don't forget field aliases**: When API field name differs (e.g., `"client"`), use `Field(alias="client")`
7. **Don't use camelCase for file names**: Always use `snake_case` for model and resource files. See [Naming Conventions](#naming-conventions) for complete rules.
8. **Don't use wrong capitalization in class names**: Use proper `PascalCase`: `ApiKey` (not `Apikey`), `ProjectPlanStage` (not `Projectplanstage`)

### Pydantic v2 Models
9. **Don't use custom validators**: Use reusable validators from `upsales/validators.py` (`BinaryFlag`, `EmailStr`, `CustomFieldsList`, etc.)
10. **Don't forget to use to_api_dict()**: Prefer `to_api_dict()` over `to_update_dict()` for 5-50x faster serialization
11. **Don't forget custom fields validator**: Always use `custom: CustomFieldsList = []` (not `list[dict]`)
12. **Don't forget to mark read-only fields**: Use `Field(frozen=True, strict=True)` for `id`, timestamps, etc.
13. **Don't forget @computed_field**: Add `@computed_field` for `custom_fields` property and boolean helpers like `is_admin`
14. **Don't forget TypedDict for edit()**: Define `{Model}UpdateFields(TypedDict, total=False)` with ALL updatable fields for complete IDE autocomplete
15. **Don't use `self.model_fields`**: Access from class: `self.__class__.model_fields` (Pydantic v2.11+ deprecation)
16. **Don't forget @field_serializer**: Add for custom fields to clean data before API requests
17. **Don't forget field descriptions**: Add `description=` to all fields for documentation

### Configuration (pydantic-settings)
18. **Don't use manual .env loading**: Use `Upsales.from_env()` which uses pydantic-settings for type-safe configuration
19. **Don't forget to reuse validators in settings**: Settings use the same validators as models (e.g., `EmailStr`)

### Architecture
20. **Don't forget _client reference**: Models need optional `_client` for instance methods
21. **Don't forget exception groups**: Bulk operations must use `ExceptionGroup` for errors
22. **Don't forget pattern matching**: Use for HTTP status codes and complex conditionals
23. **Don't forget `from __future__ import annotations`**: Required in files using type parameter syntax with subscripting (e.g., `BaseResource[T, P]`)
