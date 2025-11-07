"""
Fetch custom fields from all Upsales entities for comprehensive analysis.

This script fetches custom field definitions from all 17 entities that support
custom fields to understand:
1. Are structures identical or entity-specific?
2. What are all possible fields across all types?
3. Which field types are available on which entities?

Usage:
    python scripts/fetch_all_custom_fields.py

Output:
    - ai_temp_files/custom_fields_raw_data.json - All raw responses
    - ai_temp_files/CUSTOM_FIELDS_ANALYSIS.md - Analysis report
    - Console output with initial findings
"""

import asyncio
import json
import os
from collections import defaultdict
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")

# All entities that support custom fields (from user's list)
ENTITIES = [
    "order",
    "orderrow",
    "account",      # User created all types here
    "agreement",
    "activity",
    "todo",
    "appointment",
    "contact",
    "product",
    "project",
    "projectPlan",
    "ticket",
    "user",
    "udo1",
    "udo2",
    "udo3",
    "udo4",
]


async def fetch_custom_fields():
    """Fetch custom fields from all entities."""

    print("\n" + "="*70)
    print("FETCHING CUSTOM FIELDS FROM ALL ENTITIES")
    print("="*70 + "\n")

    results = {}
    statistics = {
        "total_entities": len(ENTITIES),
        "successful": 0,
        "failed": 0,
        "field_types_found": set(),
        "fields_per_entity": {},
        "unique_field_properties": set(),
    }

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=30.0
    ) as client:

        for entity in ENTITIES:
            try:
                print(f"Fetching {entity}...")
                response = await client.get(f"/customFields/{entity}")

                if response.status_code == 200:
                    data = response.json()
                    fields = data.get("data", [])

                    results[entity] = {
                        "status": "success",
                        "count": len(fields),
                        "fields": fields,
                        "types_found": list(set(f.get("datatype") for f in fields if f.get("datatype")))
                    }

                    statistics["successful"] += 1
                    statistics["fields_per_entity"][entity] = len(fields)

                    # Collect field types
                    for field in fields:
                        if field.get("datatype"):
                            statistics["field_types_found"].add(field.get("datatype"))

                        # Collect all unique property keys
                        statistics["unique_field_properties"].update(field.keys())

                    print(f"  ✅ {entity}: {len(fields)} fields, types: {results[entity]['types_found']}")

                else:
                    results[entity] = {
                        "status": "error",
                        "code": response.status_code,
                        "error": response.text[:200]
                    }
                    statistics["failed"] += 1
                    print(f"  ❌ {entity}: Error {response.status_code}")

            except Exception as e:
                results[entity] = {
                    "status": "exception",
                    "error": str(e)[:200]
                }
                statistics["failed"] += 1
                print(f"  ❌ {entity}: Exception - {str(e)[:50]}")

    # Save raw data
    output_data = {
        "fetched_at": datetime.now().isoformat(),
        "statistics": {
            **statistics,
            "field_types_found": list(statistics["field_types_found"]),
            "unique_field_properties": list(statistics["unique_field_properties"]),
        },
        "entities": results,
    }

    output_file = "ai_temp_files/custom_fields_raw_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Raw data saved to: {output_file}")

    # Print statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70 + "\n")

    print(f"Total entities: {statistics['total_entities']}")
    print(f"Successful: {statistics['successful']}")
    print(f"Failed: {statistics['failed']}")
    print(f"\nField types found ({len(statistics['field_types_found'])}):")
    for field_type in sorted(statistics['field_types_found']):
        print(f"  - {field_type}")

    print(f"\nUnique field properties ({len(statistics['unique_field_properties'])}):")
    for prop in sorted(statistics['unique_field_properties']):
        print(f"  - {prop}")

    print(f"\nFields per entity:")
    for entity, count in sorted(statistics['fields_per_entity'].items(), key=lambda x: -x[1]):
        print(f"  {entity:15} {count:3} fields")

    # Analyze commonalities
    print("\n" + "="*70)
    print("INITIAL ANALYSIS")
    print("="*70 + "\n")

    # Get a sample field from account (should have all types)
    if "account" in results and results["account"]["status"] == "success":
        account_fields = results["account"]["fields"]
        if account_fields:
            print("Sample field structure (from account):")
            sample = account_fields[0]
            for key, value in sample.items():
                print(f"  {key}: {type(value).__name__} = {value}")

    # Check if field structures are identical across entities
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70 + "\n")

    print("1. Review ai_temp_files/custom_fields_raw_data.json")
    print("2. Analyze field type structures")
    print("3. Determine if CustomField model can be unified")
    print("4. Create models based on findings")

    return results, statistics


if __name__ == "__main__":
    asyncio.run(fetch_custom_fields())
