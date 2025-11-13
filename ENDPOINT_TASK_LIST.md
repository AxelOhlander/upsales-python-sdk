# Endpoint Implementation Task List

This file tracks the status of all Upsales API endpoints in the SDK.

**Last Updated**: 2025-11-07
**Source**: Synced with `api_endpoints_with_fields.json` (167 total endpoints)

---

## 📊 Implementation Status Dashboard

### Current Coverage
- **Total API Endpoints**: 167 (from api_endpoints_with_fields.json)
- **SDK Resources Implemented**: 36 (21.6% coverage)
- **Remaining to Implement**: 131 endpoints (78.4%)

### Verification Status
| Category | Count | Percentage |
|----------|-------|------------|
| **✅ Fully Verified** | 7 | 4.2% |
| **🔶 Implemented, Needs Verification** | 29 | 17.4% |
| **❌ Not Implemented** | 131 | 78.4% |

### CREATE Operation Status
| Status | Count | Details |
|--------|-------|---------|
| **✅ Verified** | 2 | Orders (5 required fields), Contacts (1 required field) |
| **🔶 Inherited, Unverified** | 14 | CREATE exists but requirements not tested |
| **❌ Not Implemented** | 73 | API supports CREATE but no SDK support |

### Coverage by Business Area
| Area | Implemented | Total | Coverage |
|------|-------------|-------|----------|
| **Core CRM** | 6 | 6 | 100% |
| **Sales Pipeline** | 2 | 4 | 50% |
| **Configuration** | 12 | 26 | 46% |
| **Customization** | 3 | 14 | 21% |
| **Integration** | 1 | 23 | 4% |
| **Reporting** | 0 | 8 | 0% |
| **Admin** | 0 | 15 | 0% |
| **Specialized** | 11 | 71 | 15% |

---

## 📈 Coverage Roadmap & Milestones

### Current: 21% Coverage (35/167 endpoints)

| Milestone | Target Coverage | Endpoints Added | Timeline |
|-----------|-----------------|-----------------|----------|
| ✅ **Foundation** | 21% | 35 resources | Completed |
| 🎯 **Phase 1** | 21% | 0 new (verify existing) | 1 week |
| 🎯 **Phase 2** | 24% | 4 new (opportunities, agreements, tickets, events) | 2 weeks |
| 🎯 **Phase 3** | 30% | 11 new (customfields, ad, quota, report) | 1 month |
| 🎯 **Phase 4** | 50% | 34 new (mid-priority specialized) | 3 months |
| 🎯 **Complete** | 100% | 132 total | 6-12 months |

### Recommended Focus

**Next Sprint (1-2 weeks)**:
1. Verify CREATE for 3 remaining high-priority endpoints (activities, appointments, accounts)
2. Implement opportunities (30 min)
3. Implement agreements (60 min)
4. **Result**: All core business operations fully verified

**This Quarter**:
1. Complete Phase 2 (high-priority missing)
2. Start Phase 3 (configuration endpoints)
3. **Result**: 30% coverage, all critical operations supported

---

## 🎯 Immediate Action Items (This Week)

### Phase 1A: Verify CREATE for High-Priority Implemented Endpoints

---

#### 1. **Verify activities CREATE** 🔴 CRITICAL
**Status**: 🔶 Implemented, Needs Verification
**API File Reference**: `api_endpoints_with_fields.json → endpoints.activities.methods.POST`

**From API File - Required Fields**:
- `date` (date, format: "YYYY-MM-DD", optional for TODO/PHONE_CALL types)
- `userId` (number)
- `activityTypeId` (number)
- `client` (object, structure: `{"id": number}`, optional for TODO type)

**Tasks**:
- [ ] Test CREATE with minimal fields
- [ ] Create `ActivityCreateFields` TypedDict
- [ ] Document conditional requirements (TODO type variations)
- [ ] Verify nested required fields pattern
- [ ] Record VCR cassette
- [ ] Update endpoint-map.md with ✅ Verified

**Estimated Time**: 60 minutes
**Dependencies**: None
**Priority**: 🔴 CRITICAL

---

#### 2. **Verify appointments CREATE** 🔴 CRITICAL
**Status**: 🔶 Implemented, Needs Verification
**API File Reference**: `api_endpoints_with_fields.json → endpoints.appointments.methods.POST`

**From API File - Needs Analysis**: Review api_endpoints_with_fields.json for required fields

**Tasks**:
- [ ] Read api_endpoints_with_fields.json for appointments.POST.required
- [ ] Test CREATE with minimal fields
- [ ] Create `AppointmentCreateFields` TypedDict
- [ ] Verify nested required fields pattern
- [ ] Record VCR cassette
- [ ] Update endpoint-map.md with ✅ Verified

**Estimated Time**: 60 minutes
**Dependencies**: None
**Priority**: 🔴 CRITICAL

---

#### 3. **Verify accounts (companies) CREATE** 🟡 MEDIUM
**Status**: 🔶 Implemented, CREATE NOT VERIFIED
**API File Reference**: `api_endpoints_with_fields.json → endpoints.accounts.methods.POST`

**From API File - Required Fields**:
- `name` (string, maxLength: 100) **ONLY ONE REQUIRED!**

**From API File - Optional Fields** (with nested structures):
- `users` (array, structure: `[{"id": number}]`)
- `addresses` (array, structure: `[{address, city, zipcode, country, type}]`)
- `categories` (array, structure: `[{"id": number}]`)
- `custom` (array)

**Missing**:
- [ ] Create `CompanyCreateFields` TypedDict
- [ ] Add test_create_company_minimal_fields() integration test
- [ ] Add test_create_company_with_optional_fields() integration test
- [ ] Test CREATE with minimal: `{name: "Test Company"}`
- [ ] Test nested arrays (users, addresses, categories)
- [ ] Record VCR cassettes
- [ ] Update endpoint-map.md with ✅ Verified

**Estimated Time**: 60 minutes
**Dependencies**: None
**Priority**: 🟡 MEDIUM (only name required, low technical risk)

**Total Estimated Time for Phase 1A**: ~2.5 hours (3 remaining tasks)

---

### Phase 1B: Implement High-Priority Missing Endpoints

#### 4. **Implement opportunities endpoint** 🔴 CRITICAL
**Status**: ❌ Not Implemented
**API File Reference**: `api_endpoints_with_fields.json → endpoints.opportunities`

**From API File**:
- Uses same model as Orders
- Difference: Stage probability must be 1-99 (not 0 or 100)
- Same required fields as Orders

**Tasks**:
- [ ] Review api_endpoints_with_fields.json for opportunities
- [ ] Add probability range validation to Order model (or subclass)
- [ ] Create OpportunitiesResource extending OrdersResource
- [ ] Override create() to validate probability 1-99
- [ ] Add to client.py as `upsales.opportunities`
- [ ] Add integration tests with VCR
- [ ] Update endpoint-map.md

**Estimated Time**: 30 minutes (reuses Order model)
**Dependencies**: None (Order model already complete)
**Priority**: 🔴 CRITICAL

---

#### 5. **Implement agreements endpoint** 🔴 HIGH
**Status**: ❌ Not Implemented
**API File Reference**: `api_endpoints_with_fields.json → endpoints.agreements`

**From API File - Required Fields (9 total)**:
- `client` (object: `{"id": number}`)
- `user` (object: `{"id": number}`)
- `name` (string, maxLength: 100)
- `startDate` (string, format: "YYYY-MM-DD")
- `endDate` (string, format: "YYYY-MM-DD")
- `value` (number)
- `interval` (number, 1=monthly, 12=yearly)
- `agreementRow` (array: `[{"product": {"id": number}}]`)
- `currency` (string)

**Tasks**:
- [ ] Generate Agreement model: `uv run upsales generate-model agreements --partial`
- [ ] Record VCR cassette (Step 2)
- [ ] Create AgreementCreateFields TypedDict (9 required fields)
- [ ] Verify nested required fields: client.id, user.id, agreementRow with product.id
- [ ] Create AgreementsResource extending BaseResource
- [ ] Add custom methods (get_active, get_by_client, get_recurring)
- [ ] Register in client.py as `upsales.agreements`
- [ ] Integration tests
- [ ] Update endpoint-map.md

**Estimated Time**: 60 minutes
**Dependencies**: None
**Priority**: 🔴 HIGH (recurring revenue tracking)

---

### Phase 2: Implement High-Priority Missing Endpoints (2 weeks)

**4 critical endpoints not yet implemented:**

#### opportunities 🔴 CRITICAL
- Shares Order model, different probability range (1-99)
- Estimated: 30 minutes (model reuse)

#### agreements 🔴 HIGH
- 9 required fields with nested structures
- Recurring revenue tracking
- Estimated: 60 minutes

#### tickets 🟡 MEDIUM
- 5 required fields
- Support ticket system
- Estimated: 60 minutes

#### events 🟡 MEDIUM
- 3 required fields
- Activity timeline events
- Estimated: 45 minutes

**Total Estimated Time for Phase 2**: ~3 hours

---

### Phase 3: Medium-Priority Configuration Endpoints (1 month)

**11 feature/configuration endpoints:**

#### CustomFields Endpoints (7 endpoints)
- `customfields_accounts` - Custom field definitions for accounts
- `customfields_activities` - Custom field definitions for activities
- `customfields_appointments` - Custom field definitions for appointments
- `customfields_contacts` - Custom field definitions for contacts
- `customfields_orderrows` - Custom field definitions for order rows
- `customfields_orders` - Custom field definitions for orders
- `customfields_products` - Custom field definitions for products

**Note**: Currently have generic `custom_fields` resource. May need entity-specific resources.

#### Advertising/Marketing (2 endpoints)
- `adAccounts` - Ad account configuration
- `adCampaigns` - Campaign management with budget/targeting

#### Reporting/Analytics (2 endpoints)
- `quota` - Sales quotas
- `report` - Dynamic reporting API (Elasticsearch-based)

**Total Estimated Time for Phase 3**: ~7-9 hours (11 endpoints × 40-50 min avg)

---

### Phase 4: Low-Priority Specialized Endpoints (3-6 months)

**129 specialized/admin endpoints** including:

**Categories**:
- Admin tools (provisioning, userInvites, roleSettings)
- Email management (mailDomains, mailEditor, emailSuggestion)
- Integration helpers (standardIntegrationData, standardIntegrationUser)
- Soliditet integration (Swedish company data - 5 endpoints)
- Marketing automation (engage*, socialEvents*, standardCreative)
- Search utilities (quickSearch, emailSuggest, placeholder)
- User-defined objects (userDefinedObject1-4)
- Misc utilities (whatIsMyIp, workerStatus, validatePage)

**Strategy**: Implement on-demand as users request features

---

## 📊 Endpoint Categories Analysis

### By Implementation Status

| Category | Implemented | Total | Coverage |
|----------|-------------|-------|----------|
| **Core CRM** (orders, contacts, accounts, activities, appointments, users) | 6/6 | 6 | 100% |
| **Sales Pipeline** (orders, opportunities, orderStages, agreements) | 2/4 | 4 | 50% |
| **Configuration** (roles, currencies, segments, etc.) | 12/26 | 26 | 46% |
| **Customization** (custom_fields, triggers, forms) | 3/14 | 14 | 21% |
| **Integration** (standard_integrations, ad*, soliditet*) | 1/23 | 23 | 4% |
| **Reporting** (report, quota, activityQuota, scoreboard) | 0/8 | 8 | 0% |
| **Admin** (provisioning, userInvites, roleSettings) | 0/15 | 15 | 0% |
| **Specialized** (mail*, esigns, voice, etc.) | 11/71 | 71 | 15% |

### By CRUD Support

From api_endpoints_with_fields.json analysis:

| Operation | Total Endpoints | Implemented | Verified | Gap |
|-----------|-----------------|-------------|----------|-----|
| **GET** (list) | 167 | 35 | 20 | 132 |
| **GET** (item) | 159 | 35 | 20 | 124 |
| **POST** (create) | 89 | 16 | 2 | 73 |
| **PUT** (update) | 82 | 16 | 1 | 66 |
| **DELETE** | 76 | 20 | 0 | 56 |

**Key Insight**: 89 endpoints support CREATE but only 2 verified (Orders, Contacts). This is the biggest gap.

---

## 🗂️ Master Endpoint Reference

**Source**: api_endpoints_with_fields.json contains 167 endpoints

### How to Use API File for Any Endpoint

**Before implementing any endpoint**, consult the API file:

```bash
# 1. Check endpoint structure
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name'

# 2. Get required fields for CREATE
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required'

# 3. Get allowed fields for UPDATE
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.PUT.allowed'

# 4. Get read-only fields
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.PUT.readOnly'
```

**See CLAUDE.md** for complete documentation on using api_endpoints_with_fields.json.

---

## Master Task List

Centralized, up-to-date tasks across the project. Status legend below applies.

### CLI
- [✓] Validate command implemented (see `upsales/cli.py:728`)
- [✓] Init resource command implemented (see `upsales/cli.py:893`)
- [ ] Add validate checks for ruff/mypy/bandit invocation outputs to be parsed and surfaced richer in table

### Query Enhancements
- [✓] Field selection in list/list_all via `f[]` (see `upsales/resources/base.py:236`)
- [✓] Sorting in list/list_all via `sort` (see `upsales/resources/base.py:241`)
- [✓] Search() helper with natural→API operator mapping (see `upsales/resources/base.py:332` and mapping at `upsales/resources/base.py:453`)
- [ ] Tests for `search()` and `f[]`/`sort` behavior in resources (no direct tests found)
- [ ] Docs: add short usage section for `search()` and operator mapping in README/docs
- [ ] Optional: QueryBuilder (fluent API) and `q[]` nested queries (not implemented)

### Mail Templates (Typed Components)
- [ ] Add typed models for attachments/labels/roles (e.g., `mail_template_components.py`)
- [~] Update `upsales/models/mail_templates.py` to use typed lists instead of `list[Any]` (partially typed; see `upsales/models/mail_templates.py:58, 96`)
- [ ] Field serializers for JSON conversion where needed
- [ ] TypedDict updates to reflect typed components
- [ ] Unit/integration tests for mail templates
- [ ] Docs update

### Contacts Model Typing
- [✓] Use `PartialSegment` and `PartialJourneyStep` (see `upsales/models/contacts.py:78`, `upsales/models/contacts.py:309`)
- [ ] Improve `ContactUpdateFields.segments` typing (currently `list[dict[str, Any]]`)
- [ ] Consider typing `Contact.journeyStep` as partial in full model for parity

### Dict-to-Model Migration (dot-access for nested objects)
- Activities (`upsales/models/activities.py`)
  - [✓] `client` → `PartialCompany`; `regBy`/`users` → `PartialUser`; `contacts` → `PartialContact`.
  - [✓] `opportunity` → `PartialOrder`; `project` → `PartialProject`.
  - [ ] `projectPlan` → typed model if stable; `callList` → typed or document as dynamic.
  - [ ] `activityType`/`lastOutcome`/`outcomes` → consider `ActivityType` and `ActivityOutcome` models or keep dict with rationale; update docs accordingly.
  - [✓] Unit test asserting dot-access added (`tests/unit/test_activities_model_typing.py`).
- Activity List Item (`upsales/models/activity_list_item.py`)
  - [✓] `project` → `PartialProject`; `opportunity` → `PartialOrder`; `regBy` → `PartialUser`; `templateId` → `PartialMailTemplate`.
  - [ ] Review `activityType`/`projectPlan`/`clientConnection` for typing vs dynamic; document rationale.
  - [✓] Unit test asserting dot-access added (`tests/unit/test_activity_list_item_typing.py`).
- Appointments (`upsales/models/appointments.py`)
  - [✓] `client`/`opportunity`/`project`/`users`/`regBy` use Partial models.
  - [ ] `activityType`/`source`/`projectPlan` → evaluate and introduce models or document as dict with reason.
- Companies (`upsales/models/company.py`)
  - [✓] `assigned` → `Assignment`; `mailAddress` → `Address`; `parent`/`operationalAccount` → `PartialCompany`; `regBy` → `PartialUser`; `processedBy` → `ProcessedBy`.
  - [ ] Review remaining dicts: `growth`, `soliditet`, `supportTickets`, `source`, `extraFields` (custom) — classify as dynamic vs model candidates; propose models where schema is stable.
  - [ ] PartialCompany extras still dicts (`operationalAccount`, `journeyStep`, `users`) — type or document where feasible.
- Orders (`upsales/models/orders.py`)
  - [✓] `client`/`user`/`contact`/`stage`/`regBy` use Partial models.
  - [ ] Consider typing `risks`, `periodization`, `salesCoach`, `lastIntegrationStatus`, `orderRow` as structured models if schemas are stable; otherwise document.
- General
  - [ ] For UpdateFields TypedDicts, keep `dict[str, Any]` for inputs unless strict schemas exist; document rationale in CONTRIBUTING.
  - [ ] Add unit tests asserting dot-access on migrated fields (e.g., `activity.project.id`, `appointment.opportunity.id`).
  - [ ] Update docstrings/examples to showcase dot-access consistently across models.

## Status Legend
- `[✓]` - Complete (model, resource, tests, all quality checks pass)
- `[→]` - In progress
- `[ ]` - Not started
- `[~]` - No data available (endpoint exists but returns empty)
- `[-]` - Skipped (deprecated or not needed)

## Completed Endpoints

### [✓] apiKeys
**Status**: COMPLETE
**Endpoint**: `/api/v2/apiKeys`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/apiKeys.py` (Apikey, PartialApikey, ApikeyUpdateFields)
- Resource: `upsales/resources/apikeys.py` (ApikeysResource)
- Unit tests: `tests/unit/test_apikeys_resource.py` (11 tests, 100% pass)
- Integration tests: `tests/integration/test_apikeys_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_active()`, `get_inactive()`, `get_by_name()`
- Computed fields: `is_active`
- Pydantic v2 validators: NonEmptyStr
- Field descriptions for all fields
- Optimized serialization with to_api_dict()
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS (N999 ignored - file matches API endpoint naming)
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 11/11 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] clientcategories
**Status**: COMPLETE
**Endpoint**: `/api/v2/clientcategories`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/clientcategories.py` (ClientCategory, PartialClientCategory, ClientCategoryUpdateFields)
- Resource: `upsales/resources/clientcategories.py` (ClientCategoriesResource)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_by_name()`, `get_with_roles()`, `get_by_type()`
- Computed fields: `has_roles`, `role_count`
- Pydantic v2 validators: NonEmptyStr
- Field descriptions for all fields
- Optimized serialization with to_api_dict()
- Integration with PartialRole for nested role data

**Quality Checks**:
- ✅ Models created with proper structure
- ✅ Resource manager with custom methods
- ✅ Registered in Upsales client
- ✅ Exported in __init__.py files
- ✅ 100% docstring coverage

**Completed**: 2025-11-03

---

### [✓] contacts
**Status**: COMPLETE ✅
**Endpoint**: `/api/v2/contacts`
**Priority**: CRITICAL (Core CRM entity)
**Verification Date**: 2025-11-07
**Files**:
- Model: `upsales/models/contacts.py` (Contact, PartialContact, ContactCreateFields, ContactUpdateFields)
- Resource: `upsales/resources/contacts.py` (ContactsResource)
- Unit tests: `tests/unit/test_contacts_resource.py`
- Integration tests: `tests/integration/test_contacts_integration.py` (6 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete) - ALL VERIFIED
- Custom methods: `get_by_email()`, `search()`
- Computed fields: `is_active`, `full_name`, `has_phone`, `custom_fields`
- Pydantic v2 validators: BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr
- Field descriptions for all fields
- Optimized serialization with to_api_dict()
- Integration with PartialCompany, PartialProject, PartialSegment, PartialJourneyStep
- 100% docstring coverage
- VCR cassettes recorded for all operations including CREATE

**CREATE Operation (Verified 2025-11-07)**:
- **Required fields**: ONLY 1 field required!
  - `client: {"id": client_id}` (minimal nested structure)
- **Optional fields**: email, name, firstName, lastName, phone, cellPhone, title, active, notes, etc.

**Important Finding**:
- Email is **OPTIONAL** (api_endpoints_with_fields.json incorrectly listed it as required)
- Only client.id is required
- Uses minimal nested required field pattern
- Simplest CREATE operation verified so far

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: PASS
- ✅ Integration tests: 6/6 PASS (including 2 CREATE tests)
- ✅ CREATE with minimal fields: VERIFIED
- ✅ CREATE with optional fields: VERIFIED
- ✅ ContactCreateFields TypedDict: COMPLETE
- ✅ VCR cassettes: RECORDED

**Completed**: 2025-11-07

---

### [✓] segments
**Status**: COMPLETE
**Endpoint**: `/api/v2/segments`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/segments.py` (Segment, PartialSegment, SegmentUpdateFields)
- Resource: `upsales/resources/segments.py` (SegmentsResource)
- Unit tests: `tests/unit/test_segments_resource.py` (11 tests, 100% pass)
- Integration tests: `tests/integration/test_segments_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_active()`, `get_populated()`, `get_by_name()`
- Computed fields: `is_active`, `has_contacts`, `is_used_for_prospecting`
- Pydantic v2 validators: BinaryFlag, NonEmptyStr
- 100% docstring coverage
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 11/11 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] triggers
**Status**: COMPLETE
**Endpoint**: `/api/v2/triggers`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/triggers.py` (Trigger, PartialTrigger, TriggerUpdateFields)
- Resource: `upsales/resources/triggers.py` (TriggersResource)
- Unit tests: `tests/unit/test_triggers_resource.py` (12 tests, 100% pass)
- Integration tests: `tests/integration/test_triggers_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_active()`, `get_by_name()`, `get_by_event()`
- Computed fields: `is_active`, `has_events`, `has_actions`, `has_criterias`
- Pydantic v2 validators: BinaryFlag, NonEmptyStr
- 100% docstring coverage
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 12/12 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [~] flows
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/flows`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "offset": 0, "limit": 1000},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [~] leads2
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/leads2`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "offset": 0, "limit": 1000},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [~] projectPlan
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/projectPlan`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "offset": 0, "limit": 2000},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [✓] projectPlanPriority
**Status**: COMPLETE
**Endpoint**: `/api/v2/projectPlanPriority`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/projectplanpriority.py` (ProjectPlanPriority, PartialProjectPlanPriority, ProjectPlanPriorityUpdateFields)
- Resource: `upsales/resources/projectplanpriority.py` (ProjectPlanPrioritiesResource)
- Unit tests: `tests/unit/test_projectplanpriority_resource.py` (16 tests, 100% pass)
- Integration tests: `tests/integration/test_projectplanpriority_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_by_category()`, `get_defaults()`, `get_by_name()`, `get_low()`, `get_medium()`, `get_high()`
- Computed fields: `is_default`, `is_low`, `is_medium`, `is_high`
- Pydantic v2 validators: NonEmptyStr
- Field descriptions for all fields
- 100% docstring coverage
- VCR cassettes recorded for integration tests
- Priority categories: LOW, MEDIUM, HIGH

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 16/16 PASS (100% resource coverage)
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] projectPlanStages
**Status**: COMPLETE
**Endpoint**: `/api/v2/projectPlanStages`
**Priority**: MEDIUM
**Verification Date**: 2025-11-09

**Files**:
- Model: `upsales/models/projectPlanStages.py` (Projectplanstage, PartialProjectplanstage, ProjectplanstageUpdateFields)
- Resource: `upsales/resources/projectPlanStages.py` (ProjectplanstagesResource)
- Unit tests: `tests/unit/test_project_plan_stages_resource.py` (10 tests, 100% pass)
- Integration tests: `tests/integration/test_project_plan_stages_integration.py` (1 test, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- BaseResource inheritance with bulk operations
- Pydantic v2 with strict validation
- Field descriptions for all fields (id, name, category, color)
- 100% docstring coverage
- VCR cassettes recorded for offline testing

**Field Structure**:
- `id` (int, frozen): Unique stage ID
- `name` (str): Stage name (e.g., "Att göra", "Pågående", "Klar")
- `category` (str): Stage category (TODO, IN_PROGRESS, DONE)
- `color` (str): Color code for visual representation (e.g., "#FCF0C0")

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS (N999 warnings acceptable)
- ✅ Mypy type check: PASS (--strict)
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 10/10 PASS (100% resource coverage)
- ✅ Integration tests: 1/1 PASS

**CRUD Operations Verified**:
- READ: ✅ Verified (3 stages returned from API)
- UPDATE: ✅ Supported (editable: name, category, color)
- Frozen fields: id (primary key)

**Notes**:
- Simple lookup/reference data endpoint
- 3 stages available in test tenant
- All fields present in 100% of API responses
- No custom fields or computed fields needed

**Completed**: 2025-11-09

---

### [~] mailCampaigns
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/mailCampaigns`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "offset": 0, "limit": 1},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [~] notifications
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/notifications`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [✓] forms
**Status**: COMPLETE
**Endpoint**: `/api/v2/forms`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/forms.py` (Form, PartialForm, FormUpdateFields)
- Resource: `upsales/resources/forms.py` (FormsResource)
- Unit tests: `tests/unit/test_forms_resource.py` (12 tests, 100% pass)
- Integration tests: `tests/integration/test_forms_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_active()`, `get_archived()`, `get_with_submissions()`, `get_by_name()`, `get_by_title()`
- Computed fields: `is_archived`, `has_submissions`, `submission_count`, `view_count`
- Pydantic v2 validators: BinaryFlag, NonEmptyStr
- 100% docstring coverage
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 12/12 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] files
**Status**: COMPLETE
**Endpoint**: `/api/v2/files`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/files.py` (File, PartialFile, FileUpdateFields)
- Resource: `upsales/resources/files.py` (FilesResource)
- Unit tests: `tests/unit/test_files_resource.py` (13 tests, 100% pass)
- Integration tests: `tests/integration/test_files_integration.py` (4 tests, 100% pass)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_by_entity()`, `get_images()`, `get_documents()`, `get_private()`, `get_public()`, `get_by_filename()`, `get_by_extension()`
- Computed fields: `is_private`, `is_public`, `file_size_mb`, `file_size_kb`, `is_image`, `is_document`, `display_name`
- Pydantic v2 validators: BinaryFlag, NonEmptyStr, PositiveInt
- 100% docstring coverage
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 13/13 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] metadata
**Status**: COMPLETE
**Endpoint**: `/api/v2/metadata`
**Priority**: HIGH
**Files**:
- Model: `upsales/models/metadata.py` (Metadata, MetadataUser, SystemParams, FieldDefinition, Currency)
- Resource: `upsales/resources/metadata.py` (MetadataResource)
- Unit tests: `tests/unit/test_metadata_resource.py` (11 tests, 100% pass)
- Integration tests: `tests/integration/test_metadata_integration.py` (4 tests, 100% pass)

**Features**:
- Read-only endpoint (no create/update/delete)
- Single dict response (not a list)
- System configuration, user info, currency settings, and field definitions
- Custom methods: `get_currencies()`, `get_default_currency()`, `get_entity_fields()`, `get_required_fields()`, `is_field_required()`, `get_user_info()`, `get_system_version()`, `get_license_count()`
- Computed fields on Metadata: `currency_count`, `master_currency`, `active_currencies`, `has_multi_currency`, `is_enterprise`
- Computed fields on MetadataUser: `is_admin`, `is_active`, `is_team_leader`, `has_crm_access`
- Computed fields on Currency: `is_master`, `is_active`
- Computed fields on FieldDefinition: `is_required`, `is_active`
- Pydantic v2 validators: NonEmptyStr, PositiveInt
- 100% docstring coverage
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 11/11 PASS
- ✅ Integration tests: 4/4 PASS
- ✅ Model coverage: 100%
- ✅ Resource coverage: 100%

**Completed**: 2025-11-03

---

### [~] visits
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/visits`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 2000, "offset": 0},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [✓] projectPlanTypes
**Status**: COMPLETE
**Endpoint**: `/api/v2/projectPlanTypes`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/project_plan_types.py` (ProjectPlanType, PartialProjectPlanType, ProjectPlanTypeUpdateFields)
- Resource: `upsales/resources/project_plan_types.py` (ProjectPlanTypesResource)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Project plan types define templates for project workflows with stages
- Pydantic v2 validators: Field frozen=True for read-only fields
- Field descriptions for all fields
- Optimized serialization with to_api_dict()
- 100% docstring coverage

**Quality Checks**:
- ✅ Models created with proper structure
- ✅ Resource manager created
- ✅ Registered in Upsales client as project_plan_types
- ✅ Exported in __init__.py files
- ✅ 100% docstring coverage

**Completed**: 2025-11-03

---

### [✓] todoViews
**Status**: COMPLETE
**Endpoint**: `/api/v2/todoViews`
**Priority**: LOW
**Files**:
- Model: `upsales/models/todoViews.py` (TodoView)
- Resource: `upsales/resources/todoViews.py` (TodoViewsResource)
- Unit tests: `tests/unit/test_todoviews_resource.py` (18 tests, 9 passed, 9 model tests)
- Integration tests: `tests/integration/test_todoviews_integration.py` (6 tests, 100% pass)

**Features**:
- Read-only list endpoint (no CRUD operations, no ID field)
- Returns 34 predefined todo view filter configurations
- Views organized by time period groups (open, today, tomorrow, week, late, etc.)
- Views filtered by activity type (all, appointments, todos, phonecalls, leads)
- Custom methods: `get_by_name()`, `get_by_group()`, `get_by_type()`, `get_available_groups()`, `get_available_types()`
- Computed fields: `is_all_types`, `is_appointments`, `is_todos`, `is_phonecalls`, `is_today_filter`, `is_late_filter`, `is_completed_filter`, `is_leads_filter`, `display_name`
- Pydantic v2 validators: NonEmptyStr
- Field descriptions for all fields
- 100% docstring coverage
- 100% resource coverage (27/27 lines)
- 100% model coverage (49/49 lines)
- VCR cassettes recorded for integration tests

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS (N999 ignored - file matches API endpoint naming)
- ✅ Mypy type check: PASS (used builtins.list to avoid shadowing)
- ✅ Interrogate (docstrings): 100%
- ✅ Integration tests: 6/6 PASS
- ✅ Model coverage: 100%
- ✅ Resource coverage: 100%

**Completed**: 2025-11-03

---

### [✓] triggerAttributes
**Status**: COMPLETE
**Endpoint**: `/api/v2/triggerAttributes`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/trigger_attributes.py` (TriggerAttribute, TriggerAttributes)
- Resource: `upsales/resources/trigger_attributes.py` (TriggerAttributesResource)
- Unit tests: `tests/unit/test_trigger_attributes_resource.py` (15 tests, 100% pass)
- Integration tests: `tests/integration/test_trigger_attributes_integration.py` (4 tests, 100% pass)

**Features**:
- Read-only endpoint (no create/update/delete)
- Returns dict by entity type (not a list)
- Provides attribute definitions for automation triggers
- Custom methods: `get_entity_attributes()`, `get_criteria_attributes()`, `get_attribute_by_id()`, `find_attributes_by_type()`, `get_select_attributes()`, `get_attributes_by_feature()`, `get_entity_types()`
- Computed fields: `can_be_criteria`, `is_select_type`, `has_range`, `requires_feature`, `entity_type`, `field_name`
- Computed fields on TriggerAttributes: `entity_types`, `total_attributes`
- Pydantic v2 validators: NonEmptyStr
- 100% docstring coverage
- Model coverage: 100% (both TriggerAttribute and TriggerAttributes)
- Resource coverage: 100%

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Unit tests: 15/15 PASS
- ✅ Integration tests: 4/4 PASS

**Completed**: 2025-11-03

---

### [✓] mail/templates
**Status**: COMPLETE
**Endpoint**: `/api/v2/mail/templates`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/mail_templates.py` (MailTemplate, PartialMailTemplate, MailTemplateUpdateFields)
- Resource: `upsales/resources/mail_templates.py` (MailTemplatesResource)

**Features**:
- Full CRUD operations (create, get, list, update, delete)
- Custom methods: `get_by_name()`, `get_active()`, `get_inactive()`, `get_private()`, `get_public()`, `get_editable()`, `get_removable()`, `get_with_attachments()`
- Computed fields: `is_active`, `is_private`, `is_editable`, `is_removable`, `has_attachments`, `attachment_count`
- Pydantic v2 validators: BinaryFlag, NonEmptyStr
- Field descriptions for all fields
- Optimized serialization with to_api_dict()
- Integration with PartialUser for nested user data
- Field aliases for API compatibility (from, fromName, bodyJson, etc.)
- 100% docstring coverage

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Models created with proper structure
- ✅ Resource manager with custom methods
- ✅ Registered in Upsales client as mail_templates
- ✅ Exported in __init__.py files
- ✅ Integration tested with real API

**Completed**: 2025-11-03

---

### [~] opportunityAI
**Status**: ENDPOINT DOES NOT EXIST
**Endpoint**: `/api/v2/opportunityAI`
**Priority**: SKIPPED

**Reason**: Endpoint does not exist in the Upsales API. Tested multiple case variations:
- `/api/v2/opportunityAI` - 404 Not Found
- `/api/v2/opportunityai` - 404 Not Found
- `/api/v2/opportunity-ai` - 404 Not Found
- `/api/v2/opportunity_ai` - 404 Not Found
- `/api/v2/opportunityAi` - 404 Not Found

**Checked**: 2025-11-03

---

### [~] salesCoaches
**Status**: ENDPOINT DOES NOT EXIST
**Endpoint**: `/api/v2/salesCoaches`
**Priority**: SKIPPED

**Reason**: Endpoint does not exist in the Upsales API. Tested multiple case variations:
- `/api/v2/salesCoaches` - 404 Not Found
- `/api/v2/salescoaches` - 404 Not Found
- `/api/v2/sales-coaches` - 404 Not Found
- `/api/v2/sales_coaches` - 404 Not Found
- `/api/v2/salesCoach` - 404 Not Found
- `/api/v2/salescoach` - 404 Not Found

**Checked**: 2025-11-03

---

### [~] standardIntegration
**Status**: ENDPOINT DOES NOT EXIST
**Endpoint**: `/api/v2/standardIntegration`
**Priority**: SKIPPED

**Reason**: Endpoint does not exist in the Upsales API. Tested multiple case variations:
- `/api/v2/standardIntegration` - 404 Not Found
- `/api/v2/standardintegration` - 404 Not Found
- `/api/v2/standard-integration` - 404 Not Found
- `/api/v2/standard_integration` - 404 Not Found
- `/api/v2/standardIntegrations` - 404 Not Found

**Checked**: 2025-11-03

---

### [✓] self
**Status**: COMPLETE
**Endpoint**: `/api/v2/self`
**Priority**: HIGH
**Files**:
- Model: `upsales/models/self.py` (Self, SelfClient, ClientDetail, VersionData, AccountManager)
- Resource: `upsales/resources/self.py` (SelfResource)

**Features**:
- Read-only endpoint (no CRUD operations)
- Single dict response (not a list)
- Current user session information, client details, version data, features, and addons
- Custom methods: `get_user_id()`, `get_client_info()`, `get_version_info()`, `check_feature()`, `check_addon()`, `get_account_manager()`
- Computed fields on Self: `has_crm`, `has_marketing_automation`, `client_count`, `feature_count`, `addon_count`
- Computed fields on ClientDetail: `is_trial`, `is_active`, `has_contact_limit`
- Computed fields on VersionData: `has_crm`, `has_marketing_automation`, `feature_count`, `addon_count`
- Computed fields on AccountManager: `has_cell_phone`
- Methods: `has_feature()`, `has_addon()`, `has_unreleased_feature()`
- Pydantic v2 validators: NonEmptyStr, PositiveInt
- Field descriptions for all fields
- 100% docstring coverage

**Quality Checks**:
- ✅ Ruff format: PASS
- ✅ Ruff lint: PASS
- ✅ Mypy type check: PASS
- ✅ Interrogate (docstrings): 100%
- ✅ Models created with proper structure
- ✅ Resource manager with custom methods
- ✅ Registered in Upsales client as self
- ✅ Exported in __init__.py files
- ✅ Integration tested with real API

**Completed**: 2025-11-03

---

### [→] mail
**Status**: REQUIRES MORE TIME
**Endpoint**: `/api/v2/mail`
**Priority**: MEDIUM
**Estimated Time**: 90-120 minutes

**Reason**: Complex endpoint with many nested objects requiring proper modeling:
- Nested models needed: PartialContact, PartialCompany, PartialUser, PartialTemplate, PartialProject, PartialAppointment, PartialActivity, PartialOpportunity
- Complex structures: recipients (to/cc/bcc with type), tags (key-value pairs), events (type-based), attachments
- Multiple relationship types (contact, client, users list, project, appointment, activity, opportunity)
- HTML body field (very long strings)
- Thread management fields

**API Response Structure**:
```json
{
  "id": 1,
  "subject": "string",
  "body": "long HTML string",
  "to": "email",
  "cc": [],
  "bcc": [],
  "date": "ISO datetime",
  "from": "email",
  "recipients": {"to": [], "cc": [], "bcc": []},
  "fromName": "string",
  "modDate": "ISO datetime",
  "template": {"name": "string", "id": 1},
  "contact": {"journeyStep": "string", "name": "string", "active": bool, "id": 1},
  "client": {"operationalAccount": null, "journeyStep": "string", "name": "string", "id": 1},
  "users": [{"name": "string", "id": 1, "role": {...}, "email": "string"}],
  "type": "out|in",
  "tags": [{"tag": "string", "value": "string"}],
  "attachments": [],
  "events": [{"id": 1, "value": "string", "type": "send|open|click", "date": "ISO"}],
  "thread": {"id": 1},
  "appointment": null,
  "activity": null,
  "opportunity": null
}
```

**Checked**: 2025-11-03

---

### [→] alliwant
**Status**: REQUIRES SIGNIFICANT TIME
**Endpoint**: `/api/v2/alliwant`
**Priority**: LOW (configuration data)
**Estimated Time**: 180-240 minutes

**Reason**: Extremely complex endpoint containing system configuration with 36+ top-level keys, each requiring proper nested model definitions:

**Top-level keys** (36 total):
- `acceptTerms` (dict): Terms acceptance configuration
- `accessRights` (dict): Entity-level access rights
- `activityTypes` (list): Activity type definitions with roles
- `appointmentTypes` (list): Appointment type definitions with roles
- `brands` (list): Brand configurations
- `clientCategories` (list): Client category definitions with roles
- `clientCategoryTypes` (list): Client category type definitions
- `contactCategories` (list): Contact category definitions
- `contactCategoryTypes` (list): Contact category type definitions
- `customFields` (dict): Custom field definitions by entity type
- `customerSelf` (dict): Current user extended information
- `customerSupportForwardEmail` (str): Support email
- `documentTemplates` (list): Document template definitions
- `hasFullReportAccess` (bool): Report access flag
- `hasSharedViews` (bool): Shared views flag
- `listViews` (dict): List view configurations by entity
- `metadata` (dict): System metadata (similar to /metadata endpoint)
- `orderStages` (list): Order stage definitions with roles
- `paymentExtensions` (list): Payment extension configurations
- `priceLists` (list): Price list definitions
- `productCategories` (list): Product category definitions
- `projectPlanPriorities` (list): Project plan priority definitions
- `projectPlanStages` (list): Project plan stage definitions
- `projectPlanStatuses` (list): Project plan status definitions
- `projectPlanTypes` (list): Project plan type definitions
- `prospectingTokenCost` (dict): Prospecting token pricing
- `reportViews` (list): Report view configurations
- `roleMap` (dict): Role ID to role object mapping
- `self` (dict): Current user information (similar to /self endpoint)
- `ticketStatuses` (list): Ticket status definitions
- `ticketTypes` (list): Ticket type definitions
- `todoTypes` (list): Todo type definitions
- `totals` (dict): System totals and counts
- `userDefinedCategories` (list): User-defined category definitions
- `userDefinedCategoryTypes` (list): User-defined category type definitions
- `userMap` (dict): User ID to user object mapping

**Complexity**: Each top-level key requires its own model(s) with proper validation, computed fields, and docstrings. Many are lists of complex objects with nested relationships.

**Recommendation**: Implement this endpoint last, after all individual entity endpoints are complete, as it aggregates configuration data from multiple other endpoints.

**Checked**: 2025-11-03

---

### [~] clientIps
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/clientIps`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "data": []
}
```

**Checked**: 2025-11-03

---

### [🔶] ProjectPlanStatus
**Status**: IMPLEMENTED, NEEDS VERIFICATION
**Endpoint**: `/api/v2/ProjectPlanStatus`
**Priority**: MEDIUM

**Notes**:
- Resource and models added: `ProjectPlanStatusesResource`, `ProjectPlanStatus`, `PartialProjectPlanStatus`.
- VCR cassette recorded for list operation (may be empty on some tenants).
- Additional CRUD operations not verified yet.

**Integration Test**:
- `tests/integration/test_projectplanstatus_integration.py::test_list_statuses`
- Cassette: `tests/cassettes/integration/projectplanstatus/test_list_statuses.yaml`

**Checked**: 2025-11-08

---

### [~] projectPlanTemplates
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/projectPlanTemplates`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Checked**: 2025-11-03

---

### [~] userDefinedObjects/1
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/userDefinedObjects/1`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Note**: User-defined object endpoint #1 (UDO1). Custom entity type that can be configured by Upsales admins but is not configured in this instance.

**Checked**: 2025-11-03

---

### [~] userDefinedObjects/2
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/userDefinedObjects/2`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Note**: User-defined object endpoint #2 (UDO2). Custom entity type that can be configured by Upsales admins but is not configured in this instance.

**Checked**: 2025-11-03

---

### [~] userDefinedObjects/3
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/userDefinedObjects/3`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Note**: User-defined object endpoint #3 (UDO3). Custom entity type that can be configured by Upsales admins but is not configured in this instance.

**Checked**: 2025-11-03

---

### [~] userDefinedObjects/4
**Status**: NO DATA AVAILABLE
**Endpoint**: `/api/v2/userDefinedObjects/4`
**Priority**: SKIPPED

**Reason**: Endpoint accessible but returns empty data array:
```json
{
  "error": null,
  "metadata": {"total": 0, "limit": 1, "offset": 0},
  "data": []
}
```

**Note**: User-defined object endpoint #4 (UDO4). Custom entity type that can be configured by Upsales admins but is not configured in this instance.

**Checked**: 2025-11-03

---

### [✓] function/whatismyip
**Status**: COMPLETE
**Endpoint**: `/api/v2/function/whatismyip`
**Priority**: LOW (utility)
**Files**:
- Resource: `upsales/resources/functions.py` (FunctionsResource)
- No model needed (returns simple string)

**Features**:
- Single utility method: `whatismyip()` returns client IP address
- Simple string response (e.g., "83.249.76.75")
- Useful for debugging, logging, or IP-based access control
- 100% docstring coverage

**Quality Checks**:
- ✅ Resource created with utility pattern
- ✅ Registered in Upsales client as functions
- ✅ Exported in __init__.py files
- ✅ 100% docstring coverage
- ✅ Integration tested with real API

**Completed**: 2025-11-03

---

### [✓] search/activitylist
**Status**: COMPLETE
**Endpoint**: `/api/v2/search/activitylist`
**Priority**: MEDIUM
**Files**:
- Model: `upsales/models/activity_list_item.py` (ActivityListItem)
- Resource: `upsales/resources/activity_list.py` (ActivityListResource)

**Features**:
- Read-only search endpoint (no create/update/delete)
- Returns heterogeneous list of activities (tasks, appointments, emails)
- Custom methods: `list()`, `list_all()`, `search()`, `get_emails()`, `get_appointments()`, `get_tasks()`
- Computed fields: `is_email`, `is_appointment`, `is_task`
- Supports pagination with limit/offset
- Flexible model accommodates varying field sets per activity type
- Field descriptions for all fields
- 100% docstring coverage

**Quality Checks**:
- ✅ Model created with flexible schema (extra="allow")
- ✅ Resource manager with custom filter methods
- ✅ Registered in Upsales client as activity_list
- ✅ Exported in __init__.py files
- ✅ 100% docstring coverage
- ✅ Integration tested with real API

**Completed**: 2025-11-03

---

## 🛠️ Implementation Checklist Template

For each endpoint from api_endpoints_with_fields.json:

### Pre-Implementation
- [ ] Read endpoint section from api_endpoints_with_fields.json
- [ ] Note required fields for POST
- [ ] Note allowed fields for PUT
- [ ] Note read-only fields
- [ ] Note nested object structures
- [ ] Check for special patterns (arrays, dates, nested IDs)

### Implementation
- [ ] Generate model: `uv run upsales generate-model {endpoint} --partial`
- [ ] Record VCR cassette (Step 2)
- [ ] Analyze cassette vs API file (Step 3)
- [ ] Create {Model}CreateFields TypedDict (if POST supported)
- [ ] Create {Model}UpdateFields TypedDict (if PUT supported)
- [ ] Mark frozen fields (from PUT.readOnly)
- [ ] Add validators from upsales/validators.py
- [ ] Add computed fields
- [ ] Create {Model}Resource extending BaseResource
- [ ] Add custom methods as needed
- [ ] Register in client.py
- [ ] Update model exports

### Testing
- [ ] Unit tests with 100% resource coverage
- [ ] Integration test for GET
- [ ] Integration test for CREATE with minimal fields
- [ ] Integration test for CREATE with optional fields
- [ ] Integration test for UPDATE
- [ ] Integration test for DELETE
- [ ] Test computed fields with VCR data

### Verification
- [ ] Compare API file fields vs VCR cassette fields
- [ ] Document discrepancies found
- [ ] Verify nested required fields pattern
- [ ] Test all custom methods
- [ ] Quality checks pass (ruff, mypy, interrogate)

### Documentation
- [ ] Update docs/endpoint-map.md with verification status
- [ ] Update ENDPOINT_TASK_LIST.md progress
- [ ] Note any pattern discoveries
- [ ] Document field requirement discrepancies

---

## 🔍 Validation Workflow

When implementing any endpoint, follow this workflow:

```
API File → Model Generation → VCR Recording → Compare → Adjust → Verify
   ↓              ↓                ↓            ↓         ↓        ↓
Starting      Initial         Real API    Find Gaps   Fix Model  Test
 Point        Model          Structure                           CREATE
```

**Step-by-step**:
1. Consult API file for expected structure
2. Generate model based on fields
3. Test with VCR to verify
4. Document discrepancies
5. Update endpoint-map.md

---

## 🎯 Recommended Next Steps

### This Week (2025-11-07 to 2025-11-14)

1. **✅ Verify contacts CREATE** ✅ **COMPLETED 2025-11-07** (45 min)
   - ✅ Consulted api_endpoints_with_fields.json
   - ✅ Tested with minimal fields: `{client: {id}}`
   - ✅ Documented in ContactCreateFields
   - ✅ Found discrepancy: Email is OPTIONAL

2. **Verify activities CREATE** (60 min)
   - Required: date, userId, activityTypeId, client.id
   - Test nested required fields
   - Document in ActivityCreateFields

3. **Verify appointments CREATE** (60 min)
   - Likely uses nested required fields pattern
   - Document in AppointmentCreateFields

4. **Verify accounts CREATE** (45 min)
   - Only requires name (simple!)
   - Test nested arrays (users, addresses)
   - Document in CompanyCreateFields

5. **Implement opportunities** (30 min)
   - Reuse Order model
   - Create OpportunitiesResource
   - Add probability validation

**Total Week 1**: ~4 hours (contacts complete, 4 remaining)

### Next Week (2025-11-15 to 2025-11-21)

6. **Implement agreements** (60 min)
7. **Verify UPDATE operations** (2 hours)
8. **Implement tickets** (60 min)
9. **Implement events** (45 min)

**Total Week 2**: ~5 hours

### Success Metrics

**By End of Week 1** (Updated 2025-11-07):
- ✅ 2 endpoints with verified CREATE (orders, contacts) - **contacts DONE!**
- Remaining: 3 endpoints to verify (activities, appointments, accounts)
- 1 new endpoint (opportunities)
- Coverage: 22%

**By End of Week 2**:
- 3 more endpoints (agreements, tickets, events)
- 5 endpoints with verified UPDATE
- Coverage: 24%

**By End of Month**:
- All high-priority endpoints implemented
- All medium-priority config endpoints implemented
- Coverage: 30%

---

## 🌟 Success Stories

### Orders Endpoint
**Before api_endpoints_with_fields.json**: Manual testing to discover fields
**With api_endpoints_with_fields.json**: API file correctly predicted all 5 required fields
**Result**: ✅ Saved ~30 minutes of trial-and-error testing
**Lesson**: File is accurate for core endpoints like orders

### Contacts Endpoint
**Challenge**: API file incorrectly listed email as required
**Discovery**: Only client.id is required (through testing)
**Result**: ✅ Documented discrepancy, simplest CREATE pattern found
**Lesson**: Always verify with actual API testing, don't trust file 100%

### Validation Approach
**Best Practice Established**:
1. Consult API file for expected structure
2. Generate model based on fields
3. Test with VCR to verify
4. Document discrepancies
5. Update endpoint-map.md

---

## Implementation Notes

Quick reference for adding endpoints:
1. Check api_endpoints_with_fields.json first
2. Generate model: `uv run upsales generate-model {endpoint} --partial`
3. Record VCR cassette: `uv run pytest tests/integration/test_{endpoint}_integration.py -v`
4. Use Implementation Checklist Template (above)
5. Update this file with completion status
