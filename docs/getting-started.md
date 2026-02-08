# Getting Started

This guide will help you get up and running with the Upsales Python SDK.

## Prerequisites

- **Python 3.13+** (required for modern syntax features)
- Upsales CRM account
- API token from Upsales

## Installation

### Using pip

```bash
pip install upsales
```

### Using uv (recommended)

```bash
uv pip install upsales
```

### From source

```bash
git clone https://github.com/AxelOhlander/upsales-python-sdk.git
cd upsales-python-sdk
uv sync
```

## Getting Your API Token

1. Log in to your Upsales account
2. Navigate to Settings → Integrations → API
3. Generate a new API token
4. Store it securely (use environment variables)

## Basic Usage

### Async Context Manager (Recommended)

```python
import asyncio
from upsales import Upsales

async def main():
    async with Upsales(token="YOUR_TOKEN") as upsales:
        # Client automatically handles cleanup
        user = await upsales.users.get(1)
        print(user.name)

asyncio.run(main())
```

### Manual Cleanup

```python
async def main():
    upsales = Upsales(token="YOUR_TOKEN")
    await upsales.__aenter__()

    try:
        user = await upsales.users.get(1)
        print(user.name)
    finally:
        await upsales.close()

asyncio.run(main())
```

### Using Environment Variables

```python
import os
from upsales import Upsales

async def main():
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN not set")

    async with Upsales(token=token) as upsales:
        users = await upsales.users.list(limit=10)
        for user in users:
            print(f"{user.id}: {user.name}")
```

## Common Operations

### Creating Resources

```python
# Create a new user
user = await upsales.users.create(
    name="John Doe",
    email="john@example.com",
    active=1,
    administrator=0
)
print(f"Created user {user.id}")

# Create a company
company = await upsales.companies.create(
    name="ACME Corporation",
    phone="+1-555-0123",
    active=1
)

# Create a product
product = await upsales.products.create(
    name="Premium Plan",
    listPrice=9999,
    active=1
)
```

### Getting a Single Resource

```python
# Get by ID
user = await upsales.users.get(1)
company = await upsales.companies.get(123)
product = await upsales.products.get(456)
```

### Listing Resources

```python
# With default pagination
users = await upsales.users.list()  # limit=100, offset=0

# Custom pagination
users = await upsales.users.list(limit=50, offset=100)

# Get all (handles pagination automatically)
all_users = await upsales.users.list_all()
```

### Searching Resources

```python
# Simple equality
active_users = await upsales.users.search(active=1)

# With comparison operators
recent_users = await upsales.users.search(
    active=1,
    regDate="gte:2024-01-01"  # Registered after Jan 1, 2024
)

# Multiple values (IN operator)
users = await upsales.users.search(
    role_id="eq:1,2,3"  # Role ID in (1, 2, 3)
)

# Range queries
products = await upsales.products.search(
    active=1,
    listPrice="gt:100",   # Price > 100
    listPrice="lt:1000"   # Price < 1000
)

# Custom fields
companies = await upsales.companies.search(
    active=1,
    custom="eq:11:Technology"  # Custom field #11 = "Technology"
)
```

**Comparison Operators**: `eq` (equals), `ne` (not equals), `gt` (greater than), `gte` (greater/equals), `lt` (less than), `lte` (less/equals), `eq:1,2,3` (multiple values)

### Updating Resources

```python
# Via resource manager
user = await upsales.users.update(1, name="New Name")

# Via model instance with IDE autocomplete
user = await upsales.users.get(1)

# When you type user.edit( your IDE suggests:
# - name: str
# - email: str
# - administrator: int
# But NOT read-only fields like: id, created_at, updated_at

updated = await user.edit(
    name="New Name",
    administrator=1
)
```

**Type Safety**: The SDK uses TypedDict to provide full IDE autocomplete. Only updatable fields appear in suggestions - read-only fields like `id` are automatically excluded.

### Bulk Operations

```python
# Bulk update with concurrency control
products = await upsales.products.bulk_update(
    ids=[1, 2, 3, 4, 5],
    data={"active": 0},
    max_concurrent=5
)

# Bulk delete
await upsales.users.bulk_delete([10, 11, 12])
```

### Working with Custom Fields

```python
# Get user with custom fields
user = await upsales.users.get(1)

# Access custom fields
custom = user.custom_fields
value = custom[11]  # By field ID
value = custom["MY_FIELD"]  # By alias (requires schema)

# Update custom fields
custom[11] = "new value"
await user.edit(custom=custom.to_api_format())
```

## Error Handling

### Basic Error Handling

```python
from upsales import Upsales
from upsales.exceptions import (
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    UpsalesError,
)

async def main():
    async with Upsales(token="YOUR_TOKEN") as upsales:
        try:
            user = await upsales.users.get(999)
        except NotFoundError:
            print("User not found")
        except AuthenticationError:
            print("Invalid token")
        except RateLimitError:
            print("Rate limit exceeded")
        except UpsalesError as e:
            print(f"API error: {e}")
```

### Bulk Operation Errors

```python
try:
    products = await upsales.products.bulk_update(ids, data)
except ExceptionGroup as eg:
    # Python 3.11+ exception groups
    print(f"Failed updates: {len(eg.exceptions)}")
    for exc in eg.exceptions:
        print(f"Error: {exc}")
```

## Rate Limiting

The Upsales API limits requests to **200 per 10 seconds** per API key.

### Automatic Retry

The SDK automatically retries on rate limit errors with exponential backoff:

```python
# This is handled automatically
user = await upsales.users.get(1)  # Retries up to 5 times if rate limited
```

### Controlling Concurrency

```python
# Limit concurrent requests for bulk operations
products = await upsales.products.bulk_update(
    ids=list(range(1, 201)),
    data={"active": 0},
    max_concurrent=50  # Max 50 concurrent requests
)
```

## Python 3.13 Free-Threaded Mode (Optional)

Python 3.13 supports running without the GIL:

```bash
python -X gil=0 your_script.py
```

### When It Helps

Free-threaded mode benefits:
- **CPU-bound callbacks**: Processing responses with heavy computation
- **Thread pools**: Mixing asyncio with ThreadPoolExecutor
- **Hybrid workloads**: CPU tasks alongside I/O operations

### Limited Benefit for Pure Async I/O

For pure HTTP requests (like bulk operations in this SDK):
- Asyncio already handles I/O concurrency efficiently
- The bottleneck is network I/O and API rate limits, not the GIL
- Free-threaded mode provides minimal performance gain

```python
# Bulk operations are efficient with or without free-threaded mode
# The real bottleneck is network latency and the 200 req/10s rate limit
products = await upsales.products.bulk_update(
    ids=list(range(1, 101)),
    data={"active": 0},
    max_concurrent=50
)
```

## Configuration

### Custom Base URL

```python
upsales = Upsales(
    token="YOUR_TOKEN",
    base_url="https://custom.upsales.com/api/v2"
)
```

### Custom Concurrency Limit

```python
upsales = Upsales(
    token="YOUR_TOKEN",
    max_concurrent=30  # Default is 50
)
```

## Next Steps

- [Advanced Patterns](examples/advanced-patterns.md) - More code examples
- [Patterns](patterns/adding-resources.md) - Learn to add new endpoints
- [API Reference](api-reference/client.md) - Full API documentation
- [Creating Models](patterns/creating-models.md) - Model creation guide

## Generating Models from API

The SDK includes a CLI tool to automatically generate models from your Upsales API:

```bash
# Generate model by analyzing real API data
uv run upsales generate-model users --partial

# Generate without partial model
uv run upsales generate-model roles
```

**What it does:**
1. Fetches up to 2000 objects from the endpoint
2. Analyzes which fields are truly required vs optional
3. Generates Python 3.13 code with TypedDict
4. Includes analysis comments explaining field requirements

**Example generated code:**
```python
class User(BaseModel):
    # Required - never null
    id: int  # Present in 100% (1847/1847)
    name: str  # Present in 100% (1847/1847)
    email: str  # Present in 100% (1847/1847)

    # Optional - null in some users
    userTitle: str | None = None  # Present in 100% (1847/1847), null in 325
```

See the CLI tool documentation above for complete model generation guide.

## Troubleshooting

### Import Errors

```python
# Make sure you're using Python 3.13+
import sys
print(sys.version)  # Should be 3.13 or higher
```

### Authentication Errors

```python
# Verify your token
async with Upsales(token="YOUR_TOKEN") as upsales:
    try:
        users = await upsales.users.list(limit=1)
        print("✓ Token is valid")
    except AuthenticationError:
        print("✗ Invalid token")
```

### Rate Limit Issues

```python
# Reduce concurrency
upsales = Upsales(token="YOUR_TOKEN", max_concurrent=25)

# Or add delays between operations
import asyncio
await asyncio.sleep(0.1)  # 100ms delay
```
