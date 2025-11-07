"""
Discover which fields are REQUIRED vs OPTIONAL when updating.

This script tests each field to determine:
1. Can it be edited? (sends full object)
2. Is it REQUIRED in update payloads? (omit and see if 400 error)
3. Is it OPTIONAL in update payloads? (omit and update still works)

Usage:
    python scripts/test_required_update_fields.py orderStages
    python scripts/test_required_update_fields.py users

Output:
    - ✅ Editable + Required (must include in every update)
    - ✅ Editable + Optional (can omit from updates)
    - ❌ Read-only (id, timestamps)
    - Documentation for model docstrings
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")


async def test_required_fields(endpoint: str):
    """
    Test which fields are required vs optional for updates.

    Strategy:
    1. Get baseline object
    2. For each field, try updating WITHOUT that field
    3. If update fails (400), field is REQUIRED
    4. If update succeeds, field is OPTIONAL
    """
    print("\n" + "="*70)
    print(f"TESTING REQUIRED FIELDS FOR UPDATES: {endpoint}")
    print("="*70 + "\n")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=30.0
    ) as client:

        # 1. Get a test object
        print("Step 1: Fetching test object...")
        response = await client.get(f"/{endpoint}", params={"limit": 1})
        data = response.json()

        if not data.get("data") or len(data["data"]) == 0:
            print(f"❌ No objects found in /{endpoint}")
            return

        original = data["data"][0]
        obj_id = original["id"]

        print(f"✅ Got object ID: {obj_id}")
        print(f"Fields: {list(original.keys())}")
        print(f"Original values: {original}\n")

        # Get all fields except system fields
        all_fields = {
            k: v for k, v in original.items()
            if not k.startswith("$") and k != "id"  # Skip id and $ fields
        }

        # 2. Establish baseline - does full update work?
        print("Step 2: Testing full object update (baseline)...")
        response = await client.put(
            f"/{endpoint}/{obj_id}",
            json=original
        )

        if response.status_code != 200:
            print(f"❌ Full object update failed: {response.status_code}")
            print("   Cannot proceed with testing")
            return

        print("✅ Full object update works (baseline confirmed)\n")

        # 3. Test each field by OMITTING it
        print("Step 3: Testing which fields are required...")
        print("-" * 70)
        print("Testing by omitting each field to see if update fails\n")

        required_fields = []
        optional_fields = []
        errors = []

        for field_to_omit in all_fields:
            # Create update payload WITHOUT this field
            update_payload = {
                k: v for k, v in all_fields.items()
                if k != field_to_omit
            }

            print(f"Testing {field_to_omit}...")

            try:
                response = await client.put(
                    f"/{endpoint}/{obj_id}",
                    json=update_payload
                )

                if response.status_code == 200:
                    # Update succeeded without this field
                    print(f"  ✅ OPTIONAL: Can omit '{field_to_omit}' in updates")
                    optional_fields.append(field_to_omit)
                elif response.status_code == 400:
                    # Update failed without this field
                    try:
                        error_data = response.json()
                        error_msg = str(error_data.get("error", "Unknown error"))
                    except:
                        error_msg = response.text[:80]

                    print(f"  ⚠️ REQUIRED: Missing '{field_to_omit}' causes error")
                    print(f"     Error: {error_msg}")
                    required_fields.append(field_to_omit)
                else:
                    print(f"  ❌ Unexpected status: {response.status_code}")
                    errors.append((field_to_omit, response.status_code))

            except Exception as e:
                print(f"  ❌ Error testing {field_to_omit}: {str(e)[:60]}")
                errors.append((field_to_omit, str(e)))

        # 4. Verify by testing update with ONLY required fields
        if required_fields:
            print("\nStep 4: Verifying minimum update (only required fields)...")
            min_payload = {k: original[k] for k in required_fields}
            min_payload["name"] = f"{original['name']}_VERIFY"  # Change something

            response = await client.put(
                f"/{endpoint}/{obj_id}",
                json=min_payload
            )

            if response.status_code == 200:
                print(f"✅ Minimum update works with only: {list(min_payload.keys())}")
            else:
                print(f"⚠️ Minimum update failed: {response.status_code}")
                print("   Required fields might be incomplete")

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70 + "\n")

        print(f"⚠️ REQUIRED fields ({len(required_fields)}):")
        if required_fields:
            for field in required_fields:
                print(f"   - {field} (MUST include in every update)")
        else:
            print("   None found (all fields optional)")

        print(f"\n✅ OPTIONAL fields ({len(optional_fields)}):")
        if optional_fields:
            for field in optional_fields:
                print(f"   - {field} (can omit from updates)")
        else:
            print("   None found (all fields required)")

        print("\n❌ Read-only:")
        print("   - id (primary key, never editable)")

        if errors:
            print(f"\n⚠️ Errors ({len(errors)}):")
            for field, error in errors:
                print(f"   - {field}: {error}")

        # Documentation template
        print("\n" + "="*70)
        print("DOCUMENTATION TEMPLATE")
        print("="*70 + "\n")

        print("Add to model docstring:")
        print("```python")
        print('"""')
        print(f"{endpoint.capitalize()} model.")
        print()
        print("Update requirements:")
        if required_fields:
            for field in required_fields:
                print(f"- {field}: REQUIRED in every update")
        if optional_fields:
            for field in optional_fields:
                print(f"- {field}: Optional (can omit)")
        print("- id: Read-only (never editable)")
        print()
        print("Use model.edit() which automatically includes all fields.")
        print()
        print("Example:")
        print(f"    >>> obj = await upsales.{endpoint}.get(1)")
        print("    >>> updated = await obj.edit(name='New Name')")
        if required_fields:
            print(f"    >>> # SDK auto-includes required: {', '.join(required_fields)}")
        print('"""')
        print("```")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_required_update_fields.py <endpoint>")
        print("Example: python scripts/test_required_update_fields.py orderStages")
        sys.exit(1)

    endpoint = sys.argv[1]

    print("\n⚠️  WARNING: This script will UPDATE a real object multiple times!")
    print("Use with test/sandbox environment only!")
    print("Press Ctrl+C to cancel, Enter to continue...")
    input()

    asyncio.run(test_required_fields(endpoint))
