# Testing Scripts

This directory contains testing utilities for the Upsales SDK.

## Compact Mode (--compact)

All main scripts support `--compact` flag for AI agent workflows:

```bash
# Verbose output (default) - for humans
python scripts/test_required_create_fields.py orders

# Compact JSON output - for AI agents (saves ~90% tokens)
python scripts/test_required_create_fields.py orders --compact
python scripts/test_field_editability_bulk.py accounts --compact
```

**Compact mode benefits:**
- Outputs structured JSON only
- No decorative headers or dividers
- No generated code examples
- ~90% token reduction for AI agents

## Available Scripts

### test_required_create_fields.py ⭐ NEW
**Test which fields are REQUIRED vs OPTIONAL when creating resources**

```bash
python scripts/test_required_create_fields.py orders
python scripts/test_required_create_fields.py contacts --compact  # For AI agents
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

### test_field_editability_bulk.py ⭐ **RECOMMENDED**
**Test which fields actually update vs are silently ignored (bulk update approach)**

```bash
python scripts/test_field_editability_bulk.py accounts
python scripts/test_field_editability_bulk.py contacts --compact  # For AI agents
python scripts/test_field_editability_bulk.py orders
```

**Purpose**: Discover which fields are truly editable vs read-only by updating ALL fields in ONE request
**Warning**: Makes ONE bulk update to a real object! Use test/sandbox environment only!

**How it works**:
1. Gets an object (baseline)
2. **Updates ALL fields in ONE bulk request** ← More efficient!
3. Fetches updated object
4. Compares before vs after to see which fields actually changed

**Output**:
- ✅ EDITABLE: Field value changed (API updated it)
- ❌ READ-ONLY: Field ignored by API (should be frozen=True)
- ⚠️ UNEXPECTED: Field changed to different value (type conversion, truncation, etc.)
- 📋 Frozen field recommendations

**Benefits vs individual updates**:
- ✅ Only 1 API call instead of 80+
- ✅ Avoids rate limiting
- ✅ Avoids auth/token issues
- ✅ Faster (completes in seconds)
- ✅ More reliable results

**Use when**:
- ✅ Discovering which fields should be `Field(frozen=True)`
- ✅ Validating `{Model}UpdateFields` TypedDict completeness
- ✅ Testing actual update behavior (not just API acceptance)
- ✅ Verifying field editability for documentation

**Example Results**:
```
✅ EDITABLE: name (18 fields total)
❌ READ-ONLY: regDate, numberOfContacts, score (29 fields)
⚠️ UNEXPECTED: modDate (auto-updated to current timestamp)
```

---

### test_field_editability.py ⚠️ **LEGACY** (Use bulk version instead)
**Test which fields can be updated via the API (individual update approach)**

```bash
python scripts/test_field_editability.py users
python scripts/test_field_editability.py companies 123
```

**Purpose**: Validate frozen fields and TypedDict accuracy for updates
**Warning**: Makes 80+ individual API updates! Can hit rate limits and auth issues!

**Output**:
- ✅ Editable fields
- ❌ Read-only fields
- ⚠️ Warnings for model mismatches

**Limitation**: Tests one field at a time (slow, can cause rate limiting)

**Use when**:
- Legacy testing approach
- Prefer `test_field_editability_bulk.py` instead

## Best Practices

1. **Use test environment** - Don't run against production data
2. **Backup data** - Have a way to restore if needed
3. **Review results** - Don't blindly trust, verify makes sense
4. **Update models** - Keep frozen fields accurate
5. **Re-test** - After model changes, re-run to verify

## Script Comparison

| Script | Operation | Tests | Creates Data | Method | Output |
|--------|-----------|-------|--------------|--------|--------|
| `test_required_create_fields.py` | **CREATE (POST)** | Required vs Optional | ✅ Yes (deletes after) | Individual field tests | TypedDict for CreateFields |
| `test_required_update_fields.py` | **UPDATE (PUT)** | Required vs Optional | ❌ No | Omit each field | Required update fields |
| `test_field_editability_bulk.py` ⭐ | **UPDATE (PUT)** | Editable vs Read-only | ❌ No | **1 bulk update** | Frozen field recommendations |
| `test_field_editability.py` ⚠️ Legacy | **UPDATE (PUT)** | Editable vs Read-only | ❌ No | 80+ individual updates | Frozen field list |

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

### Use `test_field_editability_bulk.py` when: ⭐ **RECOMMENDED**
- ✅ Discovering which fields should be `Field(frozen=True)`
- ✅ Validating which fields API actually updates vs ignores
- ✅ Creating accurate `{Model}UpdateFields` TypedDict (only editable fields)
- ✅ Testing update behavior efficiently (one bulk call)

### Use `test_field_editability.py` when: ⚠️ **LEGACY**
- ⚠️ Only if you need individual field testing
- ⚠️ Prefer bulk version to avoid rate limits and auth issues

## Recommended Workflow

### For New Endpoint with CREATE:
```bash
# 0. Check API file for expected fields (2 min)
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required'

# 1. Test CREATE requirements (5 min - automated)
python scripts/test_required_create_fields.py endpoint_name

# 2. Test UPDATE requirements (3 min - automated)
python scripts/test_required_update_fields.py endpoint_name

# 3. Test field editability (5 min - automated, bulk update)
python scripts/test_field_editability_bulk.py endpoint_name

# 4. Apply results to model
# - Add {Model}CreateFields TypedDict (from step 1 output)
# - Mark frozen fields (from step 3 output)
# - Update {Model}UpdateFields with only editable fields (from step 3)

# 5. Add integration test
# Test CREATE with minimal required fields

# 6. Record VCR cassette
uv run pytest tests/integration/test_endpoint_integration.py -v
```

**Total Time**: ~15 minutes for complete field validation (was 60-90 min manual)

### For Existing Endpoint Verification:
```bash
# 1. Check API file expectations
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name'

# 2. Test CREATE requirements (5 min)
python scripts/test_required_create_fields.py endpoint_name

# 3. Test UPDATE requirements (3 min)
python scripts/test_required_update_fields.py endpoint_name

# 4. Test field editability with bulk update (5 min) ⭐ RECOMMENDED
python scripts/test_field_editability_bulk.py endpoint_name

# 5. Update model based on findings
# - Add {Model}CreateFields TypedDict (from step 2)
# - Mark frozen=True for read-only fields (from step 4)
# - Update {Model}UpdateFields with only editable fields (from step 4)
# - Add CREATE examples to model docstring
```

**Total Time**: ~15 minutes for complete validation

## See Also

- `docs/patterns/nested-required-fields.md` - Nested required fields pattern
- `docs/guides/api-file-reference.md` - API endpoints file reference
- `api_endpoints_with_fields.json` - Expected field specifications (167 endpoints)
