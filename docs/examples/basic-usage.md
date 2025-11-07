# Basic Usage Examples

Simple examples to get started with the Upsales SDK.

## Installation

```bash
pip install upsales
# or
uv add upsales
```

## Quick Start

```python
import asyncio
from upsales import Upsales

async def main():
    # Option 1: Direct token
    async with Upsales(token="YOUR_TOKEN") as upsales:
        # Get a user
        user = await upsales.users.get(1)
        print(f"User: {user.name}")

    # Option 2: From .env file
    async with Upsales.from_env() as upsales:
        # List companies
        companies = await upsales.companies.list(limit=10)
        for company in companies:
            print(f"Company: {company.name}")

asyncio.run(main())
```

## Working with Models

See [Getting Started](../getting-started.md) for more examples.
