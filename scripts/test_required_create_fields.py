"""
Discover which fields are REQUIRED vs OPTIONAL when creating resources.

This script tests each field to determine:
1. Can resource be created WITH this field? (expect success)
2. Can resource be created WITHOUT this field? (if fails → required)
3. What's the minimal set of required fields?

Strategy:
- Start with ALL fields from api_endpoints_with_fields.json
- Test creating with all fields (baseline)
- Remove one field at a time and test creation
- If creation fails → field is REQUIRED
- If creation succeeds → field is OPTIONAL

IMPORTANT: This creates and deletes test data! Use sandbox environment only!

Usage:
    python scripts/test_required_create_fields.py orders
    python scripts/test_required_create_fields.py contacts
    python scripts/test_required_create_fields.py activities

Output:
    - ✅ REQUIRED fields (creation fails without them)
    - ⚠️ OPTIONAL fields (creation succeeds without them)
    - 📋 Minimal required field set for {Model}CreateFields TypedDict
    - 🔍 Nested object structure details

Example:
    $ python scripts/test_required_create_fields.py orders

    Testing CREATE required fields for: orders

    ✅ REQUIRED: client (object with id)
    ✅ REQUIRED: user (object with id)
    ✅ REQUIRED: stage (object with id)
    ✅ REQUIRED: date (string, YYYY-MM-DD)
    ✅ REQUIRED: orderRow (array with product.id)
    ⚠️ OPTIONAL: description (string)
    ⚠️ OPTIONAL: probability (number)

    📋 Minimal required fields:
    {
      "client": {"id": 123},
      "user": {"id": 10},
      "stage": {"id": 3},
      "date": "2025-01-15",
      "orderRow": [{"product": {"id": 5}}]
    }
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

# Global flag for compact output mode
COMPACT_MODE = False

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")


def log(message: str = "") -> None:
    """Print message only if not in compact mode."""
    if not COMPACT_MODE:
        print(message)

# Load API endpoints file for field reference
API_FILE = Path("api_endpoints_with_fields.json")
if API_FILE.exists():
    with open(API_FILE) as f:
        API_DATA = json.load(f)
else:
    API_DATA = None
    print("⚠️  api_endpoints_with_fields.json not found - will use basic testing")


async def fetch_real_ids(client: httpx.AsyncClient, endpoint: str) -> dict[str, int]:
    """
    Fetch real IDs from existing data to use in test payloads.
    
    Queries the API for existing records and extracts valid IDs for
    common foreign key fields (client, user, stage, product, etc.).
    
    Args:
        client: HTTP client for API requests
        endpoint: The endpoint being tested (to determine which IDs to fetch)
        
    Returns:
        Dict mapping field names to valid IDs (e.g., {"client": 123, "user": 456})
    """
    real_ids = {}
    
    # Common endpoints that provide IDs for foreign keys
    endpoints_to_check = {
        "client": "/accounts",
        "user": "/users",
        "stage": "/orderStages" if endpoint == "orders" else None,
        "product": "/products",
        "contact": "/contacts",
        "project": "/projects",
        "salesCoach": "/salesCoaches",
        "currency": "/currencies",
        "role": "/roles",
    }
    
    for field_name, endpoint_path in endpoints_to_check.items():
        if endpoint_path is None:
            continue
            
        try:
            response = await client.get(f"{endpoint_path}?limit=1")
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                if items and len(items) > 0:
                    real_ids[field_name] = items[0].get("id")
        except Exception:
            # Silently skip if endpoint doesn't exist or fails
            pass
    
    return real_ids


def get_test_value(
    field_name: str, 
    field_type: str, 
    structure: dict | list | None = None,
    real_ids: dict[str, int] | None = None
):
    """
    Generate a test value for a field based on its type and structure.

    Args:
        field_name: Name of the field
        field_type: Type from API file (string, number, object, array, etc.)
        structure: Structure specification for objects/arrays
        real_ids: Dict of real IDs fetched from API (e.g., {"client": 123})

    Returns:
        Test value appropriate for the field type
    """
    if real_ids is None:
        real_ids = {}
        
    # Handle nested objects (e.g., {"id": number})
    if field_type == "object" and structure:
        if isinstance(structure, dict) and "id" in structure:
            # Use real ID if available, otherwise default to 1
            real_id = real_ids.get(field_name, 1)
            return {"id": real_id}
        return structure

    # Handle arrays
    if field_type == "array":
        if structure:
            if isinstance(structure, list) and len(structure) > 0:
                # Array with structured items - need to convert placeholders
                # e.g., [{"product": {"id": "number"}}] → [{"product": {"id": 123}}]
                result = []
                for item in structure:
                    if isinstance(item, dict):
                        converted_item = {}
                        for k, v in item.items():
                            if isinstance(v, dict):
                                # Nested object like {"id": "number"}
                                converted_nested = {}
                                for nk, nv in v.items():
                                    if nv == "number":
                                        # Use real ID if available (e.g., product ID)
                                        converted_nested[nk] = real_ids.get(k, 1)
                                    elif nv == "string":
                                        converted_nested[nk] = "test"
                                    else:
                                        converted_nested[nk] = nv
                                converted_item[k] = converted_nested
                            elif v == "number":
                                converted_item[k] = 1
                            elif v == "string":
                                # Special handling for fields with restricted values
                                if k == "type":
                                    converted_item[k] = "Visit"  # Valid address type
                                else:
                                    converted_item[k] = "test"
                            else:
                                converted_item[k] = v
                        result.append(converted_item)
                    else:
                        result.append(item)
                return result
        return []

    # Handle dates
    if field_type in ("date", "datetime") or "date" in field_name.lower():
        return date.today().isoformat()  # YYYY-MM-DD

    # Handle strings
    if field_type == "string" or field_type == "text":
        return f"Test {field_name}"

    # Handle numbers
    if field_type == "number":
        # Special cases
        if "probability" in field_name.lower():
            return 50  # 0-100 range
        if "value" in field_name.lower():
            return 1000
        if "interval" in field_name.lower():
            return 1
        return 1

    # Handle booleans
    if field_type == "boolean":
        return True

    # Default fallback
    return None


async def test_create_required_fields(endpoint: str) -> dict:
    """
    Test which fields are required for creating a resource.

    Process:
    1. Load expected fields from api_endpoints_with_fields.json
    2. Build a "full" test object with all fields
    3. Test creating with all fields (baseline)
    4. Remove one field at a time and test creation
    5. Mark field as REQUIRED if creation fails without it
    6. Mark field as OPTIONAL if creation succeeds without it

    Returns:
        Dict with results for compact output mode
    """
    log("\n" + "=" * 80)
    log(f"🧪 TESTING CREATE REQUIRED FIELDS: /{endpoint}")
    log("=" * 80 + "\n")

    # Get API file info for this endpoint
    if not API_DATA:
        print("❌ Cannot proceed without api_endpoints_with_fields.json")
        return {"error": "API file not found"}

    endpoint_info = API_DATA.get("endpoints", {}).get(endpoint)
    if not endpoint_info:
        print(f"❌ Endpoint '{endpoint}' not found in api_endpoints_with_fields.json")
        return {"error": f"Endpoint '{endpoint}' not found"}

    post_method = endpoint_info.get("methods", {}).get("POST")
    if not post_method:
        print(f"❌ Endpoint '{endpoint}' does not support POST (create) operation")
        return {"error": f"Endpoint '{endpoint}' does not support POST"}

    log("📖 API File Information:")
    log(f"   Endpoint: {endpoint_info.get('base_path')}")
    log(f"   Description: {endpoint_info.get('description')}")
    log()

    # Get required and optional fields from API file
    required_from_api = post_method.get("required", [])
    optional_from_api = post_method.get("optional", [])

    log(f"📋 From api_endpoints_with_fields.json:")
    log(f"   Expected REQUIRED fields: {len(required_from_api)}")
    log(f"   Expected OPTIONAL fields: {len(optional_from_api)}")
    log()

    # Setup HTTP client first (needed for fetching real IDs)
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=30.0
    ) as client:

        # Fetch real IDs from existing data
        log("🔍 Fetching real IDs from existing data...")
        real_ids = await fetch_real_ids(client, endpoint)

        if real_ids:
            log(f"   Found {len(real_ids)} valid IDs:")
            for field_name, id_value in real_ids.items():
                log(f"   - {field_name}: {id_value}")
        else:
            log("   ⚠️  No real IDs found - using fallback values")
        log()

        # Build test payload from API file specifications
        test_payload = {}
        field_metadata = {}

        log("🔨 Building test payload from API file...")

        for field_spec in required_from_api:
            field_name = field_spec["field"]
            field_type = field_spec.get("type", "string")
            structure = field_spec.get("structure")

            test_value = get_test_value(field_name, field_type, structure, real_ids)
            test_payload[field_name] = test_value
            field_metadata[field_name] = {
                "expected": "REQUIRED",
                "type": field_type,
                "structure": structure,
                "notes": field_spec.get("notes", "")
            }

            log(f"   + {field_name}: {test_value} (expected REQUIRED)")

        for field_spec in optional_from_api:
            field_name = field_spec["field"]
            field_type = field_spec.get("type", "string")
            structure = field_spec.get("structure")
            default = field_spec.get("default")

            test_value = get_test_value(field_name, field_type, structure, real_ids)
            # Only add optional fields if they have a clear test value
            if test_value is not None:
                test_payload[field_name] = test_value
                field_metadata[field_name] = {
                    "expected": "OPTIONAL",
                    "type": field_type,
                    "structure": structure,
                    "default": default,
                    "notes": field_spec.get("notes", "")
                }
                log(f"   + {field_name}: {test_value} (expected OPTIONAL)")

        log(f"\n📦 Test payload built with {len(test_payload)} fields")
        log()

        # Step 1: Test baseline creation with ALL fields
        log("=" * 80)
        log("STEP 1: Baseline Test (Create with ALL fields)")
        log("=" * 80 + "\n")

        log("⚠️  IMPORTANT: This will create a test object in your Upsales account!")
        log(f"Payload: {json.dumps(test_payload, indent=2)}\n")

        response = await client.post(f"/{endpoint}", json=test_payload)

        if response.status_code not in (200, 201):
            print(f"❌ Baseline creation FAILED (status {response.status_code})")
            print(f"Response: {response.text}")
            return {"error": "Baseline creation failed", "status": response.status_code}

        baseline_data = response.json()
        created_id = baseline_data.get("data", {}).get("id")

        log(f"✅ Baseline creation SUCCEEDED")
        log(f"   Created ID: {created_id}")
        log(f"   Status: {response.status_code}")
        log()

        # Test DELETE operation (verify it actually deletes)
        if created_id:
            log(f"🗑️  Testing DELETE operation...")

            # Delete the object
            delete_response = await client.delete(f"/{endpoint}/{created_id}")

            if delete_response.status_code in (200, 204):
                log(f"   ✅ DELETE succeeded (status {delete_response.status_code})")

                # Verify it's actually gone (should get 404)
                verify_response = await client.get(f"/{endpoint}/{created_id}")

                if verify_response.status_code == 404:
                    log(f"   ✅ Verified deletion (GET returned 404)")
                elif verify_response.status_code == 200:
                    log(f"   ⚠️ WARNING: Object still exists after DELETE!")
                else:
                    log(f"   ⚠️ Unexpected status {verify_response.status_code}")
            else:
                log(f"   ❌ DELETE failed (status {delete_response.status_code})")

            log()

        # Step 2: Test each field individually
        log("=" * 80)
        log("STEP 2: Field-by-Field Testing")
        log("=" * 80 + "\n")

        required_fields = []
        optional_fields = []

        for field_name in test_payload.keys():
            # Skip id if it somehow got in there
            if field_name == "id":
                continue

            # Create payload WITHOUT this field
            test_without = {k: v for k, v in test_payload.items() if k != field_name}

            log(f"Testing without '{field_name}'... ", end="", flush=True) if not COMPACT_MODE else None

            try:
                response = await client.post(f"/{endpoint}", json=test_without)

                if response.status_code in (200, 201):
                    # Creation succeeded without this field
                    optional_fields.append(field_name)
                    created_id = response.json().get("data", {}).get("id")

                    log(f"⚠️  OPTIONAL (creation succeeded)")

                    # Clean up
                    if created_id:
                        await client.delete(f"/{endpoint}/{created_id}")

                elif response.status_code == 400:
                    # Creation failed - field is required
                    required_fields.append(field_name)
                    error_msg = response.json().get("error", {}).get("message", "")
                    log(f"✅ REQUIRED (got 400: {error_msg[:50]})")

                else:
                    # Unexpected status
                    log(f"⚠️  Unexpected status {response.status_code}")

            except Exception as e:
                log(f"❌ Error: {e}")

        # Build results dict (for compact mode and return value)
        results = {
            "endpoint": endpoint,
            "required_fields": [
                {
                    "field": f,
                    "type": field_metadata.get(f, {}).get("type", "unknown"),
                    "structure": field_metadata.get(f, {}).get("structure"),
                }
                for f in required_fields
            ],
            "optional_fields": [f for f in optional_fields],
            "total_tested": len(test_payload),
            "minimal_payload": {f: test_payload.get(f) for f in required_fields},
        }

        # Compact mode: output JSON only
        if COMPACT_MODE:
            print(json.dumps(results, indent=2, default=str))
            return results

        # Verbose mode: full output
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80 + "\n")

        print("✅ REQUIRED FIELDS:")
        for field in required_fields:
            meta = field_metadata.get(field, {})
            expected = meta.get("expected", "UNKNOWN")
            match = "✓" if expected == "REQUIRED" else "✗ MISMATCH!"

            # Show structure for nested objects
            if meta.get("type") == "object":
                structure = meta.get("structure", {})
                print(f"   - {field:<20} {meta.get('type'):<10} {structure} {match}")
            elif meta.get("type") == "array":
                structure = meta.get("structure", [])
                print(f"   - {field:<20} {meta.get('type'):<10} {structure} {match}")
            else:
                print(f"   - {field:<20} {meta.get('type'):<10} {match}")

            notes = meta.get("notes", "")
            if notes:
                print(f"     Notes: {notes}")

        print(f"\n⚠️  OPTIONAL FIELDS:")
        for field in optional_fields:
            meta = field_metadata.get(field, {})
            expected = meta.get("expected", "UNKNOWN")
            match = "✓" if expected == "OPTIONAL" else "✗ MISMATCH!"
            default = meta.get("default")
            default_str = f"(default: {default})" if default else ""

            print(f"   - {field:<20} {meta.get('type'):<10} {default_str} {match}")

        # Step 4: Generate TypedDict documentation
        print("\n" + "=" * 80)
        print("📋 TypedDict for IDE Autocomplete")
        print("=" * 80 + "\n")

        print(f"class {endpoint.capitalize()}CreateFields(TypedDict, total=False):")
        print(f'    """')
        print(f'    Required and optional fields for creating a {endpoint.capitalize()}.')
        print(f'    ')
        print(f'    REQUIRED fields (must be provided):')
        for field in required_fields:
            meta = field_metadata.get(field, {})
            field_type = meta.get('type', 'unknown')
            notes = meta.get('notes', '')
            structure = meta.get('structure', '')

            if structure:
                print(f'    - {field}: {field_type} - Structure: {structure}')
            else:
                print(f'    - {field}: {field_type}')
            if notes:
                print(f'      {notes}')
        print(f'    """')
        print()
        print(f'    # REQUIRED fields')
        for field in required_fields:
            meta = field_metadata.get(field, {})
            field_type = meta.get('type', 'string')

            # Map API types to Python types
            if field_type == "object":
                python_type = "dict[str, Any]"
            elif field_type == "array":
                python_type = "list[dict[str, Any]]"
            elif field_type == "number":
                python_type = "int"
            elif field_type == "boolean":
                python_type = "bool"
            else:
                python_type = "str"

            structure = meta.get('structure', '')
            if structure:
                print(f'    {field}: {python_type}  # Required: {structure}')
            else:
                print(f'    {field}: {python_type}  # Required')

        print()
        print(f'    # OPTIONAL fields')
        for field in optional_fields[:10]:  # Show first 10
            meta = field_metadata.get(field, {})
            field_type = meta.get('type', 'string')

            if field_type == "object":
                python_type = "dict[str, Any]"
            elif field_type == "array":
                python_type = "list[dict[str, Any]]"
            elif field_type == "number":
                python_type = "int"
            elif field_type == "boolean":
                python_type = "bool"
            else:
                python_type = "str"

            print(f'    {field}: {python_type}')

        if len(optional_fields) > 10:
            print(f'    # ... and {len(optional_fields) - 10} more optional fields')

        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80 + "\n")
        print(f"   Total fields tested: {len(test_payload)}")
        print(f"   ✅ REQUIRED fields: {len(required_fields)}")
        print(f"   ⚠️  OPTIONAL fields: {len(optional_fields)}")
        print()

        return results


async def main():
    """Main entry point."""
    global COMPACT_MODE

    parser = argparse.ArgumentParser(
        description="Test which fields are REQUIRED vs OPTIONAL when creating resources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_required_create_fields.py orders
  python scripts/test_required_create_fields.py contacts --compact
  python scripts/test_required_create_fields.py activities

Use --compact for AI agent workflows (outputs JSON only, minimal tokens).
        """,
    )
    parser.add_argument("endpoint", help="API endpoint name (e.g., 'orders', 'contacts')")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON only (for AI agents, saves tokens)",
    )

    args = parser.parse_args()
    COMPACT_MODE = args.compact

    if not TOKEN:
        print("❌ UPSALES_TOKEN not found in environment")
        sys.exit(1)

    if not COMPACT_MODE:
        print("⚠️  WARNING: This script will CREATE and DELETE test data!")
        print("⚠️  Use SANDBOX/TEST environment only, NOT production!")
        print()

    await test_create_required_fields(args.endpoint)


if __name__ == "__main__":
    asyncio.run(main())
