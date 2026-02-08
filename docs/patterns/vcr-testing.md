# VCR.py Integration Testing Guide

## Overview

VCR.py (Video Cassette Recorder) records real API responses and replays them in tests. This allows testing against actual API structure without hitting the API every time.

Benefits:
- Test against real API response structure
- No API calls after first recording
- Catches API changes (tests fail if structure changes)
- Fast tests (replay from disk)
- Works offline once recorded
- Filters sensitive data (tokens, passwords)
- Enables field discovery and validation

VCR.py records the complete HTTP interaction including request (method, URL, headers, body) and response (status, headers, complete body). The cassettes contain the real JSON structure from the API, making them perfect for discovering new fields, validating unmapped fields, and planning model enhancements.

## Setup

### VCR Configuration

VCR is configured in `tests/conftest.py` with:
- cassette_library_dir: `tests/cassettes/integration`
- record_mode: `once` (record once, then replay)
- Security filters: Tokens and passwords automatically redacted
- Match criteria: method, scheme, host, port, path

### Directory Structure

```
tests/
├── integration/           # Integration tests with VCR
│   ├── __init__.py
│   ├── test_users_integration.py
│   ├── test_companies_integration.py
│   ├── test_products_integration.py
│   └── test_all_models_integration.py
└── cassettes/            # Recorded API responses
    └── integration/
        ├── test_users_integration/
        │   ├── test_get_user_real_response.yaml
        │   └── ...
        ├── test_companies_integration/
        └── test_products_integration/
```

## Recording and Replaying Cassettes

### Prerequisites

1. Configure .env file with real credentials:
```env
UPSALES_TOKEN=your_actual_token
UPSALES_EMAIL=your_email@example.com
UPSALES_PASSWORD=your_password
UPSALES_ENABLE_FALLBACK_AUTH=true
```

2. Ensure API access works:
```bash
# Quick test
uv run python -c "
import asyncio
from upsales import Upsales

async def test():
    async with Upsales.from_env() as upsales:
        users = await upsales.users.list(limit=1)
        print(f'Works! Got {len(users)} users')

asyncio.run(test())
"
```

### Recording Cassettes (First Run)

Run integration tests to record real API responses:

```bash
# Record all integration tests
uv run pytest tests/integration/ -v

# Record specific test
uv run pytest tests/integration/test_users_integration.py::test_get_user_real_response -v

# Record by module
uv run pytest tests/integration/test_users_integration.py -v
```

First run:
1. Makes real API calls
2. Saves responses to `tests/cassettes/integration/*.yaml`
3. Filters sensitive data (tokens become "REDACTED")

### Replaying Cassettes (Subsequent Runs)

Once cassettes exist, tests use them automatically:

```bash
# NO API calls made - uses cassettes
uv run pytest tests/integration/ -v
```

Benefits:
- Fast (reads from disk, no network)
- Secure (no real tokens used)
- Works offline
- Consistent results every time

### Re-recording Cassettes

When API changes or you need fresh data:

```bash
# Delete old cassette
rm tests/cassettes/integration/test_users_integration/test_get_user_real_response.yaml

# Re-run test to record new response
uv run pytest tests/integration/test_users_integration.py::test_get_user_real_response -v
```

Or delete all and re-record:
```bash
rm -r tests/cassettes/integration/*
uv run pytest tests/integration/ -v
```

## Integration Test Examples

### Example 1: Test Model Parsing

```python
import pytest
import vcr
from upsales import Upsales

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    filter_headers=[("cookie", "REDACTED")],
)

@pytest.mark.asyncio
@my_vcr.use_cassette("test_users/test_get_user.yaml")
async def test_get_user():
    """Test User model parses real API response."""
    async with Upsales.from_env() as upsales:
        users = await upsales.users.list(limit=1)
        user = users[0]

        # Validate model fields
        assert isinstance(user.id, int)
        assert isinstance(user.name, str)
        assert user.email == user.email.lower()  # EmailStr validator

        # Validate computed fields
        assert isinstance(user.is_active, bool)
        assert isinstance(user.is_admin, bool)
```

### Example 2: Test Validators

```python
@pytest.mark.asyncio
@my_vcr.use_cassette("test_users/test_validators.yaml")
async def test_binary_flag_validator_with_real_data():
    """Test BinaryFlag validator works with real API data."""
    async with Upsales.from_env() as upsales:
        users = await upsales.users.list(limit=10)

        for user in users:
            # All binary flags should be 0 or 1
            assert user.active in (0, 1)
            assert user.administrator in (0, 1)
            # ... validates our BinaryFlag validator works!
```

### Example 3: Test Computed Fields

```python
@pytest.mark.asyncio
@my_vcr.use_cassette("test_products/test_profit_margin.yaml")
async def test_profit_margin_calculation():
    """Test profit_margin computed field with real product data."""
    async with Upsales.from_env() as upsales:
        products = await upsales.products.list(limit=10)

        for product in products:
            # Validate profit margin calculation
            if product.listPrice > 0:
                expected = ((product.listPrice - product.purchaseCost) / product.listPrice) * 100
                assert abs(product.profit_margin - expected) < 0.01
```

## Field Validation and Discovery

### Extracting Fields from Cassettes

Cassettes contain the complete API response, making them perfect for field discovery and validation.

#### Method 1: Read Cassette Directly (Python Script)

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

#### Method 2: Use Cassettes in Tests

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
            print(f"Found unmapped field: {field}")
            print(f"  Type: {type(contact_data[field])}")
            print(f"  Sample: {contact_data[field]}")
```

#### Method 3: Compare Model vs API Response

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

    print("\nField Analysis:")
    print(f"  API returns: {len(api_fields)} fields")
    print(f"  Model has: {len(model_fields)} fields")

    if missing_in_model:
        print(f"\nFields in API but not in model ({len(missing_in_model)}):")
        for field in sorted(missing_in_model):
            print(f"  - {field}: {type(api_data[field]).__name__}")

    if missing_in_api:
        print(f"\nFields in model but not in API ({len(missing_in_api)}):")
        for field in sorted(missing_in_api):
            print(f"  - {field}")
```

### Workflow: Adding New Endpoint Using Cassettes

#### Step 1: Record Cassette

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

#### Step 2: Analyze Cassette

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

#### Step 3: Generate Model

```bash
# Use CLI to generate model from cassette data
uv run upsales generate-model activities

# Or manually create model based on cassette structure
```

#### Step 4: Validate Model Against Cassette

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

### Practical Example: Find Unmapped Fields Across All Cassettes

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
    print("UNMAPPED FIELDS REPORT")
    print("=" * 80)

    for endpoint, info in sorted(results.items()):
        print(f"\n{endpoint.upper()}: {info['missing_count']} unmapped fields")
        for field in info["missing_fields"]:
            sample = info["sample_values"].get(field)
            print(f"  - {field}: {type(sample).__name__} = {sample}")

if __name__ == "__main__":
    find_unmapped_fields()
```

### Benefits of VCR for Field Validation

1. **Discover Unknown Fields**

```python
# Find fields we haven't added to models yet
api_fields = extract_fields_from_cassette("users.yaml")
model_fields = set(User.model_fields.keys())
missing = api_fields - model_fields
# -> ["ghost", "free", "supportAdmin", "projectAdmin"]
```

2. **Validate Nested Objects**

```python
# Check if nested objects match our Partial models
contact_client = cassette_data["client"]
# Does this match PartialCompany structure?
PartialCompany.model_validate(contact_client)  # Success or error
```

3. **Test Without API Calls**

```python
# Tests run offline using cassettes
# Fast, no rate limiting, no API dependency
pytest tests/integration/  # Uses cassettes, not real API
```

4. **API Structure Documentation**

Cassettes serve as documentation of real API responses - better than API docs because they show actual data structure, not just descriptions.

## Security

### Sensitive Data Filtering

VCR configuration automatically filters:
- API tokens: `Cookie: token=xxx` becomes `Cookie: REDACTED`
- Passwords: POST data passwords become `REDACTED`
- Emails: POST data emails become `REDACTED` (in auth requests)

Cassette files are safe to commit to git!

### Cassette File Format

Example: `tests/cassettes/integration/test_users/test_get_user.yaml`

```yaml
version: 1
interactions:
- request:
    method: GET
    uri: https://power.upsales.com/api/v2/users
    headers:
      Cookie: REDACTED  # Token filtered!
    query: limit=1&offset=0
  response:
    status:
      code: 200
      message: OK
    headers:
      content-type: application/json
    body:
      string: '{"error":null,"metadata":{"total":10,"limit":1,"offset":0},"data":[{"id":1,"name":"John Doe","email":"john@example.com","active":1,"administrator":1,...}]}'
```

## Best Practices

### Use Descriptive Cassette Names

```python
# Good - clear what's being tested
@my_vcr.use_cassette("test_users/test_list_active_users.yaml")

# Bad - unclear
@my_vcr.use_cassette("test1.yaml")
```

### One Cassette Per Test

```python
# Each test has own cassette
@my_vcr.use_cassette("users/test_get.yaml")
async def test_get_user(): ...

@my_vcr.use_cassette("users/test_list.yaml")
async def test_list_users(): ...
```

### Test Different Scenarios

```python
# Test success case
@my_vcr.use_cassette("users/test_get_success.yaml")
async def test_get_user_success(): ...

# Test not found case
@my_vcr.use_cassette("users/test_get_not_found.yaml")
async def test_get_user_not_found(): ...
```

### Organize Cassettes by Module

```
cassettes/integration/
├── test_users_integration/
│   ├── test_get_user.yaml
│   ├── test_list_users.yaml
│   └── test_update_user.yaml
├── test_companies_integration/
│   └── ...
└── test_products_integration/
    └── ...
```

## Troubleshooting

### Issue: Tests Make Real API Calls Every Time

Solution: Cassettes not found. Check:
1. Cassette directory exists: `tests/cassettes/integration/`
2. Cassette file exists for your test
3. Cassette path matches decorator: `@my_vcr.use_cassette("path/to/cassette.yaml")`

### Issue: "Could not deserialize" Error

Solution: API response structure changed.
1. Delete old cassette
2. Re-record with new structure
3. Update model if fields changed

### Issue: Sensitive Data in Cassettes

Solution: Check VCR filter configuration.
1. Verify filters in conftest.py
2. Check cassette YAML - should show "REDACTED"
3. Add more filters if needed

## Summary

VCR.py provides complete HTTP recording and replay capabilities that are essential for:
- Testing models against real API structure
- Discovering unmapped fields
- Validating field types and nested structures
- Running tests offline without API dependencies
- Documenting actual API responses

Cassettes contain the complete API response including all fields, making them perfect for field discovery and validation work. They're better than API documentation because they show actual data structure with real values.

To start recording:
1. Configure `.env` with valid credentials
2. Run `uv run pytest tests/integration/ -v`
3. Cassettes saved to `tests/cassettes/integration/`
4. Commit cassettes to git (safe - filtered)
5. Tests now run offline with consistent results

Integration tests validate:
- Model parsing with real API data
- Pydantic v2 validators work correctly
- Computed fields calculate properly
- Serialization excludes frozen fields
- Resource managers return correct types
- Field coverage and API completeness
