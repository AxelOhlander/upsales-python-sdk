"""
Test which fields are truly EDITABLE vs READ-ONLY by updating all fields at once.

This script:
1. Gets an object (baseline)
2. Updates ALL fields in ONE request
3. Fetches the updated object
4. Compares before vs after to see which fields actually changed

This is more efficient than individual updates and avoids:
- Multiple API calls (rate limiting)
- Auth/token issues
- Validation errors on each parse

Usage:
    python scripts/test_field_editability_bulk.py accounts
    python scripts/test_field_editability_bulk.py contacts
    python scripts/test_field_editability_bulk.py orders

Output:
    - ✅ EDITABLE: Field value changed (API updated it)
    - ❌ READ-ONLY: Field value unchanged (API ignored it)
    - ⚠️ UNEXPECTED: Field changed to different value than sent
    - 📋 Frozen field recommendations

Example Output:
    ✅ EDITABLE: name (sent: "Test_EDIT", got: "Test_EDIT")
    ✅ EDITABLE: phone (sent: "+1-555-TEST", got: "+1-555-TEST")
    ❌ READ-ONLY: id (sent: 999, got: 4) - Should be frozen=True
    ❌ READ-ONLY: regDate (sent: "2025-01-01", got: "2025-03-10...")

    📋 Frozen Field Recommendations:
    Mark these as Field(frozen=True):
    - id (never editable)
    - regDate (read-only timestamp)
    - modDate (read-only timestamp)
"""

import asyncio
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")


def get_test_value(field_name: str, current_value: Any, field_type: str = "unknown") -> Any:
    """
    Generate a test value different from current value.

    Args:
        field_name: Name of the field
        current_value: Current value
        field_type: Type hint from model

    Returns:
        Test value that's different from current
    """
    # For binary flags (0/1), toggle
    if current_value in (0, 1) and field_name in ("active", "administrator", "locked", "exclude"):
        return 1 - current_value

    # For booleans, toggle
    if isinstance(current_value, bool):
        return not current_value

    # For strings, append "_EDIT"
    if isinstance(current_value, str):
        if current_value:
            return f"{current_value}_EDIT"
        return "EDITED_VALUE"

    # For numbers, add 1
    if isinstance(current_value, (int, float)) and field_name not in ("id",):
        return current_value + 1

    # For None, set a test value
    if current_value is None:
        if "email" in field_name.lower():
            return "edited@example.com"
        if "name" in field_name.lower():
            return "Edited Name"
        if "phone" in field_name.lower():
            return "+1-555-EDIT"
        if "date" in field_name.lower():
            return "2025-12-31"
        return "edited_value"

    # For empty lists, add a test item (skip - can't easily test)
    if isinstance(current_value, list) and not current_value:
        return current_value  # Skip empty lists

    # For non-empty lists, keep as-is (skip complex structures)
    if isinstance(current_value, list):
        return current_value

    # For dicts, keep as-is (skip complex structures)
    if isinstance(current_value, dict):
        return current_value

    # Default: return current (won't test)
    return current_value


async def test_bulk_editability(endpoint: str):
    """
    Test field editability by updating all fields at once.

    Args:
        endpoint: API endpoint name (e.g., 'accounts', 'contacts', 'orders')
    """
    print("\n" + "=" * 80)
    print(f"🧪 TESTING FIELD EDITABILITY (BULK UPDATE): /{endpoint}")
    print("=" * 80 + "\n")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=30.0
    ) as client:

        # Step 1: Get TWO objects for real value testing
        print("Step 1: Fetching test objects...")
        response = await client.get(f"/{endpoint}", params={"limit": 2})
        data = response.json()

        if not data.get("data") or len(data["data"]) == 0:
            print(f"❌ No objects found in /{endpoint}")
            return

        objects = data["data"]
        
        # Use first object as the one to update
        original = objects[0]
        obj_id = original["id"]
        
        # Use second object as source of real test values (if available)
        value_source = objects[1] if len(objects) > 1 else original

        print(f"✅ Got object to update: ID {obj_id}")
        print(f"   Total fields: {len(original)}")
        if len(objects) > 1:
            print(f"✅ Got value source object: ID {value_source['id']}")
            print(f"   Will use real values from existing data")
        else:
            print(f"   ⚠️  Only 1 object available - will use modified values from same object")
        print()

        # Step 2: Build update payload using real values from value_source
        print("Step 2: Building update payload with real values from existing data...")

        update_payload = {}
        skip_fields = {
            "id", "$loki",
            # Skip metadata/system fields that shouldn't be updated
            "regDate", "modDate", "regBy", "modBy",
            # Skip fields with strict business rules/interdependencies
            # Orders endpoint: stage.probability and probability must be 0 or 100
            "probability", "stage",
        }
        test_values = {}  # Track what we're sending

        for field_name, current_value in original.items():
            if field_name in skip_fields:
                continue

            # Get value from source object (real data from API)
            source_value = value_source.get(field_name)
            
            # Only include if source has a different value
            if source_value is not None and source_value != current_value:
                update_payload[field_name] = source_value
                test_values[field_name] = source_value

        print(f"   Prepared {len(update_payload)} fields for update")
        print(f"   Skipped {len(skip_fields)} system fields (id, regDate, modDate, etc.)")
        unchanged = len(original) - len(update_payload) - len(skip_fields)
        if unchanged > 0:
            print(f"   Skipped {unchanged} fields (same value in both objects)\n")
        else:
            print()

        # Step 3: Update with all fields at once
        print("Step 3: Sending bulk update with all modified fields...")

        response = await client.put(
            f"/{endpoint}/{obj_id}",
            json=update_payload
        )

        if response.status_code not in (200, 201):
            print(f"❌ Update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        updated = response.json().get("data", {})
        print(f"✅ Update succeeded (status {response.status_code})")
        print(f"   Response contains {len(updated)} fields\n")

        # Step 4: Compare before vs after
        print("=" * 80)
        print("FIELD-BY-FIELD COMPARISON")
        print("=" * 80 + "\n")

        editable = []
        read_only = []
        unexpected = []

        for field_name in sorted(update_payload.keys()):
            sent_value = test_values[field_name]
            original_value = original.get(field_name)
            updated_value = updated.get(field_name)

            # Compare
            if updated_value == sent_value:
                # Field changed to what we sent
                editable.append(field_name)
                print(f"✅ EDITABLE: {field_name}")
                print(f"   Original: {repr(original_value)[:50]}")
                print(f"   Sent: {repr(sent_value)[:50]}")
                print(f"   Got: {repr(updated_value)[:50]}")

            elif updated_value == original_value:
                # Field unchanged (API ignored our update)
                read_only.append(field_name)
                print(f"❌ READ-ONLY: {field_name} (API ignored update)")
                print(f"   Original: {repr(original_value)[:50]}")
                print(f"   Sent: {repr(sent_value)[:50]}")
                print(f"   Got: {repr(updated_value)[:50]} (unchanged)")

            else:
                # Field changed but to something unexpected
                unexpected.append((field_name, sent_value, updated_value))
                print(f"⚠️ UNEXPECTED: {field_name}")
                print(f"   Original: {repr(original_value)[:50]}")
                print(f"   Sent: {repr(sent_value)[:50]}")
                print(f"   Got: {repr(updated_value)[:50]} (different!)")

            print()

        # Step 5: Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80 + "\n")

        print(f"✅ EDITABLE Fields ({len(editable)}):")
        for field in sorted(editable):
            print(f"   - {field}")

        print(f"\n❌ READ-ONLY Fields ({len(read_only)}) - Recommend Field(frozen=True):")
        for field in sorted(read_only):
            print(f"   - {field}")

        if unexpected:
            print(f"\n⚠️ UNEXPECTED Changes ({len(unexpected)}):")
            for field, sent, got in unexpected:
                print(f"   - {field}: sent {repr(sent)[:30]}, got {repr(got)[:30]}")

        # Step 6: Recommendations
        print("\n" + "=" * 80)
        print("📋 RECOMMENDATIONS")
        print("=" * 80 + "\n")

        print("Update model with frozen fields:")
        print(f"```python")
        for field in sorted(read_only):
            print(f"{field}: ... = Field(frozen=True, description='...')")
        print(f"```")

        print(f"\n{endpoint.capitalize()}UpdateFields TypedDict should include:")
        print(f"```python")
        print(f"class {endpoint.capitalize()}UpdateFields(TypedDict, total=False):")
        for field in sorted(editable)[:20]:  # Show first 20
            print(f"    {field}: Any  # Editable")
        if len(editable) > 20:
            print(f"    # ... and {len(editable) - 20} more editable fields")
        print(f"```")

        # Stats
        print("\n" + "=" * 80)
        print("📊 STATISTICS")
        print("=" * 80 + "\n")

        total_tested = len(editable) + len(read_only) + len(unexpected)
        editable_pct = (len(editable) / total_tested * 100) if total_tested > 0 else 0
        readonly_pct = (len(read_only) / total_tested * 100) if total_tested > 0 else 0

        print(f"   Total fields tested: {total_tested}")
        print(f"   ✅ Editable: {len(editable)} ({editable_pct:.1f}%)")
        print(f"   ❌ Read-only: {len(read_only)} ({readonly_pct:.1f}%)")
        print(f"   ⚠️ Unexpected: {len(unexpected)}")
        print()


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_field_editability_bulk.py <endpoint>")
        print("\nExamples:")
        print("  python scripts/test_field_editability_bulk.py accounts")
        print("  python scripts/test_field_editability_bulk.py contacts")
        print("  python scripts/test_field_editability_bulk.py orders")
        print("  python scripts/test_field_editability_bulk.py activities")
        sys.exit(1)

    endpoint = sys.argv[1]

    if not TOKEN:
        print("❌ UPSALES_TOKEN not found in environment")
        print("Create a .env file with: UPSALES_TOKEN=your_token")
        sys.exit(1)

    print("⚠️  WARNING: This script will UPDATE a real object!")
    print("⚠️  Use SANDBOX/TEST environment only, NOT production!")
    print()

    await test_bulk_editability(endpoint)


if __name__ == "__main__":
    asyncio.run(main())
