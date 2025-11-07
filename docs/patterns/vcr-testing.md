# VCR.py Integration Testing Guide

**Status**: ✅ Infrastructure Ready
**Setup**: Complete, needs .env configuration to record cassettes

---

## Overview

VCR.py (Video Cassette Recorder) records real API responses and replays them in tests. This allows testing against actual API structure without hitting the API every time.

**Benefits**:
- ✅ Test against real API response structure
- ✅ No API calls after first recording
- ✅ Catches API changes (tests fail if structure changes)
- ✅ Fast tests (replay from disk)
- ✅ Works offline once recorded
- ✅ Filters sensitive data (tokens, passwords)

---

## Setup Complete

### 1. VCR Configuration in conftest.py ✅

**File**: `tests/conftest.py`

VCR is configured with:
- **cassette_library_dir**: `tests/cassettes/integration`
- **record_mode**: `once` (record once, then replay)
- **Security filters**: Tokens and passwords automatically redacted
- **Match criteria**: method, scheme, host, port, path

### 2. Integration Tests Created ✅

**Files**:
- `tests/integration/test_users_integration.py` - 4 tests
- `tests/integration/test_companies_integration.py` - 4 tests (template)
- `tests/integration/test_products_integration.py` - 5 tests (template)
- `tests/integration/test_all_models_integration.py` - 5 cross-model tests

### 3. Directory Structure ✅

```
tests/
├── integration/           # Integration tests with VCR
│   ├── __init__.py
│   ├── test_users_integration.py
│   ├── test_companies_integration.py
│   ├── test_products_integration.py
│   └── test_all_models_integration.py
└── cassettes/            # Recorded API responses
    └── integration/      # (created on first run)
        ├── test_users_integration/
        │   ├── test_get_user_real_response.yaml
        │   └── ...
        ├── test_companies_integration/
        └── test_products_integration/
```

---

## How to Use

### Prerequisites

1. **Configure .env file** with real credentials:
```env
UPSALES_TOKEN=your_actual_token
UPSALES_EMAIL=your_email@example.com
UPSALES_PASSWORD=your_password
UPSALES_ENABLE_FALLBACK_AUTH=true
```

2. **Ensure API access** works:
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

---

### Recording Cassettes (First Run)

**Run integration tests** to record real API responses:

```bash
# Record all integration tests
uv run pytest tests/integration/ -v

# Record specific test
uv run pytest tests/integration/test_users_integration.py::test_get_user_real_response -v

# Record by module
uv run pytest tests/integration/test_users_integration.py -v
```

**First run**:
1. Makes real API calls
2. Saves responses to `tests/cassettes/integration/*.yaml`
3. Filters sensitive data (tokens → "REDACTED")

**Cassette files created**:
```
tests/cassettes/integration/
└── test_users_integration/
    ├── test_get_user_real_response.yaml
    ├── test_list_users_real_response.yaml
    ├── test_user_computed_fields_with_real_data.yaml
    └── test_user_custom_fields_with_real_data.yaml
```

---

### Replaying Cassettes (Subsequent Runs)

Once cassettes exist, tests use them automatically:

```bash
# NO API calls made - uses cassettes
uv run pytest tests/integration/ -v
```

**Benefits**:
- ⚡ Fast (reads from disk, no network)
- 🔒 Secure (no real tokens used)
- 📴 Works offline
- 🔄 Consistent results every time

---

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

---

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

---

## Security

### Sensitive Data Filtering

VCR configuration automatically filters:
- ✅ **API tokens**: `Cookie: token=xxx` → `Cookie: REDACTED`
- ✅ **Passwords**: POST data passwords → `REDACTED`
- ✅ **Emails**: POST data emails → `REDACTED` (in auth requests)

**Cassette files are safe to commit to git!**

---

## Cassette File Format

**Example**: `tests/cassettes/integration/test_users/test_get_user.yaml`

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

**Safe to commit**: No sensitive data!

---

## Best Practices

### 1. Use Descriptive Cassette Names

```python
# ✅ Good - clear what's being tested
@my_vcr.use_cassette("test_users/test_list_active_users.yaml")

# ❌ Bad - unclear
@my_vcr.use_cassette("test1.yaml")
```

### 2. One Cassette Per Test

```python
# ✅ Each test has own cassette
@my_vcr.use_cassette("users/test_get.yaml")
async def test_get_user(): ...

@my_vcr.use_cassette("users/test_list.yaml")
async def test_list_users(): ...
```

### 3. Test Different Scenarios

```python
# Test success case
@my_vcr.use_cassette("users/test_get_success.yaml")
async def test_get_user_success(): ...

# Test not found case
@my_vcr.use_cassette("users/test_get_not_found.yaml")
async def test_get_user_not_found(): ...
```

### 4. Organize Cassettes by Module

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

---

## Current Status

### ✅ What's Ready
- VCR configuration in `tests/conftest.py`
- Integration test templates created (18 tests total)
- Directory structure created
- Security filters configured
- Documentation complete

### ⏳ What's Needed to Record
- Valid .env file with working credentials
- API access from test environment
- Run: `uv run pytest tests/integration/ -v`

### 🎯 Once Recorded
- Commit cassettes to git (safe - filtered)
- Tests run offline forever
- No API calls needed
- Fast, consistent results

---

## Troubleshooting

### Issue: Tests Make Real API Calls Every Time

**Solution**: Cassettes not found. Check:
1. Cassette directory exists: `tests/cassettes/integration/`
2. Cassette file exists for your test
3. Cassette path matches decorator: `@my_vcr.use_cassette("path/to/cassette.yaml")`

### Issue: "Could not deserialize" Error

**Solution**: API response structure changed.
1. Delete old cassette
2. Re-record with new structure
3. Update model if fields changed

### Issue: Sensitive Data in Cassettes

**Solution**: Check VCR filter configuration.
1. Verify filters in conftest.py
2. Check cassette YAML - should show "REDACTED"
3. Add more filters if needed

---

## Alternative: pytest-recording Plugin

If you prefer pytest integration:

```bash
# Install
uv add --dev pytest-recording

# Configure in pyproject.toml
[tool.pytest.ini_options]
vcr_record_mode = "once"
```

Then use:
```python
@pytest.mark.vcr  # No parentheses, no cassette path needed
async def test_something():
    # Cassette path auto-generated from test name
    ...
```

---

## Summary

**VCR.py infrastructure is complete and ready to use!**

To start recording:
1. Configure `.env` with valid credentials
2. Run `uv run pytest tests/integration/ -v`
3. Cassettes saved to `tests/cassettes/integration/`
4. Commit cassettes to git
5. Tests now run offline forever

**18 integration tests ready** to validate:
- Model parsing with real API data
- Pydantic v2 validators work correctly
- Computed fields calculate properly
- Serialization excludes frozen fields
- Resource managers return correct types

See integration test files for examples!

---

**Created**: 2025-11-01
**Status**: ✅ Ready (needs .env to record)
**Tests Created**: 18
**Documentation**: Complete
