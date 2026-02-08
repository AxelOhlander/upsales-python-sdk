# TASKS.md — Production-Ready SDK Roadmap

This file tracks work needed to bring the upsales-python-sdk to full API coverage and production readiness.

**Goal**: Cover all 167 Upsales API endpoints, fix known issues, expand testing, and publish to PyPI.

---

## Phase 0: Quality & Cleanup

Unblock everything else by fixing known issues in the current codebase.

- [x] **Fix failing unit tests in `test_contacts_resource.py`** — 4 tests fixed: updated httpx mock URLs to match actual query parameters
- [x] **Fix mypy errors across 3 files** — Fixed 11 errors in `http.py`, `resources/mail_editor.py`, `resources/base.py`, plus 1 pre-existing import typo in `models/form_submits.py`. Now 0 errors across 246 files
- [ ] **Commit staged work** — `agreement_groups`, `lead_channels`, `lead_sources` models and resources are staged but uncommitted
- [x] **Remove duplicate `ImageComposeResource` in `resources/__init__.py` `__all__`**
- [x] **Add missing exports to `resources/__init__.py` `__all__`** — Added `PagesResource` and `UnsubsResource`
- [x] **Update `pyproject.toml` author email** — Updated to `will@upsales.com`
- [x] **Add mypy to CI pipeline** — Added `uv run mypy upsales` step to `.github/workflows/ci.yml`

---

## Phase 1: Internal Project Enablement

Endpoints and features needed by **nk-premeeting-summary** and **nn-bio-import**.

- [ ] **Verify file upload resource works end-to-end** — nk-premeeting-summary uses file uploads; add VCR integration test
- [ ] **Add `/notify/users` endpoint** — not in SDK or API reference; investigate if this is a sub-route of an existing endpoint or a standalone resource
- [ ] **Verify UDO 1–4 CRUD works** — models and resources exist for `user_defined_object_{1,2,3,4}`; add integration tests for nn-bio-import use cases
- [ ] **Verify UDO custom field management** — ensure custom fields can be read, set, and searched on UDO objects
- [ ] **Add custom field shorthand search syntax** — support `custom=wc:fieldId:value` pattern in `search()` for custom field filtering

---

## Phase 2: Missing CRUD Endpoints (13 Tier-1)

Endpoints with POST or PUT support that are not yet implemented. Each needs a model, resource, client registration, and tests.

- [ ] `assign` — GET, PUT, DELETE
- [ ] `accountManagerHistory` — PUT
- [ ] `accountManagerHistorySpecific` — PUT
- [ ] `cancelEsign` — PUT
- [ ] `contract` — GET, PUT
- [ ] `customfields_accounts` — full CRUD (GET, POST, PUT, DELETE)
- [ ] `export` — POST
- [ ] `importMailCampaign` — POST
- [ ] `integrationLog` — GET, PUT
- [ ] `sendEsignReminder` — PUT
- [ ] `soliditetMatcher` — GET, PUT
- [ ] `soliditetSearchBuy` — POST
- [ ] `standardField` — GET, PUT
- [ ] `translateTags` — POST

---

## Phase 3: Missing Read-Only Endpoints (46 Tier-2)

GET-only endpoints. Can be batch-implemented since they follow the same pattern. Grouped by domain.

### Search & Lookup
- [ ] `quickSearch` — cross-entity search
- [ ] `lookup` — entity lookup
- [ ] `findProspect` — prospect finder
- [ ] `emailDuplicates` — duplicate email detection
- [ ] `emailSuggest` — email suggestions
- [ ] `emailSuggestion` — email suggestion (alternate)

### Reporting
- [ ] `report` — report data
- [ ] `reportWidget` — report widget data
- [ ] `reportWidgetMetadata` — report widget metadata
- [ ] `reportClientCompanyType` — company type report
- [ ] `scoreboard` — scoreboard data

### Mail
- [ ] `mailByThread` — mail grouped by thread
- [ ] `mailCampaignInfo` — campaign info
- [ ] `mailCampaignInfoPreview` — campaign preview
- [ ] `mailTemplatesRecentlyUsed` — recently used templates
- [ ] `mailTemplatesUsedIn` — template usage info

### Leads
- [ ] `leads2` — leads v2 endpoint
- [ ] `leadSources2` — lead sources v2 endpoint

### Integrations & SSO
- [ ] `lookerSSO` — Looker SSO
- [ ] `lookerExplores` — Looker explores
- [ ] `lookerLooks` — Looker looks
- [ ] `doceboSSO` — Docebo SSO
- [ ] `standardIntegrationUser` — integration user info

### Notifications & Signals
- [ ] `unreadNotifications` — unread notification count
- [ ] `signalsFeed` — signals feed

### Ads
- [ ] `adCredits` — ad credits
- [ ] `adLocations` — ad locations

### Files & Resources
- [ ] `file_download` — file download
- [ ] `resourcesDownloadAdgear` — adgear resource download
- [ ] `resourcesDownloadInternal` — internal resource download

### Forms & Pages
- [ ] `clientForm` — client-facing forms
- [ ] `formsExternalLeadSource` — external lead source forms
- [ ] `landingPageTemplate` — landing page templates
- [ ] `engageSiteTemplate` — engage site templates

### Flows & Journeys
- [ ] `flowContacts` — contacts in a flow
- [ ] `journeyStepHistory` — journey step history

### Soliditet
- [ ] `soliditetMatcherSearch` — Soliditet matcher search
- [ ] `soliditetSearch` — Soliditet search

### Other
- [ ] `deleteLog` — deletion audit log
- [ ] `eventsPrior` — prior events
- [ ] `groupStructure` — group structure
- [ ] `industries` — industry list
- [ ] `links` — link tracking
- [ ] `placeholder` — placeholder data
- [ ] `roleSettings` — role settings
- [ ] `whatIsMyIp` — IP lookup utility
- [ ] `workerStatus` — background worker status

---

## Phase 4: Missing Action & Hybrid Endpoints (3 Tier-3)

- [ ] `mailBounce` — DELETE only
- [ ] `socialEventsDefaultTemplates` — GET, DELETE
- [ ] `userDefinedObjectCategoryTypes` — GET, DELETE

---

## Phase 5: Undocumented Endpoints (8)

These exist in `api_endpoints_with_fields.json` but have no HTTP methods documented. Investigate whether they are active or deprecated.

- [ ] `contactCategoryTypes`
- [ ] `contactcategories`
- [ ] `customfields_activities`
- [ ] `customfields_appointments`
- [ ] `customfields_contacts`
- [ ] `customfields_orderrows`
- [ ] `customfields_orders`
- [ ] `customfields_products`

---

## Phase 6: Test Coverage Expansion

- [ ] **Add VCR integration tests for all implemented endpoints** — many of the 96 implemented resources lack integration tests
- [ ] **Add coverage threshold enforcement in CI** — set minimum coverage percentage in `pyproject.toml` and enforce in CI
- [ ] **Add bandit security scanning to CI** — `bandit` is already a dev dependency but not in CI pipeline
- [ ] **Add interrogate docstring check to CI** — enforce 90% docstring coverage

---

## Phase 7: Publishing

- [ ] **Create `CHANGELOG.md`** — document changes for initial release
- [ ] **Finalize `pyproject.toml` metadata** — description, classifiers, project URLs, license
- [ ] **Publish to PyPI as `0.1.0`** — initial public release
- [ ] **Add GitHub release workflow** — automate releases via CI on tag push
