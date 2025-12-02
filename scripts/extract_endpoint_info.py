#!/usr/bin/env python
"""
Extract single endpoint information from api_endpoints_with_fields.json.

This creates a lightweight, endpoint-specific reference file that agents can read
instead of the full 3535-line API file.

Usage:
    python scripts/extract_endpoint_info.py orders
    python scripts/extract_endpoint_info.py contacts
    python scripts/extract_endpoint_info.py --all  # Extract all endpoints

Output:
    ai_temp_files/{endpoint}_api_spec.json (50-100 lines vs 3535)

Benefits:
    - Agents read 50 lines instead of 3535 (98% reduction)
    - Saves ~11K tokens per agent
    - Faster loading and processing
    - Focused context for better quality
"""

import json
import sys
from pathlib import Path


def extract_endpoint_info(endpoint: str, api_data: dict) -> dict | None:
    """
    Extract information for a single endpoint.

    Args:
        endpoint: Endpoint name (e.g., 'orders', 'contacts')
        api_data: Full API data from api_endpoints_with_fields.json

    Returns:
        Endpoint-specific data or None if not found
    """
    endpoint_info = api_data.get("endpoints", {}).get(endpoint)

    if not endpoint_info:
        return None

    # Create focused output
    return {
        "endpoint": endpoint,
        "base_path": endpoint_info.get("base_path"),
        "description": endpoint_info.get("description"),
        "methods": endpoint_info.get("methods", {}),
        "extracted_at": "2025-11-13",
        "source": "api_endpoints_with_fields.json"
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_endpoint_info.py <endpoint>")
        print("       python scripts/extract_endpoint_info.py --all")
        print("\nExamples:")
        print("  python scripts/extract_endpoint_info.py orders")
        print("  python scripts/extract_endpoint_info.py contacts")
        print("  python scripts/extract_endpoint_info.py --all  # Extract all 167")
        sys.exit(1)

    # Load full API file
    api_file = Path("api_endpoints_with_fields.json")
    if not api_file.exists():
        print(f"❌ API file not found: {api_file}")
        print("Run this from project root directory")
        sys.exit(1)

    with open(api_file) as f:
        api_data = json.load(f)

    # Create output directory
    output_dir = Path("ai_temp_files")
    output_dir.mkdir(exist_ok=True)

    # Handle --all flag
    if sys.argv[1] == "--all":
        endpoints = list(api_data.get("endpoints", {}).keys())
        print(f"Extracting info for all {len(endpoints)} endpoints...")
        print()

        success_count = 0
        for endpoint in endpoints:
            endpoint_data = extract_endpoint_info(endpoint, api_data)
            if endpoint_data:
                output_path = output_dir / f"{endpoint}_api_spec.json"
                with open(output_path, "w") as f:
                    json.dump(endpoint_data, f, indent=2)
                success_count += 1

        print(f"✅ Extracted {success_count}/{len(endpoints)} endpoints")
        print(f"   Output: ai_temp_files/*_api_spec.json")
        print(f"   Total size: ~{success_count * 2}KB (vs 400KB full file)")
        return

    # Single endpoint
    endpoint = sys.argv[1]

    endpoint_data = extract_endpoint_info(endpoint, api_data)

    if not endpoint_data:
        print(f"❌ Endpoint '{endpoint}' not found in API file")
        print("\nAvailable endpoints:")
        available = list(api_data.get("endpoints", {}).keys())
        # Show suggestions
        suggestions = [e for e in available if endpoint.lower() in e.lower()]
        if suggestions:
            print("Did you mean:")
            for suggestion in suggestions[:10]:
                print(f"  - {suggestion}")
        else:
            print("First 20 endpoints:")
            for ep in sorted(available)[:20]:
                print(f"  - {ep}")
        sys.exit(1)

    # Save to output file
    output_path = output_dir / f"{endpoint}_api_spec.json"
    with open(output_path, "w") as f:
        json.dump(endpoint_data, f, indent=2)

    # Get file size
    size_bytes = output_path.stat().st_size
    size_kb = size_bytes / 1024

    # Get original size for comparison
    original_size_kb = api_file.stat().st_size / 1024

    print(f"✅ Extracted endpoint info: {endpoint}")
    print(f"   Output: {output_path}")
    print(f"   Size: {size_kb:.1f} KB (vs {original_size_kb:.0f} KB full file)")
    print(f"   Reduction: {((original_size_kb - size_kb) / original_size_kb * 100):.1f}%")
    print()
    print("📋 Contains:")
    print(f"   - Base path: {endpoint_data['base_path']}")
    print(f"   - Methods: {', '.join(endpoint_data['methods'].keys())}")

    # Show required fields if POST exists
    post_method = endpoint_data.get("methods", {}).get("POST")
    if post_method:
        required = post_method.get("required", [])
        print(f"   - Required fields (CREATE): {len(required)}")

    # Show updatable fields if PUT exists
    put_method = endpoint_data.get("methods", {}).get("PUT")
    if put_method:
        allowed = put_method.get("allowed", [])
        readonly = put_method.get("readOnly", [])
        print(f"   - Editable fields (UPDATE): {len(allowed)}")
        print(f"   - Read-only fields: {len(readonly)}")

    print()
    print("💡 Use in agent prompts:")
    print(f"   'Read ai_temp_files/{endpoint}_api_spec.json (not the full API file)'")


if __name__ == "__main__":
    main()
