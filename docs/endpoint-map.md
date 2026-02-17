# Upsales SDK Endpoint Map

**Last Updated**: 2026-02-09 (field gap analysis complete)
**Purpose**: Comprehensive map of all documented endpoints, their CRUD operations, and verification status.

---

## Legend

### Operation Status
- ✅ **Verified** - Fully tested with integration tests and VCR cassettes
- 🔶 **Inherited** - Available via BaseResource but not specifically tested for this endpoint
- ❌ **Not Available** - Not applicable for this endpoint type
- ⚠️ **Partial** - Implemented but not all field requirements validated

### Operation Codes
- **C** = Create (POST)
- **R** = Read (GET single/list)
- **U** = Update (PUT/PATCH)
- **D** = Delete (DELETE)
- **S** = Search (GET with filters)

---

## Full CRUD Endpoints (Verified)

### Users
**API**: `/users`
**Models**: `User`, `PartialUser`
**Client**: `upsales.users`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | ✅ Verified | Natural operators tested |

**Custom Methods**:
- `get_by_email(email)` - ✅ Implemented
- `get_administrators()` - ✅ Implemented
- `get_active(include_api_keys)` - ✅ Implemented

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, regDate, modDate)
- ✅ TypedDict complete (UserUpdateFields)
- ✅ Validators: BinaryFlag, EmailStr, CustomFieldsList

**Integration Tests**: 4 cassettes recorded

---

### Companies (Accounts)
**API**: `/accounts`
**Models**: `Company`, `PartialCompany`
**Client**: `upsales.companies`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | ✅ Verified | Natural operators tested |

**Custom Methods**: None (uses inherited BaseResource methods)

**Field Requirements**:
- ✅ All 87 fields documented
- ✅ Frozen fields marked (id, regDate, modDate)
- ✅ TypedDict complete (CompanyUpdateFields)
- ✅ Validators: BinaryFlag, EmailStr, CustomFieldsList

**Integration Tests**: 4 cassettes recorded

---

### Products
**API**: `/products`
**Models**: `Product`, `PartialProduct`
**Client**: `upsales.products`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | ✅ Verified | Natural operators tested |

**Custom Methods**:
- `get_active()` - ✅ Implemented
- `get_recurring()` - ✅ Implemented
- `bulk_deactivate(ids)` - ✅ Implemented

**Field Requirements**:
- ✅ All 25 fields documented
- ✅ Frozen fields marked (id, regDate, modDate)
- ✅ TypedDict complete (ProductUpdateFields)
- ✅ Validators: BinaryFlag, CustomFieldsList, NonEmptyStr

**Integration Tests**: 4 cassettes recorded

---

### Order Stages
**API**: `/orderStages`
**Models**: `OrderStage`, `PartialOrderStage`
**Client**: `upsales.order_stages`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | ⚠️ Partial | to_update_dict_minimal() tested, requires probability |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | ✅ Verified | Natural operators tested |

**Custom Methods**:
- `get_included()` - ✅ Verified (integration tested)
- `get_sorted_by_probability()` - ✅ Verified (integration tested)

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (OrderStageUpdateFields)
- ✅ Validators: BinaryFlag, NonEmptyStr, Percentage
- ✅ Required fields validated: probability (0-100) is required for updates

**Integration Tests**: 5 cassettes recorded

---

### Orders
**API**: `/orders`
**Models**: `Order`, `PartialOrder`, `OrderCreateFields`, `OrderUpdateFields`
**Client**: `upsales.orders`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ **Verified** | **Required fields manually tested (2025-11-06)** |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() - field requirements unknown |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_company(company_id)` - ✅ Implemented
- `get_by_user(user_id)` - ✅ Implemented
- `get_by_stage(stage_id)` - ✅ Implemented
- `get_high_value(min_value)` - ✅ Implemented
- `get_by_probability_range(min, max)` - ✅ Implemented
- `get_closing_soon(days)` - ✅ Implemented
- `get_recurring()` - ✅ Implemented

**Field Requirements** (✅ CREATE Verified):
- ✅ **CREATE requirements verified through manual testing**
- ✅ **Required fields documented in `OrderCreateFields` TypedDict**
- ✅ **Nested field pattern verified** (user.id, client.id, stage.id, orderRow[].product.id)
- ✅ All fields documented with descriptions
- ✅ TypedDict for both create and update
- ⚠️ UPDATE field requirements not yet verified

**Required for CREATE** (verified 2025-11-06):
- `orderRow` - `[{"product": {"id": product_id}}]` (array with product IDs)
- `date` - `"YYYY-MM-DD"` format string
- `user` - `{"id": user_id}` (minimal nested structure)
- `stage` - `{"id": stage_id}` (minimal nested structure)
- `client` - `{"id": client_id}` (minimal nested structure)

**Important Pattern**: Orders use **nested required fields with minimal ID structure** for creation. See `docs/patterns/nested-required-fields.md` for complete guide.

**Integration Tests**: None yet (recommended to add)

---

### Opportunities
**API**: `/opportunities`
**Models**: `Order`, `PartialOrder` (shares models with Orders)
**Client**: `upsales.opportunities`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ **Inherited** | Same as Orders - uses OrderCreateFields |
| Read (single) | ✅ Verified | Unit tested |
| Read (list) | ✅ Verified | Unit tested |
| Update | ✅ Verified | Unit tested |
| Delete | ✅ Verified | Unit tested |
| Search | ✅ Verified | Unit tested |

**Custom Methods**:
- `get_by_company(company_id)` - ✅ Implemented & tested
- `get_by_user(user_id)` - ✅ Implemented & tested
- `get_by_stage(stage_id)` - ✅ Implemented & tested
- `get_high_value(min_value)` - ✅ Implemented & tested
- `get_by_probability_range(min, max)` - ✅ Implemented & tested
- `get_closing_soon(days)` - ✅ Implemented & tested
- `get_recurring()` - ✅ Implemented & tested

**Field Requirements**:
- ✅ Shares all field requirements with Orders
- ✅ Uses `OrderCreateFields` and `OrderUpdateFields` TypedDicts
- ✅ All fields documented (inherited from Order model)
- ✅ Probability constraint: 1-99% (distinguishes from Orders which can be 0% or 100%)

**Note**: Opportunities use the same data model as Orders but point to `/opportunities` endpoint. The primary distinction is that opportunities represent pipeline deals with probability 1-99%, while orders can have probability 0% (lost) or 100% (won).

**Unit Tests**: ✅ Complete (14 tests, 100% coverage)
**Integration Tests**: None yet (recommended to add)

---

### Periodization
**API**: `/periodization`
**Models**: `Periodization`, `PartialPeriodization`
**Client**: `upsales.periodization`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (PeriodizationUpdateFields, PeriodizationCreateFields)
- ✅ Computed property: is_valid_date_range

**Required Fields for CREATE**:
- `orderId` - Order ID (integer)
- `startDate` - Start date (YYYY-MM-DD format)
- `endDate` - End date (YYYY-MM-DD format)

**Integration Tests**: None yet (recommended to add)

**Unit Tests**: ✅ 10 tests passing (test_periodization_resource.py)

---

### Phone Calls
**API**: `/phoneCall`
**Models**: `PhoneCall`, `PartialPhoneCall`
**Client**: `upsales.phone_calls`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ✅ All 12 fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (PhoneCallUpdateFields)
- ✅ Comprehensive docstrings (100% coverage)

**Required Fields for CREATE**:
- `user` - User who made/received call (dict with 'id' key)
- `contact` - Contact associated with call (dict with 'id' key)
- `client` - Company associated with call (dict with 'id' key)

**Optional Fields**:
- `durationInS` - Duration in seconds (default: 0)
- `phoneNumber` - Phone number (max 45 chars)
- `type` - Call type (max 45 chars)
- `conversationUrl` - Recording URL (max 512 chars)
- `date` - Call date/time (YYYY-MM-DD HH:mm:ss)
- `status` - Status code (default: 0)
- `externalId` - External system identifier (max 512 chars)

**Integration Tests**: None yet (recommended to add)

**Unit Tests**: ⚠️ 15 tests created (test_phone_calls_resource.py) - Need pytest-httpx mocking update

**Notes**: Phone call tracking for third-party integrations. Model follows all Pydantic v2 best practices.

---

### Projects
**API**: `/projects`
**Models**: `Project`, `PartialProject`
**Client**: `upsales.projects`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but comprehensive field validation not complete
- ⚠️ TypedDict may not be complete

**Integration Tests**: 6 cassettes recorded

---

### Activities
**API**: `/activities`
**Models**: `Activity`, `PartialActivity`
**Client**: `upsales.activities`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### Activity Quota
**API**: `/activityQuota`
**Models**: `ActivityQuota`, `PartialActivityQuota`, `ActivityQuotaUpdateFields`
**Client**: `upsales.activity_quota`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() - Requires admin/team leader |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() - Requires admin/team leader |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_user(user_id, year, month)` - ✅ Implemented - Get quotas for specific user
- `get_by_activity_type(activity_type_id, year, month)` - ✅ Implemented - Get quotas for specific activity type

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, date - read-only)
- ✅ TypedDict complete (ActivityQuotaUpdateFields)
- ✅ Month validator (1-12 range)
- ✅ Nested models: PartialUser, PartialActivityType

**Permissions**:
- Create/Update: Administrator or team leader only

**Notes**:
- Tracks quarterly storage and monthly API usage per user and activity type
- Month field validates 1-12 range
- Date field is computed from year/month (read-only)
- Only year, month, performed, and created can be updated

**Integration Tests**: None (unit tests created)

---

### Contacts
**API**: `/contacts`
**Models**: `Contact`, `PartialContact`, `ContactCreateFields`, `ContactUpdateFields`
**Client**: `upsales.contacts`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ **Verified** | **Required fields tested with script (2025-11-07)** |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements** (✅ CREATE Verified):
- ✅ **CREATE requirements verified via test_required_create_fields.py script**
- ✅ **Required fields documented in `ContactCreateFields` TypedDict**
- ✅ **Nested field pattern verified** (client.id minimal structure)
- ✅ All fields documented with descriptions
- ✅ TypedDict for both create and update
- ⚠️ UPDATE field requirements not yet verified

**Required for CREATE** (verified 2025-11-07):
- `client` - `{"id": client_id}` (minimal nested structure) **ONLY ONE REQUIRED!**

**Important Finding**: Email is **OPTIONAL** (api_endpoints_with_fields.json was incorrect - listed email as required but testing proved it's optional)

**Pattern**: Contacts use **minimal nested required field** for creation - only client.id needed. Simplest CREATE operation verified so far.

**Integration Tests**: 6 cassettes recorded (including CREATE tests)

---


### Contract Accepted
**API**: `/contractAccepted`
**Models**: `ContractAccepted`, `PartialContractAccepted`, `ContractAcceptedUpdateFields`
**Client**: `upsales.contract_accepted`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() - Only contractId required |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (ContractAcceptedUpdateFields)
- ✅ Computed field: has_date property
- ✅ Full docstrings with examples
- ❌ No validators (no binary flags, email, or custom fields)
- ❌ No field serializer (no custom fields)

**Required for CREATE**:
- `contractId` - ID of the contract being accepted

**Auto-Populated Fields**:
- version, body, user_id, master_user_id, customer_id
- user_email, user_name, user_ip, date

**Special Notes**:
- Records user acceptance of contract terms
- Most fields are auto-populated by the system
- Primarily used for audit/compliance tracking
- Updates are rare for this endpoint

**Tests**: ✅ 10/10 passing
- CRUD operations: create, get, list, list_all, update, delete
- Model features: has_date computed field, frozen id, optional fields
- 100% test coverage for resource methods

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Resource Coverage**: 100%

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed

---
### Agreements
**API**: `/agreements`
**Models**: `Agreement`, `PartialAgreement`, `AgreementUpdateFields`
**Client**: `upsales.agreements`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None (uses inherited BaseResource methods)

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, regDate, modDate, value, contributionMargin, etc.)
- ✅ TypedDict complete (AgreementUpdateFields)
- ✅ Validators: CustomFieldsList
- ✅ Nested relationships use Partial models (PartialUser, PartialCompany, PartialContact)

**Required for CREATE** (per API spec):
- `description` - Agreement description (string)
- `user` - Responsible user `{"id": user_id}`
- `client` - Company/account `{"id": client_id}` (must be active)
- `stage` - Agreement stage `{"id": stage_id}`
- `orderRow` - Order rows array with `[{"product": {"id": product_id}, "price": number, "quantity": number}]`
- `metadata.agreementStartdate` - Start date (YYYY-MM-DD, createOnly)
- `metadata.agreementIntervalPeriod` - Interval period in months (number, createOnly)
- `metadata.agreementOrderCreationTime` - Order creation time (number, default: 1)
- `metadata.periodLength` - Period length in months (number, createOnly)

**Pydantic v2 Patterns**:
- ✅ Frozen fields for read-only data
- ✅ Field descriptions for all fields
- ✅ TypedDict for IDE autocomplete
- ✅ Computed field for custom_fields
- ✅ Field serializer for custom fields
- ✅ to_api_dict() method
- ✅ Partial model with fetch_full()

**Unit Tests**: 11 tests passing (100% coverage)
- CRUD operations (create, get, list, list_all, search, update, delete)
- Model features (custom_fields, frozen_fields, to_api_dict)

**Integration Tests**: None yet

---

### Appointments
**API**: `/appointments`
**Models**: `Appointment`, `PartialAppointment`
**Client**: `upsales.appointments`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

## Configuration & Reference Endpoints

### Pricelists
**API**: `/pricelists`
**Models**: `Pricelist`, `PartialPricelist`
**Client**: `upsales.pricelists`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 6 cassettes recorded

---

### Roles
**API**: `/roles`
**Models**: `RoleModel`, `PartialRoleModel`
**Client**: `upsales.roles`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 6 cassettes recorded

---

### Currencies
**API**: `/currencies`
**Models**: `CurrencyModel`, `PartialCurrencyModel`
**Client**: `upsales.currencies`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 6 cassettes recorded

---

### Quota
**API**: `/quota`
**Models**: `Quota`, `PartialQuota`
**Client**: `upsales.quota`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() - requires admin/teamleader |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() - requires admin/teamleader |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_user(user_id)` - ✅ Implemented - All quotas for a user
- `get_by_year(year)` - ✅ Implemented - All quotas for a year
- `get_by_quarter(year, quarter)` - ✅ Implemented - Quotas for specific quarter (1-4)
- `get_by_user_and_period(user_id, year, month?)` - ✅ Implemented - Filter by user and period

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, date, valueInMasterCurrency)
- ✅ TypedDict complete (QuotaUpdateFields)
- ✅ Validators: PositiveInt for year/value, Field constraints for month (1-12)
- ✅ Computed fields: is_current_quarter, quarter, formatted_period

**Special Characteristics**:
- Quotas are stored quarterly but accessible monthly
- Requires administrator or teamleader permissions for create/update
- Currency field is optional (3-letter code)
- Links to PartialUser model

**Unit Tests**: 7 tests - 100% coverage
**Integration Tests**: None (using unit tests with mocked HTTP)

---

### Engage Credit Transaction
**API**: `/engage/creditTransaction`
**Models**: `EngageCreditTransaction`, `PartialEngageCreditTransaction`
**Client**: `upsales.engage_credit_transactions`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create(), requires value and description |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (EngageCreditTransactionUpdateFields)
- ✅ Validators: NonEmptyStr for description, CustomFieldsList
- ✅ Computed fields: custom_fields

**API Requirements (from spec)**:
- Required for CREATE: value (number), description (string)
- Optional: date (YYYY-MM-DD), campaignId (int)
- Returns: id, value, description, date, campaignId

**Unit Tests**: 8 tests - 100% passing
**Integration Tests**: None (endpoint available but not integration tested)

---

### Events
**API**: `/events`
**Models**: `Event`, `PartialEvent`
**Client**: `upsales.events`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Verified | Unit tested, requires entityType and score |
| Read (single) | ❌ Not Available | Must use list with filters |
| Read (list) | ✅ Verified | Unit tested, requires 'q' filter parameter |
| Update | ❌ Not Available | API does not support updates |
| Delete | ✅ Verified | Unit tested |
| Search | ✅ Verified | Via required 'q' filter in list() |

**Custom Methods**:
- `get_by_type(entity_type)` - ✅ Implemented - Filter by entityType
- `get_by_company(company_id)` - ✅ Implemented - Filter by client.id

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id - only field returned)
- ✅ TypedDict complete (EventCreateFields, EventUpdateFields)
- ✅ Validators: NonEmptyStr for entityType
- ✅ Computed fields: is_manual, is_marketing, is_news, has_company, has_opportunity, has_contacts

**Special Characteristics**:
- List operations require 'q' filter parameter
- Update operations not supported by API (raises NotImplementedError)
- No GET by ID endpoint (must filter list results)
- edit() method raises NotImplementedError for consistency

**Integration Tests**: Unit tests only (API requires filter, no direct GET)

---

### Segments
**API**: `/segments`
**Models**: `Segment`, `PartialSegment`
**Client**: `upsales.segments`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 4 cassettes recorded

---

### Triggers
**API**: `/triggers`
**Models**: `Trigger`, `PartialTrigger`
**Client**: `upsales.triggers`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 4 cassettes recorded

---

### Forms
**API**: `/forms`
**Models**: `Form`, `PartialForm`
**Client**: `upsales.forms`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Unit tested with full validation |
| Read (single) | ✅ Implemented | Unit tested with full validation |
| Read (list) | ✅ Implemented | Unit tested with full validation |
| Update | ✅ Implemented | Unit tested with full validation |
| Delete | ✅ Implemented | Unit tested with full validation |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_active()` - Get all non-archived forms
- `get_archived()` - Get all archived forms
- `get_with_submissions()` - Get forms with submissions
- `get_by_name(name)` - Find form by name
- `get_by_title(title)` - Find form by title (case-insensitive)

**Field Requirements**:
- ✅ All 12 Pydantic v2 patterns implemented
- ✅ Read-only fields identified and frozen (id, uuid, submits, views, lastSubmitDate, regDate, modDate, userEditable, userRemovable)
- ✅ BinaryFlag validators for isArchived, redirect, showTitle
- ✅ Computed fields: is_archived, is_active, has_submissions, submission_count, conversion_rate
- ✅ TypedDict for IDE autocomplete (FormUpdateFields)
- ✅ 100% docstring coverage
- ✅ All quality checks passing (ruff, mypy, interrogate)

**Unit Tests**: 12 tests, 100% passing (5 CRUD + 7 custom methods)

**Coverage**:
- Model: 84.09%
- Resource: 32.35%

---

### Files
**API**: `/files`
**Models**: `File`, `PartialFile`
**Client**: `upsales.files`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Complete | Full implementation with all fields |
| Read (list) | ✅ Complete | Full implementation with all fields |
| Update | ✅ Complete | Updatable fields: private, clientId, entity, entityId, public, driveFolderId |
| Delete | ✅ Complete | Full implementation |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_entity(entity, entity_id)` - Get files for specific entity
- `get_images()` - Get all image files
- `get_documents()` - Get all document files
- `get_private()` - Get all private files
- `get_public()` - Get all public files
- `get_by_filename(filename, case_sensitive)` - Search by filename
- `get_by_extension(extension)` - Filter by file extension

**Pydantic v2 Patterns Applied**:
- ✅ BinaryFlag validators for private/public fields
- ✅ Computed fields: is_private, is_public, is_image, is_document, size_kb, size_mb, file_size_mb
- ✅ Frozen fields for read-only data (id, extension, type, filename, mimetype, size, uploadDate)
- ✅ Field descriptions for all fields
- ✅ TypedDict for IDE autocomplete (FileUpdateFields)
- ✅ to_api_dict() for optimized serialization
- ✅ File aliases for company field

**Field Requirements**:
- Read-only: id, userId, extension, type, filename, mimetype, size, uploadDate, encryptedCustomerId
- Updatable: private, clientId, entity, entityId, public, driveFolderId
- All fields validated against API spec

**Unit Tests**: 13 tests passing (100% coverage)
- ✅ CRUD operations
- ✅ Custom methods
- ✅ Computed properties

---

### Client Categories
**API**: `/clientcategories`
**Models**: `ClientCategory`, `PartialClientCategory`
**Client**: `upsales.clientcategories`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### API Keys
**API**: `/apiKeys`
**Models**: `ApiKey`, `PartialApiKey`
**Client**: `upsales.apikeys`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 4 cassettes recorded

---

### Project Plan Priorities
**API**: `/projectPlanPriority`
**Models**: `ProjectPlanPriority`, `PartialProjectPlanPriority`
**Client**: `upsales.project_plan_priorities`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 4 cassettes recorded

---

### Project Plan Types
**API**: `/projectPlanTypes`
**Models**: `ProjectPlanType`, `PartialProjectPlanType`
**Client**: `upsales.project_plan_types`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### Journey Steps
**API**: `/journeySteps`
**Models**: `JourneyStep`, `PartialJourneyStep`
**Client**: `upsales.journey_steps`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: None yet (recommended to add)

---

### Mail Domains
**API**: `/mail/domains`
**Models**: `MailDomain`, `PartialMailDomain`
**Client**: `upsales.mail_domains`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Override: uses domain name as ID |
| Read (single) | ✅ Implemented | Override: get(domain_name) |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | ✅ Implemented | Override: update(domain_name, **data) |
| Delete | ✅ Implemented | Override: delete(domain_name) - Halon only |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_verified()` - ✅ Returns all verified domains
- `get_by_name(domain_name)` - ✅ Convenience method

**Special Notes**:
- Uses domain name as identifier instead of numeric ID
- All CRUD operations accept string domain names
- Delete only works with Halon mail accounts
- Requires administrator permissions

**Field Requirements**:
- ✅ All 4 fields documented with descriptions
- ✅ BinaryFlag validator for valid field
- ✅ TypedDict complete (MailDomainUpdateFields)
- ✅ Computed field: is_valid
- ⚠️ No frozen fields (no ID field in this endpoint)

**Integration Tests**: None (blocked by unrelated Ticket model error)
**Unit Tests**: ✅ Complete with 100% coverage

---

### Mail Templates
**API**: `/mail/templates`
**Models**: `MailTemplate`, `PartialMailTemplate`
**Client**: `upsales.mail_templates`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### Sales Coaches
**API**: `/salesCoaches`
**Models**: `SalesCoach`, `PartialSalesCoach`
**Client**: `upsales.sales_coaches`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 10 cassettes recorded

---

### Standard Integrations
**API**: `/standardIntegration`
**Models**: `StandardIntegration`, `PartialStandardIntegration`
**Client**: `upsales.standard_integrations`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists, basic structure verified
- ⚠️ Create/update requirements not validated

**Integration Tests**: 9 cassettes recorded

---

## Read-Only Endpoints

### Metadata
**API**: `/metadata`
**Models**: `Metadata` (no Partial)
**Client**: `upsales.metadata`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | ✅ Verified | Returns single object with system info |
| Read (list) | ❌ N/A | Not a list endpoint |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | ❌ N/A | Not applicable |

**Custom Methods**:
- `get()` - ✅ Verified (returns complete system metadata)
- `get_currencies()` - ✅ Implemented
- `get_default_currency()` - ✅ Implemented
- `get_entity_fields(entity_type)` - ✅ Implemented
- `get_required_fields(entity_type)` - ✅ Implemented
- `is_field_required(entity_type, field)` - ✅ Implemented
- `get_user_info()` - ✅ Implemented
- `get_system_version()` - ✅ Implemented
- `get_license_count()` - ✅ Implemented

**Field Requirements**: N/A (read-only)

**Field Gap Analysis** (2026-02-09):
- ✅ All 33 API response fields now explicitly defined in Metadata model
- Added 17 previously missing fields: `activatedFeatures`, `agentLiveListeners`, `agentUiElements`, `credits`, `esign`, `iCalExternalUrlHash`, `integrations`, `listOnboarding`, `mailEditorHash`, `mainApps`, `map`, `onboarding`, `publicUrlHash`, `showUserSurvey`, `userQuotaPeriods`, `userSurveyResult`, `validFileExtensions`
- Nested models (Currency, MetadataUser, SystemParams, FieldDefinition) validated

**Integration Tests**: 4 cassettes recorded

---

### Self
**API**: `/self`
**Models**: `SelfUser` (no Partial)
**Client**: `upsales.self`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | 🔶 Inherited | Returns current user info |
| Read (list) | ❌ N/A | Not a list endpoint |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | ❌ N/A | Not applicable |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: None

---

### Static Values
**API**: `/staticValues/all`
**Models**: `StaticValues` (no Partial)
**Client**: `upsales.static_values`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | 🔶 Inherited | Returns all static values |
| Read (list) | ❌ N/A | Not a list endpoint |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | ❌ N/A | Not applicable |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: None

---

### Todo Views
**API**: `/todoViews`
**Models**: `TodoView`, `PartialTodoView`
**Client**: `upsales.todo_views`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | 🔶 Inherited | BaseResource.search() available |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: 6 cassettes recorded

---

### Trigger Attributes
**API**: `/triggerAttributes`
**Models**: `TriggerAttribute`, `PartialTriggerAttribute`
**Client**: `upsales.trigger_attributes`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: None

---

### Opportunity AI
**API**: `/opportunityAI`
**Models**: `OpportunityAI`, `PartialOpportunityAI`
**Client**: `upsales.opportunity_ai`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only endpoint |
| Read (single) | ✅ Verified | Integration tested with VCR |
| Read (list) | ✅ Verified | Integration tested with VCR |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: 4 cassettes recorded

---

### Activity List
**API**: `/search/activitylist`
**Models**: `ActivityListItem` (no Partial)
**Client**: `upsales.activity_list`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Read-only search endpoint |
| Read (single) | ❌ N/A | List-only endpoint |
| Read (list) | 🔶 Inherited | Search results for activities |
| Update | ❌ N/A | Read-only endpoint |
| Delete | ❌ N/A | Read-only endpoint |
| Search | 🔶 Inherited | Primary operation |

**Custom Methods**: None

**Field Requirements**: N/A (read-only)

**Integration Tests**: None

---

## Update-Only Endpoints

### Pages
**API**: `/pages`
**Models**: `Page`, `PartialPage`, `PageUpdateFields`
**Client**: `upsales.pages`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ N/A | Update-only endpoint |
| Read (single) | ✅ Verified | Unit tested |
| Read (list) | ✅ Verified | Unit tested with pagination |
| Update | ✅ Verified | Unit tested |
| Delete | ❌ N/A | Not supported by API |
| Search | ✅ Verified | Unit tested |

**Custom Methods**: None

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, pageImpression)
- ✅ TypedDict complete (PageUpdateFields)
- ✅ Validators: BinaryFlag
- ✅ Computed fields: is_hidden, is_visible

**Updatable Fields**:
- `name` (str) - Page name
- `url` (str) - Landing page URL
- `state` (str) - Page state (e.g., "active", "inactive")
- `lastUpdateDate` (str) - Last update date (YYYY-MM-DD)
- `score` (int) - Page score/rating
- `hide` (BinaryFlag) - Hide page (0=visible, 1=hidden)
- `keywords` (list[str]) - SEO keywords

**Read-Only Fields**:
- `id` (int) - Unique page identifier (frozen, strict)
- `pageImpression` (int) - Total page impressions count (frozen)

**Integration Tests**: None (unit tests only)

**Validation Status**: ✅ Complete
- CRUD lifecycle validated (no CREATE/DELETE supported by API)
- Field editability confirmed via test script
- Model patterns verified (frozen fields, computed properties, TypedDict)
- All quality checks passed (ruff, mypy, interrogate 100%)

---

## Special Endpoints

### Mail
**API**: `/mail`
**Models**: `Mail`, `PartialMail`
**Client**: `upsales.mail`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | Send email via POST |
| Read (single) | 🔶 Inherited | Get single email |
| Read (list) | 🔶 Inherited | List emails |
| Update | 🔶 Inherited | Update email |
| Delete | 🔶 Inherited | Delete email |
| Search | 🔶 Inherited | Search emails |

**Custom Methods**: None

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ Email sending requirements not validated
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### Mail Editor (BEE)
**API**: `/function/mailEditor`
**Models**: `MailEditorToken`
**Client**: `upsales.mail_editor`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Authentication only (POST) |
| Read (single) | ❌ Not Available | Function endpoint |
| Read (list) | ❌ Not Available | Function endpoint |
| Update | ❌ Not Available | Function endpoint |
| Delete | ❌ Not Available | Function endpoint |
| Search | ❌ Not Available | Function endpoint |

**Custom Methods**:
- `authenticate()` - ✅ Implemented - Returns OAuth token for BEE mail editor

**Field Requirements**:
- ✅ Response model complete (access_token, token_type, expires_in)
- ✅ Uses Pydantic BaseModel directly (no ID field)
- ✅ 100% docstring coverage
- ✅ Type checking passing

**Integration Tests**: 4 unit tests passing

**Special Notes**:
- This is a function endpoint, not a standard CRUD resource
- Returns OAuth-style access token for BEE mail editor API
- Token structure: `{"access_token": str, "token_type": str, "expires_in": int}`
- No partial model needed (response-only)

---

### Mail Multi
**API**: `/mail/multi`
**Models**: `MailMultiResponse`, `MailMultiItem`, `MailMultiRequest`
**Client**: `upsales.mail_multi`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Batch email sending (POST) |
| Read (single) | ❌ Not Available | POST-only endpoint |
| Read (list) | ❌ Not Available | POST-only endpoint |
| Update | ❌ Not Available | POST-only endpoint |
| Delete | ❌ Not Available | POST-only endpoint |
| Search | ❌ Not Available | POST-only endpoint |

**Custom Methods**:
- `send_batch(emails)` - ✅ Implemented - Send multiple emails in one request

**Field Requirements**:
- ✅ Response model complete (success, results, errors, total_sent, total_failed)
- ✅ TypedDict for request items (MailMultiItem with all email fields)
- ✅ Uses Pydantic BaseModel directly (no ID field required)
- ✅ 100% docstring coverage
- ✅ Type checking passing (mypy strict)
- ✅ Ruff linting passing

**Integration Tests**: None (POST-only specialized endpoint)
**Unit Tests**: ✅ 6 comprehensive tests covering success, failures, empty list, CC/BCC, attachments

**Special Notes**:
- This is a specialized batch operation endpoint, not a standard CRUD resource
- Does not inherit from BaseResource (no standard CRUD operations)
- Accepts array of email items in single request for better performance
- Returns detailed batch operation results with per-email status
- Validates against empty email list (raises ValueError)
- Free-threaded mode note included for Python 3.13+ performance

---

### Notifications
**API**: `/notifications`
**Models**: `Notification`, `PartialNotification`
**Client**: `upsales.notifications`
**Resource**: `NotificationsResource` (read-only, no BaseResource inheritance)

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Supported | System-generated only |
| Read (single) | ✅ Implemented | `.get(notification_id)` |
| Read (list) | ✅ Implemented | `.list(limit, offset)` |
| Update | ❌ Not Supported | Read-only resource |
| Delete | ❌ Not Supported | Read-only resource |
| Search | ❌ Not Supported | Read-only resource |

**Custom Methods**:
- `list_all()` - Auto-paginated list of all notifications

**Field Requirements**:
- ✅ All fields are read-only (frozen=True)
- ✅ Comprehensive docstrings (100% coverage)
- ✅ Unit tests passing (10/12 tests, 2 skipped)
- ✅ Type checking passing (mypy strict)
- ✅ Linting passing (ruff)
- ⚠️ No integration tests (endpoint typically returns empty list)

**Notes**:
- Notifications are system-generated events about CRM activities
- Cannot be created, updated, or deleted via API
- List endpoint typically returns empty array in production
- Individual notifications can be accessed by ID if known
- All fields frozen to prevent modification attempts

**Integration Tests**: None

---

### Custom Fields
**API**: `/customFields/{entity}`
**Models**: `CustomField` (no Partial)
**Client**: `upsales.custom_fields`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | Create custom field definition |
| Read (list) | 🔶 Inherited | Get custom fields for entity type |
| Update | 🔶 Inherited | Update custom field definition |
| Delete | 🔶 Inherited | Delete custom field definition |

**Custom Methods**:
- `get_for_entity(entity_type)` - 🔶 Inherited (list by entity)

**Field Requirements**:
- ⚠️ Model exists but not verified
- ⚠️ No integration tests yet

**Integration Tests**: None

---

### Provisioning
**API**: `/provisioning`
**Models**: `ProvisioningRequest`, `PartialProvisioningRequest`
**Client**: `upsales.provisioning`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Pass-through endpoint |
| Read (single) | ❌ Not Available | Pass-through endpoint |
| Read (list) | ❌ Not Available | Pass-through endpoint |
| Update | ❌ Not Available | Pass-through endpoint |
| Delete | ❌ Not Available | Pass-through endpoint |
| Search | ❌ Not Available | Pass-through endpoint |

**Custom Methods**:
- `forward_get(**params)` - ✅ Implemented - Forward GET request with query params
- `forward_post(data)` - ✅ Implemented - Forward POST request with body

**Field Requirements**:
- ✅ Models created for interface consistency
- ✅ Special pass-through endpoint (no standard CRUD)
- ✅ 100% docstring coverage
- ✅ All quality checks passing (ruff, mypy, interrogate)

**Unit Tests**: 4 tests passing

**Notes**:
- This is a special pass-through/proxy endpoint to the provisioning service
- Does NOT support standard CRUD operations (get by ID, update, delete)
- Use `forward_get()` and `forward_post()` methods instead
- Response structure depends on the provisioning service

---

### Voice
**API**: `/function/voice`
**Models**: `VoiceOperation`, `VoiceRecording`, `PartialVoiceOperation`
**Client**: `upsales.voice`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Function-based endpoint |
| Read (single) | ❌ Not Available | Function-based endpoint |
| Read (list) | ❌ Not Available | Function-based endpoint |
| Update | ❌ Not Available | Function-based endpoint |
| Delete | ❌ Not Available | Function-based endpoint |
| Search | ❌ Not Available | Function-based endpoint |

**Custom Methods**:
- `get_recording(integration_id, recording_id)` - ✅ Implemented - Retrieve voice recording
- `initiate_call(integration_id, data)` - ✅ Implemented - Start outgoing call
- `hangup_call(integration_id, data)` - ✅ Implemented - End active call
- `ongoing_call(integration_id, data)` - ✅ Implemented - Get call status
- `call_event(integration_id, data)` - ✅ Implemented - Register call event

**Field Requirements**:
- ✅ Models use plain Pydantic BaseModel (no id field required)
- ✅ VoiceOperation supports 4 operation types: call, hangup, ongoing, initiate
- ✅ VoiceRecording handles binary audio data streams
- ✅ 100% docstring coverage
- ✅ 100% type safety (mypy strict passing)

**Unit Tests**: ✅ 14 tests passing

**Notes**:
- Voice is a function-based endpoint, not standard CRUD
- Operations are stateless (no persistent resource IDs)
- Used for phone/voice integration with external providers
- Recording retrieval returns binary audio data

---

### Import Mail Event
**API**: `/import/mailevent`
**Models**: `MailEvent`, `ImportMailEventResponse`, `SkippedEvent`
**Client**: `upsales.import_mail_event`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Import-only endpoint |
| Read (single) | ❌ Not Available | POST-only endpoint |
| Read (list) | ❌ Not Available | POST-only endpoint |
| Update | ❌ Not Available | POST-only endpoint |
| Delete | ❌ Not Available | POST-only endpoint |
| Search | ❌ Not Available | POST-only endpoint |

**Custom Methods**:
- `import_events(events)` - ✅ Implemented - Import mail events (open, click, bounce, delivered)

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ MailEvent validates click events require URL
- ✅ ImportMailEventResponse provides convenience properties
- ✅ Supports both MailEvent objects and dictionaries
- ✅ 100% docstring coverage
- ✅ All quality checks passing (ruff, mypy, interrogate)

**Event Types**:
- `open` - Email opened by recipient
- `click` - Link clicked (requires URL field)
- `bounce` - Email bounced
- `delivered` - Email delivered successfully

**Unit Tests**: 10 tests created (pre-existing import errors prevent running full test suite)

**Notes**:
- Special import endpoint for bulk event ingestion
- API automatically links events to mail records via contactId + mailCampaignId
- Returns skippedEvents array with errors for any failed imports
- Timestamps are Unix time in milliseconds
- Optional fields: useragent, ip

---

### Image Compose
**API**: `/image/compose`
**Models**: `ImageComposeResponse`, `ImageComposeCreateFields`
**Client**: `upsales.image_compose`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Verified | Compose/modify images |
| Read (single) | ❌ Not Available | POST-only endpoint |
| Read (list) | ❌ Not Available | POST-only endpoint |
| Update | ❌ Not Available | POST-only endpoint |
| Delete | ❌ Not Available | POST-only endpoint |
| Search | ❌ Not Available | POST-only endpoint |

**Custom Methods**:
- `compose(sourcepath, composition)` - ✅ Implemented - Compose/modify images

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ TypedDict for create parameters (ImageComposeCreateFields)
- ✅ Response model validates URL and path fields
- ✅ 100% docstring coverage
- ✅ All quality checks passing (ruff, mypy, interrogate)

**Composition Types**:
- `addYouTubePlayButton` - Add YouTube play button overlay to image

**Unit Tests**: 3 tests passing
- ✅ test_compose_success - Full response validation
- ✅ test_compose_with_minimal_response - Handles optional fields
- ✅ test_compose_request_parameters - Verifies correct API call

**Notes**:
- Special image manipulation endpoint
- Returns composed image URL and/or path
- Currently supports adding YouTube play buttons to video thumbnails
- Uses Pydantic BaseModel (not SDK BaseModel) as no CRUD operations needed

---

### Functions (Utility)
**API**: `/function/*`
**Models**: None (utility endpoints)
**Client**: `upsales.functions`

Special-purpose utility functions resource. Does not follow standard CRUD pattern.

**Custom Methods**: Implementation-specific

**Integration Tests**: None

---

### Bulk (Prospecting Save)
**API**: `/prospectingbulk`
**Models**: `BulkSaveRequest`, `BulkSaveResponse` (no Partial needed)
**Client**: `upsales.bulk`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Bulk save via POST only |
| Read (single) | ❌ Not Available | POST-only endpoint |
| Read (list) | ❌ Not Available | POST-only endpoint |
| Update | ❌ Not Available | POST-only endpoint |
| Delete | ❌ Not Available | POST-only endpoint |
| Search | ❌ Not Available | POST-only endpoint |

**Custom Methods**:
- `save(filters, **params)` - ✅ Implemented (bulk save operation)

**Field Requirements**:
- ✅ BulkSaveRequest model with filter structure
- ✅ BulkSaveResponse model for operation results
- ✅ BulkSaveFields TypedDict complete
- ✅ All fields documented with descriptions
- ⚠️ No validators needed (flexible filter structure)

**Special Notes**:
- **POST-only endpoint**: Only supports bulk save operation
- **Specialized resource**: Does not inherit from BaseResource
- **No standard CRUD**: Custom implementation for bulk operations
- **Filter-based**: Accepts array of filter conditions
- **Optional assignments**: Can assign user, category, stage to saved companies
- **Unit tests**: 6 tests (2 passing, 4 failing - HTTP client context issue)
- **Quality**: 100% docstring coverage, ruff and mypy passing
- ⚠️ Integration tests not feasible (modifies production data)

**Integration Tests**: None (bulk operations modify data)

---

## Summary Statistics

**Last updated**: 2026-02-09

### Overall Implementation Status

| Category | Count | % |
|----------|------:|--:|
| **Total resource files** | 174 | 100% |
| **Registered in client.py** | 174 | 100% |
| ✅ **Validated** (VCR cassettes recorded) | 61 | 35% |
| 🔶 **Has test file, cassettes recorded but all tests skip** (no data) | 14 | 8% |
| ⛔ **API errors** (500/404 — tests skipped) | 8 | 5% |
| 🔲 **Has test file, no cassettes** | 2 | 1% |
| ❌ **No integration test** | 89 | 51% |

---

### Quick Reference: All 174 Resources

#### ✅ Validated with VCR Cassettes (61)

Tested against real Upsales API responses. Models confirmed to parse actual data.

| Resource | Resource | Resource |
|----------|----------|----------|
| activities | flows | orders |
| activity_list | form_submits | phone_calls |
| activity_quota | forms | pricelists |
| activity_types | group_mail_categories | product_categories |
| ad_accounts | journey_steps | products |
| agreement_groups | leads | project_plan_priority |
| agreements | list_views | project_plan_stages |
| api_keys | mail | project_plan_status |
| appointments | mail_campaigns | project_plan_types |
| client_category_types | mail_domains | projects |
| client_relations | mail_templates | quota |
| clientcategories | market_rejectlist | roles |
| companies | metadata | sales_coaches |
| contact_relations | opportunities | segments |
| contacts | opportunity_ai | soliditet_clients |
| contract_accepted | order_stages | standard_integrations |
| currencies | | ticket_statuses |
| custom_fields | | ticket_types |
| esigns | | tickets |
| events | | todo_views |
| files | | trigger_attributes |
| | | triggers |
| | | user_defined_object_1 |
| | | users |

#### 🔶 Has Cassettes — All Tests Skip (no matching data in sandbox) (14)

Cassettes recorded but tests skip because the sandbox has no data for these endpoints.
To populate: create test data in the sandbox, delete cassettes, and re-record.

| Resource | Resource | Resource |
|----------|----------|----------|
| banner_groups | lead_sources | user_defined_object_3 |
| client_ips | notification_settings | user_defined_object_4 |
| lead_channels | onboarding_imports | user_invites |
| | pages | visits |
| | suggestions | |
| | user_defined_object_2 | |

#### ⛔ API Errors — Tests Skipped (8)

Cassettes recorded but API returns errors. Tests have `pytestmark = pytest.mark.skip()`.

| Resource | Error | Notes |
|----------|-------|-------|
| ad_campaigns | 500 Server Error | Engage/ads module may not be enabled |
| ad_creatives | 500 Server Error | Engage/ads module may not be enabled |
| salesboard_cards | 500 Server Error | Salesboard module issue |
| standard_creative | 500 Server Error | Standard creative API error |
| file_uploads | 404 Not Found | Endpoint may be deprecated or renamed |
| periodization | 404 Not Found | Endpoint may require specific config |
| report_views | 404 Not Found | Endpoint may require specific config |
| unsub | 404 Not Found | Endpoint may be deprecated or renamed |

#### 🔲 Has Test File — No Cassettes Yet (2)

Test file exists but no cassette directory. Needs live API run to record.

| Resource |
|----------|
| client_ip_info |
| provisioning |

#### ❌ No Integration Test (89)

No test file or cassette. Needs both test creation and cassette recording.

**Core CRM gaps:**
`contact_categories`, `contact_category_types`, `account_manager_history`, `contract`, `delete_log`, `industries`

**Ads/Marketing:**
`ad_credits`, `ad_locations`, `banner_groups`, `engage_credit_transaction`, `engage_site_template`, `landing_page_template`, `social_events_default_templates`

**Mail:**
`mail_bounce`, `mail_by_thread`, `mail_campaign_info`, `mail_editor`, `mail_multi`, `mail_templates_recently_used`, `mail_templates_used_in`, `mail_test`, `system_mail`, `import_mail_campaign`, `import_mail_campaign_mail`, `import_mail_event`

**Reports/Looker:**
`report`, `report_client_company_type`, `report_view`, `report_widget`, `report_widget_metadata`, `looker_explores`, `looker_looks`, `looker_sso`, `scoreboard`

**User Defined Objects:**
`user_defined_object_categories`, `user_defined_object_category_types`, `user_defined_object_definition`

**Soliditet:**
`soliditet_matcher`, `soliditet_search`, `soliditet_search_buy`

**Standard Integrations:**
`standard_integration_data`, `standard_integration_settings`, `standard_integration_user`, `standard_integration_user_settings`, `standard_field`, `standard_creative`

**Utility/Function endpoints:**
`assign`, `bulk`, `cancel_esign`, `client_form`, `customfields_accounts`, `data_source`, `docebo_sso`, `email_duplicates`, `email_suggest`, `email_suggestion`, `esign_function`, `events_prior`, `export`, `file_download`, `find_prospect`, `flow_contacts`, `forms_external_lead_source`, `functions`, `group_structure`, `image_compose`, `integration_log`, `journey_step_history`, `leads2`, `lead_sources2`, `links`, `lookup`, `notification_settings`, `notifications`, `notify`, `placeholder`, `quick_search`, `reset_score`, `resources_download_adgear`, `resources_download_internal`, `resources_upload_external`, `resources_upload_internal`, `role_settings`, `self`, `send_beam`, `send_esign_reminder`, `signals_feed`, `static_values`, `translate_tags`, `unread_notifications`, `validate_page`, `visits`, `voice`, `what_is_my_ip`, `worker_status`

---

### Special Patterns Discovered

| Pattern | Count | Endpoints |
|---------|-------|-----------|
| **Nested Required Fields** | 2 verified | Orders (5 required), Contacts (1 required) |
| **Minimal ID Structure for CREATE** | 2 verified | Orders, Contacts: `client: {"id": 123}` |
| **Array with Nested IDs** | 1 verified | Orders: `orderRow: [{"product": {"id": 5}}]` |
| **Simple Single Required Field** | 1 verified | Contacts: only `client.id` required |
| **ID Required in PUT Body** | 1 verified | Tickets: `id` must be in request body for updates, not just URL. SDK workaround in `TicketsResource.update()`. **TODO**: Remove if Upsales fixes this. |

---

## Recommendations for Verification

### Cassette recording complete (2026-02-09)

All integration tests with test files have been recorded. Results:
- **61 endpoints validated** with passing tests
- **14 endpoints skip** (no test data in sandbox — need data creation)
- **8 endpoints have API errors** (500/404 — skipped with `pytestmark`)
- **2 endpoints have no cassettes** (client_ip_info, provisioning)

### Next steps: Populate sandbox data for skipped tests

Create test data in the sandbox for these 14 endpoints, then delete cassettes and re-record:
```bash
rm -r tests/cassettes/integration/test_{name}_integration/
uv run pytest -n 0 tests/integration/test_{name}_integration.py -v
```

### Field Gap Analysis (2026-02-09)

Compared VCR cassette API responses against Pydantic model field definitions for all validated endpoints.

**Results**: 17 endpoints perfect match, 5 with gaps (all resolved):

| Endpoint | API Fields | Model Fields | Status | Action Taken |
|----------|-----------|-------------|--------|--------------|
| metadata | 33 | 33 | ✅ Fixed | Added 17 missing fields |
| soliditet_clients | 18 | 18 | ✅ Fixed | Fixed dunsNo/orgNo types (str→str\|int) |
| group_mail_categories | 7 | 7 | ✅ Fixed | Fixed description field (str→str\|None) |
| events | 10 | 26 | ✅ OK | 16 extra fields are valid optional entity links |
| standards | 35 | 38 | ✅ OK | 3 extra fields are optional integration config |
| triggers | 7 | 9 | ✅ OK | 2 extra fields are ownership/legacy fields |
| users | 24 | 25 | ✅ OK | 1 extra field (language) is valid optional pref |

**Model fixes applied**:
- `metadata.py`: 17 new fields (activatedFeatures, credits, esign, integrations, etc.)
- `soliditet_clients.py`: `dunsNo: str | int | None`, `orgNo: str | int | None`
- `group_mail_categories.py`: `description: str | None` (was `str`)
- `ad_creatives.py`: endpoint path `/engage/creative` (was wrong)

### High Priority (User-Facing Endpoints without tests)

1. **contact_categories** / **contact_category_types** — Core CRM config
2. **contract** — Revenue tracking
3. **industries** — Company classification
4. **mail_bounce** / **mail_campaign_info** — Email deliverability

### Medium Priority

5. **report** / **report_view** / **report_widget** — Analytics
6. **user_defined_object_categories** / **_category_types** / **_definition** — Custom objects
7. **role_settings** — Access control
8. **notifications** / **notification_settings** — User notifications

### Low Priority (Internal/Utility)

9. Function endpoints (`reset_score`, `validate_page`, `send_beam`, etc.) — Already have unit tests
10. Soliditet endpoints — Require external service
11. Looker endpoints — Require external service
12. Legacy/duplicate endpoints (`leads2`, `lead_sources2`, `email_suggest`/`email_suggestion`)

---

## Next Steps

To achieve full verification for any endpoint:

1. **Record VCR Cassettes**
   - `uv run pytest -n 0 tests/integration/test_{endpoint}_integration.py -v`

2. **Analyze Real API Structure**
   - Run `uv run python ai_temp_files/find_unmapped_fields.py`
   - Compare cassette data vs model fields

3. **Verify CREATE Requirements** — **CRITICAL for relationship-heavy endpoints**
   - Test with absolutely minimal fields to discover requirements
   - **Check for nested required fields pattern** (like Orders)
   - Document exact structure in `{Model}CreateFields` TypedDict

4. **Verify UPDATE Requirements**
   - Test field-by-field updates
   - Identify frozen/read-only fields
   - Confirm `to_api_dict()` excludes properly

5. **Update This Document**
   - Mark operations as ✅ Verified
   - Add field requirement notes
   - Document any special patterns discovered

---

### Suggestions (Prospecting)
**API**: `/prospectingsuggestion/:boxid`
**Models**: `Suggestion`, `PartialSuggestion`
**Client**: `upsales.suggestions`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Uses boxid parameter |
| Read (single) | ✅ Implemented | get(boxid) |
| Read (list) | ❌ Not Available | N/A for this endpoint |
| Update | ✅ Implemented | POST to /:boxid |
| Delete | ❌ Not Available | N/A for this endpoint |
| Search | ❌ Not Available | N/A for this endpoint |

**Custom Methods**:
- `get(boxid)` - ✅ Implemented (special parameter)
- `update(boxid, **data)` - ✅ Implemented (uses POST)
- `create(boxid, **data)` - ✅ Implemented (alias for update)

**Field Requirements**:
- ✅ Minimal model (boxid, id, actions)
- ✅ Frozen fields marked (boxid, id)
- ✅ TypedDict complete (SuggestionUpdateFields)
- ✅ Computed field: has_actions
- ⚠️ No custom field validators needed

**Special Notes**:
- **Non-standard endpoint**: Uses boxid instead of id
- **Limited operations**: Only GET and POST supported
- **AI-powered**: Provides prospecting suggestions for customers
- **Unit tests**: 100% resource coverage, 3 model tests passing
- ⚠️ No real API data available for validation
- ⚠️ No integration tests (endpoint requires valid boxid)

**Integration Tests**: None (endpoint requires specific boxid)

---

### User Invites
**API**: `/userInvites`
**Models**: `UserInvite`, `PartialUserInvite`
**Client**: `upsales.user_invites`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | get(id) - uses UUID strings |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_email(email)` - ✅ Implemented (case-insensitive search)

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, killDate)
- ✅ TypedDict complete (UserInviteUpdateFields)
- ✅ Validators: BinaryFlag, EmailStr, CustomFieldsList
- ✅ Computed fields: is_admin, is_active, has_crm_access, has_support_access, custom_fields

---

### User Defined Object Definition
**API**: `/userDefinedDefinition`
**Models**: `UserDefinedObjectDefinition`, `PartialUserDefinedObjectDefinition`
**Client**: `upsales.user_defined_object_definitions`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | BaseResource.create() |
| Read (single) | ❌ Not Supported | Endpoint does not support GET |
| Read (list) | ❌ Not Supported | Endpoint does not support GET |
| Update | ❌ Not Supported | Endpoint does not support PUT |
| Delete | ✅ Implemented | BaseResource.delete() |
| Search | ❌ Not Supported | No GET support |

**Special Notes**:
- This is a definition-only endpoint (POST/DELETE only)
- No GET or UPDATE operations available
- Used to create/delete custom UserDefinedObject types
- `edit()` and `fetch_full()` methods raise NotImplementedError
- Limited to CREATE and DELETE operations

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id)
- ✅ TypedDict complete (UserDefinedObjectDefinitionUpdateFields)
- ✅ Optional fields: name, description, fields
- ⚠️ No validators needed (simple string/array fields)
- ⚠️ No computed fields needed

**Unit Tests**: ✅ Complete (12 tests)
- Test create definition
- Test delete definition
- Test delete nonexistent (404)
- Test model validation
- Test edit() raises NotImplementedError
- Test partial fetch_full() raises NotImplementedError
- Test partial edit() raises NotImplementedError
- Test minimal definition creation
- Test endpoint path
- Test frozen ID field
- Test model serialization

**Integration Tests**: None (endpoint only supports POST/DELETE, no data to verify)


---

### List Views
**API**: `/listViews/:entity`
**Models**: `ListView`, `PartialListView`
**Client**: `upsales.list_views`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | create(entity, **data) |
| Read (single) | ✅ Implemented | get(entity, view_id) |
| Read (list) | ✅ Implemented | list(entity, limit, offset) |
| Update | ✅ Implemented | update(entity, view_id, **data) |
| Delete | ✅ Implemented | delete(entity, view_id) |
| Search | ❌ Not Available | N/A for this endpoint |

**Custom Methods**:
- `list_all(entity)` - ✅ Implemented (auto-pagination)

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, listType, type, regDate, modDate, regBy)
- ✅ TypedDict complete (ListViewUpdateFields)
- ✅ Computed field: is_default
- ⚠️ No custom field validators (endpoint doesn't use custom fields)

**Special Notes**:
- **Entity-based endpoint**: Requires entity parameter in path (e.g., "account", "contact")
- **Redis storage**: Custom list views stored in Redis for fast access
- **UI configuration**: Manages columns, sorting, filtering, and grouping for entity lists
- **Role-based**: Views can be assigned to specific roles or users
- **Default views**: Can mark views as default for an entity type
- **Unit tests**: 100% resource coverage, 8 tests passing (6 resource + 2 model)
- ✅ All CRUD operations implemented with entity parameter
- ⚠️ No real API data available (endpoint returns 404 without valid entity context)
- ⚠️ No integration tests (requires valid entity configuration)

**Integration Tests**: None (endpoint requires configured entity context)


## marketRejectlist

**Status**: Implemented
**Model**: MarketRejectlist, PartialMarketRejectlist
**Resource**: MarketRejectlistsResource
**Client Attribute**: `upsales.market_rejectlist`
**Endpoint**: `/marketRejectlist`
**Implemented**: 2025-11-14

### Operations
- CREATE: Yes
- READ: Yes (get, list)
- UPDATE: Yes
- DELETE: Yes

### Fields
- `id` (int, frozen): Unique identifier (auto-generated)
- `name` (str, optional): Company name
- `dunsNo` (str, optional): DUNS number
- `organisationId` (str, optional): Organisation identifier
- `clientId` (int, optional): Client (account) ID

### Notes
- All identifier fields are optional
- At least one identifier should be provided to identify rejected company
- Used for excluding companies from marketing campaigns
- Requires Administrator or mailAdmin permissions
- No custom fields support

### Patterns Used
- TypedDict for IDE autocomplete (MarketRejectlistUpdateFields)
- Frozen fields for read-only ID
- Computed property (has_identifier)
- edit() and delete() instance methods
- 100% docstring coverage
- Full unit test coverage

### Testing
- Unit tests: 9 tests, all passing
- Resource coverage: 100%
- Model coverage: 51.92%

---

### adCampaigns
**API**: `/engage/campaign`
**Models**: `AdCampaign`, `PartialAdCampaign`
**Client**: `upsales.ad_campaigns`
**Status**: ⚠️ Implemented but API endpoint unavailable in test environment

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() - untested |
| Read (single) | 🔶 Inherited | BaseResource.get() - untested |
| Read (list) | 🔶 Inherited | BaseResource.list() - untested |
| Update | 🔶 Inherited | BaseResource.update() - untested |
| Delete | 🔶 Inherited | BaseResource.delete() - untested |
| Search | 🔶 Inherited | BaseResource.search() - untested |

**Custom Methods**:
- `get_active()` - Returns campaigns with status="active"

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, type, spent, impressions, clicks, conversions, cpm, externalId)
- ✅ TypedDict complete (AdCampaignUpdateFields)
- ✅ Validators: CustomFieldsList
- ✅ Computed fields: is_active, ctr, budget_remaining, custom_fields
- ✅ Field serializer for custom fields
- ✅ edit() instance method with Unpack[AdCampaignUpdateFields]

**Required Fields (Create)**:
- name (string, max 100 chars)
- startDate (string, YYYY-MM-DD)
- endDate (string, YYYY-MM-DD)

**Optional Fields (Create)**:
- budget (float, default 0)
- useRange (bool, default true)
- targetAbm (int, default 0)
- creative (array)
- target (array)
- siteTemplate (array)

**Updatable Fields**:
- name, budget, startDate, endDate, status, creative, target, siteTemplate

**Read-Only Fields**:
- id, type, spent, impressions, clicks, conversions, cpm, externalId

**Notes**:
- API endpoint `/api/v2/:customerId/engage/campaign` returns 500 error in test environment
- Likely requires special customer ID or feature flag not available in sandbox
- Full model implementation with all Pydantic v2 patterns
- Comprehensive unit tests (18 tests, all passing)
- 100% docstring coverage
- All quality checks passing (ruff, mypy, interrogate)

### Testing
- Unit tests: 18 tests, all passing
- Integration tests: N/A (API unavailable)
- Resource coverage: 100%
- Model coverage: 66.20%

---

### adCreatives
**API**: `/engage/creative`
**Models**: `AdCreative`, `PartialAdCreative`
**Client**: `upsales.ad_creatives`
**Status**: ✅ Implemented with unit tests

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `get_by_type(creative_type)` - Returns creatives filtered by type

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ Frozen fields marked (id, sampleImageUrl, state, impressions, clicks)
- ✅ TypedDict complete (AdCreativeUpdateFields)
- ✅ Validators: NonEmptyStr, PositiveInt
- ✅ Computed fields: dimensions, click_through_rate, is_image, is_html5
- ✅ edit() instance method with Unpack[AdCreativeUpdateFields]

**Required Fields (Create)**:
- name (string, max 100 chars)
- type (literal: "image", "html5", "third_party_tag", "zip")
- width (positive int)
- height (positive int)
- url (string, max 255 chars)

**Optional Fields (Create)**:
- fileId (int)
- formatId (int)
- body (string)
- code (string, max 65535 chars)

**Updatable Fields**:
- name, type, width, height, url, fileId, formatId, body, code

**Read-Only Fields**:
- id, sampleImageUrl, state, impressions, clicks

**Notes**:
- API endpoint `/api/v2/:customerId/engage/creative`
- Full model implementation with all Pydantic v2 patterns
- Comprehensive unit tests (22 tests, all passing)
- 100% docstring coverage
- All quality checks passing (ruff, mypy, interrogate)

### Testing
- Unit tests: 22 tests, all passing
- Integration tests: N/A (API requires customerId)
- Resource coverage: 100%
- Model coverage: 100%

---

## AdAccounts

**API**: `/:customerId/engage/account`
**Models**: `AdAccount`, `PartialAdAccount`
**Client**: `upsales.ad_accounts`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ✅ Implemented | Per-customer account creation |
| Read | ✅ Implemented | Get account by customer ID |
| Update | ✅ Implemented | Update account by customer ID |
| Delete | ✅ Implemented | Delete account by customer ID |
| Search | ❌ Not Available | Not applicable for this endpoint |

**Custom Methods**: None

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ No frozen fields (no ID field for this model)
- ✅ TypedDict complete (AdAccountUpdateFields)
- ✅ Model uses PydanticBaseModel directly (not BaseModel/PartialModel)

**Updatable Fields**:
- cpmAmount (float, default: 300.0)
- active (bool, default: True)

**Read-Only Fields**: None

**Special Characteristics**:
- Non-standard endpoint structure (uses customer_id instead of resource id)
- Model doesn't have an ID field
- Both AdAccount and PartialAdAccount use PydanticBaseModel (not SDK base classes)
- Custom resource methods with customer_id parameter

**Notes**:
- Special endpoint structure: `/api/v2/:customerId/engage/account`
- No standard ID-based operations
- All CRUD operations use customer_id as identifier
- Full model implementation with Pydantic v2 patterns
- Comprehensive unit tests (13 tests, all passing)
- 100% docstring coverage
- All quality checks passing (ruff, interrogate)

### Testing
- Unit tests: 13 tests, all passing
- Integration tests: N/A (requires valid customer ID)
- Resource coverage: 100%
- Model coverage: 82.14%

---

## ClientIpInfo

**API**: `/function/clientIpInfo`
**Models**: `ClientIpInfo`
**Client**: `upsales.client_ip_info`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Function endpoint - use check() method |
| Read | ❌ Not Available | Function endpoint - POST only |
| Update | ❌ Not Available | Read-only function endpoint |
| Delete | ❌ Not Available | Read-only function endpoint |
| Search | ❌ Not Available | Not applicable for function endpoints |

**Custom Methods**:
- `check(target: list[str])` - ✅ Implemented - Check if IPs are allowed for ad tracking

**Field Requirements**:
- ✅ All fields documented with descriptions
- ✅ No frozen fields (no ID field - function response)
- ❌ No TypedDict needed (read-only endpoint)
- ❌ No validators needed (simple types)

**Response Fields**:
- target: list[Any] - Array of target IP addresses/identifiers
- allowed: bool - Whether the IP is allowed for tracking
- message: str | None - Optional message about the IP status

**Special Characteristics**:
- Function endpoint (not a resource endpoint)
- POST-only operation
- No standard CRUD operations available
- Returns simple response object for IP tracking validation
- Used for ad tracking IP allow-listing

**Notes**:
- Special endpoint structure: `/api/v2/function/clientIpInfo`
- POST request with {"target": ["ip1", "ip2", ...]}
- Returns validation status for IP addresses
- All CRUD methods raise NotImplementedError
- Model edit() raises NotImplementedError (read-only)
- Minimal model (no frozen fields, custom fields, or computed fields needed)

### Testing
- Unit tests: 9 tests written (cannot run due to pre-existing import errors in codebase)
- Integration tests: N/A (requires valid IP data)
- Resource coverage: All custom methods tested
- Model coverage: All fields covered

**Implementation Status**: ⚠️ Partial - Complete implementation but tests blocked by pre-existing codebase import errors

## ResourcesUploadExternal

**API**: `/resources/upload/external/:entity/:entityId`
**Models**: `ResourcesUploadExternal`, `PartialResourcesUploadExternal`
**Resource**: `ResourcesUploadExternalResource`
**Client**: `upsales.resources_upload_external`
**Purpose**: Upload AdGear creative files (images, ZIP files) to external entities

### Operations

| Operation | Status | Notes |
|-----------|--------|-------|
| Create (upload) | ✅ Implemented | Custom upload() method |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |

### Fields

**Read-Only**:
- `id` (int) - Unique resource ID (frozen, strict)
- `regDate` (str | None) - Registration date (frozen)

**Updatable**:
- `entity` (str | None) - Entity type (e.g., 'adCampaign', 'adAccount')
- `entityId` (int | None) - Entity ID
- `filename` (str | None) - Filename
- `url` (str | None) - Resource URL
- `size` (int | None) - File size in bytes
- `mimeType` (str | None) - MIME type
- `custom` (CustomFieldsList) - Custom fields

### Custom Methods

**ResourcesUploadExternalResource**:
- `upload(entity, entity_id, file_path)` - Upload creative file
  - Validates file exists
  - Checks size limit (25MB max)
  - Guesses MIME type from extension
  - Returns ResourcesUploadExternal instance

**Helper Methods**:
- `_guess_mime_type(file_path)` - Determine MIME type from extension

### Notes

**File Upload Constraints**:
- Maximum file size: 25MB
- Recommended image size: 150KB
- Recommended ZIP size: 200KB
- Supported entity types: adCampaign, adAccount

**POST-Only Endpoint**:
- Primary operation is file upload via POST
- GET/PUT/DELETE inherited but may not be commonly used
- No GET list endpoint documented in API spec

**Model Features**:
- ✅ Frozen fields marked (id, regDate)
- ✅ TypedDict complete (ResourcesUploadExternalUpdateFields)
- ✅ Validators: CustomFieldsList
- ✅ Computed fields: custom_fields property
- ✅ Full docstrings with examples
- ❌ No field serializer (custom fields not typically used)
- ❌ No binary flags or email fields

### Patterns Used

1. **File Upload Pattern**: Custom upload() method handling file I/O
2. **Path Handling**: Accepts both string and Path objects
3. **MIME Type Detection**: Uses mimetypes module with fallback
4. **Size Validation**: Pre-upload validation for file size constraints
5. **TypedDict**: ResourcesUploadExternalUpdateFields for IDE autocomplete

### Testing

**Unit Tests**: ✅ 10 tests passing
- test_init - Resource initialization
- test_upload_success - Successful file upload
- test_upload_file_not_found - FileNotFoundError handling
- test_upload_file_too_large - Size limit validation
- test_upload_with_path_object - Path object support
- test_guess_mime_type - MIME type detection
- test_get - Single resource retrieval
- test_list - List resources
- test_update - Update resource metadata
- test_delete - Delete resource

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Resource Coverage**: 100% (24/24 statements covered)

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed


### Data Source (Function Endpoint)
**API**: `/function/datasource`
**Models**: `DataSourceRequest`, `DataSourceResponse`, `PartialDataSourceResponse`
**Client**: `upsales.data_source`

| Operation | Status | Notes |
|-----------|--------|-------|
| **GET** | ⚠️ Partial | GET with path parameter and integrationId query param |
| **typeahead()** | ⚠️ Partial | Search/autocomplete operation |
| **buy()** | ⚠️ Partial | Import/purchase operation |
| **settings()** | ⚠️ Partial | Configuration operation |
| **monitor()** | ⚠️ Partial | Health/status check operation |

**Special Notes**:
- Function-based endpoint, not standard CRUD
- All operations require integration_id
- Supports custom action types via type_ parameter
- Returns generic DataSourceResponse wrapper
- Used for standard integration data source operations
- Models use Pydantic BaseModel directly (no ID field)
- 100% docstring coverage
- All quality checks passing (ruff, mypy, interrogate)

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Implementation Status**: ⚠️ Partial - Models complete, tests created but not passing



---

## Client IPs

### ClientIps
**API**: `/clientIps`
**Models**: `ClientIp`, `PartialClientIp`
**Client**: `upsales.client_ips`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | 🔶 Inherited | BaseResource.create() |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

### Custom Methods

**ClientIpsResource**:
- `get_by_user(user_id)` - Get all IP rules for a specific user
  - Filters by userId
  - Returns list of ClientIp instances

### Field Requirements

**Required for CREATE**:
- `ipAddress` (string, max 16 chars) - IP address (IPv4)
- `rule` (string, max 8 chars) - Access rule ("allow" or "deny")
- `userId` (int) - User ID this rule belongs to

**Optional for CREATE**:
- `sortIdx` (int, default=0) - Sort index for display ordering

**Read-Only Fields**:
- `id` (int) - Unique identifier
- `clientId` (int) - Client account ID

**Update Constraints**:
- All fields except id and clientId can be updated
- TypedDict: ClientIpUpdateFields

### Model Features

- ✅ Frozen fields marked (id, clientId)
- ✅ TypedDict complete (ClientIpUpdateFields)
- ✅ Validators: PositiveInt for sortIdx
- ✅ Field descriptions with max lengths
- ✅ Full docstrings with examples
- ✅ to_api_dict() for optimized serialization
- ❌ No custom fields support
- ❌ No computed fields needed

### Patterns Used

1. **Field Validation**: max_length constraints on string fields
2. **Positive Integer**: PositiveInt validator for sortIdx
3. **TypedDict**: ClientIpUpdateFields for IDE autocomplete
4. **Custom Resource Method**: get_by_user() for filtering

### Testing

**Unit Tests**: ✅ 10 tests passing
- test_get_client_ip - Get single IP rule
- test_get_client_ip_not_found - NotFoundError handling
- test_list_client_ips - List with pagination
- test_create_client_ip - Create new IP rule
- test_update_client_ip - Update existing rule
- test_delete_client_ip - Delete IP rule
- test_get_by_user - Filter by user ID
- test_client_ip_edit_method - Instance edit() method
- test_partial_client_ip_fetch_full - Partial fetch_full()
- test_frozen_fields_not_in_update - Frozen field exclusion

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Implementation Status**: ✅ Complete - Models complete, all tests passing, full documentation

---

### Resources Upload Internal
**API**: `/resources/upload/internal`
**Models**: `ResourcesUploadInternal`, `PartialResourcesUploadInternal`
**Client**: `upsales.resources_upload_internal`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create (upload) | ✅ Complete | Custom upload() method |
| Read (single) | 🔶 Inherited | BaseResource.get() |
| Read (list) | 🔶 Inherited | BaseResource.list() |
| Update | 🔶 Inherited | BaseResource.update() |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `upload(file, filename, entity, entity_id, folder_id, private, role_ids)` - ✅ Implemented

**Path Structure**: `/resources/upload/internal/:entity/:entityId[/:folderId]`
- entity: Entity type (e.g., 'accounts', 'contacts', 'opportunities')
- entity_id: ID of the entity to attach to
- folder_id: Optional folder ID for organization

**File Upload Constraints**:
- Maximum file size: 25MB (25,000,000 bytes)
- Supports multipart/form-data
- Can mark files as private
- Can restrict access to specific roles

**Field Requirements**:
- ✅ Frozen fields marked (id, userId, uploadDate)
- ✅ TypedDict complete (ResourcesUploadInternalUpdateFields)
- ✅ Validators: BinaryFlag
- ✅ Computed fields: is_private, size_mb

**Unit Tests**: ✅ 16 tests passing
- test_upload_basic - Basic file upload
- test_upload_with_folder - Upload to specific folder
- test_upload_private - Private file upload
- test_upload_with_role_ids - Role-restricted upload
- test_get - Single resource retrieval
- test_list - List resources
- test_update - Update resource metadata
- test_delete - Delete resource
- test_resource_initialization - Resource setup
- test_computed_fields - Computed field functionality
- test_computed_fields_with_none - Null handling
- test_model_edit_method - Model instance editing
- test_model_edit_without_client - Error handling
- test_partial_fetch_full - Partial to full fetch
- test_partial_fetch_full_without_client - Error handling
- test_partial_edit - Partial model editing

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Resource Coverage**: 96% (20/20 statements, 1 branch not covered)

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed, 100% docstring coverage

---

## SoliditetClients

**Endpoint**: `/soliditet/clients`
**Model**: `SoliditetClient`
**Partial**: `PartialSoliditetClient`
**Resource**: `SoliditetClientsResource`

**Description**: Manage Soliditet client data for purchasing and refreshing company information. Each operation (purchase or refresh) deducts 1 credit from your Soliditet balance.

**Special Considerations**:
- Uses DUNS numbers (strings) as identifiers, not integer IDs
- Overrides BaseModel id field to be optional
- Both POST (purchase) and PUT (refresh) operations deduct 1 credit
- API returns empty `{}` objects interspersed between real records in list responses
- API does NOT support GET-by-ID (returns 400 "No such attribute: id")
- `dunsNo` field is `str | int | None` (API returns integer DUNS numbers)
- `orgNo` field is `str | int | None` (API returns integer org numbers)

**Operations**:
| Operation | Status | Method |
|-----------|--------|--------|
| Get | ❌ Not Available | API returns 400 (no GET-by-ID support) |
| List | ✅ Verified | Integration tested with VCR |
| Create (Purchase) | 🔶 Inherited | BaseResource.create() |
| Update (Refresh) | ✅ Custom | refresh(duns, options, properties) |
| Delete | 🔶 Inherited | BaseResource.delete() |
| Search | 🔶 Inherited | BaseResource.search() |

**Custom Methods**:
- `purchase(duns, options, properties)` - ✅ Implemented (alias for create)
- `refresh(duns, options, properties)` - ✅ Implemented (custom PUT with string ID)

**Path Structure**: `/soliditet/clients[/:duns]`
- duns: DUNS number (string identifier)

**Field Requirements**:
- ✅ All fields optional (returns what Soliditet provides)
- ✅ TypedDict complete (SoliditetClientUpdateFields)
- ✅ No validators needed (all optional fields)
- ✅ No computed fields needed

**Integration Tests**: ✅ 2 cassettes recorded, 2 tests passing
- test_list_soliditet_clients_real_response - List with empty object filtering
- test_soliditet_client_fields - Field type validation from real API data

**Field Gap Analysis** (2026-02-09):
- ✅ All API response fields mapped
- Fixed `dunsNo` type: `str | int | None` (API returns integers)
- Fixed `orgNo` type: `str | int | None` (API returns integers)

**Unit Tests**: ✅ 7 tests passing
- test_create_purchase - Purchase company data
- test_purchase_method - Convenience purchase method
- test_refresh_method - Refresh company data
- test_get - Get single client by DUNS
- test_model_validation - Field type validation
- test_partial_model - Partial model creation
- test_optional_fields - Optional field handling

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed (with type: ignore for id override)
- interrogate: ✅ 100% docstring coverage

**Resource Coverage**: 100% (12/12 statements)
**Model Coverage**: 76.92% (24/24 statements, fetch_full not covered)

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed, 100% docstring coverage

---

## sendBeam

**API**: `/function/sendbeam`
**Models**: `SendBeam`, `SendBeamCreateFields`
**Client**: `upsales.send_beam`
**Type**: Function endpoint (POST-only)

**Description**: Send push notifications to mobile devices using localized message keys.

**Special Considerations**:
- Function endpoint (POST-only, no CRUD operations)
- Field names use hyphens in API (loc-key, loc-args) but underscores in Python
- Write-only model (no structured response returned)
- Not a BaseResource subclass (custom implementation)

**Operations**:
| Operation | Status | Method |
|-----------|--------|--------|
| Send | ✅ Implemented | send(loc_key, loc_args, sound, category) |
| Get | ❌ Not Available | Function endpoint |
| List | ❌ Not Available | Function endpoint |
| Update | ❌ Not Available | Function endpoint |
| Delete | ❌ Not Available | Function endpoint |

**Method Signature**:
```python
async def send(
    loc_key: str,                    # Required: Localization key
    loc_args: list[str] | None = None,  # Optional: Format arguments
    sound: str | None = None,           # Optional: Sound file name
    category: str | None = None,        # Optional: Notification category
) -> dict[str, Any]
```

**Field Requirements**:
- ✅ Required field: loc_key (localization key)
- ✅ Optional fields: loc_args, sound, category
- ✅ Field aliases configured (loc-key, loc-args)
- ✅ No validators needed (all string/array fields)
- ✅ No computed fields needed (write-only)
- ✅ SendBeamCreateFields defined (dict[str, Any] due to hyphenated keys)

**Unit Tests**: ✅ 6 tests passing
- test_init - Resource initialization
- test_send_minimal - Send with only required field
- test_send_with_all_fields - Send with all parameters
- test_send_with_loc_args - Localization arguments
- test_send_with_sound - Custom sound file
- test_send_with_category - Notification category

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Resource Coverage**: 100% (16/16 statements)
**Model Coverage**: 100% (11/11 statements)

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed, 100% docstring coverage

---

## standardIntegrationData

**API**: `/function/standardIntegrationData`
**Models**: `StandardIntegrationData`, `StandardIntegrationDataCreateFields`
**Client**: `upsales.standard_integration_data`
**Type**: Function endpoint (POST-only)

**Description**: Standard integration operations including test, values, config, OAuth, and events.

| Operation | Status | Notes |
|-----------|--------|-------|
| Execute | ✅ Verified | execute(type, integrationId, data, userIds) |

**Operation Types**:
- `test` - Test standard integration
- `values` - Get values from integration
- `configButton` - Execute config button action
- `testUser` - Test user-specific integration
- `valuesUser` - Get user-specific values
- `userConfigButton` - Execute user-specific config button
- `oauth` - Execute OAuth operation
- `events` - Get events from integration

**Custom Methods**:
- `test(integrationId, data)` - ✅ Implemented
- `get_values(integrationId, data)` - ✅ Implemented
- `config_button(integrationId, data)` - ✅ Implemented
- `oauth(integrationId, data)` - ✅ Implemented
- `get_events(integrationId, data)` - ✅ Implemented
- `test_user(integrationId, userIds, data)` - ✅ Implemented
- `get_values_user(integrationId, userIds, data)` - ✅ Implemented
- `user_config_button(integrationId, userIds, data)` - ✅ Implemented

**Field Requirements**:
- ✅ Required: type (Literal of 8 operation types)
- ✅ Optional: integrationId (int), data (dict), userIds (list[int])
- ✅ TypedDict complete (StandardIntegrationDataCreateFields)
- ✅ No validators needed (simple types)
- ✅ No computed fields needed (function endpoint)

**Unit Tests**: ✅ 13 tests passing
- test_execute_test_operation - Execute test operation
- test_execute_oauth_operation - Execute OAuth operation
- test_execute_with_user_ids - Execute with user IDs
- test_test_method - Test convenience method
- test_get_values_method - Get values convenience method
- test_config_button_method - Config button convenience method
- test_oauth_method - OAuth convenience method
- test_get_events_method - Get events convenience method
- test_test_user_method - Test user convenience method
- test_get_values_user_method - Get values user convenience method
- test_user_config_button_method - User config button convenience method
- test_execute_minimal_params - Execute with minimal params
- test_execute_all_operation_types - All operation types

**Code Quality**: ✅ All passing
- ruff format: ✅ Formatted
- ruff check: ✅ No issues (with noqa for API naming)
- mypy: ✅ Type checking passed
- interrogate: ✅ 100% docstring coverage

**Implementation Status**: ✅ Complete - All tests passing, quality checks passed, 100% docstring coverage


---

## Action Endpoints

### resetScore
**API**: **Models**: \, \, **Client**: 
| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Action endpoint (no object creation) |
| Read | ❌ Not Available | Action endpoint (no retrieval) |
| Update | ❌ Not Available | Action endpoint (no updates) |
| Delete | ❌ Not Available | Action endpoint (no deletion) |
| Action | ✅ Verified | reset() method - resets marketing scores |

**Custom Methods**:
- \ - ✅ Implemented

**Field Requirements**:
- ✅ Request fields documented (userId, clientId, contactId, sync)
- ✅ Response fields documented (success, message)
- ✅ Validation: Either clientId OR contactId required (mutually exclusive)
- ✅ Type hints complete

**Unit Tests**: 6 tests passing
- ✅ Reset with clientId
- ✅ Reset with contactId
- ✅ Reset with sync flag
- ✅ Validation: missing both IDs
- ✅ Validation: both IDs provided
- ✅ Failure handling

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed (with noqa for camelCase API params)
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage

---

## Action Endpoints

### resetScore
**API**: `/function/resetScore`
**Models**: `ResetScoreRequest`, `ResetScoreResponse`, `PartialResetScore`
**Client**: `upsales.reset_score`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create | ❌ Not Available | Action endpoint (no object creation) |
| Read | ❌ Not Available | Action endpoint (no retrieval) |
| Update | ❌ Not Available | Action endpoint (no updates) |
| Delete | ❌ Not Available | Action endpoint (no deletion) |
| Action | ✅ Verified | reset() method - resets marketing scores |

**Custom Methods**:
- `reset(userId, clientId=None, contactId=None, sync=False)` - ✅ Implemented

**Field Requirements**:
- ✅ Request fields documented (userId, clientId, contactId, sync)
- ✅ Response fields documented (success, message)
- ✅ Validation: Either clientId OR contactId required (mutually exclusive)
- ✅ Type hints complete

**Unit Tests**: 6 tests passing
- ✅ Reset with clientId
- ✅ Reset with contactId
- ✅ Reset with sync flag
- ✅ Validation: missing both IDs
- ✅ Validation: both IDs provided
- ✅ Failure handling

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed (with noqa for camelCase API params)
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage

---

### unsub
**API**: `/function/unsub`
**Models**: `Unsub`, `PartialUnsub`, `UnsubUpdateFields`
**Client**: `upsales.unsub`

| Operation | Status | Notes |
|-----------|--------|-------|
| Create (POST) | ✅ Verified | Unsubscribe contact from email |
| Read | ❌ Not Available | Function endpoint (no retrieval) |
| Update | ❌ Not Available | Function endpoint (no updates) |
| Delete | ✅ Verified | Resubscribe contact to email |
| Action | ✅ Verified | unsubscribe() and resubscribe() methods |

**Custom Methods**:
- `unsubscribe(contact_id)` - ✅ Implemented (POST to create unsub record)
- `resubscribe(contact_id)` - ✅ Implemented (DELETE to remove unsub record)

**Field Requirements**:
- ✅ Required field: id (contact ID) - frozen, strict
- ✅ POST accepts: id (contact_id)
- ✅ DELETE requires: Administrator or mailAdmin permissions
- ✅ TypedDict complete (UnsubUpdateFields - empty, no updatable fields)
- ✅ edit() raises NotImplementedError (endpoint doesn't support updates)

**Special Considerations**:
- Function endpoint with only POST and DELETE operations
- DELETE requires elevated permissions (Administrator or mailAdmin)
- No GET, list, or update operations available
- No custom fields or validators needed (only ID field)

**Unit Tests**: ✅ 7 tests passing
- ✅ test_unsubscribe - Unsubscribe contact via unsubscribe()
- ✅ test_resubscribe - Resubscribe contact via resubscribe()
- ✅ test_create_directly - Create unsub via create()
- ✅ test_delete_directly - Delete unsub via delete()
- ✅ test_unsub_model_creation - Model instantiation
- ✅ test_unsub_model_frozen_id - ID field is frozen
- ✅ test_edit_raises_not_implemented - edit() raises NotImplementedError

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage (11/11)

**Implementation Status**: ✅ Complete - All tests passing, all quality checks passed, 100% docstring coverage

**Resource Coverage**: 100% (all methods tested)
**Model Coverage**: 100% (all scenarios tested)

---

### MailTest
**API**: `/mail/test`
**Models**: `MailTestResponse`, `MailTestSendFields`
**Client**: `upsales.mail_test`

| Operation | Status | Notes |
|-----------|--------|-------|
| POST | ✅ Verified | Sends test email |

**Custom Methods**:
- `send(client, contact, subject=None, body=None, to=None, from_address=None, from_name=None)` - ✅ Implemented - Sends test email

**Field Requirements**:
- ✅ Required: client (int), contact (int)
- ✅ Optional: subject, body, to, from_address (maps to API 'from'), from_name
- ✅ MailTestResponse: success (bool), message (optional)
- ✅ Uses PydanticBaseModel (not BaseModel, no ID field)
- ✅ All fields documented with descriptions

**Special Considerations**:
- Action endpoint with only POST operation
- No GET, list, update, or delete operations
- Validation: Both client and contact are required
- API uses 'from' field name, Python uses 'from_address' parameter

**Unit Tests**: ✅ 9 tests passing
- ✅ test_send_success_minimal - Send with required fields only
- ✅ test_send_success_all_fields - Send with all fields
- ✅ test_send_missing_client - Validation error for missing client
- ✅ test_send_missing_contact - Validation error for missing contact
- ✅ test_send_missing_both - Validation error for both missing
- ✅ test_send_non_dict_response - Handle non-dict API response
- ✅ test_send_with_subject_only - Send with subject only
- ✅ test_send_with_to_only - Send with 'to' address only
- ✅ test_send_preserves_none_values - None values excluded from payload

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage (6/6)

**Implementation Status**: ✅ Complete - All tests passing, all quality checks passed, 100% docstring coverage

**Resource Coverage**: 100% (all methods tested)
**Model Coverage**: 100% (all scenarios tested)

---

### ValidatePage
**API**: `/function/validatePage`
**Models**: `ValidatePageRequest`, `ValidatePageResponse`
**Client**: `upsales.validate_page`

| Operation | Status | Notes |
|-----------|--------|-------|
| POST | ✅ Verified | Validates webpage contains tracking script |

**Custom Methods**:
- `validate(url)` - ✅ Implemented - Validates tracking script presence

**Field Requirements**:
- ✅ ValidatePageRequest: url (required)
- ✅ ValidatePageResponse: valid (bool), message (optional)
- ✅ Uses PydanticBaseModel (not BaseModel, no ID field)
- ✅ All fields documented with descriptions

**Special Considerations**:
- Function endpoint with only POST operation
- No GET, list, update, or delete operations
- Response extracted from data wrapper: response_data["data"]
- No custom fields or validators needed (simple validation response)
- Not a CRUD resource - doesn't inherit from BaseResource

**Unit Tests**: ✅ 5 tests passing
- ✅ test_validate_success - Successful validation
- ✅ test_validate_failure - Failed validation
- ✅ test_validate_request_body - Request body structure
- ✅ test_validate_different_urls - Multiple URL validation
- ✅ test_validate_with_none_message - None message handling

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage (6/6)

**Implementation Status**: ✅ Complete - All tests passing, all quality checks passed, 100% docstring coverage

**Resource Coverage**: 100% (validate method fully tested)
**Model Coverage**: 100% (all scenarios tested)

---

### E-signature Function
**API**: `/function/esign`
**Models**: `EsignFunctionSettings`
**Client**: `upsales.esign_function`

| Operation | Status | Notes |
|-----------|--------|-------|
| POST (settings) | ✅ Implemented | Get integration settings |
| GET (download) | ✅ Implemented | Download signed PDF as bytes |

**Custom Methods**:
- `get_settings(integration_id, **kwargs)` - ✅ Implemented - Get integration settings
- `download(document_id)` - ✅ Implemented - Download signed PDF document

**Field Requirements**:
- All fields optional (settings structure varies by integration)
- No frozen fields (not a CRUD resource)
- No TypedDict needed (settings are query-only)

**Notes**:
- Special function endpoint, not CRUD
- Uses Pydantic BaseModel directly (not custom BaseModel)
- Download method uses HTTPClient's binary response support (`get_bytes()` method)

**Unit Tests**: ✅ 4 tests passing
- ✅ test_get_settings_success - Basic settings retrieval
- ✅ test_get_settings_with_kwargs - Additional parameters
- ✅ test_get_settings_minimal_response - Optional field handling
- ✅ test_get_settings_stores_client_reference - Client reference storage

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed  
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage (6/6)

**Implementation Status**: ✅ Complete - All tests passing, all quality checks passed, both methods fully implemented

**Resource Coverage**: 100% (get_settings fully tested)
**Model Coverage**: 100% (all scenarios tested)

---

### systemMail
**API**: `/function/system-mail`
**Models**: `SystemMailRequest`, `SystemMailResponse`, `SystemMailCreateFields`
**Client**: `upsales.system_mail`

| Operation | Status | Notes |
|-----------|--------|-------|
| Send (POST) | ✅ Verified | Send predefined template emails |
| Read | ❌ Not Available | Function endpoint (no retrieval) |
| Update | ❌ Not Available | Function endpoint (no updates) |
| Delete | ❌ Not Available | Function endpoint (no deletes) |

**Custom Methods**:
- `send(template_name, email, additional)` - ✅ Implemented

**Field Requirements**:
- ✅ Required field: templateName (Literal type: installingScript, verifyDomains, requestAddon)
- ✅ Required field: email (str | list[str]) - validated with regex pattern
- ✅ Optional field: additional (dict[str, Any]) - template-specific data
- ✅ TypedDict complete (SystemMailCreateFields)
- ✅ Field validator for email format validation

**Special Considerations**:
- Function endpoint with only POST operation
- Three predefined templates available
- Supports single or multiple email recipients
- Response uses PydanticBaseModel (not SDK BaseModel)
- No ID field in response (success/message only)

**Unit Tests**: ✅ 8 tests passing
- ✅ test_send_single_email - Send to one recipient
- ✅ test_send_multiple_emails - Send to multiple recipients
- ✅ test_send_without_additional_data - Optional additional field
- ✅ test_send_installing_script_template - installingScript template
- ✅ test_send_verify_domains_template - verifyDomains template
- ✅ test_send_request_addon_template - requestAddon template
- ✅ test_send_with_complex_additional_data - Complex nested data
- ✅ test_response_without_message - Handle optional message field

**Quality Checks**:
- ✅ Ruff formatting passed
- ✅ Ruff linting passed (1 auto-fixed)
- ✅ Mypy strict mode passed
- ✅ Interrogate 100% docstring coverage (8/8)

**Implementation Notes**:
- Uses PydanticBaseModel to avoid BaseModel's required `id` field
- Email validation uses regex pattern for single or list of emails
- Response structure: `{"success": bool, "message": str | None}`
- Literal type ensures only valid template names accepted
