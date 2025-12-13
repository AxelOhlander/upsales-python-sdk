# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an async Python wrapper for the Upsales CRM API, designed as both a production-ready library and a template-driven system for AI-assisted development. The project **requires Python 3.13+** and leverages modern language features exclusively.

## API Endpoints Reference File

**CRITICAL**: `api_endpoints_with_fields.json` documents **all 167 Upsales API endpoints** with field information for GET/POST/PUT/DELETE operations.

### Quick Queries

| Purpose | Command |
|---------|---------|
| Required fields (POST) | `jq '.endpoints.orders.methods.POST.required' api_endpoints_with_fields.json` |
| Updatable fields (PUT) | `jq '.endpoints.contacts.methods.PUT.allowed' api_endpoints_with_fields.json` |
| Read-only fields | `jq '.endpoints.accounts.methods.PUT.readOnly' api_endpoints_with_fields.json` |
| Returned fields (GET) | `jq '.endpoints.activities.methods.GET_list.returns' api_endpoints_with_fields.json` |
| All endpoint names | `jq '.endpoints \| keys' api_endpoints_with_fields.json` |

### Development Workflow

1. **Consult API file**: `jq '.endpoints.endpoint_name' api_endpoints_with_fields.json`
2. **Generate model**: `uv run upsales generate-model endpoint_name --partial`
3. **Verify with VCR**: `uv run pytest tests/integration/test_endpoint_integration.py -v`
4. **Compare**: `uv run python ai_temp_files/find_unmapped_fields.py`
5. **Document**: Update `docs/endpoint-map.md` with verified info

### ⚠️ Important Caveat

**Use as starting point, not final authority.** Field info may be incomplete, incorrect, or outdated. Always validate with VCR cassettes and real API testing before trusting required/optional designations.

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

**Nested Field Mapping**: API field `"client"` → Python `company` using Pydantic `Field(alias="client")`. See [Field Aliases](#field-aliases) in Pydantic v2 Patterns for implementation details.

See `docs/terminology.md` for complete rationale.

## Naming Conventions

**CRITICAL**: This project follows strict PEP 8 naming conventions.

### Quick Reference

| Element | Convention | Example | Wrong |
|---------|-----------|---------|-------|
| **Model/Resource file** | snake_case, plural | `order_stages.py` | `orderStages.py`, `order_stage.py` |
| **Model class** | PascalCase, singular | `OrderStage` | `Orderstage`, `OrderStages` |
| **Partial class** | Partial + PascalCase | `PartialOrderStage` | `PartialOrderstage` |
| **Resource class** | PascalCase plural + Resource | `OrderStagesResource` | `OrderStageResource` |
| **Client attribute** | snake_case, plural | `upsales.order_stages` | `upsales.orderStages` |
| **TypedDict** | PascalCase + Fields | `OrderStageUpdateFields` | `orderStageUpdateFields` |

### Conversion Rules

**API endpoint → File → Class:**
```
/orderStages      → order_stages.py  → OrderStage
/projectPlanStages → project_plan_stages.py → ProjectPlanStage
/apiKeys          → api_keys.py      → ApiKey
```

**Acronyms**: Treat as words - `ApiKey` not `APIKey`, `HttpClient` not `HTTPClient`
(Exception: `URL`, `ID` alone are acceptable)

### Standardization Script

Fix legacy naming issues with `python scripts/standardize_naming.py --dry-run` (preview) or `--execute` (apply).

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
# Run all unit tests (default: parallel)
uv run pytest -n auto tests/unit/

# Run specific test file
uv run pytest -n auto tests/unit/test_custom_fields.py

# Run single test
uv run pytest -n auto tests/unit/test_custom_fields.py::test_get_by_id

# With coverage report
uv run pytest -n auto --cov=upsales --cov-report=html

# Integration tests with VCR.py (requires .env configuration)
uv run pytest -n 0 tests/integration/ -v  # First run records real API responses
# Subsequent runs replay from cassettes (no API calls, fast!)

# Re-record cassettes (delete old ones first)
rm -r tests/cassettes/integration/*
uv run pytest -n 0 tests/integration/ -v
```

**VCR.py Integration Testing**:
- Records real API responses on first run
- Replays from cassettes on subsequent runs (offline, fast)
- Validates models work with actual API structure
- Automatically filters sensitive data (tokens, passwords)
- See `docs/patterns/vcr-testing.md` for complete guide

**Pytest-xdist**:
- Default test command uses `-n auto` for parallel execution (requires `pytest-xdist` installed).
- Use `-n 0` for VCR cassette recording to avoid concurrent writes to `tests/cassettes/`.

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
- Automatic retry with exponential backoff on rate limits (429) - see [Rate Limiting](#rate-limiting)
- Tenacity integration (5 retries, 1-60s backoff)
- Upsales API response wrapper parsing (`{"error": ..., "data": ...}`)

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
