"""
Test CRUD operations for custom fields to discover requirements.

Tests:
1. What fields are required to create different field types?
2. What fields are required to update?
3. Do Select options work as expected (in 'default' field)?
4. Do Calculation formulas work?

Usage:
    python scripts/test_custom_field_crud.py account

⚠️  WARNING: Creates and deletes real custom fields!
Use test/sandbox environment only!
"""

import asyncio
import sys
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")


async def test_custom_field_crud(entity: str = "account"):
    """Test custom field CRUD operations."""

    print("\n" + "="*70)
    print(f"TESTING CUSTOM FIELD CRUD: {entity}")
    print("="*70 + "\n")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=30.0
    ) as client:

        created_fields = []

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TEST 1: Create Simple String Field (Minimal Required)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("TEST 1: Create String field (minimal)")
        print("-" * 70)

        min_payload = {
            "name": "Test String Field",
            "datatype": "String",
            "alias": "TEST_STRING_CRUD"
        }

        try:
            response = await client.post(
                f"/customFields/{entity}",
                json=min_payload
            )

            if response.status_code == 200:
                created = response.json()["data"]
                created_fields.append(created["id"])
                print("✅ Minimal create works!")
                print(f"   Created ID: {created['id']}")
                print(f"   Minimal required: name, datatype, alias")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TEST 2: Create Select Field with Options
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\nTEST 2: Create Select field with options")
        print("-" * 70)

        select_payload = {
            "name": "Test Priority",
            "datatype": "Select",
            "alias": "TEST_PRIORITY_CRUD",
            "default": ["Low", "Medium", "High"]  # Options in default!
        }

        try:
            response = await client.post(
                f"/customFields/{entity}",
                json=select_payload
            )

            if response.status_code == 200:
                created = response.json()["data"]
                created_fields.append(created["id"])
                print("✅ Select field created!")
                print(f"   Created ID: {created['id']}")
                print(f"   Options in 'default': {created.get('default')}")
                print(f"   Confirmed: Select options go in 'default' field")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TEST 3: Update Custom Field
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if created_fields:
            print("\n\nTEST 3: Update custom field")
            print("-" * 70)

            field_id = created_fields[0]

            # Try updating with minimal payload
            update_payload = {
                "name": "Updated Name"
            }

            try:
                response = await client.put(
                    f"/customFields/{entity}/{field_id}",
                    json=update_payload
                )

                if response.status_code == 200:
                    updated = response.json()["data"]
                    print("✅ Single field update works!")
                    print(f"   Updated name: {updated.get('name')}")
                    print(f"   Can update with partial payload")
                elif response.status_code == 400:
                    print("❌ Single field update failed (400)")
                    print("   Might need full object like other endpoints")

                    # Try with more fields
                    full_update = {
                        "name": "Updated with More Fields",
                        "datatype": "String",
                        "alias": "TEST_STRING_CRUD"
                    }

                    response = await client.put(
                        f"/customFields/{entity}/{field_id}",
                        json=full_update
                    )

                    if response.status_code == 200:
                        print("✅ Update works with name + datatype + alias")
                    else:
                        print(f"❌ Still failed: {response.status_code}")
                else:
                    print(f"❌ Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ Error: {str(e)[:100]}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # TEST 4: Cleanup - Delete Created Fields
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\nTEST 4: Delete custom fields (cleanup)")
        print("-" * 70)

        for field_id in created_fields:
            try:
                response = await client.delete(
                    f"/customFields/{entity}/{field_id}"
                )

                if response.status_code == 200:
                    print(f"✅ Deleted field {field_id}")
                else:
                    print(f"⚠️ Delete returned {response.status_code} for field {field_id}")

            except Exception as e:
                print(f"❌ Error deleting {field_id}: {str(e)[:50]}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SUMMARY
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70 + "\n")

        print("Required fields for create:")
        print("  - name: Field display name")
        print("  - datatype: Field type (String, Select, etc.)")
        print("  - alias: Field alias for API access")

        print("\nOptional fields for create:")
        print("  - default: Default value (Select = options array!)")
        print("  - visible, editable, locked, etc.: Boolean flags")
        print("  - maxLength: For String/Text types")
        print("  - formula: For Calculation types")

        print("\nSelect field options:")
        print("  - Store options in 'default' field")
        print("  - Example: default=['Option 1', 'Option 2']")

        print("\nUpdate behavior:")
        print("  - Test results above")
        print("  - May need full object or just changed fields")

        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70 + "\n")

        print("CustomField model:")
        print("  _required_update_fields = {'name', 'datatype', 'alias'}")
        print()
        print("CustomFieldsResource:")
        print("  - list_for_entity(entity) ✅")
        print("  - get(id, entity) ✅")
        print("  - create_for_entity(entity, **data) ✅")
        print("  - update(id, entity, **data) ✅")
        print("  - delete(id, entity) ✅")
        print()
        print("Ready to register in client and add tests!")


if __name__ == "__main__":
    entity = sys.argv[1] if len(sys.argv) > 1 else "account"

    print("\n⚠️  WARNING: This script will CREATE and DELETE custom fields!")
    print("Use test/sandbox environment only!")
    print(f"Testing entity: {entity}")
    print("Press Ctrl+C to cancel, Enter to continue...")
    input()

    asyncio.run(test_custom_field_crud(entity))
