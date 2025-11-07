"""
Sandbox Authentication Example

Shows how to use automatic token refresh for sandbox environments
that reset daily.

Setup:
    1. Copy .env.example to .env
    2. Fill in your credentials:
       UPSALES_TOKEN=your_token
       UPSALES_ENABLE_FALLBACK_AUTH=true
       UPSALES_EMAIL=demo_se@upsales.com
       UPSALES_PASSWORD=your_password

Run:
    python examples/sandbox_auth.py

How it works:
    - Uses token from .env
    - If token expires (401), automatically:
      1. POSTs credentials to /session/
      2. Gets new token
      3. Retries original request
    - Perfect for sandboxes that reset at 03:00!
"""

import asyncio

from upsales import Upsales
from upsales.exceptions import AuthenticationError


async def basic_example():
    """
    Basic example with automatic token refresh.

    Even if the sandbox reset at 03:00 and your token is invalid,
    this will automatically refresh and continue working!
    """
    print("=" * 60)
    print("BASIC EXAMPLE: Automatic Token Refresh")
    print("=" * 60)

    try:
        # Load from .env file
        async with Upsales.from_env() as upsales:
            print("\n✅ Client created from .env")
            print(f"   Base URL: {upsales.http.base_url}")
            print(f"   Fallback enabled: {upsales.http.auth_manager is not None}")

            # Make a request
            # If token is expired, automatically refreshes!
            print("\n📡 Making API request...")
            users = await upsales.users.list(limit=5)

            print(f"\n✅ Success! Got {len(users)} users")
            for user in users[:3]:
                print(f"   - {user.name}")

            print("\n💡 If token was expired, it was refreshed automatically!")

    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nCheck your .env file:")
        print("  - UPSALES_TOKEN set?")
        print("  - UPSALES_EMAIL set?")
        print("  - UPSALES_PASSWORD set?")
        print("  - UPSALES_ENABLE_FALLBACK_AUTH=true?")


async def manual_configuration():
    """Example with manual configuration (no .env file)."""
    print("\n" + "=" * 60)
    print("MANUAL CONFIGURATION")
    print("=" * 60)

    async with Upsales(
        token="your_token",
        email="demo_se@upsales.com",
        password="demo150",
        enable_fallback_auth=True,
    ) as upsales:
        print("\n✅ Client created with manual configuration")
        print("   Automatic token refresh: ENABLED")

        # Make requests - auto-refreshes if needed
        try:
            users = await upsales.users.list(limit=3)
            print(f"\n✅ Got {len(users)} users")
        except AuthenticationError as e:
            print(f"\n❌ Error: {e}")


async def production_example():
    """Example for production (no fallback)."""
    print("\n" + "=" * 60)
    print("PRODUCTION EXAMPLE (No Fallback)")
    print("=" * 60)

    async with Upsales(token="your_permanent_token") as upsales:
        print("\n✅ Client created for production")
        print("   Automatic token refresh: DISABLED")
        print("   Uses permanent API token only")

        # In production, use permanent tokens that don't expire
        # No fallback authentication needed


async def check_environment():
    """Check if environment is configured correctly."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)

    import os

    from dotenv import load_dotenv

    load_dotenv()

    checks = {
        "UPSALES_TOKEN": os.getenv("UPSALES_TOKEN"),
        "UPSALES_EMAIL": os.getenv("UPSALES_EMAIL"),
        "UPSALES_PASSWORD": os.getenv("UPSALES_PASSWORD"),
        "UPSALES_ENABLE_FALLBACK_AUTH": os.getenv("UPSALES_ENABLE_FALLBACK_AUTH"),
    }

    print("\nEnvironment Variables:")
    for key, value in checks.items():
        status = "✅" if value else "❌"
        display = "***" if value and key == "UPSALES_PASSWORD" else (value or "NOT SET")
        print(f"  {status} {key}: {display}")

    # Check if fallback auth will work
    fallback_enabled = checks["UPSALES_ENABLE_FALLBACK_AUTH"] == "true"
    has_credentials = checks["UPSALES_EMAIL"] and checks["UPSALES_PASSWORD"]

    print("\nFallback Authentication:")
    if fallback_enabled and has_credentials:
        print("  ✅ ENABLED - Token will auto-refresh if expired")
    elif fallback_enabled and not has_credentials:
        print("  ⚠️  ENABLED but missing credentials")
    else:
        print("  ❌ DISABLED - Using token only")


async def main():
    """Run all examples."""
    print("\nUpsales Python SDK - Sandbox Authentication Examples")
    print("Python 3.13+ with automatic token refresh\n")

    await check_environment()
    await basic_example()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  - Use fallback auth for sandbox environments")
    print("  - Use permanent tokens for production")
    print("  - Token refresh only happens when needed (401/403)")
    print("  - Only one refresh attempt per request (prevents loops)")


if __name__ == "__main__":
    asyncio.run(main())
