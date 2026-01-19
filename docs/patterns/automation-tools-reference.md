# Automation Tools - Quick Reference Card

**Date**: 2025-11-07
**Purpose**: Fast field validation for new endpoints

---

## 🚀 Complete Workflow (15 minutes total)

### Step 0: Check API File (2 min)
```bash
ENDPOINT="contacts"  # Change to your endpoint

# Required fields for CREATE
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.POST.required"

# Allowed fields for UPDATE
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.PUT.allowed"

# Read-only fields
cat api_endpoints_with_fields.json | jq ".endpoints.$ENDPOINT.methods.PUT.readOnly"
```

**Output**: Expected field requirements (verify with testing!)

---

### Step 1: Test CREATE Requirements (5 min)
```bash
python scripts/test_required_create_fields.py contacts
```

**What it does**:
- Creates test object with ALL fields
- Removes one field at a time and retests
- Reports REQUIRED vs OPTIONAL
- Generates `ContactCreateFields` TypedDict template
- Cleans up all test data

**Output Example**:
```
✅ REQUIRED: client (object with {"id": number})
⚠️ OPTIONAL: email
⚠️ OPTIONAL: name

📋 ContactCreateFields TypedDict:
class ContactCreateFields(TypedDict, total=False):
    client: dict[str, int]  # Required
    email: str  # Optional
    name: str  # Optional
```

**Copy the TypedDict** to `upsales/models/contacts.py`

---

### Step 2: Test UPDATE Requirements (3 min)
```bash
python scripts/test_required_update_fields.py contacts
```

**What it does**:
- Gets an object
- Tries updating WITHOUT each field
- Reports if field is REQUIRED (update fails) or OPTIONAL (update succeeds)

**Output Example**:
```
⚠️ REQUIRED fields (1):
   - probability (must include in every update)

✅ OPTIONAL fields (15):
   - name (can omit)
   - active (can omit)
   - ...
```

**Document any required fields** in model docstring

---

### Step 3: Test Field Editability (5 min) ⭐ **NEW & IMPROVED**
```bash
python scripts/test_field_editability_bulk.py contacts
```

**What it does**:
- Gets an object (baseline)
- **Updates ALL fields in ONE bulk request** ← Key improvement!
- Fetches updated object
- Compares: which fields changed vs stayed same

**Output Example**:
```
✅ EDITABLE (18 fields):
   - name (sent: "Test_EDIT", got: "Test_EDIT")
   - phone (sent: "+1-555-TEST", got: "+1-555-TEST")
   - active (sent: 0, got: 0)

❌ READ-ONLY (29 fields) - Mark frozen=True:
   - regDate (API ignored update)
   - score (calculated field, ignored)
   - numberOfContacts (calculated, ignored)

⚠️ UNEXPECTED (14 fields):
   - modDate (auto-updated to current timestamp)
```

**Use results to**:
1. Mark read-only fields: `Field(frozen=True)`
2. Update `{Model}UpdateFields` with only editable fields
3. Document special behaviors

---

## 📊 Script Comparison

| Script | What It Tests | API Calls | Time | Output |
|--------|---------------|-----------|------|--------|
| `test_required_create_fields.py` | Which fields needed for CREATE | ~10-15 | 5 min | CreateFields TypedDict |
| `test_required_update_fields.py` | Which fields needed for UPDATE | ~80 | 3 min | Required update fields |
| `test_field_editability_bulk.py` ⭐ | Which fields actually update | **1** | **5 min** | Frozen field list |
| `test_field_editability.py` ⚠️ | Which fields actually update | 80+ | 15+ min | Frozen field list |

**Recommendation**: Use the **bulk** version (1 call vs 80+)

---

## 🎯 Real Example: Contacts Endpoint

### Step 0: API File Check
```bash
$ cat api_endpoints_with_fields.json | jq '.endpoints.contacts.methods.POST.required'
[
  {"field": "email", "type": "string"},
  {"field": "client", "type": "object", "structure": {"id": "number"}}
]
```

### Step 1: Test CREATE
```bash
$ python scripts/test_required_create_fields.py contacts

✅ REQUIRED: client
⚠️ OPTIONAL: email (API file was WRONG!)
```

**Discovery**: Only `client.id` required (not email)!

### Step 2: Test UPDATE
```bash
$ python scripts/test_required_update_fields.py contacts

✅ OPTIONAL: All 40 fields (no required fields)
```

### Step 3: Test Editability
```bash
$ python scripts/test_field_editability_bulk.py contacts

✅ EDITABLE: name, email, phone, active (15 fields)
❌ READ-ONLY: regDate, score, hadActivity (25 fields)
```

**Total Time**: 13 minutes
**Result**: Complete field validation for Contacts endpoint

---

## 📝 Applying Results to Model

### From Step 1 (CREATE)
```python
class ContactCreateFields(TypedDict, total=False):
    """Required: client.id only (verified 2025-11-07)"""
    client: dict[str, int]  # Required
    email: str  # Optional (API file incorrect)
    name: str
    phone: str
    # ... other optional fields
```

### From Step 2 (UPDATE)
```python
# If any required fields found, document in model docstring:
"""
UPDATE requirements:
- probability: REQUIRED (must include in every update)
"""
```

### From Step 3 (Editability)
```python
# Mark read-only fields as frozen:
regDate: str = Field(frozen=True, description="...")
score: int = Field(frozen=True, description="...")  # Calculated
numberOfContacts: int = Field(frozen=True, description="...")  # Calculated

# Update TypedDict to include only editable fields:
class ContactUpdateFields(TypedDict, total=False):
    name: str  # Editable
    email: str  # Editable
    phone: str  # Editable
    active: int  # Editable
    # Don't include: regDate, score, numberOfContacts (frozen)
```

---

## 💡 Key Benefits

### Before Automation
- ⏱️ 60-90 minutes manual testing per endpoint
- ❓ Guessing which fields are required
- 🤔 Trial-and-error CREATE testing
- 🐌 80+ individual update calls
- ⚠️ Rate limiting issues
- ❌ Auth/token failures
- 🎲 Incomplete frozen field marking

### After Automation
- ⏱️ **15 minutes** with automation scripts
- ✅ **Exact required fields** discovered automatically
- ✅ **1 bulk update** instead of 80+
- ✅ **No rate limiting** (minimal API calls)
- ✅ **Reliable results** (single request)
- ✅ **Complete frozen field list** from real testing

**Time Savings**: 45-75 minutes per endpoint × 89 endpoints = **67-112 hours saved!**

---

## 🔍 Discovered Patterns

### From Testing Contacts
- Only `client.id` required (api_endpoints_with_fields.json was wrong about email)
- 15 editable fields
- 25 read-only fields (score, regDate, had*/has* tracking)

### From Testing Accounts
- Only `name` required (simplest CREATE!)
- 18 editable fields
- 29 read-only fields (all had*/has*, calculated counts, etc.)
- 14 fields with special behavior (type conversion, auto-updates)

### From Testing Orders
- 5 required fields with nested structures
- Complex nested required fields pattern
- orderRow requires array with product.id

---

## 📚 Documentation Updated

### Files Updated (2025-11-07)
- ✅ `docs/guides/adding-endpoints-ai.md` - Added Steps 0, 3A, 3B, 3C with automation
- ✅ `scripts/README.md` - Complete documentation of all 4 scripts
- ✅ Both include workflow examples and time estimates

### New Scripts Created
- ✅ `scripts/test_required_create_fields.py` (280 lines)
- ✅ `scripts/test_field_editability_bulk.py` (260 lines)

### Reference Documents
- ✅ `ai_temp_files/ACCOUNTS_FIELD_VALIDATION_RESULTS.md`
- ✅ `ai_temp_files/COMPANIES_COMPLETE_VALIDATION_SUMMARY.md`
- ✅ This quick reference

---

## 🎯 Next Endpoint Checklist

For any new endpoint:

- [ ] `cat api_endpoints_with_fields.json | jq '.endpoints.{endpoint}'`
- [ ] `python scripts/test_required_create_fields.py {endpoint}`
- [ ] `python scripts/test_required_update_fields.py {endpoint}`
- [ ] `python scripts/test_field_editability_bulk.py {endpoint}`
- [ ] Apply results to model (CreateFields, frozen fields, UpdateFields)
- [ ] Add examples to model docstring
- [ ] Generate resource
- [ ] Add integration tests
- [ ] Update endpoint-map.md with ✅ Verified

**Estimated Time**: 45-60 minutes with automation

---

**Last Updated**: 2025-11-07
**Scripts Location**: `scripts/`
**Documentation**: `docs/guides/adding-endpoints-ai.md`
