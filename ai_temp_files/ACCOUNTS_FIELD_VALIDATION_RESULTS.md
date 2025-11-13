# Accounts (Companies) Field Validation Results

**Date**: 2025-11-07
**Endpoint**: `/api/v2/accounts`
**SDK Resource**: `upsales.companies`
**Model**: `Company`, `PartialCompany`

---

## 🎯 Key Findings

### CREATE (POST) Requirements ✅ VERIFIED

**Required Fields**: **1 field only!**
- `name` (string) - Company name

**Optional Fields**: All others (users, addresses, phone, etc.)

**Test Results**:
```
✅ CREATE with only 'name': SUCCESS (Created ID: 36)
✅ CREATE with optional fields: SUCCESS (Created ID: 37)
```

**Simplicity**: Accounts/Companies is the **simplest CREATE operation** - even simpler than contacts!

---

### UPDATE (PUT) Requirements ✅ VERIFIED

**Required Fields**: **NONE!**

**All 85 fields are OPTIONAL** for updates, including:
- name
- phone
- addresses
- users
- custom
- All other fields

**Read-Only Fields**: Only `id` (handled by frozen=True)

**Test Results**:
```
✅ Tested 85 fields - ALL optional for updates
✅ Full object update works (baseline confirmed)
✅ Can update with any subset of fields
```

---

## 📋 CompanyCreateFields TypedDict

```python
class CompanyCreateFields(TypedDict, total=False):
    """
    Required and optional fields for creating a new Company (Account).

    REQUIRED fields (verified 2025-11-07):
    - name: Company name (only required field!)

    IMPORTANT: Only name is required! This is the simplest CREATE operation.
    All other fields (email, phone, addresses, users, etc.) are optional.

    Example Minimal:
        >>> new_company = await upsales.companies.create(
        ...     name="ACME Corporation"
        ... )

    Example With Optional Fields:
        >>> detailed_company = await upsales.companies.create(
        ...     name="ACME Corporation",
        ...     phone="+1-555-0123",
        ...     webpage="www.acme.com",
        ...     active=1,
        ...     orgNo="123456789",
        ...     addresses=[
        ...         {
        ...             "address": "123 Main St",
        ...             "city": "New York",
        ...             "zipcode": "10001",
        ...             "country": "US",
        ...             "type": "Visit"
        ...         }
        ...     ],
        ...     users=[{"id": 10}],  # Account managers
        ...     categories=[{"id": 5}],
        ... )
    """

    # REQUIRED field
    name: str  # Required: Company name

    # OPTIONAL fields - Basic info
    phone: str
    phoneCountryCode: str
    fax: str
    webpage: str
    notes: str
    orgNo: str
    active: int  # 0 or 1

    # OPTIONAL fields - Relationships
    parent: dict[str, int]  # Parent company: {"id": parent_id}
    operationalAccount: dict[str, int]  # Operational account: {"id": account_id}
    users: list[dict[str, int]]  # Account managers: [{"id": user_id}, ...]
    categories: list[dict[str, int]]  # Categories: [{"id": category_id}, ...]
    projects: list[dict[str, int]]  # Projects: [{"id": project_id}, ...]

    # OPTIONAL fields - Addresses
    addresses: list[dict[str, Any]]  # Full address objects with type, address, city, etc.
    mailAddress: dict[str, Any]  # Mail address object

    # OPTIONAL fields - Business data
    turnover: int
    profit: int
    noEmployees: int
    registrationDate: str  # ISO 8601
    companyForm: str
    status: str

    # OPTIONAL fields - Industry codes
    sniCode: str
    sicCode: str
    ukSicCode: str
    naceCode: str
    naicsCode: str
    dunsNo: str

    # OPTIONAL fields - Social media
    facebook: str
    twitter: str
    linkedin: str

    # OPTIONAL fields - Journey
    journeyStep: str
    score: int

    # OPTIONAL fields - Custom
    custom: list[dict[str, Any]]
    extraFields: dict[str, Any]

    # OPTIONAL fields - External
    isExternal: int
    externalClientData: dict[str, Any]

    # OPTIONAL fields - Monitoring
    isMonitored: bool
    excludedFromProspectingMonitor: bool

    # OPTIONAL fields - Misc
    currency: str
    priceListId: int
    headquarters: int
    cfar: int
    about: str
    importId: Any
```

---

## 📊 Comparison with API File

### API File Prediction
```json
{
  "required": [
    {"field": "name", "type": "string", "maxLength": 100}
  ]
}
```

### Actual Testing Result
✅ **CORRECT!** - API file was 100% accurate for accounts

Only `name` is required, exactly as documented.

---

## 🔍 Important Details

### Field Structures from Real API Response

**Addresses Array**:
```json
[
  {
    "type": "Visit",
    "address": "Stationsgatan 37",
    "zipcode": "30250",
    "state": "HALLAND",
    "city": "Halmstad",
    "municipality": "HALMSTAD",
    "country": "SE",
    "latitude": 56.665614,
    "longitude": 12.862652
  }
]
```

**Users Array** (Account Managers):
```json
[
  {
    "name": "Axel Öhlander",
    "id": 1,
    "role": {"name": "role", "id": 1},
    "email": "axel@upsales.com"
  }
]
```

**Growth Object** (Read-only, calculated):
```json
{
  "salesLast12Months": 0,
  "cmLast12Months": 0,
  "salesTrend12Months": 0,
  "numberOfActivities": 0,
  "arr": 0,
  "mrr": 0,
  ...
}
```

**AdCampaign**: API returns `[]` (empty array), model expects single object or None

**Assigned**: API returns `[]` (array), model might expect single Assignment

---

## 🚨 Model Validation Issues Found

While testing, we discovered the Company model has validation errors when parsing real API responses:

### Issue 1: `addresses` Field
- **Model expects**: `AddressList` instance
- **API returns**: `list[dict]` (raw array)
- **Fix needed**: Add `@field_validator` to convert list → AddressList

### Issue 2: `adCampaign` Field
- **Model expects**: `AdCampaign` (single object)
- **API returns**: `list` (array, can be empty)
- **Fix needed**: Change type to `list[AdCampaign]` or add validator

### Issue 3: `assigned` Field
- **Model expects**: `Assignment` (single object)
- **API returns**: `list` (array, can be empty)
- **Fix needed**: Change type to `list[Assignment]` or add validator

### Issue 4: `externalClientData` Field
- **Model expects**: `list`
- **API returns**: `dict` (empty object `{}`)
- **Fix needed**: Change type to `dict[str, Any]`

---

## ✅ Verified Patterns

### CREATE Pattern
```python
# Minimal - just name
new_company = await upsales.companies.create(
    name="ACME Corporation"
)

# With basic info
new_company = await upsales.companies.create(
    name="ACME Corporation",
    phone="+1-555-0123",
    webpage="www.acme.com",
    active=1
)

# With relationships (nested minimal structure)
new_company = await upsales.companies.create(
    name="ACME Corporation",
    users=[{"id": 10}, {"id": 15}],  # Account managers
    categories=[{"id": 5}],
    parent={"id": 20}  # Parent company
)

# With addresses
new_company = await upsales.companies.create(
    name="ACME Corporation",
    addresses=[
        {
            "address": "123 Main St",
            "city": "New York",
            "zipcode": "10001",
            "country": "US",
            "type": "Visit"
        }
    ]
)
```

### UPDATE Pattern
```python
# Update any field(s) - all optional
company = await upsales.companies.get(1)

# Update single field
await company.edit(name="New Name")

# Update multiple fields
await company.edit(
    phone="+1-555-9999",
    webpage="www.newsite.com",
    active=0
)

# Update relationships
await company.edit(
    users=[{"id": 10}, {"id": 15}],
    categories=[{"id": 5}, {"id": 7}]
)
```

---

## 📝 Next Steps

### 1. Add CompanyCreateFields to Model
- [ ] Add TypedDict to `upsales/models/company.py`
- [ ] Export in `upsales/models/__init__.py`
- [ ] Update model docstring with CREATE examples

### 2. Fix Company Model Validation Issues
- [ ] Add `@field_validator` for addresses list → AddressList
- [ ] Fix adCampaign type (list vs single object)
- [ ] Fix assigned type (list vs single object)
- [ ] Fix externalClientData type (dict vs list)

### 3. Add Integration Tests
- [ ] Create `test_create_company_minimal_fields.py`
- [ ] Test CREATE with only name
- [ ] Test CREATE with addresses array
- [ ] Test CREATE with users array
- [ ] Record VCR cassettes

### 4. Update Documentation
- [ ] Mark accounts CREATE as ✅ Verified in endpoint-map.md
- [ ] Update statistics (CREATE verified: 2 → 3)
- [ ] Document as "simplest CREATE" (only 1 required field)

---

## 🎯 Summary

**CREATE Requirements**:
- ✅ Only `name` required
- ✅ All other fields optional
- ✅ API file was 100% accurate
- ✅ Nested arrays use minimal `{"id": n}` structure

**UPDATE Requirements**:
- ✅ ALL 85 fields optional
- ✅ No required fields for updates
- ✅ Can update any subset of fields

**Model Issues**:
- ❌ Field validators needed for type conversion
- ❌ Some field types mismatch (list vs object)
- ⚠️ Blocking 13 tests from passing

**Priority**: Fix Company model validators → unlocks 13 tests

---

**Verification Status**: ✅ **COMPLETE**
**Next Action**: Add CompanyCreateFields TypedDict + fix model validation
**Estimated Time**: 45 minutes total
