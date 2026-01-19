# api_endpoints_with_fields.json - Quick Reference

**File**: `api_endpoints_with_fields.json` (root directory)
**Endpoints**: 167 total
**Purpose**: Fast lookup for field requirements before implementation

---

## 🚀 Quick Commands

### List All Endpoints
```bash
cat api_endpoints_with_fields.json | jq '.endpoints | keys'
```

### Check Specific Endpoint
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name'
```

### Get Required Fields for CREATE
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required'
```

### Get Optional Fields for CREATE
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.optional'
```

### Get Updatable Fields
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.PUT.allowed'
```

### Get Read-Only Fields
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.PUT.readOnly'
```

### Get All Returned Fields
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.GET_list.returns'
```

---

## 📖 Common Queries

### Find Endpoints with CREATE Support
```bash
cat api_endpoints_with_fields.json | jq '.endpoints | to_entries[] |
  select(.value.methods.POST) | .key'
```

### Find Endpoints with UPDATE Support
```bash
cat api_endpoints_with_fields.json | jq '.endpoints | to_entries[] |
  select(.value.methods.PUT) | .key'
```

### Count Required Fields for an Endpoint
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required |
  length'
```

### Find Endpoints with Nested Required Fields
```bash
cat api_endpoints_with_fields.json | jq '.endpoints | to_entries[] |
  select(.value.methods.POST.required[]?.type == "object") | .key'
```

---

## 🎯 Before Implementing Any Endpoint

Run this checklist:

```bash
ENDPOINT="endpoint_name"

echo "=== $ENDPOINT Endpoint Analysis ==="

echo -e "\n1. Required for CREATE:"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.POST.required"

echo -e "\n2. Optional for CREATE:"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.POST.optional" | head -20

echo -e "\n3. Updatable fields (PUT):"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.PUT.allowed"

echo -e "\n4. Read-only fields:"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.PUT.readOnly"

echo -e "\n5. Returned by GET:"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.GET_list.returns"
```

---

## 📝 Common Patterns

### Pattern 1: Minimal Nested Structure
```json
{
  "field": "client",
  "type": "object",
  "structure": {"id": "number"}
}
```
**Interpretation**: Required nested object with just ID
**SDK Implementation**: `client: dict[str, int]` in CreateFields TypedDict

### Pattern 2: Array with Nested Objects
```json
{
  "field": "orderRow",
  "type": "array",
  "structure": [{"product": {"id": "number"}}]
}
```
**Interpretation**: Array of objects, each with nested product.id
**SDK Implementation**: `orderRow: list[dict[str, Any]]` in CreateFields

### Pattern 3: Date Format
```json
{
  "field": "date",
  "type": "string",
  "format": "YYYY-MM-DD"
}
```
**Interpretation**: Date string in ISO format
**SDK Implementation**: `date: str  # Required: 'YYYY-MM-DD'`

### Pattern 4: Conditional Requirements
```json
{
  "field": "date",
  "notes": "Optional for TODO/PHONE_CALL types"
}
```
**Interpretation**: Field may be optional under certain conditions
**SDK Implementation**: Document in docstring with conditions

---

## 🔍 Real Examples

### Example 1: Orders (Verified Accurate)
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.orders.methods.POST.required'
```

**Output**:
```json
[
  {"field": "client", "type": "object", "structure": {"id": "number"}},
  {"field": "user", "type": "object", "structure": {"id": "number"}},
  {"field": "stage", "type": "object", "structure": {"id": "number"}},
  {"field": "date", "type": "string", "format": "YYYY-MM-DD"},
  {"field": "orderRow", "type": "array", "structure": [{"product": {"id": "number"}}]}
]
```

**Verification**: ✅ 100% accurate (manually tested)

### Example 2: Contacts (To Be Verified)
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.contacts.methods.POST.required'
```

**Output**:
```json
[
  {"field": "email", "type": "string", "maxLength": 128},
  {"field": "client", "type": "object", "structure": {"id": "number"}}
]
```

**Next Step**: Verify with manual testing

### Example 3: Accounts (To Be Verified)
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.accounts.methods.POST.required'
```

**Output**:
```json
[
  {"field": "name", "type": "string", "maxLength": 100}
]
```

**Interpretation**: Only name required! Very simple.

---

## ⚡ Quick Reference Table

| Endpoint | Required Fields (Count) | Has Nested Objects | Complexity |
|----------|-------------------------|-------------------|------------|
| orders | 5 | Yes (4 nested) | High |
| opportunities | 5 | Yes (same as orders) | High |
| agreements | 9 | Yes (3 nested) | High |
| contacts | 2 | Yes (1 nested) | Low |
| accounts | 1 | No | Very Low |
| activities | 4 | Yes (1-2 nested) | Medium |
| appointments | ? | Likely yes | Medium |
| tickets | 5 | Yes | Medium |
| events | 3 | Yes | Low |
| products | ? | Likely no | Low |
| users | N/A | N/A | N/A (admin only) |

---

## 🛠️ Workflow Integration

### Step 0: Before Implementation
```bash
# Quick check
ENDPOINT="contacts"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.POST.required"
```

### Step 1: Generate Model
```bash
uv run upsales generate-model $ENDPOINT --partial
```

### Step 2: Record VCR
```bash
# Create test, run to record
uv run pytest tests/integration/test_${ENDPOINT}_integration.py -v
```

### Step 3: Verify Requirements
```python
# Test CREATE with fields from API file
new_item = await upsales.endpoint.create(**api_file_required_fields)
```

### Step 4: Document
```markdown
# Update endpoint-map.md
- ✅ CREATE Verified
- Required fields: [list from API file]
- Verification date: 2025-11-07
```

---

## ⚠️ Important Reminders

1. **API file is a guide, not gospel** - Always verify with VCR testing
2. **Nested objects need minimal structure** - `{"id": 10}` for CREATE
3. **Date formats matter** - "YYYY-MM-DD" is strict
4. **Optional != always optional** - Some have conditional requirements
5. **Read-only fields won't be in POST** - Use PUT.readOnly for frozen fields

---

## 📊 Statistics Tracking

As you verify endpoints, track in endpoint-map.md:

```bash
# Check current verification status
grep "✅ Verified" docs/endpoint-map.md | grep "CREATE" | wc -l

# Check coverage percentage
# (Implemented / 167) * 100
```

Current:
- CREATE Verified: 1/89 (1.1%)
- Overall Implemented: 35/167 (21%)

Target after Week 1:
- CREATE Verified: 6/89 (6.7%)
- Overall Implemented: 36/167 (21.6%)

---

**Last Updated**: 2025-11-07
**Maintained By**: Keep updated as verifications complete
