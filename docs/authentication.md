# Authentication

Guide for authenticating with the Upsales API.

## Overview

The SDK supports two authentication methods:

1. **API Token** (Primary) - Permanent token for production use
2. **Username/Password Fallback** - Automatic token refresh for sandbox environments

## Basic Authentication (API Token)

### From Environment Variables (Recommended)

Create a `.env` file:

```bash
# .env
UPSALES_TOKEN=your_api_token_here
```

Then use in code:

```python
import asyncio
from upsales import Upsales

async def main():
    # Automatically loads from .env
    async with Upsales.from_env() as upsales:
        user = await upsales.users.get(1)
        print(user.name)

asyncio.run(main())
```

### Direct Initialization

```python
async with Upsales(token="YOUR_API_TOKEN") as upsales:
    user = await upsales.users.get(1)
```

## Fallback Authentication (Sandbox Environments)

For sandbox environments that reset daily (e.g., tokens expire at 03:00), enable automatic token refresh using username/password.

###Configuration

Create a `.env` file with fallback credentials:

```bash
# .env
UPSALES_TOKEN=your_initial_token
UPSALES_ENABLE_FALLBACK_AUTH=true
UPSALES_EMAIL=user@email.com
UPSALES_PASSWORD=your_password
```

### How It Works

1. Client attempts request with API token
2. If token is invalid (401/403), automatically:
   - Posts credentials to `/session/` endpoint
   - Receives new token
   - Retries original request with new token
3. New token is used for subsequent requests

### Example

```python
import asyncio
from upsales import Upsales

async def main():
    # Loads configuration from .env
    # Automatically refreshes token when it expires
    async with Upsales.from_env() as upsales:
        # Even if token expired, this works!
        user = await upsales.users.get(1)
        print(user.name)

        # Subsequent requests use refreshed token
        users = await upsales.users.list(limit=10)

asyncio.run(main())
```

## Manual Configuration

Enable fallback authentication programmatically:

```python
from upsales import Upsales

async with Upsales(
    token="YOUR_TOKEN",
    email="user@email.com",
    password="password",
    enable_fallback_auth=True,
) as upsales:
    user = await upsales.users.get(1)
```

## Environment Variables

Complete list of authentication-related environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `UPSALES_TOKEN` | Yes | API authentication token |
| `UPSALES_EMAIL` | No | Email for fallback auth |
| `UPSALES_PASSWORD` | No | Password for fallback auth |
| `UPSALES_ENABLE_FALLBACK_AUTH` | No | Enable automatic refresh (`true`/`false`, default: `false`) |
| `UPSALES_BASE_URL` | No | Custom API URL (default: `https://power.upsales.com/api/v2`) |
| `UPSALES_MAX_CONCURRENT` | No | Max concurrent requests (default: `50`) |

## Token Refresh Flow

```
┌─────────────────┐
│ Make API Request│
└────────┬────────┘
         │
    ┌────▼────┐
    │ 200 OK? │───Yes───► Success
    └────┬────┘
         │ No
    ┌────▼──────┐
    │ 401/403?  │───No────► Raise Error
    └────┬──────┘
         │ Yes
    ┌────▼────────────┐
    │ Fallback Enabled│───No────► Raise AuthenticationError
    │ & Credentials?  │
    └────┬────────────┘
         │ Yes
    ┌────▼────────────┐
    │ POST /session/  │
    │ {email,password}│
    └────┬────────────┘
         │
    ┌────▼──────┐
    │ Get Token │
    └────┬──────┘
         │
    ┌────▼────────────┐
    │ Retry Request   │
    │ with New Token  │
    └─────────────────┘
```

## Security Best Practices

### Production Environments

✅ **DO:**
- Use permanent API tokens
- Store tokens in environment variables or secure secret managers
- Rotate tokens periodically
- Use service accounts with minimal permissions

❌ **DON'T:**
- Enable fallback authentication in production
- Commit `.env` files to version control
- Share API tokens
- Log tokens in application logs

### Development/Sandbox Environments

✅ **DO:**
- Enable fallback authentication for auto-reset environments
- Use separate credentials for sandbox
- Store credentials in `.env` file (gitignored)

❌ **DON'T:**
- Use production credentials in sandbox
- Commit credentials to repository

## Error Handling

```python
from upsales import Upsales
from upsales.exceptions import AuthenticationError

async def main():
    try:
        async with Upsales.from_env() as upsales:
            user = await upsales.users.get(1)
    except AuthenticationError as e:
        # Handle authentication failures
        if "Token refresh failed" in str(e):
            print("Check your UPSALES_EMAIL and UPSALES_PASSWORD")
        else:
            print(f"Authentication error: {e}")
    except ValueError as e:
        # Handle missing configuration
        print(f"Configuration error: {e}")
```

## Troubleshooting

### Token Refresh Not Working

Check that all required settings are configured:

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("Token:", "✓" if os.getenv("UPSALES_TOKEN") else "✗")
print("Fallback:", "✓" if os.getenv("UPSALES_ENABLE_FALLBACK_AUTH") == "true" else "✗")
print("Email:", "✓" if os.getenv("UPSALES_EMAIL") else "✗")
print("Password:", "✓" if os.getenv("UPSALES_PASSWORD") else "✗")
```

### Invalid Credentials

If token refresh fails with "Invalid email or password":

1. Verify credentials in `.env` file
2. Try logging in manually at https://power.upsales.com
3. Check for special characters in password (ensure proper escaping)

### Infinite Loop Protection

The SDK only attempts token refresh **once per request**. If the refreshed token also fails, an `AuthenticationError` is raised to prevent infinite loops.

## Advanced: Manual Token Refresh

For advanced use cases, manually refresh tokens:

```python
from upsales.auth import AuthenticationManager

async def main():
    auth = AuthenticationManager(
        token="expired_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    # Manually refresh token
    new_token = await auth.refresh_token()
    print(f"New token: {new_token}")

    # Use in client
    async with Upsales(token=new_token) as upsales:
        user = await upsales.users.get(1)
```

## Session Endpoint Details

The SDK uses the `/session/` endpoint for token refresh:

**Request:**
```http
POST /api/v2/session/
Content-Type: application/json

{
  "email": "user@email.com",
  "password": "password",
  "samlBypass": null
}
```

**Response:**
```json
{
  "data": {
    "token": "new_api_token",
    "isTwoFactorAuth": false
  }
}
```

## Example: Complete Setup

```bash
# .env file
UPSALES_TOKEN=your_initial_token_here
UPSALES_ENABLE_FALLBACK_AUTH=true
UPSALES_EMAIL=sandbox@yourcompany.com
UPSALES_PASSWORD=your_sandbox_password
```

```python
# app.py
import asyncio
from upsales import Upsales

async def main():
    """
    Works seamlessly even when sandbox resets daily at 03:00.
    Token automatically refreshes on first use after reset.
    """
    async with Upsales.from_env() as upsales:
        # Get users
        users = await upsales.users.list(limit=10)
        for user in users:
            print(f"{user.id}: {user.name}")

        # Bulk operations
        products = await upsales.products.bulk_update(
            ids=[1, 2, 3],
            data={"active": 0}
        )
        print(f"Updated {len(products)} products")

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- [Getting Started](getting-started.md) - Basic SDK usage
- [Basic Usage Examples](examples/basic-usage.md) - SDK usage examples
- [Pydantic Settings](patterns/pydantic-v2-features.md#pydantic-settings-configuration) - Type-safe configuration
