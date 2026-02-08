# Contributing Guide

Thank you for contributing to the Upsales Python SDK! This guide will help you understand the project structure and patterns.

## Python 3.13+ Requirements

This project **requires Python 3.13+** and leverages modern Python features throughout.

### ✅ DO Use These Python 3.13 Features:

#### 1. Native Type Hints (3.9+)
```python
# ✅ Good - No typing imports needed
def get_users() -> list[dict[str, str | None]]:
    pass

user: User | None = None
data: dict[str, Any] = {}
items: list[int] = []
```

```python
# ❌ Bad - Outdated syntax
from typing import List, Dict, Optional, Union

def get_users() -> List[Dict[str, Optional[str]]]:
    pass

user: Optional[User] = None
```

#### 2. Type Parameter Syntax (3.12+)
```python
# ✅ Good - Clean generic syntax
class BaseResource[T: BaseModel, P: PartialModel]:
    def get(self, id: int) -> T:
        pass
```

```python
# ❌ Bad - Old generic syntax
from typing import Generic, TypeVar

T = TypeVar('T', bound=BaseModel)
P = TypeVar('P', bound=PartialModel)

class BaseResource(Generic[T, P]):
    pass
```

#### 3. Pattern Matching (3.10+)
```python
# ✅ Good - Clean and readable
match response.status_code:
    case 200 | 201:
        return parse_success(response)
    case 404:
        raise NotFoundError()
    case 429:
        raise RateLimitError()
    case code if code >= 500:
        raise ServerError(code)
    case _:
        response.raise_for_status()
```

```python
# ❌ Bad - Nested conditionals
if response.status_code in (200, 201):
    return parse_success(response)
elif response.status_code == 404:
    raise NotFoundError()
# ... etc
```

#### 4. Exception Groups (3.11+)
```python
# ✅ Good - For bulk operations
results = await asyncio.gather(*tasks, return_exceptions=True)
errors = [r for r in results if isinstance(r, Exception)]
if errors:
    raise ExceptionGroup("Bulk update failed", errors)
```

#### 5. Dictionary Merge Operator (3.9+)
```python
# ✅ Good - Clean merging
defaults = {"limit": 100}
params = {"offset": 0}
all_params = defaults | params
```

```python
# ❌ Bad - Verbose
all_params = {**defaults, **params}
```

#### 6. F-String Debugging (3.12+)
```python
# ✅ Good - Easy debugging
print(f"{user.name = }, {user.id = }")
# Output: user.name = 'John', user.id = 1
```

#### 7. Asyncio Concurrency
```python
# ✅ Good - Accurate about asyncio benefits
"""
Uses asyncio for efficient concurrent execution. The bottleneck
for bulk operations is typically network I/O and API rate limits,
not the GIL.

Free-threaded mode (python -X gil=0) benefits CPU-bound callbacks
or hybrid workloads, but provides limited gains for pure I/O.
"""
```

### ❌ DON'T Use These Outdated Patterns:

```python
# ❌ Don't import from typing unless absolutely necessary
from typing import List, Dict, Optional, Union, Tuple

# ❌ Don't use old generic syntax
from typing import Generic, TypeVar

# ❌ Don't use complex nested if/elif chains
# Use pattern matching instead
```

## Adding New API Endpoints

### Step 1: Generate Models

**Recommended: Use the CLI to generate from real API data**

```bash
# Generate model (analyzes up to 2000 objects for accuracy!)
uv run upsales generate-model users --partial

# Generate without partial model
uv run upsales generate-model roles

# Custom output path
uv run upsales generate-model products --output custom/path.py
```

**The CLI will:**
- Fetch up to 2000 objects from the API
- Analyze field presence and null values
- Generate accurate required vs optional fields
- Create TypedDict for IDE autocomplete
- Mark nested objects for PartialModel creation
- Include analysis comments showing why fields are optional

**Example output comments:**
```python
# Required - never null
email: str  # Present in 100% (1847/1847)

# Optional - null in some
userTitle: str | None = None  # Present in 100% (1847/1847), null in 325
```

Or create manually following this pattern:

```python
# upsales/models/user.py
"""
User models for Upsales API.

Uses Python 3.13 native type hints throughout.
"""

from typing import Unpack, TypedDict
from pydantic import Field
from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields


# TypedDict for IDE autocomplete in edit()
class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    Only includes updatable fields (excludes frozen fields like id).
    All fields are optional (total=False).
    """
    name: str
    email: str
    administrator: int
    active: int
    custom: list[dict]


class User(BaseModel):
    """
    Full User model from Upsales API.

    Attributes:
        id: Unique user identifier (read-only).
        created_at: Creation timestamp (read-only).
        updated_at: Last update timestamp (read-only).
        name: User's full name.
        email: User's email address.
        administrator: Whether user is admin (0 or 1).
        active: Active status (0 or 1).
        role: User's role (partial object).
        custom: Custom fields for this user.

    Example:
        >>> user = User(
        ...     id=1,
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     administrator=0,
        ... )
        >>> print(f"{user.name = }")
    """

    # Read-only fields - marked with frozen=True
    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)

    # Updatable fields
    name: str
    email: str
    administrator: int
    active: int = 1
    role: PartialRole | None = None
    custom: list[dict] = []

    @property
    def custom_fields(self) -> CustomFields:
        """Get custom fields helper."""
        return CustomFields(self.custom)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """
        Edit this user with type-safe autocomplete.

        IDE provides autocomplete for: name, email, administrator, active, custom.
        IDE does NOT suggest read-only fields: id, created_at, updated_at.

        Args:
            **kwargs: Fields to update. See UserUpdateFields for options.

        Returns:
            Updated user.

        Example:
            >>> user = await upsales.users.get(1)
            >>> updated = await user.edit(name="Jane", administrator=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(
            self.id,
            **self.to_api_dict(**kwargs)
        )


class PartialUser(PartialModel):
    """
    Partial User model (nested in responses).

    Only guaranteed fields are present.

    Example:
        >>> partial = PartialUser(id=1, name="John")
        >>> full = await partial.fetch_full()
    """

    id: int
    name: str
    email: str | None = None

    async def fetch_full(self) -> User:
        """Fetch full user data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.get(self.id)

    async def edit(self, **kwargs) -> User:
        """Edit this user."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(self.id, **kwargs)
```

### Step 2: Create Resource Manager

```python
# upsales/resources/users.py
"""
Users resource manager for Upsales API.

Uses Python 3.13 type parameter syntax.
"""

from upsales.http import HTTPClient
from upsales.models.user import User, PartialUser
from upsales.resources.base import BaseResource


class UsersResource(BaseResource[User, PartialUser]):
    """
    Resource manager for /users endpoint.

    Inherits CRUD operations from BaseResource.
    Add endpoint-specific methods here.

    Example:
        >>> users = client.users
        >>> user = await users.get(1)
        >>> all_admins = await users.get_administrators()
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize users resource."""
        super().__init__(
            http=http,
            endpoint="/users",
            model_class=User,
            partial_class=PartialUser,
        )

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: Email address to search for.

        Returns:
            User if found, None otherwise.

        Example:
            >>> user = await upsales.users.get_by_email("john@example.com")
        """
        response = await self._http.get(self._endpoint, email=email)
        results = response["data"]
        return (
            self._model_class(**results[0], _client=self._http._client)
            if results
            else None
        )

    async def get_administrators(self) -> list[User]:
        """
        Get all administrator users.

        Returns:
            List of admin users.

        Example:
            >>> admins = await upsales.users.get_administrators()
        """
        return await self.list_all(administrator=1)
```

### Step 3: Update Client

```python
# upsales/client.py

from upsales.resources.users import UsersResource

class Upsales:
    def __init__(self, token: str, ...):
        self.http = HTTPClient(token, ...)

        # Add new resource
        self.users = UsersResource(self.http)
```

### Step 4: Validation Checklist

Before submitting, ensure:

- [ ] Uses Python 3.13 type parameter syntax `[T, P]`
- [ ] No imports from `typing` for `List`, `Dict`, `Optional`, `Union` (except `Unpack`, `TypedDict`, `TYPE_CHECKING`)
- [ ] All type hints use native syntax (`list`, `dict`, `|`)
- [ ] Read-only fields marked with `Field(frozen=True)`
- [ ] TypedDict created for `edit()` method with only updatable fields
- [ ] `edit()` uses `Unpack[{Model}UpdateFields]` for IDE autocomplete
- [ ] `edit()` calls `to_update_dict(**kwargs)` to exclude frozen fields
- [ ] Pattern matching used where appropriate
- [ ] Exception groups for bulk operations
- [ ] Comprehensive docstrings (90%+ coverage)
- [ ] Examples in docstrings
- [ ] Accurate notes about asyncio concurrency (avoid overstating free-threaded benefits)
- [ ] All tests passing

### Step 5: Run Validation

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check . --fix

# Type check
uv run mypy upsales

# Check docstrings
uv run interrogate upsales

# Run tests
uv run pytest

# Or use pre-commit
uv run pre-commit run --all-files
```

## Development Setup

### Prerequisites

- Python 3.13+
- uv package manager

### Installation

```bash
# Clone repository
git clone https://github.com/AxelOhlander/upsales-python-sdk.git
cd upsales-python-sdk

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

# Watch mode
uv run pytest-watch
```

### Building Documentation

```bash
# Serve locally
uv run mkdocs serve

# Build
uv run mkdocs build
```

## Free-Threaded Mode

Python 3.13 supports running without the GIL:

```bash
python -X gil=0 your_script.py
```

**When it helps**: CPU-bound callbacks, thread pools, or hybrid workloads mixing threads with asyncio.

**Limited benefit for pure async I/O**: For HTTP requests like this SDK's bulk operations, asyncio already provides efficient concurrency. The bottleneck is network I/O and API rate limits, not the GIL.

```python
# Bulk operations are efficient with or without free-threaded mode
products = await upsales.products.bulk_update(
    ids=list(range(1, 101)),
    data={"active": 0},
    max_concurrent=50,
)
```

## Code Style

- Line length: 100 characters
- Use ruff for formatting and linting
- Use mypy in strict mode
- Minimum 90% docstring coverage
- All public APIs must have examples in docstrings

## Questions?

Open an issue or start a discussion!
