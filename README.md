# Upsales Python SDK

Modern, async Python wrapper for the Upsales CRM API, built for **Python 3.13+** with free-threaded mode support.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Why This SDK?

- ✅ **Python 3.13+** - Leverages free-threaded mode for true parallelism
- ✅ **Modern Syntax** - Native type hints, type parameters, pattern matching
- ✅ **Async-First** - Built on httpx for high-performance async operations
- ✅ **Type-Safe** - Full type coverage with Pydantic v2
- ✅ **Production-Ready** - Auto-retry, rate limiting, comprehensive error handling
- ✅ **Template-Driven** - Easy to extend with new endpoints
- ✅ **Well-Documented** - 90%+ docstring coverage with examples

## Quick Start

### Installation

```bash
pip install upsales
# or
uv pip install upsales
```

### Basic Usage

```python
import asyncio
from upsales import Upsales

async def main():
    # From environment variables (.env file)
    async with Upsales.from_env() as upsales:
        # Get a user
        user = await upsales.users.get(1)
        print(f"User: {user.name} ({user.email})")

        # List users with pagination
        users = await upsales.users.list(limit=50, offset=0)
        print(f"Found {len(users)} users")

        # Update a user
        updated = await user.edit(name="New Name")

        # Bulk operations (leverages Python 3.13 free-threaded mode)
        products = await upsales.products.bulk_update(
            ids=list(range(1, 101)),
            data={"active": 0}
        )

asyncio.run(main())
```

### Authentication with Auto-Refresh (Sandbox)

For sandbox environments that reset daily:

```bash
# .env
UPSALES_TOKEN=your_token
UPSALES_ENABLE_FALLBACK_AUTH=true
UPSALES_EMAIL=user@email.com
UPSALES_PASSWORD=password
```

```python
# Automatically refreshes token when it expires!
async with Upsales.from_env() as upsales:
    user = await upsales.users.get(1)
```

See [Authentication Guide](docs/authentication.md) for details.

## Python 3.13 Features

This SDK is designed for **Python 3.13+** and leverages modern features:

### 1. Native Type Hints (No typing imports!)

```python
# ✅ Clean and modern
def get_users() -> list[dict[str, str | None]]:
    pass

user: User | None = None
```

### 2. Type Parameter Syntax

```python
# ✅ Clean generics
class BaseResource[T, P]:
    async def get(self, id: int) -> T:
        pass
```

### 3. Pattern Matching

```python
# ✅ Readable error handling
match response.status_code:
    case 200 | 201:
        return parse_success(response)
    case 404:
        raise NotFoundError()
```

### 4. Free-Threaded Mode (The Big One!)

```bash
# Enable true parallelism without GIL
python -X gil=0 your_script.py
```

With free-threaded mode, bulk operations run in **true parallel**:

```python
# These 100 updates run in TRUE parallel (no GIL!)
# Maximizes throughput within the 200 req/10s rate limit
products = await upsales.products.bulk_update(
    ids=list(range(1, 101)),
    data={"active": 0},
    max_concurrent=50  # True parallelism!
)
```

## Features

### Type-Safe Updates with IDE Autocomplete

Uses TypedDict for full IDE autocomplete when editing objects:

```python
user = await upsales.users.get(1)

# IDE suggests: name, email, administrator, active
# IDE does NOT suggest read-only fields: id, created_at
await user.edit(
    name="Jane",           # ✅ Autocomplete
    email="jane@..."       # ✅ Type checked
)
```

### Automatic Rate Limiting

Respects Upsales API limits (200 req/10s) with exponential backoff:

```python
# Automatically retries on rate limits
user = await upsales.users.get(1)  # Retries up to 5 times if needed
```

### Bulk Operations

Efficient bulk updates with concurrency control:

```python
# Update 1000 products efficiently
products = await upsales.products.bulk_update(
    ids=list(range(1, 1001)),
    data={"active": 0},
    max_concurrent=50
)

# Handle errors with exception groups
try:
    results = await upsales.products.bulk_update(ids, data)
except ExceptionGroup as eg:
    print(f"Failed: {len(eg.exceptions)}")
```

### Custom Fields Support

Dict-like access to custom fields:

```python
user = await upsales.users.get(1)

# Access by field ID
value = user.custom_fields[11]

# Access by alias (with schema)
value = user.custom_fields["MY_FIELD"]

# Update custom fields
user.custom_fields[11] = "new value"
await user.edit(custom=user.custom_fields.to_api_format())
```

### Error Handling

Comprehensive exception hierarchy:

```python
from upsales.exceptions import (
    NotFoundError,
    RateLimitError,
    AuthenticationError,
    UpsalesError,
)

try:
    user = await upsales.users.get(999)
except NotFoundError:
    print("User not found")
except RateLimitError:
    print("Rate limit exceeded")
except UpsalesError as e:
    print(f"API error: {e}")
```

## Terminology

**Note**: This SDK uses **user-friendly naming** that matches the Upsales UI:
- **`Upsales`** (not "UpsalesClient") - Simple SDK class name. No collision with data models.
- **`Company`** (not "Account") - Matches UI terminology, even though API uses `/accounts`
- When API returns `"client"` in nested responses, we map to `company` in Python

```python
# Clean separation between SDK and data
upsales = Upsales(token="...")
company = await upsales.companies.get(1)
contact.company  # No naming collision!
```

See [Terminology Guide](docs/terminology.md) for complete details.

## Project Structure

This SDK is designed to be **template-driven** - easy for developers (and Claude!) to extend:

```
upsales/
├── client.py              # Main Upsales
├── http.py                # HTTP layer with retry logic
├── exceptions.py          # Exception hierarchy
├── auth.py                # Authentication with token refresh
├── cli.py                 # CLI tool for code generation
├── models/
│   ├── base.py           # BaseModel & PartialModel (TEMPLATE)
│   ├── custom_fields.py  # CustomFields helper
│   └── *.py              # Model definitions (Company, User, Product, etc.)
└── resources/
    ├── base.py           # BaseResource (TEMPLATE)
    └── *.py              # Resource managers (CompaniesResource, etc.)
```

## Adding New Endpoints

### Step 1: Create Models

```python
# upsales/models/user.py
from typing import Unpack, TypedDict
from pydantic import Field
from upsales.models.base import BaseModel, PartialModel

# TypedDict for IDE autocomplete
class UserUpdateFields(TypedDict, total=False):
    name: str
    email: str
    administrator: int

class User(BaseModel):
    # Read-only fields
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)

    # Updatable fields
    name: str
    email: str
    administrator: int

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit with IDE autocomplete."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )

class PartialUser(PartialModel):
    id: int
    name: str
```

### Step 2: Create Resource Manager

```python
# upsales/resources/companies.py
from upsales.resources.base import BaseResource

class CompaniesResource(BaseResource[Company, PartialCompany]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/accounts",  # API endpoint (not /companies!)
            model_class=Company,
            partial_class=PartialCompany,
        )
```

**Note**: Use UI-friendly naming (`Company`) even when API uses different endpoint (`/accounts`).

### Step 3: Add to Client

```python
# upsales/client.py
class Upsales:
    def __init__(self, token: str, ...):
        self.companies = CompaniesResource(self.http)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed patterns.

## CLI Tool

Generate models from API responses automatically:

```bash
# Generate model (main only)
upsales generate-model roles

# Generate with partial model
upsales generate-model users --partial

# Custom output path
upsales generate-model products --output custom/path.py

# Validate code
upsales validate

# Initialize new resource
upsales init-resource orders
```

The `generate-model` command:
- Fetches real data from your Upsales API
- Generates Python 3.13 syntax (native type hints)
- Creates TypedDict for IDE autocomplete
- Auto-refreshes expired tokens
- Marks TODOs for manual review

## Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and basic usage
- **[Patterns](docs/patterns/)** - Templates for adding endpoints
  - [Creating Models](docs/patterns/creating-models.md)
  - [Adding Resources](docs/patterns/adding-resources.md)
- **[API Reference](docs/api-reference/)** - Full API documentation
- **[Examples](examples/)** - Code examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Development

### Prerequisites

- Python 3.13+
- uv package manager

### Setup

```bash
# Clone repository
git clone <repo-url>
cd upsales-python

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=upsales

# Type checking
uv run mypy upsales

# Linting
uv run ruff check .
```

### Building Documentation

```bash
# Serve locally
uv run mkdocs serve

# Build
uv run mkdocs build
```

## Requirements

- Python 3.13+ (required for modern syntax)
- httpx >= 0.27.0
- pydantic >= 2.0.0
- tenacity >= 8.0.0

## Project Goals

1. **Production-ready library** for Upsales integration
2. **Template-driven design** for easy extension
3. **Claude skill** - Well-documented for AI-assisted development
4. **CLI tool** - Automated model generation

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/yourusername/upsales-python/issues)
- [Documentation](https://yourdomain.com/upsales-python)

## Credits

Built with modern Python features:
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [tenacity](https://tenacity.readthedocs.io/) - Retry logic
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Ruff](https://github.com/astral-sh/ruff) - Linting and formatting
