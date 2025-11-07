"""
Find unmapped fields in VCR cassettes.

This script analyzes all VCR cassettes to find fields that the API returns
but aren't in our Pydantic models yet.

Usage:
    python ai_temp_files/find_unmapped_fields.py
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Any

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Installing...")
    import subprocess
    subprocess.run(["uv", "pip", "install", "pyyaml"], check=True)
    import yaml

# Import models
from upsales.models.user import User
from upsales.models.company import Company
from upsales.models.product import Product

MODEL_MAP = {
    "users": User,
    "companies": Company,
    "products": Product,
}


def extract_fields_from_response(response_data: dict[str, Any]) -> set[str]:
    """Extract all field names from API response data."""
    if isinstance(response_data, list):
        # List response - get fields from first item
        if response_data:
            return set(response_data[0].keys())
        return set()
    elif isinstance(response_data, dict):
        # Single object response
        return set(response_data.keys())
    return set()


def analyze_cassette(cassette_path: Path) -> dict[str, Any] | None:
    """Analyze a single cassette file."""
    try:
        with open(cassette_path) as f:
            cassette = yaml.safe_load(f)

        # Get first interaction
        if not cassette.get("interactions"):
            return None

        interaction = cassette["interactions"][0]
        response_str = interaction["response"]["body"]["string"]

        # Parse JSON response
        response = json.loads(response_str)

        if "data" not in response:
            return None

        # Extract fields
        fields = extract_fields_from_response(response["data"])

        # Get sample data (first item)
        sample = response["data"]
        if isinstance(sample, list) and sample:
            sample = sample[0]

        return {"fields": fields, "sample": sample}

    except Exception as e:
        print(f"⚠️  Error analyzing {cassette_path.name}: {e}")
        return None


def main():
    """Main analysis function."""
    print("🔍 VCR CASSETTE FIELD ANALYSIS")
    print("=" * 80)
    print()

    cassettes_dir = Path("tests/cassettes/integration")

    results = {}

    # Analyze each endpoint
    for endpoint, model_class in MODEL_MAP.items():
        # Find cassettes for this endpoint
        endpoint_dir = cassettes_dir / f"test_{endpoint}_integration"

        if not endpoint_dir.exists():
            print(f"⚠️  No cassettes found for {endpoint}")
            continue

        # Get first "get" or "list" cassette
        cassette_files = list(endpoint_dir.glob("test_get_*.yaml")) + list(
            endpoint_dir.glob("test_list_*.yaml")
        )

        if not cassette_files:
            print(f"⚠️  No suitable cassettes for {endpoint}")
            continue

        # Analyze first cassette
        analysis = analyze_cassette(cassette_files[0])

        if not analysis:
            continue

        api_fields = analysis["fields"]
        sample = analysis["sample"]

        # Get model fields (excluding computed fields)
        model_fields = set()
        for field_name, field_info in model_class.model_fields.items():
            # Skip computed fields (they don't map to API)
            if not getattr(field_info, "computed", False):
                model_fields.add(field_name)

        # Find differences
        missing_in_model = api_fields - model_fields
        extra_in_model = model_fields - api_fields

        results[endpoint] = {
            "api_fields_count": len(api_fields),
            "model_fields_count": len(model_fields),
            "missing_in_model": missing_in_model,
            "extra_in_model": extra_in_model,
            "sample": sample,
        }

    # Print results
    for endpoint, info in sorted(results.items()):
        print(f"📦 {endpoint.upper()}")
        print(f"   API returns: {info['api_fields_count']} fields")
        print(f"   Model has: {info['model_fields_count']} fields")

        if info["missing_in_model"]:
            print(
                f"   ❌ Missing in model: {len(info['missing_in_model'])} fields"
            )
            for field in sorted(info["missing_in_model"]):
                value = info["sample"].get(field)
                value_type = type(value).__name__
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                print(f"      - {field}: {value_type} = {value_str}")

        if info["extra_in_model"]:
            print(
                f"   ⚠️  Extra in model: {len(info['extra_in_model'])} fields"
            )
            for field in sorted(info["extra_in_model"]):
                print(f"      - {field}")

        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    total_missing = sum(len(r["missing_in_model"]) for r in results.values())
    total_extra = sum(len(r["extra_in_model"]) for r in results.values())

    print(f"   Total unmapped API fields: {total_missing}")
    print(f"   Total extra model fields: {total_extra}")
    print()
    print("💡 TIP: Use these cassettes to:")
    print("   1. Add missing fields to models")
    print("   2. Remove fields that API doesn't return")
    print("   3. Validate nested object structures")
    print("   4. Discover new endpoint fields")


if __name__ == "__main__":
    main()
