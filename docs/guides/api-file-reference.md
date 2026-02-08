# API Endpoints File Reference

**File**: `api_endpoints_with_fields.json` (root directory)
**Endpoints**: 167 total
**Purpose**: Fast lookup for field requirements before implementation

---

## Overview

The `api_endpoints_with_fields.json` file documents all 167 Upsales API endpoints with complete field information for GET, POST, PUT, and DELETE operations. This file serves as a starting point for discovering:

- Required fields for CREATE operations
- Optional fields for CREATE operations
- Updatable fields for PUT operations
- Read-only fields that cannot be modified
- Field types, formats, and constraints
- Nested object structures

---

## Quick Commands

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

## Common Queries

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

### Before Implementation Checklist
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

## Common Patterns

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

## Real Examples

### Example 1: Orders
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

**Interpretation**: Complex CREATE operation requiring nested objects and arrays

### Example 2: Contacts
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

**Interpretation**: Simple CREATE with email and company reference

### Example 3: Accounts
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.accounts.methods.POST.required'
```

**Output**:
```json
[
  {"field": "name", "type": "string", "maxLength": 100}
]
```

**Interpretation**: Very simple CREATE, only name required

---

## Quick Reference Table

| Endpoint | Required Fields (Count) | Has Nested Objects | Complexity |
|----------|-------------------------|-------------------|------------|
| orders | 5 | Yes (4 nested) | High |
| opportunities | 5 | Yes (same as orders) | High |
| agreements | 9 | Yes (3 nested) | High |
| contacts | 2 | Yes (1 nested) | Low |
| accounts | 1 | No | Very Low |
| activities | 4 | Yes (1-2 nested) | Medium |
| tickets | 5 | Yes | Medium |
| events | 3 | Yes | Low |

---

## Workflow Integration

### Step 0: Consult API File
```bash
# Quick check before implementation
ENDPOINT="contacts"
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.POST.required"
```

### Step 1: Generate Model
```bash
uv run upsales generate-model $ENDPOINT --partial
```

### Step 2: Record VCR Cassette
```bash
# Create test, run to record real API responses
uv run pytest tests/integration/test_${ENDPOINT}_integration.py -v
```

### Step 3: Verify Requirements
```python
# Test CREATE with fields from API file
new_item = await upsales.endpoint.create(**api_file_required_fields)
```

### Step 4: Document Findings
Update `docs/endpoint-map.md` with verification status:
```markdown
- CREATE Verified
- Required fields: [list from API file]
- Notes: [any discrepancies found]
```

### Time Savings

**Old Workflow** (trial-and-error):
1. Generate model
2. Trial-and-error test CREATE
3. Discover required fields through failures
4. Repeat until success

**New Workflow** (with API file):
1. Consult API file for requirements
2. Test with expected fields
3. Verify (usually succeeds first try)

**Estimated savings**: 30 minutes per endpoint with CREATE operations

---

## Important Caveats

### 1. Use as Guide, Not Gospel
The API file is a starting point, not final authority. Always verify with VCR testing and real API responses before trusting field designations.

### 2. Known Limitations
- Optional field defaults may differ from API file
- Conditional requirements may not be fully documented
- Field constraints may be incomplete
- Edge cases may not be covered

### 3. Nested Objects Pattern
For CREATE operations, nested objects typically need minimal structure:
- Correct: `{"id": 10}`
- Incorrect: `{"id": 10, "name": "...", "email": "..."}`

### 4. Date Formats Matter
Date formats are strict:
- Required format: "YYYY-MM-DD"
- Example: "2025-11-07"

### 5. Read-Only Fields
Read-only fields won't appear in POST requirements. Use `PUT.readOnly` to identify fields to mark with `Field(frozen=True)` in models.

---

## Strategic Insights

### The Nested Required Fields Pattern
From API file analysis:
- Orders: 5 required fields, 4 are nested objects
- Agreements: 9 required fields, 3 are nested objects
- Contacts: 2 required fields, 1 is nested object
- Activities: 4 required fields, 1-2 are nested objects

**Pattern**: `{"id": number}` is the standard minimal structure for nested references

### Most Endpoints Are Simple
- accounts: Only 1 required field (name)
- Many configuration endpoints: 1-2 required fields
- Complex endpoints (orders, agreements) are the minority

**Implication**: After implementing complex endpoints, most others are quick

### CREATE Operations Are Priority
With BaseResource providing GET/UPDATE/DELETE automatically:
- GET: Works by default
- UPDATE: Can be tested incrementally
- DELETE: Low risk (just needs ID)
- CREATE: High risk (missing required fields = failure)

**Focus**: Verify CREATE first, others follow naturally

---

## Maintenance

### Keeping Current
- Source: Upsales GitHub codebase
- Refresh frequency: Quarterly or when major API changes announced
- Track discrepancies in endpoint-map.md

### Tracking Accuracy
When verification finds API file inaccuracies:
1. Document in endpoint-map.md with actual requirements
2. Note common patterns of discrepancies
3. Use VCR cassette as source of truth
