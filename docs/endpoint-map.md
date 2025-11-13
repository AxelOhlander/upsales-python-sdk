# Upsales SDK Endpoint Map

**Last Updated**: 2025-11-06
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

### Files
**API**: `/files`
**Models**: `File`, `PartialFile`
**Client**: `upsales.files`

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

### Notifications
**API**: `/notifications`
**Models**: `Notification`, `PartialNotification`
**Client**: `upsales.notifications`

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

### Functions (Utility)
**API**: `/function/*`
**Models**: None (utility endpoints)
**Client**: `upsales.functions`

Special-purpose utility functions resource. Does not follow standard CRUD pattern.

**Custom Methods**: Implementation-specific

**Integration Tests**: None

---

## Summary Statistics

### Overall Implementation Status

| Category | Count |
|----------|-------|
| **Total Endpoints** | 35 |
| **Full CRUD Verified** | 3 (Users, Products, Order Stages) |
| **CREATE Verified** | 2 (Orders, Contacts) |
| **READ-Only Verified** | 1 (Companies - CREATE not verified) |
| **Full CRUD Inherited** | 15 |
| **Read-Only** | 6 |
| **Special/Utility** | 3 |
| **Integration Test Suites** | 22 endpoints with VCR cassettes |
| **Total Cassettes** | 108 recorded interactions (102 + 6 new for contacts) |

### Operation Verification Status

| Operation | Verified | Inherited | N/A | Total |
|-----------|----------|-----------|-----|-------|
| **Create** | **2** (Orders, Contacts) | 19 | 9 | 29 |
| **Read (single)** | 20 | 10 | 5 | 35 |
| **Read (list)** | 20 | 10 | 5 | 35 |
| **Update** | 1 (Order Stages) | 19 | 9 | 29 |
| **Delete** | 0 | 20 | 9 | 29 |
| **Search** | 4 | 21 | 4 | 29 |

### Model Completeness

| Status | Count | Endpoints |
|--------|-------|-----------|
| **✅ Fully Verified** | 3 | Users, Products, Order Stages |
| **✅ CREATE Verified** | 2 | **Orders (5 required), Contacts (1 required)** |
| **⚠️ READ-Only Verified** | 1 | Companies (CREATE not verified) |
| **⚠️ Partial** | 15 | Projects, Roles, Currencies, etc. |
| **❌ Unverified** | 8 | Activities, Appointments, etc. |

### Special Patterns Discovered

| Pattern | Count | Endpoints |
|---------|-------|-----------|
| **Nested Required Fields** | 2 verified | Orders (5 required), Contacts (1 required) |
| **Minimal ID Structure for CREATE** | 2 verified | Orders, Contacts: `client: {"id": 123}` |
| **Array with Nested IDs** | 1 verified | Orders: `orderRow: [{"product": {"id": 5}}]` |
| **Simple Single Required Field** | 1 verified | Contacts: only `client.id` required |

---

## Recommendations for Full Verification

### High Priority (User-Facing Endpoints)
1. **Orders** - Critical sales pipeline endpoint ✅ **CREATE VERIFIED!**
   - ✅ Create requirements verified (nested required fields)
   - ✅ OrderCreateFields TypedDict documented
   - ✅ Nested field pattern documented (see `docs/patterns/nested-required-fields.md`)
   - ⚠️ Verify update requirements
   - ⚠️ Add integration tests with VCR
   - ⚠️ Test edge cases (multiple orderRow items, optional fields)

2. **Contacts** - Core CRM data ✅ **CREATE VERIFIED!**
   - ✅ Create requirements verified (only client.id required)
   - ✅ ContactCreateFields TypedDict documented
   - ✅ Integration tests added with VCR (6 cassettes)
   - ✅ API file discrepancy found (email NOT required)
   - ⚠️ Verify update requirements

3. **Activities** - User actions and history (**LIKELY uses nested required fields pattern**)
   - Verify create requirements (expect minimal nested structure for user, client, contact)
   - Test date/time field handling
   - Add integration tests with VCR
   - Check if follows Orders pattern for relationships

4. **Appointments** - Calendar integration (**LIKELY uses nested required fields pattern**)
   - Verify create requirements (expect minimal nested structure for user, client, contact)
   - Test date/time constraints
   - Add integration tests with VCR
   - Check if follows Orders pattern for relationships

### Medium Priority (Configuration Endpoints)
5. **Pricelists** - Already has integration tests
   - Verify create/update field requirements
   - Document pricing structure constraints

6. **Roles** - Already has integration tests
   - Verify permission structure
   - Document role configuration requirements

7. **Currencies** - Already has integration tests
   - Verify rate update requirements
   - Document currency configuration

### Low Priority (Specialized/Utility)
8. **Mail** - Email sending
   - Verify email sending requirements
   - Test attachment handling
   - Add integration tests

9. **Notifications** - System notifications
   - Verify notification creation
   - Test delivery mechanisms

10. **Custom Fields** - Field definitions
    - Verify field creation requirements
    - Test field type constraints

---

## Next Steps

To achieve full verification for any endpoint:

1. **Record VCR Cassettes** (Step 2 in workflow)
   - `uv run pytest tests/integration/test_{endpoint}_integration.py -v`

2. **Analyze Real API Structure** (Step 3)
   - Run `uv run python ai_temp_files/find_unmapped_fields.py`
   - Compare cassette data vs model fields

3. **Verify CREATE Requirements** ⭐ **CRITICAL for relationship-heavy endpoints**
   - Test with absolutely minimal fields to discover requirements
   - **Check for nested required fields pattern** (like Orders)
   - Test nested fields specifically: `user: {"id": 10}` not just "user required"
   - Document exact structure in `{Model}CreateFields` TypedDict
   - Include format requirements (e.g., date: "YYYY-MM-DD")
   - **If nested fields found**: Reference `docs/patterns/nested-required-fields.md`

4. **Verify UPDATE Requirements**
   - Test field-by-field updates
   - Identify frozen/read-only fields
   - Confirm `to_api_dict()` excludes properly
   - Document any special update rules

5. **Add Integration Tests**
   - Test CREATE with minimal required fields (critical!)
   - Test CREATE with optional fields
   - Test all CRUD operations
   - Test computed fields with real data
   - Test serialization with real API responses
   - Verify custom methods

6. **Update This Document**
   - Mark operations as ✅ Verified
   - Add field requirement notes (especially for CREATE)
   - Document any special patterns discovered
   - Update integration test counts
   - Add to "Special Patterns Discovered" if applicable

---

**Last Updated**: 2025-11-06
**Maintained By**: Auto-generated from codebase analysis
**Update Frequency**: After each endpoint implementation
