# TASKS.md — Production-Ready SDK Roadmap

This file tracks work needed to bring the upsales-python-sdk to full API coverage and production readiness.

**Goal**: Cover all 167 Upsales API endpoints, fix known issues, expand testing, and publish to PyPI.

---

## Phase 0: Quality & Cleanup

Unblock everything else by fixing known issues in the current codebase.

- [x] **Fix failing unit tests in `test_contacts_resource.py`** — 4 tests fixed: updated httpx mock URLs to match actual query parameters
- [x] **Fix mypy errors across 3 files** — Fixed 11 errors in `http.py`, `resources/mail_editor.py`, `resources/base.py`, plus 1 pre-existing import typo in `models/form_submits.py`. Now 0 errors across 246 files
- [x] **Commit staged work** — Committed as `95ffa4d`; Phase 0 fixes committed as `b8728e7`
- [x] **Remove duplicate `ImageComposeResource` in `resources/__init__.py` `__all__`**
- [x] **Add missing exports to `resources/__init__.py` `__all__`** — Added `PagesResource` and `UnsubsResource`
- [x] **Update `pyproject.toml` author email** — Updated to `will@upsales.com`
- [x] **Add mypy to CI pipeline** — Added `uv run mypy upsales` step to `.github/workflows/ci.yml`

---

## Phase 1: Internal Project Enablement

Endpoints and features needed by **nk-premeeting-summary** and **nn-bio-import**.

- [x] **Verify file upload resource works end-to-end** — Validated: model has all fields (id, userId, extension, type, filename, mimetype, private, size, entity, entityId, uploadDate), endpoint is `/file/upload`, private sent as string "true"/"false". Unit tests pass.
- [x] **Add `/notify/users` endpoint** — Implemented: 3 POST endpoints (`/notify/users`, `/notify/admins`, `/notify/all`) as `NotifyResource` with `send_to_users()`, `send_to_admins()`, `send_to_all()`. Fields: message, from, type (info/error), userIds, entityId. Registered on client as `upsales.notify`.
- [x] **Verify UDO 1–4 CRUD works** — Validated: all 4 UDO resources have correct endpoint paths (`/userDefinedObjects/:nr`), full CRUD (GET/POST/PUT/DELETE), all fields match detective findings (notes, notes1-4, clientId, contactId, projectId, userId, roleId, custom, categories). Read-only fields are frozen.
- [x] **Verify UDO custom field management** — Validated: custom fields work via standard `custom` array format, `custom_fields` computed property works, custom field search with `custom=eq:fieldId:value` syntax works.
- [x] **Add custom field shorthand search syntax** — Already implemented in `search()` method. Supports both natural (`=11:Technology`) and API (`eq:11:Technology`) syntax. Also supports `wc`, `ne`, `gt`, `gte`, `lt`, `lte` operators.

---

## Phase 2: Missing CRUD Endpoints (13 Tier-1)

Endpoints with POST or PUT support that are not yet implemented. Each needs a model, resource, client registration, and tests.

- [x] `assign` — GET, PUT, DELETE → `AssignResource` with `get()`, `assign_user()`, `remove()` at `/function/assign/:id`
- [x] `accountManagerHistory` — PUT → `AccountManagerHistoryResource` with `set_history()` and `set_specific()` at `/function/accountManagerHistory`
- [x] `cancelEsign` — PUT → `CancelEsignResource` with `cancel()` at `/function/cancelEsign/:id`
- [x] `contract` — GET, PUT → `ContractsResource` with `list()`, `get()`, `update()` at `/contract`
- [x] `customfields_accounts` — full CRUD → `CustomfieldsAccountsResource` at `/customfields/account`
- [x] `export` — POST → `ExportResource` with `trigger()` at `/function/export`
- [x] `importMailCampaign` — POST → `ImportMailCampaignResource` with `create()` at `/import/mailcampaign`
- [x] `integrationLog` — full CRUD → `IntegrationLogResource` at `/integrationLog` (has GET/POST/PUT/DELETE)
- [x] `sendEsignReminder` — PUT → `SendEsignReminderResource` with `send()` at `/function/sendEsignReminder/:id`
- [x] `soliditetMatcher` — GET, PUT, search → `SoliditetMatcherResource` at `/soliditet/matcher`
- [x] `soliditetSearchBuy` — POST → `SoliditetSearchBuyResource` with `buy()` at `/soliditet/search/buy`
- [x] `standardField` — GET, PUT → `StandardFieldsResource` at `/standardField`
- [x] `translateTags` — POST → `TranslateTagsResource` with `translate()` at `/function/translate`

---

## Phase 3: Missing Read-Only Endpoints (46 Tier-2)

GET-only endpoints. Can be batch-implemented since they follow the same pattern. Grouped by domain.

### Search & Lookup
- [x] `quickSearch` — `QuickSearchResource` at `/quicksearch`
- [x] `lookup` — `LookupResource` at `/lookup`
- [x] `findProspect` — `FindProspectResource` at `/findProspect`
- [x] `emailDuplicates` — `EmailDuplicatesResource` at `/function/email-duplicates`
- [x] `emailSuggest` — `EmailSuggestResource` at `/function/email-suggest`
- [x] `emailSuggestion` — `EmailSuggestionResource` at `/emailSuggestion`

### Reporting
- [x] `report` — `ReportResource` at `/report/api/:entity`
- [x] `reportWidget` — `ReportWidgetResource` at `/report/widget`
- [x] `reportWidgetMetadata` — `ReportWidgetMetadataResource` at `/report/metadata/widget`
- [x] `reportClientCompanyType` — `ReportClientCompanyTypeResource` at `/report/clientCompanyType`
- [x] `scoreboard` — `ScoreboardResource` at `/scoreboard`

### Mail
- [x] `mailByThread` — `MailByThreadResource` at `/mail/byThread`
- [x] `mailCampaignInfo` — `MailCampaignInfoResource` at `/mailCampaignInfo` (includes `preview()`)
- [x] `mailTemplatesRecentlyUsed` — `MailTemplatesRecentlyUsedResource` at `/mail/templates/recentlyUsed`
- [x] `mailTemplatesUsedIn` — `MailTemplatesUsedInResource` at `/mail/templates/usedIn`

### Leads
- [x] `leads2` — `Leads2Resource` at `/leads2`
- [x] `leadSources2` — `LeadSources2Resource` at `/leadsources2`

### Integrations & SSO
- [x] `lookerSSO` — `LookerSSOResource` at `/function/externalSSO/looker/:type/:id`
- [x] `lookerExplores` — `LookerExploresResource` at `/looker/explores`
- [x] `lookerLooks` — `LookerLooksResource` at `/looker/looks`
- [x] `doceboSSO` — `DoceboSSOResource` at `/function/externalSSO/docebo`
- [x] `standardIntegrationUser` — `StandardIntegrationUserResource` at `/standardIntegrationUser`

### Notifications & Signals
- [x] `unreadNotifications` — `UnreadNotificationsResource` at `/notificationsUnread/:id`
- [x] `signalsFeed` — `SignalsFeedResource` at `/prospecting/signals`

### Ads
- [x] `adCredits` — `AdCreditsResource` at `/engage/credit`
- [x] `adLocations` — `AdLocationsResource` at `/engage/location`

### Files & Resources
- [x] `file_download` — `FileDownloadResource` at `/file/download`
- [x] `resourcesDownloadAdgear` — `ResourcesDownloadAdgearResource` at `/resources/download/adgear`
- [x] `resourcesDownloadInternal` — `ResourcesDownloadInternalResource` at `/resources/download/internal`

### Forms & Pages
- [x] `clientForm` — `ClientFormResource` at `/clientform`
- [x] `formsExternalLeadSource` — `FormsExternalLeadSourceResource` at `/forms/external-lead-source`
- [x] `landingPageTemplate` — `LandingPageTemplateResource` at `/landingPageTemplate`
- [x] `engageSiteTemplate` — `EngageSiteTemplateResource` at `/engage/siteTemplate`

### Flows & Journeys
- [x] `flowContacts` — `FlowContactsResource` at `/flows/:flowId/:stepId/contacts/:statsType`
- [x] `journeyStepHistory` — `JourneyStepHistoryResource` at `/journeyStepHistory`

### Soliditet
- [x] `soliditetMatcherSearch` — already in `SoliditetMatcherResource.search()` at `/soliditet/matcher/search`
- [x] `soliditetSearch` — `SoliditetSearchResource` at `/soliditet/search`

### Other
- [x] `deleteLog` — `DeleteLogResource` at `/deleteLog`
- [x] `eventsPrior` — `EventsPriorResource` at `/events/prior`
- [x] `groupStructure` — `GroupStructureResource` at `/prospectinggroupstructure`
- [x] `industries` — `IndustriesResource` at `/industries`
- [x] `links` — `LinksResource` at `/links`
- [x] `placeholder` — `PlaceholderResource` at `/placeholder/:feature`
- [x] `roleSettings` — `RoleSettingsResource` at `/roleSettings`
- [x] `whatIsMyIp` — `WhatIsMyIpResource` at `/function/whatismyip`
- [x] `workerStatus` — `WorkerStatusResource` at `/worker/status`

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
