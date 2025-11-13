"""
Test and validate sorting functionality.

Validates that sort parameter actually sorts results correctly, not just
that it doesn't error.

Tests:
- Ascending sort (sort="field")
- Descending sort (sort="-field")
- Verifies actual field values are in correct order

Usage:
    python scripts/test_sort_validation.py accounts
    python scripts/test_sort_validation.py contacts
    python scripts/test_sort_validation.py products

Output:
    - ✅ VALIDATED: Sort works AND results are in correct order
    - ❌ FAILED: Sort doesn't work or results not sorted
    - ⚠️ PARTIAL: Sort works but some results out of order

Example:
    $ python scripts/test_sort_validation.py accounts

    Testing sort="name" (ascending)...
    ✅ VALIDATED: 10 results in ascending order
       Result[0].name: "ABC Corp"
       Result[1].name: "Beta Inc"
       ...

    Testing sort="-turnover" (descending)...
    ✅ VALIDATED: 8 results in descending order
       Result[0].turnover: 5000000
       Result[1].turnover: 3000000
       ...
"""

import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from upsales import Upsales

load_dotenv()


def is_sorted_ascending(values: list[Any]) -> bool:
    """
    Check if list is sorted in ascending order.

    API behavior:
    - Strings: Case-insensitive sort
    - Numbers: Standard numeric sort
    - None values: Placed LAST (not first)
    """
    for i in range(len(values) - 1):
        val1 = values[i]
        val2 = values[i+1]

        # None handling: API puts None LAST in ascending order
        if val1 is None and val2 is None:
            continue  # Both None, ok
        elif val1 is None:
            return False  # None before non-None is wrong for ascending
        elif val2 is None:
            continue  # Non-None before None is correct for ascending

        # Compare non-None values (case-insensitive for strings)
        try:
            if isinstance(val1, str) and isinstance(val2, str):
                if val1.upper() > val2.upper():
                    return False
            elif val1 > val2:
                return False
        except TypeError:
            # Can't compare these types
            continue
    return True


def is_sorted_descending(values: list[Any]) -> bool:
    """
    Check if list is sorted in descending order.

    API behavior:
    - Strings: Case-insensitive sort
    - Numbers: Standard numeric sort
    - None values: Placed LAST (after all values)
    """
    for i in range(len(values) - 1):
        val1 = values[i]
        val2 = values[i+1]

        # None handling: API puts None LAST (even in descending)
        if val1 is None and val2 is None:
            continue  # Both None, ok
        elif val1 is None:
            return False  # None before non-None is wrong
        elif val2 is None:
            continue  # Non-None before None is correct (None always last)

        # Compare non-None values (case-insensitive for strings)
        try:
            if isinstance(val1, str) and isinstance(val2, str):
                if val1.upper() < val2.upper():
                    return False
            elif val1 < val2:
                return False
        except TypeError:
            # Can't compare these types
            continue
    return True


async def test_sort_validation(endpoint_name: str):
    """
    Test and validate sorting functionality.

    Args:
        endpoint_name: Endpoint to test (companies, contacts, products, etc.)
    """
    print("\n" + "=" * 80)
    print(f"🧪 TESTING SORT VALIDATION: {endpoint_name}")
    print("=" * 80 + "\n")

    async with Upsales.from_env() as upsales:
        resource = getattr(upsales, endpoint_name)

        # Define fields to test based on endpoint
        if endpoint_name == "companies":
            test_sorts = [
                ("name", "string", "ascending"),
                ("-name", "string", "descending"),
                ("turnover", "number", "ascending"),
                ("-turnover", "number", "descending"),
                ("numberOfContacts", "number", "ascending"),
                ("-numberOfContacts", "number", "descending"),
                ("regDate", "date", "ascending"),
                ("-regDate", "date", "descending"),
            ]
        elif endpoint_name == "contacts":
            test_sorts = [
                ("name", "string", "ascending"),
                ("-name", "string", "descending"),
                ("score", "number", "ascending"),
                ("-score", "number", "descending"),
                ("regDate", "date", "ascending"),
                ("-regDate", "date", "descending"),
            ]
        elif endpoint_name == "products":
            test_sorts = [
                ("name", "string", "ascending"),
                ("-name", "string", "descending"),
                ("price", "number", "ascending"),
                ("-price", "number", "descending"),
            ]
        else:
            test_sorts = [
                ("name", "string", "ascending"),
                ("-name", "string", "descending"),
            ]

        results = {
            "validated": [],
            "failed": [],
            "partial": [],
        }

        for sort_param, field_type, direction in test_sorts:
            # Extract field name (remove - prefix if present)
            field_name = sort_param.lstrip("-")
            is_descending = sort_param.startswith("-")

            print(f"Testing sort='{sort_param}' ({field_type}, {direction})... ", end="", flush=True)

            try:
                # Get sorted results
                sorted_results = await resource.list(sort=sort_param, limit=10)

                if len(sorted_results) < 2:
                    print(f"⚠️ Not enough results to validate ({len(sorted_results)} results)")
                    results["partial"].append((sort_param, "Not enough results"))
                    continue

                print(f"({len(sorted_results)} results) ", end="", flush=True)

                # Extract field values
                field_values = []
                for obj in sorted_results:
                    try:
                        value = getattr(obj, field_name)
                        field_values.append(value)
                    except AttributeError:
                        print(f"❌ Field '{field_name}' not found on object")
                        results["failed"].append((sort_param, f"Field not found"))
                        continue

                # Validate sort order
                if is_descending:
                    is_sorted = is_sorted_descending(field_values)
                else:
                    is_sorted = is_sorted_ascending(field_values)

                if is_sorted:
                    print(f"✅ VALIDATED ({direction})")
                    # Show first 3 values
                    print(f"      Values: {field_values[:3]}")
                    results["validated"].append((sort_param, direction, field_values[:5]))
                else:
                    print(f"❌ NOT SORTED ({direction})")
                    print(f"      Values: {field_values[:5]}")
                    results["failed"].append((sort_param, f"Results not in {direction} order"))

            except Exception as e:
                error_msg = str(e)[:80]
                print(f"❌ ERROR: {error_msg}")
                results["failed"].append((sort_param, error_msg))

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80 + "\n")

        print(f"✅ VALIDATED Sorts ({len(results['validated'])}):")
        print("   (Results are actually sorted correctly)\n")
        for sort_param, direction, sample_values in results["validated"]:
            print(f"   - {sort_param:<25} {direction:<12} Sample: {sample_values[:3]}")

        if results["partial"]:
            print(f"\n⚠️ PARTIAL ({len(results['partial'])}):")
            for sort_param, reason in results["partial"]:
                print(f"   - {sort_param:<25} {reason}")

        if results["failed"]:
            print(f"\n❌ FAILED ({len(results['failed'])}):")
            for sort_param, reason in results["failed"]:
                print(f"   - {sort_param:<25} {reason[:50]}")

        # Statistics
        total = len(results["validated"]) + len(results["failed"]) + len(results["partial"])
        validated_pct = (len(results["validated"]) / total * 100) if total > 0 else 0

        print(f"\n📊 STATISTICS:")
        print(f"   Total sort tests: {total}")
        print(f"   ✅ Validated: {len(results['validated'])} ({validated_pct:.1f}%)")
        print(f"   ⚠️ Partial: {len(results['partial'])}")
        print(f"   ❌ Failed: {len(results['failed'])}")

        # Usage examples
        print(f"\n💡 USAGE EXAMPLES:")
        print(f"   # Ascending order")
        print(f"   results = await upsales.{endpoint_name}.list(sort='name')")
        print()
        print(f"   # Descending order")
        print(f"   results = await upsales.{endpoint_name}.list(sort='-turnover')")
        print()
        print(f"   # Combined with search")
        print(f"   results = await upsales.{endpoint_name}.search(")
        print(f"       active=1,")
        print(f"       sort='-regDate'  # Newest first")
        print(f"   )")
        print()


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_sort_validation.py <endpoint>")
        print("\nExamples:")
        print("  python scripts/test_sort_validation.py companies")
        print("  python scripts/test_sort_validation.py contacts")
        print("  python scripts/test_sort_validation.py products")
        print("\nValidates:")
        print("  - Ascending sort (sort='field')")
        print("  - Descending sort (sort='-field')")
        print("  - Actual result order matches expected")
        sys.exit(1)

    endpoint = sys.argv[1]
    await test_sort_validation(endpoint)


if __name__ == "__main__":
    asyncio.run(main())
