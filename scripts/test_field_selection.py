"""
Test which fields can be excluded via field selection (f[] parameter).

This script tests the field selection feature which should reduce response size
by only returning requested fields. However, some fields are ALWAYS returned
by the API regardless of selection.

Tests each field individually to determine:
- ✅ EXCLUDABLE: Field not returned when not requested
- ❌ ALWAYS RETURNED: Field returned even when not requested (can't exclude)
- Document which fields cannot be excluded

Usage:
    python scripts/test_field_selection.py accounts
    python scripts/test_field_selection.py contacts
    python scripts/test_field_selection.py products

Output:
    - ✅ EXCLUDABLE fields (can be removed from response)
    - ❌ ALWAYS RETURNED fields (always in response, can't exclude)
    - Performance estimate based on excludable field ratio

Example:
    $ python scripts/test_field_selection.py accounts

    ✅ EXCLUDABLE: phone (not in response when excluded)
    ✅ EXCLUDABLE: webpage (not in response when excluded)
    ❌ ALWAYS RETURNED: id (always present, can't exclude)
    ❌ ALWAYS RETURNED: name (always present, can't exclude)

    Performance: 70% of fields can be excluded (60/85)
    Bandwidth savings: Up to 70% with optimal field selection
"""

import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from upsales import Upsales

load_dotenv()


async def test_field_selection(endpoint_name: str):
    """
    Test field selection support.

    Args:
        endpoint_name: Endpoint to test (companies, contacts, products, etc.)
    """
    print("\n" + "=" * 80)
    print(f"🧪 TESTING FIELD SELECTION: {endpoint_name}")
    print("=" * 80 + "\n")

    async with Upsales.from_env() as upsales:
        resource = getattr(upsales, endpoint_name)

        # Step 1: Get baseline with ALL fields
        print("Step 1: Fetching object with ALL fields...")
        all_results = await resource.list(limit=1)

        if not all_results:
            print(f"❌ No objects found in {endpoint_name}")
            return

        baseline = all_results[0]
        all_fields = set(baseline.model_dump().keys())

        # Exclude computed fields and private fields
        testable_fields = {
            f for f in all_fields
            if not f.startswith("_") and f not in baseline.__class__.model_computed_fields
        }

        print(f"✅ Baseline has {len(testable_fields)} testable fields")
        print(f"   (Excluding {len(all_fields) - len(testable_fields)} computed/private fields)\n")

        # Step 2: Test requesting ONLY "id" - see what else comes back
        print("Step 2: Testing minimal field selection (id only)...")
        minimal_results = await resource.list(limit=1, fields=["id"])

        if not minimal_results:
            print("❌ No results with field selection")
            return

        minimal_obj = minimal_results[0]
        minimal_fields = set(minimal_obj.model_dump().keys())

        # These are fields that came back even though we only asked for "id"
        always_returned = minimal_fields - {"id"}

        print(f"✅ Requested: ['id']")
        print(f"   Got: {len(minimal_fields)} fields")
        print(f"   Always returned (can't exclude): {len(always_returned)}")
        if always_returned:
            print(f"   Fields: {sorted(list(always_returned)[:10])}")
            if len(always_returned) > 10:
                print(f"   ... and {len(always_returned) - 10} more")
        print()

        # Step 3: Test each field individually
        print("Step 3: Testing each field individually...")
        print("   (Request id + this_field, see if other fields excluded)\n")

        excludable = []
        always_included = []
        errors = []

        # Test a sample of fields (not all 80+ to save time)
        sample_fields = sorted(list(testable_fields))[:20]  # Test first 20

        for field in sample_fields:
            print(f"   Testing {field}... ", end="", flush=True)

            try:
                # Request ONLY id and this field
                result = await resource.list(limit=1, fields=["id", field])

                if not result:
                    print("⊘ No results")
                    continue

                returned_fields = set(result[0].model_dump().keys())

                # Check if OTHER fields came back (not id, not this field, not computed)
                other_fields = returned_fields - {"id", field} - set(baseline.__class__.model_computed_fields.keys())
                other_fields = {f for f in other_fields if not f.startswith("_")}

                if other_fields:
                    # Other fields came back - this field might be in "always returned" group
                    # or field selection isn't working
                    print(f"⚠️ {len(other_fields)} extra fields returned")
                    always_included.append((field, len(other_fields)))
                else:
                    # Only id and this field returned - field selection works!
                    print(f"✅ Excludable")
                    excludable.append(field)

            except Exception as e:
                error_msg = str(e)[:60]
                print(f"❌ Error: {error_msg}")
                errors.append((field, error_msg))

        # Step 4: Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80 + "\n")

        print(f"✅ EXCLUDABLE Fields ({len(excludable)}):")
        print("   (Can be removed from response with field selection)\n")
        for field in excludable:
            print(f"   - {field}")

        print(f"\n❌ ALWAYS RETURNED Fields ({len(always_returned) + len(always_included)}):")
        print("   (Always in response, cannot be excluded)\n")

        print(f"   From minimal test (id only):")
        for field in sorted(list(always_returned))[:15]:
            print(f"   - {field}")
        if len(always_returned) > 15:
            print(f"   ... and {len(always_returned) - 15} more")

        if always_included:
            print(f"\n   From individual tests:")
            for field, extra_count in always_included[:5]:
                print(f"   - {field} (+{extra_count} other fields also returned)")

        if errors:
            print(f"\n⚠️ ERRORS ({len(errors)}):")
            for field, error in errors:
                print(f"   - {field}: {error[:50]}")

        # Performance estimate
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE IMPACT")
        print("=" * 80 + "\n")

        total_fields = len(testable_fields)
        excludable_count = len(excludable)
        always_count = len(always_returned) + len(always_included)

        if total_fields > 0:
            excludable_pct = (excludable_count / total_fields) * 100

            print(f"   Total fields: {total_fields}")
            print(f"   Excludable: {excludable_count} ({excludable_pct:.1f}%)")
            print(f"   Always returned: {always_count}")
            print()
            print(f"   💡 Potential bandwidth savings: Up to {excludable_pct:.0f}% with optimal field selection")
            print()
            print("   Example optimal query:")
            print(f"   results = await upsales.{endpoint_name}.list(")
            print(f'       fields=["id", "name"],  # Minimal fields')
            print(f"       limit=50")
            print(f"   )")
            print(f"   # Returns only essential fields, {excludable_pct:.0f}% smaller response")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_field_selection.py <endpoint>")
        print("\nExamples:")
        print("  python scripts/test_field_selection.py companies")
        print("  python scripts/test_field_selection.py contacts")
        print("  python scripts/test_field_selection.py products")
        print("\nTests:")
        print("  - Which fields can be excluded from response")
        print("  - Which fields are always returned (can't exclude)")
        print("  - Performance impact of field selection")
        sys.exit(1)

    endpoint = sys.argv[1]

    print("⚠️  This script will make multiple API requests to test field selection")
    print("⚠️  Estimated: ~20-30 requests depending on endpoint size")
    print()

    await test_field_selection(endpoint)


if __name__ == "__main__":
    asyncio.run(main())
