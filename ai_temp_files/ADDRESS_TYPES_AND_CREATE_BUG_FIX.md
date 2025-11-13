# Address Types Enum & CREATE Script Bug Fix

**Date**: 2025-11-07

---

## ✅ Created: AddressType Enum

### New File: `upsales/models/address_types.py`

**Contains**:
```python
from enum import Enum

class AddressType(str, Enum):
    MAIL = "Mail"          # Mailing/postal address
    VISIT = "Visit"        # Physical visiting address
    POSTAL = "Postal"      # Postal address
    BILLING = "Billing"    # Billing address
    DELIVERY = "Delivery"  # Delivery address
    OTHER = "Other"        # Miscellaneous

# Constant list
VALID_ADDRESS_TYPES = ["Mail", "Visit", "Postal", "Billing", "Delivery", "Other"]
```

**Exported in** `upsales/models/__init__.py`:
```python
from upsales.models.address_types import AddressType, VALID_ADDRESS_TYPES

__all__ = [
    ...
    "AddressType",
    "VALID_ADDRESS_TYPES",
    ...
]
```

---

## 🎯 Usage

### In User Code
```python
from upsales.models import AddressType

# Create company with typed address
new_company = await upsales.companies.create(
    name="ACME Corp",
    addresses=[{
        "type": AddressType.VISIT,  # Type-safe!
        "address": "123 Main St",
        "city": "New York",
        "country": "US"
    }]
)

# Check address type
if company.addresses.visit:
    print(f"Visit us at: {company.addresses.visit.city}")
```

### In Scripts/Testing
```python
from upsales.models.address_types import VALID_ADDRESS_TYPES
import random

# Generate random valid address type
address_type = random.choice(VALID_ADDRESS_TYPES)

# Validate user input
if user_address_type in VALID_ADDRESS_TYPES:
    # Valid type
    ...
```

---

## 🐛 CREATE Script Bug (FIXED)

### The Bug

**File**: `scripts/test_required_create_fields.py`
**Line**: 101 (original)

**Problem**: Script used placeholder values from `api_endpoints_with_fields.json` literally instead of converting them to actual test values.

**Example**:
```python
# API file structure:
{"id": "number"}

# Bug: Script sent this literally
sent = {"id": "number"}  # ❌ String "number" instead of int!

# API error:
"User id is not a number"
```

### The Fix

**Lines 100-131**: Added recursive conversion of placeholders:

```python
# Before (BUG):
if field_type == "array":
    return structure  # Returns [{"id": "number"}] literally!

# After (FIXED):
if field_type == "array":
    # Convert placeholders to actual values
    for k, v in item.items():
        if v == "number":
            converted[k] = 1  # ✅ Actual number!
        elif v == "string":
            if k == "type":  # Address type
                converted[k] = "Visit"  # ✅ Valid value!
            else:
                converted[k] = "test"
```

**Result**:
```python
# API file structure:
[{"address": "string", "type": "string", ...}]

# Script now generates:
[{"address": "test", "type": "Visit", ...}]  # ✅ Valid!
```

---

## 📊 Before vs After

### Before Fix
```bash
$ python scripts/test_required_create_fields.py accounts

❌ Baseline creation FAILED (status 400)
Response: {"error": "User id is not a number"}
```

**Sent to API**:
```json
{
  "users": [{"id": "number"}],  // ❌ Wrong!
  "addresses": [{"type": "string", ...}]  // ❌ Wrong!
}
```

### After Fix
```bash
$ python scripts/test_required_create_fields.py accounts

✅ Baseline creation SUCCEEDED
   Created ID: 43
   Status: 200

🗑️ Testing DELETE operation...
   ✅ DELETE succeeded (status 200)
   ✅ Verified deletion (GET returned 404)
```

**Sent to API**:
```json
{
  "users": [{"id": 1}],  // ✅ Actual number!
  "addresses": [{"type": "Visit", ...}]  // ✅ Valid type!
}
```

---

## 🎯 Why AddressType Enum is Important

### 1. **Type Safety**
```python
# With enum
address = {"type": AddressType.VISIT}  # IDE autocomplete!

# Without enum
address = {"type": "Vist"}  # ❌ Typo! No validation
```

### 2. **Documentation**
```python
# Clear valid values
VALID_ADDRESS_TYPES = ["Mail", "Visit", "Postal", "Billing", "Delivery", "Other"]

# Users know exactly what's valid
```

### 3. **Script Test Data Generation**
```python
# Before: Hardcoded or guessed
address_type = "test"  # ❌ Invalid!

# After: Use enum
from upsales.models.address_types import AddressType
address_type = AddressType.VISIT  # ✅ Valid!
```

### 4. **Validation**
```python
# Can validate user input
if user_type not in VALID_ADDRESS_TYPES:
    raise ValueError(f"Invalid address type. Must be one of: {VALID_ADDRESS_TYPES}")
```

---

## 📝 Address Types Discovered

**From sources**:

1. **AddressList properties** (implicit):
   - Mail, Visit, Postal, Billing, Delivery

2. **Real API data** (VCR cassettes):
   - Mail, Visit, Other

3. **Combined set**:
   - Mail ✅
   - Visit ✅
   - Postal ✅ (property exists, may be used)
   - Billing ✅ (property exists, may be used)
   - Delivery ✅ (property exists, may be used)
   - Other ✅ (seen in API)

---

## ✅ Summary

### What Was Fixed
1. ✅ Created `AddressType` enum with 6 valid types
2. ✅ Exported `AddressType` and `VALID_ADDRESS_TYPES` from models
3. ✅ Fixed `test_required_create_fields.py` to convert placeholders:
   - `{"id": "number"}` → `{"id": 1}`
   - `{"type": "string"}` → `{"type": "Visit"}`
4. ✅ CREATE script now works for accounts/companies

### Benefits
- ✅ Type-safe address creation
- ✅ Clear documentation of valid types
- ✅ Scripts can generate valid test data
- ✅ Users have autocomplete for address types

### Test Results
**CREATE script** (accounts):
- ✅ Baseline creation: PASSED
- ✅ DELETE verification: PASSED
- ✅ Required fields: name only
- ✅ Optional fields: 12 fields

---

**Your question led to creating a proper AddressType enum that will help users and scripts!** 🎯

---

**Last Updated**: 2025-11-07
**Files Created**: 1 (address_types.py)
**Scripts Fixed**: 1 (test_required_create_fields.py)
**Bug Status**: ✅ RESOLVED
