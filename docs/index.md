# Upsales Python SDK

Modern, async Python wrapper for the Upsales CRM API, built for Python 3.13+.

## Features

- ✅ **Python 3.13+** with modern syntax (native type hints, pattern matching)
- ✅ **Async-first** design using httpx
- ✅ **Type-safe** with Pydantic v2, TypedDict, and native type hints
- ✅ **IDE autocomplete** for all update operations (excludes read-only fields)
- ✅ **Auto-retry** with exponential backoff for rate limits
- ✅ **Rate limiting** respects 200 req/10s limit
- ✅ **Bulk operations** with efficient concurrent execution
- ✅ **Custom fields** support with dict-like access
- ✅ **Binary downloads** support for PDFs, audio files, and other non-JSON responses

## Terminology Note

This SDK uses **user-friendly naming** that matches the Upsales UI:
- SDK class: `Upsales` (simple, clean - no collision with data models)
- Customer data: `Company` (matches UI, even though API uses `/accounts`)
- Nested fields: API `"client"` → Python `company`

```python
upsales = Upsales(token="...")      # SDK instance
company = await upsales.companies.get(1)  # Customer data
contact.company                     # No naming collision!
```

See [Terminology Guide](terminology.md) for complete rationale.

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
    async with Upsales(token="YOUR_TOKEN") as upsales:
        # Get a user
        user = await upsales.users.get(1)
        print(f"{user.name = }, {user.email = }")

        # Update user
        updated = await user.edit(name="New Name")

        # List with pagination
        users = await upsales.users.list(limit=50, offset=0)

        # Bulk operations with concurrency control
        products = await upsales.products.bulk_update(
            ids=list(range(1, 101)),
            data={"active": 0}
        )

asyncio.run(main())
```

## Why Python 3.13+?

This SDK leverages modern Python features for cleaner, faster code:

### Native Type Hints
```python
# No typing imports needed!
def get_users() -> list[dict[str, str | None]]:
    pass
```

### Type Parameter Syntax
```python
class BaseResource[T, P]:  # Clean generics!
    async def get(self, id: int) -> T:
        pass
```

### Pattern Matching
```python
match status_code:
    case 200 | 201:
        return success()
    case 404:
        raise NotFoundError()
```

### Free-Threaded Mode (Optional)
```python
# Python 3.13 supports running without GIL
# python -X gil=0 script.py

# Benefits: CPU-bound callbacks, thread pools, hybrid workloads
# Limited benefit for pure async I/O (network is the bottleneck)
await upsales.products.bulk_update(ids, data)
```

## Project Goals

1. **Production-ready library** for Python projects integrating with Upsales
2. **Template-driven design** - Patterns you can replicate for new endpoints
3. **Claude skill** - Well-documented reference for AI-assisted development
4. **CLI tool** - Generate models from API responses automatically

## Next Steps

- [Getting Started Guide](getting-started.md)
- [API Reference](api-reference/client.md)
- [Patterns for Adding Endpoints](patterns/adding-resources.md)
- [Examples](examples/basic-usage.md)

## Requirements

- Python 3.13+
- Upsales CRM account with API access
- API token from Upsales

## Support

- [GitHub Issues](https://github.com/yourusername/upsales-python/issues)
- [Documentation](https://yourdomain.com/upsales-python)
