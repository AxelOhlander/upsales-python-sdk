# Terminology Guide

This SDK uses user-friendly naming that matches what users see in the Upsales UI, even when it differs from API endpoints.

## Naming Decisions

### SDK Class: `Upsales` (not `UpsalesClient`)

**The Situation:**
- Originally named `UpsalesClient`
- But API returns nested field called `"client"` which we map to `company`
- Potential confusion: `client = UpsalesClient(...)` vs `contact.client`

**Our Decision: Use `Upsales`**

Simple, clean class name following industry patterns (like `Stripe`, `GitHub` SDKs):

```python
# ✅ Clean and clear
upsales = Upsales(token="...")
company = await upsales.companies.get(1)
contact_company = contact.company  # No naming collision!

# ❌ Old naming (confusing)
client = UpsalesClient(token="...")
company = ???  # Was called "client" in API nested responses
```

**Benefits:**
1. **No collision**: `Upsales` (SDK) vs `company` (data) are completely distinct
2. **Industry standard**: Follows naming pattern of major SDKs (Stripe, GitHub, etc.)
3. **Cleaner**: Shorter, simpler name
4. **Unambiguous**: `upsales` variable name clearly refers to SDK instance

### Companies (not Accounts)

**The Situation:**
- **Upsales UI**: Displays "Companies"
- **API Endpoint**: `/accounts`
- **Nested Responses**: Field named `"client"`

**Our Decision: Use "Company"**

We use `Company` in the Python SDK to match what users see in the Upsales UI:

```python
# ✅ SDK naming (user-friendly)
company = await client.companies.get(1)
companies = await client.companies.list()

# ❌ NOT: client.accounts (matches API but confusing for users)
```

**Rationale:**
1. **User Experience**: Developers using this SDK are Upsales users who think in terms of "companies"
2. **Consistency**: SDK naming matches what users see in the UI
3. **Clarity**: Avoids confusion with "Upsales account" (your CRM account)
4. **Pythonic**: Abstract away API inconsistencies

### Campaigns vs Projects

**The Situation:**
- **Campaigns**: UI displays "Campaigns", API endpoint `/projects`
- **Projects**: UI displays "Projects", API endpoint `/projectPlans`
- Confusing naming: API uses `projects` for what UI calls "Campaigns"

**Our Decision: Follow UI Terminology**

We use `Campaign` and `Project` in the Python SDK to match what users see in the Upsales UI:

```python
# ✅ SDK naming (user-friendly)
campaign = await upsales.campaigns.get(1)  # List of companies/orders/contacts
project = await upsales.projects.get(1)    # Trello-style board

# ❌ NOT: upsales.projects for campaigns (matches API but confusing)
```

**What They Are:**

1. **Campaign** (API: `/projects`): A collection/list containing:
   - Companies
   - Orders
   - Contacts
   - Activities
   - (Possibly more items)

2. **Project** (API: `/projectPlans`): A Trello-style project board with:
   - Phases (columns)
   - Cards (moved between phases)
   - Sub-tasks
   - Assignments

**Rationale:**
1. **User Experience**: Developers using this SDK see "Campaigns" and "Projects" in the UI
2. **Clarity**: Distinct terms prevent confusion between the two features
3. **Consistency**: SDK naming matches UI terminology throughout
4. **Pythonic**: Abstract away API endpoint naming inconsistencies

## Terminology Mapping

| Concept | Upsales UI | API Endpoint | Nested Field Name | SDK Name | SDK Access |
|---------|------------|--------------|-------------------|----------|------------|
| SDK Instance | - | - | - | `Upsales` | `upsales = Upsales(...)` |
| Customer/Company | Companies | `/accounts` | `"client"` | `Company` | `upsales.companies` |
| User | Users | `/users` | - | `User` | `upsales.users` |
| Product | Products | `/products` | - | `Product` | `upsales.products` |
| Campaign/List | Campaigns | `/projects` | - | `Campaign` | `upsales.campaigns` |
| Project Board | Projects | `/projectPlans` | - | `Project` | `upsales.projects` |

## Handling Nested Field Names

When the API returns a field with a different name (like `"client"`), we use Pydantic field aliases:

### Problem

API returns:
```json
{
  "id": 1,
  "name": "Contact Name",
  "client": {
    "id": 123,
    "name": "Company Name"
  }
}
```

But we want Python users to access it as `contact.company`, not `contact.client`.

### Solution: Pydantic Field Aliases

```python
from pydantic import Field
from upsales.models.base import BaseModel
from upsales.models.company import PartialCompany


class Contact(BaseModel):
    """
    Contact model.

    Note: API returns "client" but we expose it as "company" for clarity.
    """

    id: int
    name: str

    # API field name: "client" → Python property name: "company"
    company: PartialCompany = Field(alias="client")


# Usage - clean and user-friendly!
contact = await client.contacts.get(1)
print(contact.company.name)  # ✅ User-friendly
# Not: contact.client.name  # ❌ Works but confusing
```

### How It Works

**Reading from API** (deserialization):
```python
# API sends: {"client": {"id": 123, "name": "ACME Corp"}}
# Pydantic maps: "client" → company property
contact = Contact(**api_data)
print(contact.company.name)  # "ACME Corp"
```

**Writing to API** (serialization):
```python
# When sending back to API
data = contact.model_dump(by_alias=True)
# Returns: {"client": {...}, "name": "..."}
# Field is sent as "client" to match API expectations
```

### Pattern for All Nested Fields

Follow this pattern for any mismatched field names:

```python
class MyModel(BaseModel):
    id: int

    # Python name → API name via alias
    company: PartialCompany = Field(alias="client")
    owner: PartialUser = Field(alias="user")  # If API uses different name
    category: PartialCategory = Field(alias="cat")  # If API abbreviates
```

## Why Not Match the API Exactly?

We considered three options:

### Option 1: Match API Endpoint (`/accounts`)
```python
# ❌ Rejected
company = await client.accounts.get(1)  # Confusing!
```

**Problems:**
- Users see "Companies" in UI but code says "accounts"
- "Account" is ambiguous (Upsales account? Customer account?)

### Option 2: Match Nested Field Name (`"client"`)
```python
# ❌ Rejected
company = await client.clients.get(1)  # Very confusing!
```

**Problems:**
- Conflicts with `Upsales` (the SDK client class)
- `client.clients` is terrible naming
- "client" is ambiguous (SDK client? Customer?)

### Option 3: Match UI ("Companies") ✅ **CHOSEN**
```python
# ✅ Adopted
company = await client.companies.get(1)  # Clear!
contact.company  # Makes sense!
```

**Benefits:**
- Clear and unambiguous
- Matches what users see in UI
- Natural Python: `contact.company` reads well
- SDK abstracts API inconsistencies (this is good design!)

## Implementation Notes

### Models

```python
# upsales/models/company.py
class Company(BaseModel):
    """Note: API endpoint is /accounts"""
    id: int
    name: str


class PartialCompany(PartialModel):
    """Used when Company appears nested as 'client' in API responses"""
    id: int
    name: str
```

### Resources

```python
# upsales/resources/companies.py
class CompaniesResource(BaseResource[Company, PartialCompany]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/accounts",  # API endpoint stays as-is!
            model_class=Company,    # But Python uses Company
            partial_class=PartialCompany,
        )

# upsales/resources/campaigns.py
class CampaignsResource(BaseResource[Campaign, PartialCampaign]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/projects",  # API endpoint is /projects
            model_class=Campaign,   # But Python uses Campaign
            partial_class=PartialCampaign,
        )

# upsales/resources/projects.py
class ProjectsResource(BaseResource[Project, PartialProject]):
    def __init__(self, http: HTTPClient):
        super().__init__(
            http=http,
            endpoint="/projectPlans",  # API endpoint is /projectPlans
            model_class=Project,        # But Python uses Project
            partial_class=PartialProject,
        )
```

### Client

```python
# upsales/client.py
class Upsales:
    def __init__(self, ...):
        self.companies = CompaniesResource(self.http)  # Not .accounts!
        self.campaigns = CampaignsResource(self.http)  # Not .projects!
        self.projects = ProjectsResource(self.http)    # Not .projectPlans!
```

## Documentation Conventions

When documenting the SDK:

**✅ DO:**
- Use "company" and "companies" in user-facing docs
- Use "campaign" and "campaigns" for the list/collection feature
- Use "project" and "projects" for the Trello-style board feature
- Mention API endpoint in technical docs: "Note: API endpoint is /accounts"
- Use `upsales.companies`, `upsales.campaigns`, `upsales.projects` in all examples

**❌ DON'T:**
- Use "account" in user-facing documentation
- Use "project" to refer to campaigns (use "campaign")
- Use "projectPlan" in user-facing docs (use "project")
- Mix terminology (be consistent)

## Future Endpoints

For other endpoints where API and UI naming differs:

1. **Choose UI terminology** for user-friendliness
2. **Document the API endpoint** in model/resource docstrings
3. **Use Field(alias="...")** for nested field name mismatches
4. **Update this terminology guide** with the mapping

## Questions?

If you encounter another naming mismatch:

1. Check what users see in Upsales UI
2. Check API endpoint name
3. Check nested field names in responses
4. Choose UI naming (most user-friendly)
5. Document the choice here
