"""
Basic usage examples for Upsales Python SDK.

Demonstrates common operations using Python 3.13 features.

Requirements:
    - Python 3.13+
    - UPSALES_TOKEN environment variable set (or full .env config)

Run with free-threaded mode for best performance:
    python -X gil=0 examples/basic_usage.py

Note: This SDK uses user-friendly naming (e.g., 'companies' not 'accounts')
to match what you see in the Upsales UI.
"""

import asyncio
import os

from upsales import Upsales
from upsales.exceptions import NotFoundError, UpsalesError


async def basic_operations():
    """Demonstrate basic CRUD operations."""
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("=== Basic Operations ===\n")

        # Get single user
        try:
            user = await upsales.users.get(1)
            print(f"User: {user.name} ({user.email})")
            print(f"{user.id = }, {user.administrator = }")
        except NotFoundError:
            print("User not found")

        # List users with pagination
        users = await upsales.users.list(limit=10, offset=0)
        print(f"\nFound {len(users)} users:")
        for user in users[:3]:
            print(f"  - {user.name}")

        # Update user
        try:
            updated = await upsales.users.update(1, name="Updated Name")
            print(f"\nUpdated user: {updated.name}")
        except UpsalesError as e:
            print(f"Update failed: {e}")


async def bulk_operations():
    """
    Demonstrate bulk operations.

    With Python 3.13 free-threaded mode, these run in true parallel!
    Run with: python -X gil=0 examples/basic_usage.py
    """
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("\n=== Bulk Operations ===\n")

        # Bulk update products
        product_ids = list(range(1, 11))  # Update 10 products

        try:
            print(f"Updating {len(product_ids)} products...")
            products = await upsales.products.bulk_update(
                ids=product_ids, data={"active": 0}, max_concurrent=5
            )
            print(f"Successfully updated {len(products)} products")

        except ExceptionGroup as eg:
            # Exception groups (Python 3.11+)
            print(f"Failed to update {len(eg.exceptions)} products")
            for exc in eg.exceptions:
                print(f"  Error: {exc}")


async def custom_fields_example():
    """Demonstrate custom fields usage."""
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("\n=== Custom Fields ===\n")

        # Get user with custom fields
        user = await upsales.users.get(1)

        # Access custom fields
        custom = user.custom_fields

        # By field ID
        if 11 in custom:
            value = custom[11]
            print(f"Custom field 11: {value}")

        # Update custom field
        custom[11] = "new value"

        # Save changes
        await user.edit(custom=custom.to_api_format())
        print("Updated custom fields")


async def error_handling_example():
    """Demonstrate error handling."""
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("\n=== Error Handling ===\n")

        # Handle specific errors
        try:
            user = await upsales.users.get(999999)
        except NotFoundError:
            print("User not found (expected)")
        except UpsalesError as e:
            print(f"API error: {e}")

        # Pattern matching for error handling (Python 3.10+)
        try:
            result = await upsales.users.get(999999)
        except Exception as e:
            match e:
                case NotFoundError():
                    print("Pattern match: Resource not found")
                case UpsalesError():
                    print(f"Pattern match: API error - {e}")
                case _:
                    print(f"Pattern match: Unexpected error - {e}")


async def pagination_example():
    """Demonstrate pagination."""
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("\n=== Pagination ===\n")

        # Manual pagination
        page1 = await upsales.users.list(limit=10, offset=0)
        print(f"Page 1: {len(page1)} users")

        page2 = await upsales.users.list(limit=10, offset=10)
        print(f"Page 2: {len(page2)} users")

        # Automatic pagination (get all)
        all_users = await upsales.users.list_all(batch_size=50)
        print(f"Total users: {len(all_users)}")


async def model_methods_example():
    """Demonstrate model instance methods."""
    token = os.getenv("UPSALES_TOKEN")
    if not token:
        raise ValueError("UPSALES_TOKEN environment variable not set")

    async with Upsales(token=token) as upsales:
        print("\n=== Model Methods ===\n")

        # Get user
        user = await upsales.users.get(1)

        # Edit via model instance
        updated = await user.edit(name="New Name")
        print(f"Updated via model: {updated.name}")

        # Partial model to full model
        # (if you have a partial user from nested data)
        # full = await partial_user.fetch_full()


async def main():
    """Run all examples."""
    print("Upsales Python SDK - Basic Usage Examples")
    print("Python 3.13+ with modern features\n")

    try:
        await basic_operations()
        await bulk_operations()
        await custom_fields_example()
        await error_handling_example()
        await pagination_example()
        await model_methods_example()

        print("\n=== All examples completed! ===")

    except ValueError as e:
        print(f"Error: {e}")
        print("\nSet UPSALES_TOKEN environment variable:")
        print("  export UPSALES_TOKEN='your_token_here'")


if __name__ == "__main__":
    # Run with free-threaded mode for best performance:
    # python -X gil=0 examples/basic_usage.py
    asyncio.run(main())
