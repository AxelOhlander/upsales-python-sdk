# Testing Scripts

This directory contains testing utilities for the Upsales SDK.

## Available Scripts

### test_required_create_fields.py ⭐ NEW
**Test which fields are REQUIRED vs OPTIONAL when creating resources**

```bash
python scripts/test_required_create_fields.py orders
python scripts/test_required_create_fields.py contacts
python scripts/test_required_create_fields.py activities
```

**Purpose**: Discover required fields for POST (create) operations
**Warning**: Creates and deletes test data! Use test/sandbox environment only!

**How it works**:
1. Loads expected fields from `api_endpoints_with_fields.json`
2. Creates test object with ALL fields (baseline)
3. Removes one field at a time and tests creation
4. If creation fails → field is REQUIRED
5. If creation succeeds → field is OPTIONAL

**Output**:
- ✅ REQUIRED fields (creation fails without them)
- ⚠️ OPTIONAL fields (creation succeeds without them)
- 📋 TypedDict template for {Model}CreateFields
- 💡 Example usage code
- 🔍 Nested object structure details

**Use when**:
- Adding new endpoint with CREATE support
- Verifying CREATE requirements for existing endpoints
- Documenting nested required fields pattern
- Creating {Model}CreateFields TypedDict

**Example Output**:
```
✅ REQUIRED: client (object with {"id": number})
✅ REQUIRED: user (object with {"id": number})
✅ REQUIRED: date (string, YYYY-MM-DD)
⚠️ OPTIONAL: description (string)

📋 Minimal required fields:
{
  "client": {"id": 123},
  "user": {"id": 10},
  "date": "2025-01-15"
}
```

---

### test_required_update_fields.py
**Test which fields are REQUIRED vs OPTIONAL when updating resources**

```bash
python scripts/test_required_update_fields.py orderStages
python scripts/test_required_update_fields.py users
```

**Purpose**: Discover required fields for PUT/PATCH (update) operations
**Warning**: Makes real API updates! Use test/sandbox environment only!

**Output**:
- ✅ Editable + Required (must include in every update)
- ✅ Editable + Optional (can omit from updates)
- ❌ Read-only fields

**Use when**:
- Verifying UPDATE requirements
- Documenting required fields like "probability" for OrderStages

---

### test_field_editability.py
**Test which fields can be updated via the API**

```bash
python scripts/test_field_editability.py users
python scripts/test_field_editability.py companies 123
```

**Purpose**: Validate frozen fields and TypedDict accuracy for updates
**Warning**: Makes real API updates! Use test/sandbox environment only!

**Output**:
- ✅ Editable fields
- ❌ Read-only fields
- ⚠️ Warnings for model mismatches

**Use when**:
- Adding new endpoint
- Validating existing models
- Updating frozen field definitions

## Best Practices

1. **Use test environment** - Don't run against production data
2. **Backup data** - Have a way to restore if needed
3. **Review results** - Don't blindly trust, verify makes sense
4. **Update models** - Keep frozen fields accurate
5. **Re-test** - After model changes, re-run to verify

## Script Comparison

| Script | Operation | Tests | Creates Data | Output |
|--------|-----------|-------|--------------|--------|
| `test_required_create_fields.py` | **CREATE (POST)** | Required vs Optional for creation | ✅ Yes (then deletes) | TypedDict for CreateFields |
| `test_required_update_fields.py` | **UPDATE (PUT)** | Required vs Optional for updates | ❌ No (updates existing) | Required update fields |
| `test_field_editability.py` | **UPDATE (PUT)** | Editable vs Read-only | ❌ No (updates existing) | Frozen field list |

## When to Use Which Script

### Use `test_required_create_fields.py` when:
- ✅ Implementing a new endpoint with CREATE support
- ✅ Verifying what fields are needed to create a resource
- ✅ Documenting nested required fields (e.g., `user: {"id": 10}`)
- ✅ Creating `{Model}CreateFields` TypedDict
- ✅ Following the "nested required fields pattern" (like Orders)

### Use `test_required_update_fields.py` when:
- ✅ Verifying UPDATE operation requirements
- ✅ Checking if certain fields are always required in updates (like "probability" for OrderStages)
- ✅ Documenting update constraints

### Use `test_field_editability.py` when:
- ✅ Determining which fields should be `Field(frozen=True)`
- ✅ Validating existing model's frozen field definitions
- ✅ Updating `{Model}UpdateFields` TypedDict

## Recommended Workflow

### For New Endpoint with CREATE:
```bash
# 1. Check API file for expected fields
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required'

# 2. Test CREATE requirements (automated)
python scripts/test_required_create_fields.py endpoint_name

# 3. Create TypedDict from output
# Copy the generated TypedDict to upsales/models/endpoint_name.py

# 4. Add integration test
# Test CREATE with minimal required fields

# 5. Record VCR cassette
uv run pytest tests/integration/test_endpoint_integration.py -v
```

### For Existing Endpoint Verification:
```bash
# 1. Test CREATE requirements
python scripts/test_required_create_fields.py endpoint_name

# 2. Test UPDATE requirements
python scripts/test_required_update_fields.py endpoint_name

# 3. Test field editability
python scripts/test_field_editability.py endpoint_name

# 4. Update model based on findings
# Add CreateFields TypedDict, update frozen fields, etc.
```

## See Also

- `docs/guides/testing-field-capabilities.md` - Complete testing guide
- `docs/guides/adding-endpoints.md` - Endpoint addition workflow
- `docs/patterns/nested-required-fields.md` - Nested required fields pattern
- `api_endpoints_with_fields.json` - Expected field specifications (167 endpoints)
