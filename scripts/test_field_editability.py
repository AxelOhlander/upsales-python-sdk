"""
Test which fields are editable via the Upsales API.

This script tests each field in a model to determine if it can be updated.
Useful for validating frozen fields and TypedDict accuracy.

Usage:
    python scripts/test_field_editability.py users
    python scripts/test_field_editability.py companies
    python scripts/test_field_editability.py products

Requirements:
    - .env file with UPSALES_TOKEN
    - At least one object exists in the endpoint
    - Permission to update objects (use test/sandbox environment!)

Output:
    - ✅ Editable fields (API accepts and changes value)
    - ❌ Read-only fields (API rejects or ignores)
    - ⚠️ Warnings for mismatches with model definitions
"""

import asyncio
import sys
from typing import Any

from upsales import Upsales


def get_test_value(field_name: str, current_value: Any) -> Any:
    """
    Generate a safe test value for a field.

    Args:
        field_name: Name of the field.
        current_value: Current value of the field.

    Returns:
        Safe test value that won't break data.
    """
    # For binary flags, toggle
    if field_name in ("active", "administrator", "billingAdmin") and current_value in (0, 1):
        return 1 - current_value  # Toggle 0/1

    # For strings, append "_TEST"
    if isinstance(current_value, str):
        return f"{current_value}_TEST"

    # For numbers, add 1
    if isinstance(current_value, (int, float)) and field_name not in ("id",):
        return current_value + 1

    # For booleans, toggle
    if isinstance(current_value, bool):
        return not current_value

    # For None, try setting to a value
    if current_value is None:
        if "email" in field_name.lower():
            return "test@example.com"
        if "name" in field_name.lower():
            return "Test Name"
        if "phone" in field_name.lower():
            return "+1-555-TEST"
        return "test_value"

    # Default: return current value (won't test, but safe)
    return current_value


async def test_endpoint_editability(endpoint_name: str, test_id: int | None = None):
    """
    Test which fields are editable for an endpoint.

    Args:
        endpoint_name: Name of endpoint (users, companies, products).
        test_id: Optional specific ID to test. If None, uses first object.
    """
    print(f"\n{'='*60}")
    print(f"Testing Field Editability: {endpoint_name}")
    print(f"{'='*60}\n")

    async with Upsales.from_env() as upsales:
        resource = getattr(upsales, endpoint_name)

        # Get test object
        if test_id:
            test_obj = await resource.get(test_id)
            print(f"Using object ID: {test_id}")
        else:
            objects = await resource.list(limit=1)
            if not objects:
                print("❌ No objects found to test")
                print("Create at least one object first")
                return
            test_obj = objects[0]
            print(f"Using first object (ID: {test_obj.id})")

        print(f"Testing {len(test_obj.model_fields)} fields...\n")

        # Track results
        editable = []
        read_only = []
        errors = []
        warnings = []

        # Get frozen fields from model
        frozen_fields = {
            name
            for name, field_info in test_obj.__class__.model_fields.items()
            if field_info.frozen
        }

        # Test each field
        for field_name, field_info in test_obj.model_fields.items():
            # Skip private fields and client reference
            if field_name.startswith("_"):
                continue

            # Get current value
            current_value = getattr(test_obj, field_name)

            # Generate test value
            test_value = get_test_value(field_name, current_value)

            # Skip if we couldn't generate a different test value
            if test_value == current_value and current_value is not None:
                print(f"  ⊘ {field_name}: Skipped (couldn't generate test value)")
                continue

            # Try to update just this field
            try:
                updated = await resource.update(test_obj.id, **{field_name: test_value})

                # Check if value actually changed
                updated_value = getattr(updated, field_name)

                if updated_value == test_value:
                    editable.append(field_name)
                    status = "✅ EDITABLE"

                    # Warning if it's marked as frozen but is actually editable
                    if field_name in frozen_fields:
                        warnings.append(
                            f"⚠️ {field_name}: Marked frozen but API allows updates!"
                        )
                        status += " (⚠️ MARKED FROZEN!)"

                    print(f"  {status}: {field_name}")

                elif updated_value == current_value:
                    read_only.append(field_name)
                    status = "❌ READ-ONLY (ignored)"

                    # Warning if it's NOT marked frozen but API ignores updates
                    if field_name not in frozen_fields:
                        warnings.append(
                            f"⚠️ {field_name}: Not frozen but API ignores updates"
                        )
                        status += " (⚠️ SHOULD BE FROZEN?)"

                    print(f"  {status}: {field_name}")
                else:
                    # Value changed but to something unexpected
                    print(f"  ⚠️ {field_name}: Changed to unexpected value")
                    print(f"     Sent: {test_value}, Got: {updated_value}")

            except Exception as e:
                errors.append((field_name, str(e)))
                error_msg = str(e)[:50]
                print(f"  ❌ ERROR: {field_name} - {error_msg}")

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}\n")

        print(f"✅ Editable Fields ({len(editable)}):")
        for field in editable:
            frozen_marker = " (⚠️ marked frozen!)" if field in frozen_fields else ""
            print(f"   - {field}{frozen_marker}")

        print(f"\n❌ Read-Only Fields ({len(read_only)}):")
        for field in read_only:
            frozen_marker = " (not marked frozen)" if field not in frozen_fields else ""
            print(f"   - {field}{frozen_marker}")

        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for field, error in errors:
                print(f"   - {field}: {error[:80]}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")

        # Recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}\n")

        # Check TypedDict accuracy
        print("Check TypedDict completeness:")
        print(f"  - Should include {len(editable)} editable fields")
        print(f"  - Should exclude {len(read_only)} read-only fields")

        if warnings:
            print("\n⚠️ Fix model definitions:")
            for warning in warnings:
                if "Marked frozen but API allows" in warning:
                    field = warning.split(":")[1].strip().split()[0]
                    print(f"  - Remove frozen=True from {field}")
                elif "Not frozen but API ignores" in warning:
                    field = warning.split(":")[1].strip().split()[0]
                    print(f"  - Add frozen=True to {field}")

        print("\nNext steps:")
        print("  1. Update model with frozen field corrections")
        print("  2. Update TypedDict to match editable fields")
        print("  3. Re-run tests to verify")
        print("  4. Re-record VCR cassettes if model changed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_field_editability.py <endpoint>")
        print("Example: python scripts/test_field_editability.py users")
        sys.exit(1)

    endpoint = sys.argv[1]
    test_id = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("\n⚠️  WARNING: This script will UPDATE a real object!")
    print("Use with test/sandbox environment only!")
    print("Press Ctrl+C to cancel, Enter to continue...")
    input()

    asyncio.run(test_endpoint_editability(endpoint, test_id))
