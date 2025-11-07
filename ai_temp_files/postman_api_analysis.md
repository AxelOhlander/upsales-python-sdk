# Upsales API Comprehensive Pattern Analysis

**Source**: Upsales API Postman Collection
**Base URL**: `https://integration.upsales.com/api/v2/`
**Collection ID**: `3883d184-148e-4ff5-a8a3-1b914413f4f2`

---

## 1. HTTP Method Patterns (CRUD Operations)

The API uses standard RESTful HTTP verbs:

| Operation | HTTP Method | Pattern |
|-----------|-------------|---------|
| **List** | `GET` | `/api/v2/{resource}` |
| **Get Single** | `GET` | `/api/v2/{resource}/{id}` |
| **Create** | `POST` | `/api/v2/{resource}` |
| **Update** | `PUT` | `/api/v2/{resource}/{id}` |
| **Delete** | `DELETE` | `/api/v2/{resource}/{id}` |

**Key Findings**:
- **No PATCH**: API uses `PUT` exclusively for updates (not `PATCH`)
- **Consistent pattern** across all resources
- State transitions (close, mark done) also use `PUT` with special fields

### Examples:

```http
# Company CRUD
GET    /api/v2/accounts/
GET    /api/v2/accounts/{id}
POST   /api/v2/accounts/
PUT    /api/v2/accounts/{id}/
DELETE /api/v2/accounts/{id}

# Opportunity CRUD (note: uses /orders endpoint)
GET    /api/v2/orders?probability=gte:1&probability=lte:99
GET    /api/v2/orders/{id}
POST   /api/v2/orders
PUT    /api/v2/orders/{id}
DELETE /api/v2/orders/{id}

# Order CRUD (probability=100 distinguishes from opportunities)
GET    /api/v2/orders?probability=100
```

---

## 2. Endpoint Structure & Categories

### API Version
- **Version**: `v2` (in path: `/api/v2/`)
- **Versioning approach**: Path-based versioning

### Endpoint Categories (26 total)

| Category | API Endpoint | Notes |
|----------|--------------|-------|
| **Company** | `/accounts` | Core CRM entity (not /companies) |
| **Contacts** | `/contacts` | Person records |
| **Users** | `/users` | System users |
| **Products** | `/products` | Product catalog |
| **Opportunity** | `/orders` | Deals with probability < 100 |
| **Order** | `/orders` | Closed deals with probability = 100 |
| **Campaign** | `/campaigns` | Marketing campaigns |
| **Appointment** | `/appointments` | Calendar events |
| **Tasks** | `/activities` | To-dos and phone calls |
| **Custom fields** | `/customfields/{object}` | Custom field schemas |
| **Price Lists** | `/priceLists` | Product pricing |
| **Product categories** | `/productCategories` | Product taxonomy |
| **Opportunity & Order stages** | `/orderstages` | Pipeline stages |
| **Activity types** | `/todoTypes`, `/activitytypes/activity`, `/activitytypes/appointment` | Task type definitions |
| **Appointment types** | `/activitytypes/appointment` | Appointment categories |
| **Client categories** | `/clientCategoryTypes`, `/clientcategories` | Company taxonomy (type + values) |
| **Contact categories** | `/contactCategoryTypes`, `/contactcategories` | Contact taxonomy |
| **Event** | `/events` (inferred) | Marketing events |
| **Subscriptions** | `/agreements` | Recurring revenue |
| **NPS** | `/nps` | Net Promoter Score |
| **Upload documents** | `/resources/upload/internal/{entity}/{id}` | File attachments |
| **User defined object** | `/udos` | Custom objects |
| **Phone calls** | `/phoneCall` | Call records |
| **Projects** | `/projects` | Project management |
| **Use cases** | N/A | Folder of example workflows |

### Key Path Patterns

```
/api/v2/{resource}                              # List/Create
/api/v2/{resource}/{id}                         # Get/Update/Delete
/api/v2/customfields/{objectType}              # Get custom field schema
/api/v2/resources/upload/internal/{entity}/{id} # Upload files
/api/v2/activitytypes/{type}                   # Activity type management
/api/v2/master/users                           # Master account users
```

---

## 3. Authentication

### Primary Method: Token via Query Parameter OR Cookie

**Query Parameter** (most common in examples):
```http
GET /api/v2/accounts/?token={{token}}
```

**Cookie Header** (SDK implementation):
```http
Cookie: token=YOUR_API_TOKEN
```

### Headers
```http
Content-Type: application/json
```

**Note**: Collection description mentions:
- API keys managed under Settings (admin only)
- Keys should be kept secure
- No authentication object in collection (uses variables)

---

## 4. Pagination

### Query Parameters

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `limit` | Number of results per page | 1000 | 2000 |
| `offset` | Number of records to skip | 0 | - |

### Example
```http
GET /api/v2/accounts/?token={{token}}&limit=50&offset=0
```

### Response Metadata

List endpoints return metadata:
```json
{
    "error": null,
    "metadata": {
        "total": 2,
        "limit": 1000,
        "offset": 0
    },
    "data": [...]
}
```

### Best Practice for Complete Pagination

From collection description:
> To be 100% sure you get all entities you need to sort on ID when you do pagination.
> Example: `/api/v2/accounts?sort=id&limit=1000&id=gt:LAST_ID_OF_PREV_BATCH`

**SDK Implementation Note**: Use cursor-based pagination with `id=gt:X` + `sort=id` for reliability.

---

## 5. Request/Response Format

### Standard Response Wrapper

**All responses** use consistent envelope:
```json
{
    "error": null,           // Error message or null
    "metadata": {...},       // Only on list endpoints
    "data": {...}            // Single object or array
}
```

### Single Resource Response
```json
{
    "error": null,
    "data": {
        "id": 3,
        "name": "Richard Hendricks",
        "email": "richard.hendricks@piedpiper.com",
        "client": {
            "name": "Pied piper",
            "id": 2,
            "users": [...]
        },
        "custom": [],
        "regDate": "2018-04-21T10:35:57.000Z",
        "active": 1,
        ...
    }
}
```

### List Response
```json
{
    "error": null,
    "metadata": {
        "total": 2,
        "limit": 1000,
        "offset": 0
    },
    "data": [
        {
            "id": 2,
            "name": "Salesboard",
            ...
        }
    ]
}
```

### Request Body (POST/PUT)

**Standard JSON structure with nested objects referenced by ID**:

#### Create Company
```json
{
    "name": "Salesboard",
    "phone": "+46(0)8123456",
    "users": [
        {"id": 1}
    ]
}
```

#### Update Company (with custom fields)
```json
{
    "name": "Salesboard",
    "users": [{"id": 1}],
    "custom": [
        {
            "value": "2210",
            "fieldId": 3
        }
    ],
    "phone": "+46(0)8123456",
    "webpage": "http://salesboard.com"
}
```

#### Create Order/Opportunity
```json
{
    "description": "10 licenses",
    "date": "2018-07-23",
    "user": {"id": 1},
    "client": {"id": 2},
    "stage": {"id": 12},
    "probability": 100,
    "orderRow": [
        {
            "quantity": 1,
            "price": 9000,
            "listPrice": 10000,
            "purchaseCost": 4500,
            "product": {"id": 1}
        }
    ]
}
```

**Pattern**: Related entities referenced with `{"id": X}` format.

---

## 6. Filtering System

### Filter Syntax

**Standard attributes**:
```
?attribute=comparisontype:value
```

**Custom fields**:
```
?custom=comparisontype:fieldId:value
```

**Default** (no comparison type):
```
?attribute=value  # Defaults to equals
```

**Multiple values**:
```
?attribute=comparisontype:1,2,3,4,7
```

### Comparison Operators

| Operator | Name | Description |
|----------|------|-------------|
| `eq` | Equals | Exact match (default) |
| `ne` | Not equals | Exact non-match |
| `gt` | Greater than | Value greater than |
| `gte` | Greater than or equal | Value >= |
| `lt` | Less than | Value less than |
| `lte` | Less than or equal | Value <= |

### Nested Field Filters

**Filter on related entity fields** using dot notation:
```http
# Companies where user.id not equals 1
/api/v2/accounts?user.id=ne:1

# Orders where value > 100000 AND date >= 2016-01-01
/api/v2/orders?value=gt:100000&date=gte:2016-01-01
```

### Custom Field Filter Examples

```http
# Contacts where custom field 1 >= 2016-01-01
/api/v2/contacts?custom=gte:1:2016-01-01

# Companies with custom field 4 = 1 on nested client
/api/v2/contacts?client.custom=eq:4:1
```

### Real Examples from Collection

```http
# Filter companies: limit 50, user.id equals X, scoreUpdateDate >= date, not external
/api/v2/accounts/?token={{token}}&limit=50&user.id={{id}}&scoreUpdateDate=gte:2018-04-16&isExternal=0

# Get opportunities (probability between 1-99)
/api/v2/orders?token={{token}}&probability=gte:1&probability=lte:99

# Get orders (probability = 100)
/api/v2/orders?token={{token}}&probability=100
```

---

## 7. Special Endpoints & Features

### File Uploads

**Pattern**: `/api/v2/resources/upload/internal/{entity}/{entityId}/`

**Method**: `POST` with `multipart/form-data`

**Supported entities**:
- Company (client): `/resources/upload/internal/client/{clientId}/`
- Contact: `/resources/upload/internal/contact/{contactId}/`
- Order: `/resources/upload/internal/order/{orderId}/`
- Appointment: `/resources/upload/internal/appointment/{appointmentId}/`

**Body format**:
```http
Content-Type: multipart/form-data
```

### Product Bundles

**Create bundle** via `/api/v2/products` with special `bundle` field:
```json
{
    "name": "SaaS bundle",
    "listPrice": 20000,
    "active": 1,
    "bundle": [
        {
            "quantity": 5,
            "productId": 1,
            "tierQuantity": 1
        },
        {
            "quantity": 1,
            "productId": 2,
            "tierQuantity": 1
        }
    ],
    "bundlePriceAdjustment": 1.1
}
```

### State Transitions

**Close phone call** (add `closeDate`):
```json
PUT /api/v2/activities/{{id}}
{
    "description": "Book a meeting",
    "notes": "No answer, follow up tomorrow",
    "closeDate": "2021-09-29"
}
```

**Mark to-do as done**:
```json
PUT /api/v2/activities/{{todoID}}
{
    "closeDate": "2021-09-29"
}
```

### Events (Marketing Events)

**List events**:
```http
GET /api/v2/events
```

**Event-specific endpoints**:
- Get draft events
- Exclude draft events
- Get attending contacts
- Get attended contacts

**Response structure**:
```json
{
    "error": null,
    "metadata": {"total": 3},
    "data": [
        {
            "id": 1,
            "name": "Upsales for B2B Marketing Professionals",
            "description": "...",
            "date": "2018-12-18T08:00:00+00:00",
            "endDate": "2018-12-18T11:00:00+00:00",
            "attendingScore": 2,
            "checkInScore": 4,
            "location": "Sveavägen 21, 111 34 Stockholm, Sverige",
            "venue": "Upsales",
            "draft": 1,
            "timezone": "Europe/Stockholm"
        }
    ]
}
```

### Custom Field Metadata

**Get custom field schemas by object type**:
```http
GET /api/v2/customFields/company
GET /api/v2/customFields/contact
GET /api/v2/customFields/order
GET /api/v2/customFields/udo
```

**Response**:
```json
{
    "data": [
        {
            "id": 11,
            "name": "Field Name",
            "alias": "FIELD_ALIAS",
            "datatype": "String"
        }
    ]
}
```

### User-Defined Objects (UDOs)

**CRUD operations**:
```http
POST   /api/v2/udos
PUT    /api/v2/udos/{id}
DELETE /api/v2/udos/{id}
```

### Category Taxonomy (Two-Level System)

**Category Types** (schemas) + **Category Values** (instances):

```http
# Client category types
GET    /api/v2/clientCategoryTypes
POST   /api/v2/clientCategoryTypes
PUT    /api/v2/clientCategoryTypes/{id}
DELETE /api/v2/clientCategoryTypes/{id}

# Client category values
GET    /api/v2/clientcategories
GET    /api/v2/clientcategories/{id}
POST   /api/v2/clientcategories
PUT    /api/v2/clientcategories/{id}
DELETE /api/v2/clientcategories/{id}
```

Same pattern for contacts: `/contactCategoryTypes` + `/contactcategories`

---

## 8. Common Query Parameters

**Extracted from collection**:

| Parameter | Usage | Example |
|-----------|-------|---------|
| `token` | Authentication | `token={{token}}` |
| `limit` | Pagination limit | `limit=50` |
| `offset` | Pagination offset | `offset=100` |
| `sort` | Sort field | `sort=id` |
| `probability` | Order/opportunity filter | `probability=100` |
| `draft` | Include drafts | `draft=1` |
| `status` | Status filter | `status=active` |
| `isExternal` | External flag | `isExternal=0` |
| `user.id` | User filter (nested) | `user.id=ne:1` |
| `scoreUpdateDate` | Score date filter | `scoreUpdateDate=gte:2018-04-16` |
| `usingFirstnameLastname` | Name format flag | `usingFirstnameLastname=1` |

---

## 9. Error Responses & Status Codes

### HTTP Status Codes

| Code | Description | Handling |
|------|-------------|----------|
| **200** | OK | Success |
| **201** | Created | Success (resource created) |
| **400** | Bad Request | Missing required parameter |
| **401** | Unauthorized | Invalid API key |
| **404** | Not Found | Resource doesn't exist or no access |
| **429** | Too Many Requests | Rate limit exceeded |
| **5xx** | Server Error | Server-side issue |

### Error Response Format

```json
{
    "error": "Error message here",
    "metadata": null,
    "data": null
}
```

### Rate Limit Headers

```http
X-RateLimit-Limit: 200       # Requests allowed per 10 seconds
X-RateLimit-Remaining: 150   # Requests remaining
X-RateLimit-Reset: 7         # Seconds until reset
```

---

## 10. API-Wide Conventions

### Naming Conventions

1. **Endpoint naming**: Lowercase, plural nouns (`/accounts`, `/contacts`, `/orders`)
2. **Field naming**: camelCase (`regDate`, `modDate`, `listPrice`)
3. **Custom fields**: Always array of objects with `fieldId` and `value`
4. **Related entities**: Nested objects with `id` reference
5. **Timestamps**: ISO 8601 format (`2018-04-21T10:35:57.000Z`)
6. **Binary flags**: Integer 0/1 (not boolean) for `active`, `draft`, `administrator`

### Common Field Patterns

**Every resource has**:
```json
{
    "id": 123,
    "regDate": "2018-04-21T10:35:57.000Z",
    "modDate": "2018-04-21T10:35:57.000Z",
    "custom": [],
    "userRemovable": true,
    "userEditable": true
}
```

**User/Contact nested structure**:
```json
{
    "regBy": {
        "id": 1,
        "name": "Gustav Petterson",
        "role": null,
        "email": "apidocs@upsales.com"
    }
}
```

**Company nested in contacts**:
```json
{
    "client": {
        "name": "Pied piper",
        "id": 2,
        "users": [...]
    }
}
```

### Deletion Patterns

1. **Hard delete**: `DELETE` endpoint removes record
2. **Soft delete**: Set `active: 0` via `PUT`
3. **Disable**: Some resources use `active: 0` (products, price lists)
4. **Inactivate**: Campaigns use special "inactivate" terminology

---

## 11. SDK Design Implications

### Resource Naming Translation

| UI/SDK Name | API Endpoint | Notes |
|-------------|--------------|-------|
| `companies` | `/accounts` | User-friendly naming |
| `contacts` | `/contacts` | Direct match |
| `users` | `/users` | Direct match |
| `products` | `/products` | Direct match |
| `opportunities` | `/orders?probability<100` | Filter distinguishes |
| `orders` | `/orders?probability=100` | Same endpoint |
| `campaigns` | `/campaigns` | Direct match |
| `subscriptions` | `/agreements` | API uses "agreements" |

### Critical Patterns to Support

1. **Cursor-based pagination**: `sort=id&id=gt:LAST_ID` for reliability
2. **Nested filtering**: `client.custom=eq:4:1` (dot notation + custom fields)
3. **Comparison operators**: All 6 types (eq, ne, gt, gte, lt, lte)
4. **Custom fields**: Array structure with fieldId
5. **File uploads**: multipart/form-data on special `/resources/upload` endpoint
6. **State transitions**: `closeDate` field pattern
7. **Binary flags**: Integer 0/1 validation (not bool)
8. **Related entities**: `{"id": X}` reference format

### Recommended Base Resource Operations

Every resource should support:
```python
- get(id) -> T
- list(limit, offset, **filters) -> list[T]
- list_all(**filters) -> list[T]  # Auto-paginate
- create(**data) -> T
- update(id, **data) -> T
- delete(id) -> bool
- filter(**kwargs) -> list[T]  # Support comparison operators
```

### Bulk Operations Consideration

No native bulk endpoints found - SDK should implement:
- `bulk_create()` - Multiple POSTs with semaphore
- `bulk_update()` - Multiple PUTs with semaphore
- `bulk_delete()` - Multiple DELETEs with semaphore

Rate limit: 200 req/10s requires careful concurrency control.

---

## 12. Additional Notes

### String Trimming
> "Upsales trims all string fields, which means that spaces are removed at the beginning and end of a string."

**SDK implication**: Validate and document that whitespace will be trimmed.

### Rate Limiting Best Practices

From description:
> "We ask you to please optimize your API traffic in order for your customers to not perceive your service as a larger expense than it has to be."

**Cost tiers**:
- Free: Up to 99,999 API calls/day
- Paid: Tier-based fees for higher usage

**SDK implication**:
- Implement efficient batch operations
- Document rate limit handling
- Provide guidance on optimizing API usage

### API Documentation Changelog

Most recent update: 2023-10-27 (Added information about rate limits)

---

## Summary of Key Findings

1. **CRUD Convention**: GET (list/single), POST (create), PUT (update), DELETE (remove)
2. **No PATCH**: Always use PUT for updates
3. **Consistent wrapper**: `{error, metadata, data}` on all responses
4. **Token auth**: Via query param or Cookie header
5. **Pagination**: `limit` (max 2000) + `offset`, with metadata response
6. **Cursor pagination recommended**: `sort=id&id=gt:X` for reliability
7. **Powerful filtering**: Comparison operators + nested fields + custom fields
8. **File uploads**: Special endpoint with multipart/form-data
9. **Rate limit**: 200 req/10s with exponential backoff on 429
10. **Binary flags**: Use 0/1 integers (not boolean)
11. **Related entities**: `{"id": X}` reference pattern
12. **Custom fields**: Array of `{fieldId, value}` objects
13. **Timestamps**: ISO 8601 format
14. **Two-level categories**: Types + Values endpoints
15. **State transitions**: Via PUT with special fields (closeDate)

---

## Recommended Next Steps for SDK

1. ✅ **Already implemented**: Response wrapper parsing, rate limiting, HTTPClient retry logic
2. ✅ **Already implemented**: Custom fields helper (`CustomFields` class)
3. ✅ **Already implemented**: Binary flag validators
4. **To implement**: Comparison operator support in filters (`eq:`, `gt:`, etc.)
5. **To implement**: Nested field filter support (`client.custom=eq:4:1`)
6. **To implement**: Cursor-based pagination (`list_all` with `id=gt:X`)
7. **To implement**: File upload resources (multipart/form-data)
8. **To implement**: Product bundle support
9. **To implement**: Event resources
10. **To document**: Rate limiting best practices for users
11. **To document**: Cost implications of API usage patterns
