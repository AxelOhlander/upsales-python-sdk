# Upsales SDK - API Implementation Roadmap

**Generated**: 2025-11-07
**Source**: api_endpoints_with_fields.json (167 endpoints)
**Current Coverage**: 35 resources (21%)
**Remaining**: 132 endpoints (79%)

---

## 📊 Executive Summary

### Current Status
- ✅ **Implemented**: 35 resources (21% of API coverage)
- ✅ **Verified CREATE**: 1 endpoint (Orders with nested required fields)
- 🔶 **Inherited CREATE**: 15 endpoints (field requirements need verification)
- ❌ **Not Implemented**: 132 endpoints

### Coverage by Category
- **Core Business Operations**: 8/12 (67%) - Good foundation
- **Configuration & Reference**: 15/26 (58%) - Solid coverage
- **Specialized/Admin**: 12/129 (9%) - Low priority

---

## 🎯 Implementation Priorities

### Phase 1: Verify Existing CREATE Operations (IMMEDIATE)

**15 endpoints with inherited CREATE that need verification:**

| Endpoint | SDK Resource | Priority | Notes |
|----------|-------------|----------|-------|
| accounts | companies | 🔴 High | Verify nested structure (users, addresses) |
| contacts | contacts | 🔴 High | Verify required: email, client.id |
| activities | activities | 🔴 High | Verify nested: userId, activityTypeId, client.id |
| appointments | appointments | 🔴 High | Likely uses nested required fields |
| products | products | 🟡 Medium | Simple structure, low risk |
| users | users | 🟢 Low | No CREATE in production (admin only) |
| currencies | currencies | 🟢 Low | Configuration, rare creation |
| forms | forms | 🟢 Low | Configuration endpoint |
| mail | mail | 🟡 Medium | Email sending, special handling |
| mailTemplates | mail_templates | 🟢 Low | Template management |
| orderStages | order_stages | 🟢 Low | Configuration, rarely created |
| pricelists | pricelists | 🟢 Low | Configuration endpoint |
| projects | projects | 🟡 Medium | May have complex requirements |
| roles | roles | 🟢 Low | Admin configuration |
| triggers | triggers | 🟢 Low | Automation configuration |

**Action Items**:
1. For each 🔴 High priority:
   - Consult `api_endpoints_with_fields.json` for required fields
   - Test CREATE with minimal fields
   - Create `{Model}CreateFields` TypedDict
   - Record VCR cassette
   - Update `docs/endpoint-map.md` with ✅ Verified status

2. For 🟡 Medium priority:
   - Review API file for requirements
   - Test when needed by users
   - Document findings

3. For 🟢 Low priority:
   - Document as "admin-only" or "rare use"
   - Implement on-demand

---

### Phase 2: Implement High-Priority Missing Endpoints (HIGH PRIORITY)

**4 critical endpoints not yet implemented:**

#### 1. **opportunities** 🔴 CRITICAL
**API Path**: `/api/v2/opportunities`
**Description**: Pipeline deals with probability 1-99 (same model as orders)
**Status**: ❌ Not Implemented

**Details from API File**:
- Same model as Orders (shares all fields)
- Difference: Stage probability must be 1-99 (not 0 or 100)
- Required fields: Same as Orders
- Can reuse Order model with probability validation

**Implementation Plan**:
- ✅ Model exists (Order) - just add probability range validation
- ❌ Need OpportunitiesResource extending OrdersResource
- ❌ Register in client as `upsales.opportunities`
- ⏱️ Estimated time: 30 minutes (model reuse)

**Priority**: 🔴 **CRITICAL** - Core sales pipeline

---

#### 2. **agreements** 🔴 HIGH
**API Path**: `/api/v2/agreements`
**Description**: Recurring revenue agreements
**Status**: ❌ Not Implemented

**Details from API File**:
```json
{
  "required": [
    {"field": "client", "type": "object", "structure": {"id": "number"}},
    {"field": "user", "type": "object", "structure": {"id": "number"}},
    {"field": "name", "type": "string", "maxLength": 100},
    {"field": "startDate", "type": "string", "format": "YYYY-MM-DD"},
    {"field": "endDate", "type": "string", "format": "YYYY-MM-DD"},
    {"field": "value", "type": "number"},
    {"field": "interval", "type": "number", "notes": "1=monthly, 12=yearly"},
    {"field": "agreementRow", "type": "array", "structure": [{"product": {"id": "number"}}]},
    {"field": "currency", "type": "string"}
  ],
  "optional": [
    {"field": "description", "type": "string"},
    {"field": "contact", "type": "object", "structure": {"id": "number"}},
    {"field": "custom", "type": "array"},
    {"field": "stakeholders", "type": "array"}
  ]
}
```

**Implementation Plan**:
- ❌ Need Agreement model with 9 required fields
- ❌ Uses nested required fields pattern (like Orders)
- ❌ Need AgreementsResource
- ❌ Register in client as `upsales.agreements`
- ⏱️ Estimated time: 60 minutes (new model)

**Priority**: 🔴 **HIGH** - Recurring revenue tracking

---

#### 3. **tickets** 🟡 MEDIUM
**API Path**: `/api/v2/tickets`
**Description**: Support ticket system
**Status**: ❌ Not Implemented

**Details from API File**:
```json
{
  "required": [
    {"field": "client", "type": "object", "structure": {"id": "number"}},
    {"field": "subject", "type": "string", "maxLength": 255},
    {"field": "description", "type": "text"},
    {"field": "status", "type": "object", "structure": {"id": "number"}},
    {"field": "type", "type": "object", "structure": {"id": "number"}}
  ],
  "optional": [
    {"field": "contact", "type": "object", "structure": {"id": "number"}},
    {"field": "user", "type": "object", "structure": {"id": "number"}},
    {"field": "priority", "type": "number", "default": 3},
    {"field": "custom", "type": "array"}
  ]
}
```

**Implementation Plan**:
- ❌ Need Ticket model with 5 required fields
- ❌ Uses nested required fields pattern
- ❌ Need TicketsResource
- ⏱️ Estimated time: 60 minutes

**Priority**: 🟡 **MEDIUM** - Support system

---

#### 4. **events** 🟡 MEDIUM
**API Path**: `/api/v2/events`
**Description**: Activity timeline events
**Status**: ❌ Not Implemented

**Details from API File**:
```json
{
  "required": [
    {"field": "client", "type": "object", "structure": {"id": "number"}},
    {"field": "date", "type": "string", "format": "YYYY-MM-DD"},
    {"field": "description", "type": "string"}
  ],
  "optional": [
    {"field": "user", "type": "object", "structure": {"id": "number"}},
    {"field": "contact", "type": "object", "structure": {"id": "number"}},
    {"field": "custom", "type": "array"}
  ]
}
```

**Implementation Plan**:
- ❌ Need Event model with 3 required fields
- ❌ Simpler than orders (fewer requirements)
- ❌ Need EventsResource
- ⏱️ Estimated time: 45 minutes

**Priority**: 🟡 **MEDIUM** - Timeline tracking

---

### Phase 3: Implement Medium-Priority Configuration Endpoints

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

**Total Estimated Time**: ~7-9 hours (11 endpoints × 40-50 min avg)

---

### Phase 4: Low-Priority Specialized Endpoints

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

## 📋 Detailed Task Breakdown

### Immediate Actions (Next 2-3 Days)

**Priority: 🔴 CRITICAL**

#### Task 1: Verify CREATE for contacts
- [ ] Read `api_endpoints_with_fields.json` for contacts.POST requirements
- [ ] Test CREATE with minimal fields: `{email, client: {id}}`
- [ ] Create `ContactCreateFields` TypedDict
- [ ] Verify nested structure for client.id
- [ ] Record VCR cassette for creation test
- [ ] Update endpoint-map.md with ✅ Verified
- [ ] Document any discrepancies found
- ⏱️ **Estimated**: 45 minutes

#### Task 2: Verify CREATE for activities
- [ ] Read `api_endpoints_with_fields.json` for activities.POST requirements
- [ ] Required fields from API file: date, userId, activityTypeId, client.id
- [ ] Test CREATE with minimal fields
- [ ] Create `ActivityCreateFields` TypedDict
- [ ] Verify nested required fields pattern
- [ ] Record VCR cassette
- [ ] Update endpoint-map.md with ✅ Verified
- ⏱️ **Estimated**: 60 minutes

#### Task 3: Verify CREATE for appointments
- [ ] Read `api_endpoints_with_fields.json` for appointments.POST requirements
- [ ] Test CREATE with minimal fields
- [ ] Create `AppointmentCreateFields` TypedDict
- [ ] Verify nested required fields pattern
- [ ] Record VCR cassette
- [ ] Update endpoint-map.md with ✅ Verified
- ⏱️ **Estimated**: 60 minutes

#### Task 4: Verify CREATE for accounts (companies)
- [ ] Read `api_endpoints_with_fields.json` for accounts.POST requirements
- [ ] Required from API file: name (only one!)
- [ ] Test CREATE with minimal field: `{name: "Test Company"}`
- [ ] Test nested arrays (users, addresses, categories)
- [ ] Create `CompanyCreateFields` TypedDict
- [ ] Record VCR cassette
- [ ] Update endpoint-map.md with ✅ Verified
- ⏱️ **Estimated**: 45 minutes

**Total Phase 1**: ~3.5 hours

---

### Short-Term Actions (Next 1-2 Weeks)

**Priority: 🔴 HIGH**

#### Task 5: Implement opportunities endpoint
- [ ] Review api_endpoints_with_fields.json for opportunities
- [ ] Note: Shares Order model, different probability range (1-99)
- [ ] Add probability range validation to Order model
- [ ] Create OpportunitiesResource extending OrdersResource
- [ ] Override create() to enforce probability 1-99 validation
- [ ] Add to client.py as `upsales.opportunities`
- [ ] Add integration tests with VCR
- [ ] Update endpoint-map.md
- ⏱️ **Estimated**: 30 minutes (reuses Order model)

#### Task 6: Implement agreements endpoint
- [ ] Read api_endpoints_with_fields.json for agreements structure
- [ ] Generate Agreement model (9 required fields)
- [ ] Verify nested required fields: client.id, user.id, agreementRow with product.id
- [ ] Create AgreementCreateFields TypedDict
- [ ] Create AgreementsResource with BaseResource
- [ ] Add custom methods (get_active, get_by_client, get_recurring)
- [ ] Record VCR cassettes
- [ ] Add integration tests
- [ ] Register in client.py
- [ ] Update endpoint-map.md
- ⏱️ **Estimated**: 60 minutes (similar to Orders)

#### Task 7: Verify UPDATE operations for high-priority endpoints
- [ ] Orders - verify PUT.allowed fields
- [ ] Contacts - verify PUT.allowed fields
- [ ] Activities - verify PUT.allowed fields
- [ ] Accounts - verify PUT.allowed fields
- [ ] Create test cases for field-by-field updates
- [ ] Record VCR cassettes
- [ ] Update endpoint-map.md with UPDATE verified
- ⏱️ **Estimated**: 2 hours (across 4 endpoints)

**Total Short-Term**: ~4 hours

---

### Medium-Term Actions (Next Month)

**Priority: 🟡 MEDIUM**

#### Task 8: Implement tickets endpoint
- [ ] Generate Ticket model (5 required fields)
- [ ] Verify nested required fields pattern
- [ ] Create TicketsResource
- [ ] Add custom methods (get_by_status, get_by_type, get_open)
- [ ] Record VCR cassettes
- [ ] Integration tests
- ⏱️ **Estimated**: 60 minutes

#### Task 9: Implement events endpoint
- [ ] Generate Event model (3 required fields)
- [ ] Create EventsResource
- [ ] Add timeline methods
- [ ] Integration tests
- ⏱️ **Estimated**: 45 minutes

#### Task 10: Implement custom fields entity-specific endpoints
Implement 7 entity-specific customfields endpoints:
- [ ] customfields_accounts
- [ ] customfields_contacts
- [ ] customfields_activities
- [ ] customfields_appointments
- [ ] customfields_orders
- [ ] customfields_orderrows
- [ ] customfields_products

**Note**: May extend existing CustomFieldsResource or create entity-specific resources
- ⏱️ **Estimated**: 3-4 hours (shared pattern)

#### Task 11: Implement advertising endpoints
- [ ] adAccounts - Ad account configuration
- [ ] adCampaigns - Campaign management
- ⏱️ **Estimated**: 2 hours (both together)

#### Task 12: Implement quota endpoint
- [ ] Generate Quota model
- [ ] Create QuotasResource
- [ ] Handle quarterly vs monthly data
- ⏱️ **Estimated**: 60 minutes

#### Task 13: Implement reporting endpoint
- [ ] Research dynamic reporting API structure
- [ ] Create ReportResource
- [ ] May be complex (Elasticsearch-based)
- ⏱️ **Estimated**: 2-3 hours

**Total Medium-Term**: ~10-12 hours

---

### Long-Term Actions (Future)

**Priority: 🟢 LOW**

**129 specialized endpoints** organized by category:

#### Admin & Provisioning (15 endpoints)
- provisioning, userInvites, roleSettings, onboardingImports, etc.
- **Strategy**: Implement on-demand for admin features

#### Email Management (12 endpoints)
- mailDomains, mailEditor, emailSuggestion, emailDuplicates, mailTest, etc.
- **Strategy**: Extend as email features needed

#### Integration Tools (18 endpoints)
- standardIntegration*, soliditet*, doceboSSO, etc.
- **Strategy**: Per-integration basis

#### Search & Utilities (8 endpoints)
- quickSearch, emailSuggest, placeholder, whatIsMyIp, workerStatus
- **Strategy**: Utility methods in client

#### User-Defined Objects (7 endpoints)
- userDefinedObject1-4, categories, types, definitions
- **Strategy**: Generic implementation

#### Specialized Features (69 endpoints)
- Activity quotas, ad creatives, banner groups, reports, widgets, etc.
- **Strategy**: On-demand implementation

**Total Long-Term**: ~60-80 hours (but implement incrementally as needed)

---

## 📈 Coverage Roadmap

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
1. Verify CREATE for 4 high-priority implemented endpoints (contacts, activities, appointments, accounts)
2. Implement opportunities (30 min)
3. Implement agreements (60 min)
4. **Result**: All core business operations fully verified

**This Quarter**:
1. Complete Phase 2 (high-priority missing)
2. Start Phase 3 (configuration endpoints)
3. **Result**: 30% coverage, all critical operations supported

---

## 🔍 Using api_endpoints_with_fields.json

### Before Implementing Any Endpoint

**Step 1**: Check API file for structure
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name'
```

**Step 2**: Review required fields for CREATE
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.POST.required'
```

**Step 3**: Review allowed fields for UPDATE
```bash
cat api_endpoints_with_fields.json | jq '.endpoints.endpoint_name.methods.PUT.allowed'
```

**Step 4**: Note nested object structures
Look for `"structure": {"id": "number"}` patterns - these indicate nested required fields

**Step 5**: Proceed with VCR-first workflow
Follow `docs/guides/adding-endpoints.md` starting at Step 1

### Validation Workflow

```
API File → Model Generation → VCR Recording → Compare → Adjust → Verify
   ↓              ↓                ↓            ↓         ↓        ↓
Starting      Initial         Real API    Find Gaps   Fix Model  Test
 Point        Model          Structure                           CREATE
```

---

## 📊 Endpoint Categories Analysis

### By Implementation Status

| Category | Implemented | Percentage |
|----------|-------------|------------|
| **Core CRM** (orders, contacts, accounts, activities, appointments, users) | 6/6 | 100% |
| **Sales Pipeline** (orders, opportunities, orderStages, agreements) | 2/4 | 50% |
| **Configuration** (roles, currencies, segments, etc.) | 12/26 | 46% |
| **Customization** (custom_fields, triggers, forms) | 3/14 | 21% |
| **Integration** (standard_integrations, ad*, soliditet*) | 1/23 | 4% |
| **Reporting** (report, quota, activityQuota, scoreboard) | 0/8 | 0% |
| **Admin** (provisioning, userInvites, roleSettings) | 0/15 | 0% |
| **Specialized** (mail*, esigns, voice, etc.) | 11/71 | 15% |

### By CRUD Support

From api_endpoints_with_fields.json analysis:

| Operation | Total Endpoints | Implemented | Verified | Gap |
|-----------|-----------------|-------------|----------|-----|
| **GET** (list) | 167 | 35 | 19 | 132 |
| **GET** (item) | 159 | 35 | 19 | 124 |
| **POST** (create) | 89 | 16 | 1 | 73 |
| **PUT** (update) | 82 | 16 | 1 | 66 |
| **DELETE** | 76 | 20 | 0 | 56 |

**Key Insight**: 89 endpoints support CREATE but only 1 verified (Orders). This is the biggest gap.

---

## 🎯 Recommended Next Steps

### This Week (2025-11-07 to 2025-11-14)

1. **✅ Verify contacts CREATE** (45 min)
   - Consult api_endpoints_with_fields.json
   - Test with minimal fields: `{email, client: {id}}`
   - Document in ContactCreateFields

2. **✅ Verify activities CREATE** (60 min)
   - Required: date, userId, activityTypeId, client.id
   - Test nested required fields
   - Document in ActivityCreateFields

3. **✅ Verify appointments CREATE** (60 min)
   - Likely uses nested required fields pattern
   - Document in AppointmentCreateFields

4. **✅ Verify accounts CREATE** (45 min)
   - Only requires name (simple!)
   - Test nested arrays (users, addresses)
   - Document in CompanyCreateFields

5. **✅ Implement opportunities** (30 min)
   - Reuse Order model
   - Create OpportunitiesResource
   - Add probability validation

**Total Week 1**: ~4.5 hours

### Next Week (2025-11-15 to 2025-11-21)

6. **✅ Implement agreements** (60 min)
7. **✅ Verify UPDATE operations** (2 hours)
8. **✅ Implement tickets** (60 min)
9. **✅ Implement events** (45 min)

**Total Week 2**: ~5 hours

### Success Metrics

**By End of Week 1**:
- 5 endpoints with verified CREATE (orders, contacts, activities, appointments, accounts)
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
- [ ] Add to API_IMPLEMENTATION_ROADMAP.md progress
- [ ] Note any pattern discoveries
- [ ] Document field requirement discrepancies

---

## 📝 Tracking Progress

### Current Implementation Status

**✅ Fully Verified (5 endpoints)**:
1. users - GET, list, search verified
2. companies (accounts) - GET, list, search verified
3. products - GET, list, search verified
4. order_stages - GET, list, search verified + UPDATE verified
5. orders - GET, list, search verified + **CREATE verified**

**🔶 Implemented, Needs Verification (30 endpoints)**:
activities, appointments, contacts, currencies, forms, files, apikeys, clientcategories, journey_steps, mail, mail_templates, metadata (read-only), notifications, opportunity_ai (read-only), pricelists, projects, roles, sales_coaches, segments, self (read-only), standard_integrations, static_values (read-only), todo_views (read-only), trigger_attributes (read-only), triggers, activity_list (read-only), custom_fields, functions, project_plan_priorities, project_plan_types

**❌ Not Implemented (132 endpoints)**:
opportunities, agreements, tickets, events, quotes, and 127 specialized endpoints

### Progress Tracking

Track progress in three places:
1. **This file** - Roadmap and task list
2. **docs/endpoint-map.md** - Detailed verification status per endpoint
3. **ENDPOINT_TASK_LIST.md** - Original master task list (if exists)

Update after each endpoint completion.

---

## 🌟 Success Stories

### Orders Endpoint
**Before api_endpoints_with_fields.json**: Manual testing to discover fields
**With api_endpoints_with_fields.json**: API file correctly predicted all 5 required fields
**Result**: ✅ Saved ~30 minutes of trial-and-error testing
**Lesson**: File is accurate for core endpoints like orders

### Validation Approach
**Best Practice Established**:
1. Consult API file for expected structure
2. Generate model based on fields
3. Test with VCR to verify
4. Document discrepancies
5. Update endpoint-map.md

---

**Last Updated**: 2025-11-07
**Next Review**: After Phase 1 completion (verify 4 CREATE operations)
**Maintained By**: Auto-updated from implementation progress
