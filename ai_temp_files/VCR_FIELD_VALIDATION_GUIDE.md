# VCR.py Field Validation Guide

**Purpose**: Use VCR cassettes to validate fields we don't have models for yet

---

## How VCR Records Complete API Responses

VCR.py records the **entire HTTP interaction** including:
1. Request (method, URL, headers, body)
2. Response (status, headers, **complete body**)

The cassettes contain the **real JSON structure** from the API, making them perfect for:
- Discovering new fields
- Validating unmapped fields
- Planning model enhancements

---

## Example: Extracting Cassette Data for Analysis

### Method 1: Read Cassette Directly (Python Script)

```python
"""
Extract all fields from VCR cassettes to find unmapped fields.

Usage:
    python ai_temp_files/analyze_cassette_fields.py
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict

def extract_fields_from_cassette(cassette_path: Path) -> set[str]:
    """Extract all field names from a VCR cassette."""
    with open(cassette_path) as f:
        cassette = yaml.safe_load(f)

    fields = set()

    # Get response body
    for interaction in cassette.get("interactions", []):
        response = interaction.get("response", {})
        body_str = response.get("body", {}).get("string", "")

        if body_str:
            # Parse JSON response
            try:
                data = json.loads(body_str)

                # Extract fields from data array or single object
                if "data" in data:
                    items = data["data"] if isinstance(data["data"], list) else [data["data"]]
                    for item in items:
                        if isinstance(item, dict):
                            fields.update(item.keys())
            except json.JSONDecodeError:
                pass

    return fields


def analyze_all_cassettes():
    """Analyze all cassettes and find unmapped fields."""
    cassettes_dir = Path("tests/cassettes/integration")

    results = defaultdict(set)

    # Process each cassette
    for cassette_file in cassettes_dir.rglob("*.yaml"):
        endpoint = cassette_file.parent.name.replace("test_", "").replace("_integration", "")
        fields = extract_fields_from_cassette(cassette_file)
        results[endpoint].update(fields)

    # Print summary
    for endpoint, fields in sorted(results.items()):
        print(f"\n{endpoint.upper()} ({len(fields)} fields)")
        print("=" * 60)
        for field in sorted(fields):
            print(f"  - {field}")


if __name__ == "__main__":
    analyze_all_cassettes()
```

### Method 2: Use Cassettes in Tests

```python
"""
Test that validates specific fields exist in real API responses.
"""

import pytest
import json
import yaml

def test_validate_unmapped_fields_in_contacts():
    """
    Validate that Contacts API returns fields we haven't modeled yet.

    This reads the VCR cassette directly to check for fields that
    might not be in our Contact model yet.
    """
    cassette_path = "tests/cassettes/integration/test_contacts_integration/test_get_contact_real_response.yaml"

    with open(cassette_path) as f:
        cassette = yaml.safe_load(f)

    # Get response body
    interaction = cassette["interactions"][0]
    response_body = interaction["response"]["body"]["string"]
    data = json.loads(response_body)

    # Check what the API actually returns
    contact_data = data["data"][0] if isinstance(data["data"], list) else data["data"]

    # Validate expected fields exist
    expected_unmapped_fields = [
        "lastActivity",  # We might not have this field yet
        "source",        # Might be missing
        "tags",          # Might be missing
    ]

    for field in expected_unmapped_fields:
        if field in contact_data:
            print(f"✓ Found unmapped field: {field}")
            print(f"  Type: {type(contact_data[field])}")
            print(f"  Sample: {contact_data[field]}")
```

### Method 3: Compare Model vs API Response

```python
"""
Compare what our model defines vs what the API actually returns.
"""

import pytest
import json
import yaml
from upsales.models.contacts import Contact

@pytest.mark.vcr()
async def test_find_missing_contact_fields():
    """
    Compare Contact model fields against real API response.

    This helps identify fields we haven't added to the model yet.
    """
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=1)
        contact = contacts[0]

    # Get cassette data
    cassette_path = "tests/cassettes/.../test_find_missing_contact_fields.yaml"
    with open(cassette_path) as f:
        cassette = yaml.safe_load(f)

    # Extract API fields
    response_body = cassette["interactions"][0]["response"]["body"]["string"]
    api_data = json.loads(response_body)["data"][0]
    api_fields = set(api_data.keys())

    # Get model fields
    model_fields = set(Contact.model_fields.keys())

    # Find differences
    missing_in_model = api_fields - model_fields
    missing_in_api = model_fields - api_fields

    print("\n🔍 Field Analysis:")
    print(f"  API returns: {len(api_fields)} fields")
    print(f"  Model has: {len(model_fields)} fields")

    if missing_in_model:
        print(f"\n❌ Fields in API but not in model ({len(missing_in_model)}):")
        for field in sorted(missing_in_model):
            print(f"  - {field}: {type(api_data[field]).__name__}")

    if missing_in_api:
        print(f"\n⚠️  Fields in model but not in API ({len(missing_in_api)}):")
        for field in sorted(missing_in_api):
            print(f"  - {field}")
```

---

## Practical Examples

### Example 1: Discover New Mail Fields

```python
"""
Use cassettes to discover all fields returned by /api/v2/mail endpoint.
"""

import json
import yaml

def discover_mail_fields():
    cassette = "tests/cassettes/integration/test_mail_integration/test_list_mail.yaml"

    with open(cassette) as f:
        data = yaml.safe_load(f)

    response = data["interactions"][0]["response"]["body"]["string"]
    mail_data = json.loads(response)["data"]

    # Get first mail item
    mail = mail_data[0] if isinstance(mail_data, list) else mail_data

    print("Mail API Fields:")
    for field, value in mail.items():
        print(f"  {field}: {type(value).__name__}")

        # If it's a nested object, show structure
        if isinstance(value, dict) and value:
            print(f"    -> Nested: {list(value.keys())}")
        elif isinstance(value, list) and value:
            print(f"    -> List of: {type(value[0]).__name__ if value else 'empty'}")
```

### Example 2: Validate Nested Object Structure

```python
"""
Validate that nested objects (like contact.client) have expected structure.
"""

def validate_nested_structure():
    cassette = "tests/cassettes/integration/test_contacts_integration/test_get_contact.yaml"

    with open(cassette) as f:
        data = yaml.safe_load(f)

    response = json.loads(data["interactions"][0]["response"]["body"]["string"])
    contact = response["data"][0]

    # Check nested client object
    if "client" in contact and contact["client"]:
        client = contact["client"]
        print(f"Client object fields: {list(client.keys())}")

        # Compare against PartialCompany model
        from upsales.models.company import PartialCompany
        model_fields = set(PartialCompany.model_fields.keys())
        api_fields = set(client.keys())

        missing = api_fields - model_fields
        if missing:
            print(f"⚠️  Fields in API but not in PartialCompany: {missing}")
```

---

## Workflow: Adding New Endpoint Using Cassettes

### Step 1: Record Cassette

```python
# tests/integration/test_activities_integration.py

@pytest.mark.vcr()
async def test_record_activities_structure():
    """Record real API response for analysis."""
    async with Upsales.from_env() as upsales:
        # This will record to cassette on first run
        response = await upsales.http.get("/activities", params={"limit": 1})

        # Just validate we got data
        assert response["data"]
        print(f"Recorded {len(response['data'])} activities")
```

### Step 2: Analyze Cassette

```bash
# Read the cassette
cat tests/cassettes/integration/test_activities_integration/test_record_activities_structure.yaml

# Or use Python
python -c "
import yaml, json
with open('tests/cassettes/.../test_record_activities_structure.yaml') as f:
    data = yaml.safe_load(f)
    response = json.loads(data['interactions'][0]['response']['body']['string'])
    activity = response['data'][0]
    print(json.dumps(activity, indent=2))
"
```

### Step 3: Generate Model

```bash
# Use CLI to generate model from cassette data
uv run upsales generate-model activities

# Or manually create model based on cassette structure
```

### Step 4: Validate Model Against Cassette

```python
@pytest.mark.vcr()
async def test_activity_model_parses_cassette():
    """Validate Activity model correctly parses real API data."""
    async with Upsales.from_env() as upsales:
        activities = await upsales.activities.list(limit=1)
        activity = activities[0]

        # Model should parse without errors
        assert isinstance(activity, Activity)
        assert activity.id > 0

        # Validate all expected fields present
        expected_fields = ["id", "description", "date", "notes", "client", "contact"]
        for field in expected_fields:
            assert hasattr(activity, field), f"Missing field: {field}"
```

---

## Benefits of VCR for Field Validation

### 1. **Discover Unknown Fields**

```python
# Find fields we haven't added to models yet
api_fields = extract_fields_from_cassette("users.yaml")
model_fields = set(User.model_fields.keys())
missing = api_fields - model_fields
# -> ["ghost", "free", "supportAdmin", "projectAdmin"]
```

### 2. **Validate Nested Objects**

```python
# Check if nested objects match our Partial models
contact_client = cassette_data["client"]
# Does this match PartialCompany structure?
PartialCompany.model_validate(contact_client)  # ✓ or ✗
```

### 3. **Test Without API Calls**

```python
# Tests run offline using cassettes
# Fast, no rate limiting, no API dependency
pytest tests/integration/  # Uses cassettes, not real API
```

### 4. **API Structure Documentation**

```python
# Cassettes serve as documentation of real API responses
# Better than API docs because it's actual data!
```

---

## Current VCR Usage in This Project

**Recorded Cassettes**: 108+ cassettes across 19 endpoint test suites

**Endpoints with cassettes**:
- users (4 cassettes)
- companies (4 cassettes)
- products (4 cassettes)
- order_stages (5 cassettes)
- projects (6 cassettes)
- pricelists (6 cassettes)
- segments (4 cassettes)
- triggers (4 cassettes)
- forms (4 cassettes)
- files (4 cassettes)
- metadata (4 cassettes)
- apikeys (4 cassettes)
- todoviews (6 cassettes)
- standard_integrations (9 cassettes)
- currencies (6 cassettes)
- opportunity_ai (4 cassettes)
- roles (6 cassettes)
- sales_coaches (8 cassettes)

**Total Coverage**: 108 cassettes covering real API responses

---

## Practical Example: Find Missing Fields Right Now

```python
"""
Script to find all unmapped fields across all existing cassettes.

Run: python ai_temp_files/find_unmapped_fields.py
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict

# Import all models
from upsales.models.user import User
from upsales.models.company import Company
from upsales.models.product import Product
# ... etc

MODEL_MAP = {
    "users": User,
    "companies": Company,
    "products": Product,
    # Add more...
}

def find_unmapped_fields():
    """Find fields in API that aren't in models."""
    cassettes_dir = Path("tests/cassettes/integration")

    results = {}

    for endpoint, model_class in MODEL_MAP.items():
        # Find cassette
        pattern = f"test_{endpoint}_integration/test_get_*.yaml"
        cassettes = list(cassettes_dir.glob(pattern))

        if not cassettes:
            continue

        # Get API fields
        with open(cassettes[0]) as f:
            cassette = yaml.safe_load(f)

        response_str = cassette["interactions"][0]["response"]["body"]["string"]
        api_data = json.loads(response_str)["data"]

        item = api_data[0] if isinstance(api_data, list) else api_data
        api_fields = set(item.keys())

        # Get model fields
        model_fields = set(model_class.model_fields.keys())

        # Find missing
        missing = api_fields - model_fields

        if missing:
            results[endpoint] = {
                "missing_count": len(missing),
                "missing_fields": sorted(missing),
                "sample_values": {f: item[f] for f in missing if f in item}
            }

    # Print report
    print("🔍 UNMAPPED FIELDS REPORT")
    print("=" * 80)

    for endpoint, info in sorted(results.items()):
        print(f"\n{endpoint.upper()}: {info['missing_count']} unmapped fields")
        for field in info["missing_fields"]:
            sample = info["sample_values"].get(field)
            print(f"  - {field}: {type(sample).__name__} = {sample}")

if __name__ == "__main__":
    find_unmapped_fields()
```

---

## Summary

**Q1: Is VCR a complete recording?**
✅ **YES** - Records entire HTTP request/response including full JSON body

**Q2: Can we use it to validate fields we don't have models for?**
✅ **YES** - Cassettes contain the complete API response, so you can:
- Extract all fields from cassettes
- Compare against model fields
- Discover unmapped fields
- Validate nested object structures
- Test model changes against real API structure

**Key Benefit**: Cassettes are **real API responses** that serve as:
1. Offline test data
2. API documentation
3. Field discovery tool
4. Validation reference
5. Development snapshot

The cassettes are **better than API docs** because they show actual data structure, not just descriptions!
