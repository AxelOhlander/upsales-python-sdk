"""
Test complete CRUD lifecycle: CREATE → UPDATE → DELETE.

This orchestrator script runs multiple validators in sequence to test
the full lifecycle of an object:

1. CREATE: Test required fields (test_required_create_fields.py)
2. UPDATE: Test editable fields (test_field_editability_bulk.py)
3. DELETE: Test deletion (test_delete_operation.py)

Plus optional validators:
4. SEARCH: Test searchable fields (test_search_validation.py)
5. SORT: Test sorting (test_sort_validation.py)
6. FIELD SELECTION: Test field exclusion (test_field_selection.py)

Usage:
    python scripts/test_full_crud_lifecycle.py accounts
    python scripts/test_full_crud_lifecycle.py contacts --full

Options:
    --full: Run all validators including search, sort, field selection
    (default: just CREATE, UPDATE, DELETE)

Output:
    Runs each script and collects results:
    - ✅ Script passed
    - ❌ Script failed
    - Summary of all validations

Example:
    $ python scripts/test_full_crud_lifecycle.py accounts

    ========================================
    FULL CRUD LIFECYCLE TEST: accounts
    ========================================

    [1/3] Testing CREATE + DELETE...
    ✅ PASSED

    [2/3] Testing UPDATE (field editability)...
    ✅ PASSED

    [3/3] Testing standalone DELETE...
    ✅ PASSED

    ========================================
    SUMMARY: 3/3 validators passed
    ========================================
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def run_script(script_name: str, endpoint: str) -> tuple[bool, str]:
    """
    Run a validator script.

    Args:
        script_name: Name of script file
        endpoint: Endpoint to test

    Returns:
        (success, output) tuple
    """
    script_path = Path("scripts") / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    try:
        # Run script with auto-confirm (echo "" for prompts)
        result = subprocess.run(
            [sys.executable, str(script_path), endpoint],
            input="\n",  # Auto-confirm any prompts
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout per script
        )

        # Check if script succeeded (look for error indicators)
        output = result.stdout + result.stderr

        # Success indicators
        has_success = any(indicator in output for indicator in [
            "✅ VALIDATED",
            "✅ DELETE OPERATION FULLY VALIDATED",
            "✅ Baseline creation SUCCEEDED",
            "✅ Update succeeded",
        ])

        # Failure indicators
        has_failure = any(indicator in output for indicator in [
            "❌ Baseline creation FAILED",
            "❌ Cannot proceed",
            "❌ Update failed",
            "❌ DELETE failed",
            "Traceback (most recent call last)",
        ])

        success = has_success and not has_failure

        return success, output

    except subprocess.TimeoutExpired:
        return False, "Script timed out (>2 minutes)"
    except Exception as e:
        return False, f"Error running script: {e}"


async def test_full_crud_lifecycle(endpoint: str, run_full: bool = False):
    """
    Run full CRUD lifecycle validation.

    Args:
        endpoint: Endpoint to test
        run_full: If True, run all validators (search, sort, etc.)
    """
    print("\n" + "=" * 80)
    print(f"FULL CRUD LIFECYCLE TEST: {endpoint}")
    print("=" * 80 + "\n")

    if not os.getenv("UPSALES_TOKEN"):
        print("❌ UPSALES_TOKEN not found in environment")
        sys.exit(1)

    print("⚠️  This will CREATE, UPDATE, and DELETE test data!")
    print("⚠️  Use SANDBOX/TEST environment only!")
    print()

    # Core CRUD validators
    validators = [
        ("test_required_create_fields.py", "CREATE + DELETE (integrated)"),
        ("test_field_editability_bulk.py", "UPDATE (field editability)"),
        ("test_delete_operation.py", "DELETE (standalone verification)"),
    ]

    # Optional validators
    if run_full:
        validators.extend([
            ("test_search_validation.py", "SEARCH (field support + result validation)"),
            ("test_sort_validation.py", "SORT (order validation)"),
            ("test_field_selection.py", "FIELD SELECTION (excludable fields)"),
        ])

    results = []
    total = len(validators)

    # Run each validator
    for idx, (script, description) in enumerate(validators, 1):
        print(f"[{idx}/{total}] Testing {description}...")
        print(f"        Running: {script}")

        success, output = run_script(script, endpoint)

        if success:
            print(f"        ✅ PASSED\n")
            results.append((script, True, ""))
        else:
            print(f"        ❌ FAILED")
            # Show last few lines of output
            lines = output.split("\n")
            error_lines = [l for l in lines if "❌" in l or "Error" in l]
            if error_lines:
                print(f"        Error: {error_lines[-1][:60]}")
            print()
            results.append((script, False, error_lines[-1] if error_lines else "Unknown error"))

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for _, success, _ in results if success)
    failed = total - passed

    print(f"📊 Results: {passed}/{total} validators passed\n")

    print("✅ PASSED:")
    for script, success, _ in results:
        if success:
            print(f"   - {script}")

    if failed > 0:
        print(f"\n❌ FAILED ({failed}):")
        for script, success, error in results:
            if not success:
                print(f"   - {script}")
                if error:
                    print(f"     {error[:60]}")

    # Overall status
    print("\n" + "=" * 80)
    if passed == total:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 80 + "\n")
        print(f"   {endpoint.upper()} endpoint is fully validated:")
        print("   - CREATE works with correct required fields")
        print("   - UPDATE works with correct editable fields")
        print("   - DELETE works and truly removes objects")
        if run_full:
            print("   - SEARCH works with validated results")
            print("   - SORT works with correct ordering")
            print("   - FIELD SELECTION works")
    else:
        print(f"⚠️ {failed} VALIDATION(S) FAILED")
        print("=" * 80 + "\n")
        print("   Review failures above and fix issues before proceeding")

    print()

    # Next steps
    if passed == total:
        print("📝 Next Steps:")
        print(f"   1. Add {endpoint.capitalize()}CreateFields TypedDict to model")
        print(f"   2. Mark frozen fields from editability test results")
        print(f"   3. Update {endpoint.capitalize()}UpdateFields with only editable fields")
        print(f"   4. Add integration tests with VCR")
        print(f"   5. Update docs/endpoint-map.md with ✅ Verified status")
        print()


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_full_crud_lifecycle.py <endpoint> [--full]")
        print("\nExamples:")
        print("  python scripts/test_full_crud_lifecycle.py accounts")
        print("  python scripts/test_full_crud_lifecycle.py contacts --full")
        print("\nValidates:")
        print("  Default: CREATE, UPDATE, DELETE")
        print("  --full: Also tests SEARCH, SORT, FIELD SELECTION")
        print("\nThis runs multiple validators in sequence:")
        print("  1. test_required_create_fields.py (CREATE + DELETE)")
        print("  2. test_field_editability_bulk.py (UPDATE)")
        print("  3. test_delete_operation.py (DELETE standalone)")
        print("  4. test_search_validation.py (--full only)")
        print("  5. test_sort_validation.py (--full only)")
        print("  6. test_field_selection.py (--full only)")
        sys.exit(1)

    endpoint = sys.argv[1]
    run_full = "--full" in sys.argv

    if run_full:
        print("\n🔍 Running FULL validation suite (includes search, sort, field selection)")
    else:
        print("\n🎯 Running core CRUD validation (CREATE, UPDATE, DELETE)")
        print("   Add --full flag to include search, sort, and field selection tests")

    await test_full_crud_lifecycle(endpoint, run_full)


if __name__ == "__main__":
    asyncio.run(main())
