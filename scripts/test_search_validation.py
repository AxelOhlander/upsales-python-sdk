"""
Validate that search() actually returns correct results.

This script not only checks if search works, but also validates that
the returned results actually match the search criteria.

For example:
- search(active=1) → Verify all results have active=1
- search(name="*AB") → Verify all names contain "AB"
- search(turnover=">1000000") → Verify all turnover > 1000000

Usage:
    python scripts/test_search_validation.py accounts
    python scripts/test_search_validation.py contacts
    python scripts/test_search_validation.py products

Output:
    - ✅ VALIDATED: Search works AND results match criteria
    - ⚠️ PARTIAL: Search works but some results don't match (false positives)
    - ❌ FAILED: Search error or no validation possible
"""

import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from upsales import Upsales

load_dotenv()


def validate_result(obj: Any, field: str, operator: str, value: Any) -> tuple[bool, str]:
    """
    Validate that an object matches the search criteria.

    Args:
        obj: The object to validate
        field: Field name that was searched
        operator: Operator used (eq, gt, gte, lt, lte, src, in)
        value: Value that was searched for

    Returns:
        (matches, reason) tuple
    """
    # Get the actual field value from the object
    try:
        actual = getattr(obj, field)
    except AttributeError:
        return False, f"Field '{field}' not found on object"

    # Validate based on operator
    if operator == "eq":
        matches = actual == value
        return matches, f"Expected {value}, got {actual}"

    elif operator == "ne":
        matches = actual != value
        return matches, f"Expected !={value}, got {actual}"

    elif operator == "gt":
        try:
            matches = actual > value
            return matches, f"Expected >{value}, got {actual}"
        except TypeError:
            return False, f"Cannot compare {type(actual)} > {type(value)}"

    elif operator == "gte":
        try:
            matches = actual >= value
            return matches, f"Expected >={value}, got {actual}"
        except TypeError:
            return False, f"Cannot compare {type(actual)} >= {type(value)}"

    elif operator == "lt":
        try:
            matches = actual < value
            return matches, f"Expected <{value}, got {actual}"
        except TypeError:
            return False, f"Cannot compare {type(actual)} < {type(value)}"

    elif operator == "lte":
        try:
            matches = actual <= value
            return matches, f"Expected <={value}, got {actual}"
        except TypeError:
            return False, f"Cannot compare {type(actual)} <= {type(value)}"

    elif operator == "src":  # Substring
        if isinstance(actual, str) and isinstance(value, str):
            matches = value.upper() in actual.upper()
            return matches, f"Expected '{value}' in '{actual}'"
        return False, f"Substring search requires strings"

    elif operator == "in":  # IN list
        values = value.split(",") if isinstance(value, str) else value
        matches = actual in values
        return matches, f"Expected {actual} in {values}"

    else:
        return False, f"Unknown operator: {operator}"


def parse_search_query(query_value: str | int) -> tuple[str, Any]:
    """
    Parse search query to extract operator and value.

    Args:
        query_value: Raw query value (e.g., ">100", "*AB", "1,2,3")

    Returns:
        (operator, value) tuple
    """
    if isinstance(query_value, (int, float, bool)):
        return "eq", query_value

    query_str = str(query_value)

    # Check for operators
    if query_str.startswith(">="):
        return "gte", type_convert(query_str[2:])
    elif query_str.startswith(">"):
        return "gt", type_convert(query_str[1:])
    elif query_str.startswith("<="):
        return "lte", type_convert(query_str[2:])
    elif query_str.startswith("<"):
        return "lt", type_convert(query_str[1:])
    elif query_str.startswith("!="):
        return "ne", type_convert(query_str[2:])
    elif query_str.startswith("*"):
        return "src", query_str[1:]  # Substring
    elif query_str.startswith("=") and "," in query_str:
        return "in", query_str[1:].split(",")  # IN list
    elif query_str.startswith("="):
        return "eq", type_convert(query_str[1:])
    else:
        # No operator prefix, exact match
        return "eq", type_convert(query_str)


def type_convert(value: str) -> Any:
    """
    Convert string value to appropriate type.

    Args:
        value: String value

    Returns:
        Converted value (int, float, bool, or str)
    """
    # Try int
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Try bool
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Return as string
    return value


async def test_search_validation(endpoint_name: str):
    """
    Test and validate search() functionality.

    Args:
        endpoint_name: Endpoint to test (accounts, contacts, products, etc.)
    """
    print("\n" + "=" * 80)
    print(f"🧪 TESTING SEARCH VALIDATION: {endpoint_name}")
    print("=" * 80 + "\n")

    async with Upsales.from_env() as upsales:
        resource = getattr(upsales, endpoint_name)

        # Define test queries (field: query_value)
        if endpoint_name == "companies":
            test_queries = {
                "active": 1,
                "name": "*AB",
                "phone": "*555",
                "score": ">0",
                "numberOfContacts": ">0",
                "turnover": ">1000000",
                "profit": ">0",
                "isExternal": 0,
                "headquarters": 1,
                "journeyStep": "lead",
                "status": "active",
            }
        elif endpoint_name == "contacts":
            test_queries = {
                "active": 1,
                "name": "*John",
                "email": "*@example.com",
            }
        elif endpoint_name == "products":
            test_queries = {
                "active": 1,
                "name": "*Product",
                "price": ">100",
            }
        else:
            test_queries = {
                "active": 1,
            }

        results = {
            "validated": [],  # Search works AND results validated
            "partial": [],    # Search works but some results don't match
            "failed": [],     # Search failed or couldn't validate
        }

        for field, query_value in test_queries.items():
            print(f"Testing {field}='{query_value}'... ", end="", flush=True)

            try:
                # Execute search
                search_results = await resource.search(**{field: query_value})

                if len(search_results) == 0:
                    print(f"⚠️ No results (can't validate)")
                    results["partial"].append((field, query_value, "No results to validate"))
                    continue

                print(f"({len(search_results)} results) ", end="", flush=True)

                # Parse operator and value
                operator, expected_value = parse_search_query(query_value)

                # Validate each result
                mismatches = []
                for i, obj in enumerate(search_results[:10]):  # Check first 10
                    matches, reason = validate_result(obj, field, operator, expected_value)
                    if not matches:
                        mismatches.append((i, reason))

                if mismatches:
                    print(f"⚠️ PARTIAL ({len(mismatches)} mismatches)")
                    for idx, reason in mismatches[:3]:  # Show first 3
                        print(f"      Result[{idx}]: {reason}")
                    results["partial"].append((field, query_value, f"{len(mismatches)} mismatches"))
                else:
                    print(f"✅ VALIDATED (all match!)")
                    results["validated"].append((field, query_value, len(search_results)))

            except Exception as e:
                error_msg = str(e)[:80]
                print(f"❌ ERROR: {error_msg}")
                results["failed"].append((field, error_msg))

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80 + "\n")

        print(f"✅ VALIDATED Fields ({len(results['validated'])}):")
        print("   (Search works AND all results match criteria)\n")
        for field, query, count in results["validated"]:
            print(f"   - {field:<25} query='{query}' ({count} results, all valid)")

        if results["partial"]:
            print(f"\n⚠️ PARTIAL Fields ({len(results['partial'])}):")
            print("   (Search works but some results don't match)\n")
            for field, query, issue in results["partial"]:
                print(f"   - {field:<25} query='{query}' - {issue}")

        if results["failed"]:
            print(f"\n❌ FAILED Fields ({len(results['failed'])}):")
            print("   (Search error or not supported)\n")
            for field, error in results["failed"]:
                print(f"   - {field:<25} {error[:50]}")

        # Statistics
        total = len(results["validated"]) + len(results["partial"]) + len(results["failed"])
        validated_pct = (len(results["validated"]) / total * 100) if total > 0 else 0

        print(f"\n📊 STATISTICS:")
        print(f"   Total fields tested: {total}")
        print(f"   ✅ Fully validated: {len(results['validated'])} ({validated_pct:.1f}%)")
        print(f"   ⚠️ Partial/No results: {len(results['partial'])}")
        print(f"   ❌ Failed: {len(results['failed'])}")
        print()


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_search_validation.py <endpoint>")
        print("\nExamples:")
        print("  python scripts/test_search_validation.py companies")
        print("  python scripts/test_search_validation.py contacts")
        print("  python scripts/test_search_validation.py products")
        sys.exit(1)

    endpoint = sys.argv[1]
    await test_search_validation(endpoint)


if __name__ == "__main__":
    asyncio.run(main())
