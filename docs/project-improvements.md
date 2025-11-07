# Upsales SDK - Project Improvements

**Purpose**: Track potential optimizations, enhancements, and technical debt items for future implementation.

**Status**: Living document - add items as they're identified

---

## Table of Contents

1. [Performance Optimizations](#performance-optimizations)
2. [Feature Enhancements](#feature-enhancements)
3. [Developer Experience](#developer-experience)
4. [Code Quality](#code-quality)
5. [Documentation](#documentation)
6. [Testing](#testing)

---

## Critical API Insights (from Postman Collection)

**Source**: `ai_temp_files/postman_api_analysis.md` (analyzed 2025-01-02)

### Key Findings:

1. **HTTP Methods**: POST (create), GET (read), **PUT** (update - no PATCH!), DELETE (delete)
2. **Pagination Limits**: Default 1000, **Maximum 2000** (higher than expected!)
3. **Cursor Pagination Recommended**: `sort=id&id=gt:LAST_ID` for reliability
4. **Opportunities vs Orders**: Same `/orders` endpoint, distinguished by `probability` field
   - Opportunities: `probability < 100`
   - Orders: `probability = 100`
5. **File Uploads**: Special endpoint `/resources/upload/internal/{entity}/{id}/` with multipart/form-data
6. **Two-Level Categories**: Category Types + Category Values (separate endpoints)
7. **String Trimming**: API automatically trims whitespace from string fields
8. **Cost Model**: Free up to 99,999 API calls/day, then tier-based fees
9. **User-Defined Objects (UDOs)**: Custom object types at `/udos`
10. **State Transitions**: Use PUT with special fields (e.g., `closeDate` to close tasks)
11. **Nested Custom Field Filters**: `client.custom=eq:4:1` syntax supported!

**Full analysis**: See `ai_temp_files/postman_api_analysis.md` for 50+ concrete examples

---

## Performance Optimizations

### 1. Parallel Pagination in `list_all()`

**Current State**: Sequential pagination
**Location**: `upsales/resources/base.py:171-216`
**Priority**: 🟡 Medium
**Effort**: Small (~2 hours)

**Description**:

The `list_all()` method currently fetches pages sequentially:

```python
# Current implementation (sequential)
first_page = await self.list(limit=batch_size, offset=0, **params)
offset = batch_size
while True:
    page = await self.list(limit=batch_size, offset=offset, **params)  # Waits for each page
    first_page.extend(page)
    if len(page) < batch_size:
        break
    offset += batch_size
```

**Problem**: Slow for large datasets (1000+ items) because each page waits for the previous one.

**Proposed Solution**: Fetch remaining pages in parallel after first page

```python
async def list_all(self, batch_size: int = 100, max_parallel: int = 5, **params: Any) -> list[T]:
    """
    List all resources with optimized parallel pagination.

    Args:
        batch_size: Items per request (default: 100).
        max_parallel: Max concurrent page fetches (default: 5).
        **params: Additional query parameters.

    Returns:
        List of all resource objects.
    """
    # Get first page to check metadata
    first_response = await self._http.get(self._endpoint, limit=batch_size, offset=0, **params)
    first_page = [
        self._model_class(**item, _client=self._http._upsales_client)
        for item in first_response["data"]
    ]

    # Check if we have metadata with total count
    metadata = first_response.get("metadata", {})
    total = metadata.get("total")

    if len(first_page) < batch_size:
        return first_page  # Already have everything

    # If API provides total, we can calculate exact pages needed
    if total:
        total_pages = (total + batch_size - 1) // batch_size
        remaining_pages = total_pages - 1

        # Fetch remaining pages in parallel (with semaphore for rate limiting)
        semaphore = asyncio.Semaphore(max_parallel)

        async def fetch_page(page_num: int) -> list[T]:
            async with semaphore:
                offset = page_num * batch_size
                return await self.list(limit=batch_size, offset=offset, **params)

        # Fetch pages 2, 3, 4, ... in parallel
        results = await asyncio.gather(
            *[fetch_page(i) for i in range(1, total_pages)],
            return_exceptions=False
        )

        # Combine all results
        for page in results:
            first_page.extend(page)

        return first_page

    # Fallback: sequential if no metadata (current behavior)
    else:
        offset = batch_size
        while True:
            page = await self.list(limit=batch_size, offset=offset, **params)
            first_page.extend(page)
            if len(page) < batch_size:
                break
            offset += batch_size
        return first_page
```

**Benefits**:
- ⚡ **3-5x faster** for large datasets (fetching 1000 items in 2 parallel batches vs 10 sequential)
- 🎯 **Rate limit friendly** - semaphore controls concurrency
- 🔄 **Backward compatible** - falls back to sequential if no metadata
- 🆓 **Free-threaded mode ready** - true parallelism without GIL in Python 3.13+

**Considerations**:
- Need to verify Upsales API returns `metadata.total` consistently
- Default `max_parallel=5` respects rate limits (200 req/10 sec)
- More complex code - trade-off between speed and simplicity

**Testing Required**:
- ✅ Test with metadata (happy path)
- ✅ Test without metadata (fallback path)
- ✅ Test with rate limiting (verify semaphore works)
- ✅ Test with Python 3.13 free-threaded mode
- ✅ Benchmark sequential vs parallel for 1000+ items

**References**:
- Current implementation: `upsales/resources/base.py:171-216`
- Docstring already mentions parallel fetching but not implemented
- Similar pattern in `bulk_update()` and `bulk_delete()` (lines 251-379)

---

### 2. Enhanced Rate Limit Handling with Headers

**Current State**: Basic 429 retry, doesn't read rate limit headers
**Location**: `upsales/http.py`
**Priority**: 🟡 Medium
**Effort**: Small (~2 hours)

**Description**:

Current implementation catches 429 errors and retries with exponential backoff, but doesn't utilize the rate limit headers that Upsales API provides:

**Upsales API Rate Limit Specification**:
- **Limit**: 200 requests per 10 seconds per API key
- **Error**: HTTP 429 (Too Many Requests)
- **Headers Provided**:
  - `X-RateLimit-Limit`: Number of requests allowed per 10 seconds (always 200)
  - `X-RateLimit-Remaining`: Requests remaining until next reset
  - `X-RateLimit-Reset`: Seconds until rate limit reset

**Current Implementation**:
```python
# upsales/http.py (current)
match response.status_code:
    case 429:
        raise RateLimitError("Rate limit exceeded (200 req/10 sec)")
    # ...

@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
)
async def request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
    # ... makes request, raises RateLimitError on 429
```

**Problems**:
- ❌ Doesn't read headers to know exact wait time
- ❌ Uses exponential backoff instead of precise `X-RateLimit-Reset` value
- ❌ Can't expose remaining quota to users
- ❌ No proactive throttling before hitting limit

**Proposed Solution**:

```python
import asyncio
from dataclasses import dataclass

@dataclass
class RateLimitInfo:
    """Rate limit information from API headers."""
    limit: int  # Total allowed (200)
    remaining: int  # Requests remaining
    reset: int  # Seconds until reset

class HTTPClient:
    def __init__(self, ...):
        # ... existing init
        self._rate_limit_info: RateLimitInfo | None = None
        self._rate_limit_lock = asyncio.Lock()

    def _extract_rate_limit_headers(self, response: httpx.Response) -> RateLimitInfo | None:
        """Extract rate limit info from response headers."""
        try:
            return RateLimitInfo(
                limit=int(response.headers.get("X-RateLimit-Limit", 200)),
                remaining=int(response.headers.get("X-RateLimit-Remaining", 0)),
                reset=int(response.headers.get("X-RateLimit-Reset", 10)),
            )
        except (ValueError, TypeError):
            return None

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with rate limit header support."""
        if not self._client:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context.")

        endpoint = endpoint.lstrip("/")
        response = await self._client.request(method, endpoint, **kwargs)

        # Extract rate limit info from headers (every response)
        rate_limit = self._extract_rate_limit_headers(response)
        if rate_limit:
            self._rate_limit_info = rate_limit

        # Pattern matching for error handling
        match response.status_code:
            case 200 | 201:
                pass
            # ... other cases
            case 429:
                # Use precise wait time from headers
                if rate_limit and rate_limit.reset > 0:
                    wait_seconds = rate_limit.reset
                    raise RateLimitError(
                        f"Rate limit exceeded. "
                        f"{rate_limit.remaining}/{rate_limit.limit} requests remaining. "
                        f"Retry after {wait_seconds} seconds."
                    )
                else:
                    # Fallback if headers not available
                    raise RateLimitError("Rate limit exceeded (200 req/10 sec)")
            # ... rest

        # Parse response
        data: dict[str, Any] = response.json()
        return data

    @property
    def rate_limit_remaining(self) -> int | None:
        """Get remaining requests before rate limit."""
        return self._rate_limit_info.remaining if self._rate_limit_info else None

    @property
    def rate_limit_reset_seconds(self) -> int | None:
        """Get seconds until rate limit reset."""
        return self._rate_limit_info.reset if self._rate_limit_info else None

    async def wait_for_rate_limit_reset(self) -> None:
        """
        Wait for rate limit to reset.

        Useful when proactively managing rate limits.

        Example:
            >>> if client.http.rate_limit_remaining == 0:
            ...     await client.http.wait_for_rate_limit_reset()
        """
        if self._rate_limit_info and self._rate_limit_info.reset > 0:
            await asyncio.sleep(self._rate_limit_info.reset)
```

**Enhanced Retry Logic**:

```python
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

class RateLimitError(UpsalesError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, reset_seconds: int | None = None):
        super().__init__(message)
        self.reset_seconds = reset_seconds

# Custom retry that uses reset_seconds from exception
def wait_for_rate_limit_reset(retry_state):
    """Custom wait function that uses X-RateLimit-Reset header."""
    exception = retry_state.outcome.exception()
    if isinstance(exception, RateLimitError) and exception.reset_seconds:
        return exception.reset_seconds
    # Fallback to exponential backoff
    return min(2 ** (retry_state.attempt_number - 1), 60)

@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_for_rate_limit_reset,  # Use precise wait time
)
async def request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
    # ... implementation
```

**Benefits**:
- ✅ **Precise wait times** - Use X-RateLimit-Reset instead of guessing
- ✅ **Expose quota** - Users can check `client.http.rate_limit_remaining`
- ✅ **Faster recovery** - Wait exact time needed, not exponential backoff
- ✅ **Better logging** - Include remaining/limit in error messages
- ✅ **Proactive throttling** - Users can check quota before bulk operations

**User-Facing API**:

```python
async with Upsales.from_env() as upsales:
    # Check rate limit before bulk operation
    remaining = upsales.http.rate_limit_remaining
    if remaining is not None and remaining < 100:
        print(f"Only {remaining} requests remaining, waiting for reset...")
        await upsales.http.wait_for_rate_limit_reset()

    # Proceed with bulk operation
    await upsales.products.bulk_update(ids, data)

    # Check quota after
    print(f"Requests remaining: {upsales.http.rate_limit_remaining}")
```

**Testing Required**:
- ✅ Verify headers are present in 200 responses
- ✅ Verify headers are present in 429 responses
- ✅ Test reset time accuracy
- ✅ Test with bulk operations
- ✅ Verify thread-safety of _rate_limit_info updates

**Status**: Design complete, ready for implementation

---

### 3. HTTP Connection Pooling

**Current State**: New connection per request
**Location**: `upsales/http.py`
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Description**:

The HTTPClient currently doesn't explicitly configure connection pooling. HTTPX does pool by default, but we could optimize:

**Proposed Solution**:
```python
class HTTPClient:
    def __init__(self, ...):
        # Configure limits for connection pooling
        limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100,
            keepalive_expiry=30.0
        )
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            limits=limits,  # ← Add connection pool limits
            headers={"Cookie": f"token={self.token}"}
        )
```

**Benefits**:
- Faster requests by reusing TCP connections
- Reduced latency for bulk operations
- Better resource utilization

**Testing Required**:
- Benchmark request times with/without pooling
- Monitor connection counts during bulk operations

---

### 3. Response Caching (Optional)

**Current State**: No caching
**Priority**: 🟢 Low (Not recommended, see notes)
**Effort**: Large (~8 hours)

**Description**:

Discord.py uses caching extensively (`get_*()` vs `fetch_*()`), but for Upsales:

**Recommendation**: **DON'T IMPLEMENT**

**Reasons NOT to cache**:
- ❌ No real-time updates (no websocket) means cache is always potentially stale
- ❌ Complex invalidation logic needed (when to refresh?)
- ❌ Memory overhead for large datasets
- ❌ Confusion about data freshness ("why is this field not updated?")
- ❌ Most operations already happen in context of single workflow

**Alternative**: Document best practices for developers
- Store results in variables when reusing in same workflow
- Use `refresh()` method when explicit refresh needed
- Use `bulk_get()` when fetching multiple known IDs

**Status**: Won't implement - documented as decision

---

## Feature Enhancements

### 4. Add `bulk_create()` Method

**Current State**: ❌ Missing
**Priority**: 🟡 Medium
**Effort**: Small (~2 hours)

**Description**: Parallel creation for imports/migrations. See `docs/api-methods-design.md` Phase 2.

**Status**: Documented in API methods design doc

---

### 5. Add `bulk_get()` Method

**Current State**: ❌ Missing
**Priority**: 🟡 Medium
**Effort**: Small (~1 hour)

**Description**: Fetch multiple resources by IDs in parallel. More efficient than individual `get()` calls.

**Status**: Documented in API methods design doc

---

### 6. Add Instance `delete()` Method

**Current State**: ❌ Missing
**Priority**: 🟡 Medium
**Effort**: Small (~1 hour)

**Description**: OOP pattern for deleting instances. See `docs/api-methods-design.md` Phase 3.

```python
async def delete(self) -> None:
    """Delete this resource."""
    if not self._client:
        raise RuntimeError("No client available")
    await self._client.{resource}.delete(self.id)
```

**Status**: Documented in API methods design doc

---

### 7. Add Instance `refresh()` Method

**Current State**: ❌ Missing
**Priority**: 🟢 Low
**Effort**: Small (~1 hour)

**Description**: Reload instance data from API. See `docs/api-methods-design.md` Phase 3.

```python
async def refresh(self) -> Self:
    """Refresh this instance with latest data from API."""
    if not self._client:
        raise RuntimeError("No client available")
    fresh = await self._client.{resource}.get(self.id)
    self.__dict__.update(fresh.__dict__)
    return self
```

**Status**: Documented in API methods design doc

---

### 8. Cursor-Based Pagination for `list_all()`

**Current State**: Offset-based pagination only
**Location**: `upsales/resources/base.py:171-216`
**Priority**: 🟡 Medium
**Effort**: Small (~2 hours)

**Description**:

Postman collection documentation recommends cursor-based pagination for reliability:

> "To be 100% sure you get all entities you need to sort on ID when you do pagination.
> Example: `/api/v2/accounts?sort=id&limit=1000&id=gt:LAST_ID_OF_PREV_BATCH`"

**Current Implementation** (offset-based):
```python
# Fetch pages sequentially with increasing offset
offset = 0
while True:
    page = await self.list(limit=100, offset=offset, **params)
    results.extend(page)
    if len(page) < 100:
        break
    offset += 100
```

**Problems with offset**:
- ❌ Can miss or duplicate records if data changes during pagination
- ❌ Performance degrades for high offsets
- ❌ Not reliable for large datasets

**Proposed Solution** (cursor-based):
```python
async def list_all(
    self,
    batch_size: int = 1000,  # Upsales default
    use_cursor: bool = True,  # New parameter
    **params: Any
) -> list[T]:
    """
    List all resources with automatic pagination.

    Args:
        batch_size: Items per request (default: 1000, max: 2000).
        use_cursor: Use cursor-based (id>X) vs offset pagination.
        **params: Additional filters.

    Returns:
        List of all matching resources.

    Example:
        >>> # Cursor-based (recommended for reliability)
        >>> all_companies = await upsales.companies.list_all()
        >>>
        >>> # Offset-based (legacy)
        >>> all_users = await upsales.users.list_all(use_cursor=False)

    Note:
        Cursor-based pagination is more reliable when data changes
        during iteration. Uses sort=id&id=gt:X pattern.
    """
    if use_cursor:
        # Cursor-based pagination (recommended)
        results = []
        last_id = 0

        while True:
            page = await self.list(
                limit=batch_size,
                sort="id",
                id=f"gt:{last_id}",  # id greater than last
                **params
            )
            if not page:
                break

            results.extend(page)
            if len(page) < batch_size:
                break

            last_id = page[-1].id

        return results
    else:
        # Offset-based (current implementation)
        # ... existing code
```

**Benefits**:
- ✅ **Reliable pagination** - No missed/duplicate records
- ✅ **Better performance** - No offset penalty for large datasets
- ✅ **Official recommendation** - Follows Upsales best practices
- ✅ **Backward compatible** - Keep offset option via `use_cursor=False`

**Testing Required**:
- Test with data modifications during pagination
- Compare reliability vs offset-based
- Benchmark performance for 10,000+ records
- Verify `sort` parameter works on all resources

**Status**: Design complete, ready for implementation

---

### 11. File Upload Resource Support

**Current State**: Not implemented
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Description**:

Upsales API supports file uploads to attach documents to entities:

**Endpoint Pattern**:
```
POST /api/v2/resources/upload/internal/{entity}/{entityId}/
```

**Supported entities**: client, contact, order, appointment

**Request format**: `multipart/form-data`

**Proposed Implementation**:

```python
# Add to BaseModel (for entities that support uploads)
async def upload_file(
    self,
    file_path: str,
    description: str | None = None
) -> dict[str, Any]:
    """
    Upload file attachment to this resource.

    Args:
        file_path: Path to file to upload.
        description: Optional description for the file.

    Returns:
        Upload response data.

    Example:
        >>> company = await upsales.companies.get(123)
        >>> await company.upload_file("contract.pdf", "Signed contract")
    """
    if not self._client:
        raise RuntimeError("No client available")

    # Map model type to entity name
    entity_map = {
        "Company": "client",
        "Contact": "contact",
        "Order": "order",
        "Appointment": "appointment"
    }
    entity = entity_map.get(self.__class__.__name__)

    if not entity:
        raise NotImplementedError(f"{self.__class__.__name__} does not support file uploads")

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"description": description} if description else {}

        return await self._client.http.upload(
            f"/resources/upload/internal/{entity}/{self.id}/",
            files=files,
            data=data
        )


# Add to HTTPClient
async def upload(
    self,
    endpoint: str,
    files: dict[str, Any],
    data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Upload file with multipart/form-data.

    Args:
        endpoint: Upload endpoint.
        files: Files dict for httpx.
        data: Additional form data.

    Returns:
        Response data.
    """
    if not self._client:
        raise RuntimeError("HTTP client not initialized")

    response = await self._client.post(endpoint, files=files, data=data)
    return response.json()
```

**Applicability**: Companies, Contacts, Orders, Appointments

**Status**: Low priority, implement when file attachment needed

---

### 12. Update Default Pagination Limit

**Current State**: Default limit = 100
**Location**: `upsales/resources/base.py:132`
**Priority**: 🟢 Low
**Effort**: Trivial (~5 minutes)

**Description**:

Postman collection shows Upsales API defaults:
- **Default limit**: 1000 (not 100)
- **Maximum limit**: 2000

**Current SDK**:
```python
async def list(
    self,
    limit: int = 100,  # ← Too conservative
    offset: int = 0,
    **params: Any,
) -> list[T]:
```

**Proposed**:
```python
async def list(
    self,
    limit: int = 1000,  # ← Match API default
    offset: int = 0,
    **params: Any,
) -> list[T]:
    """
    List resources with pagination.

    Args:
        limit: Maximum results per page (default: 1000, max: 2000).
        offset: Offset for pagination (default: 0).
        **params: Additional query parameters for filtering.
    """
    # Cap at API maximum
    if limit > 2000:
        limit = 2000

    all_params = params | {"limit": limit, "offset": offset}
    response = await self._http.get(self._endpoint, **all_params)
    # ...
```

**Benefits**:
- ✅ Fewer API calls for large datasets
- ✅ Matches API defaults
- ✅ Better performance

**Impact**: Minor breaking change if users rely on limit=100 default

**Status**: Ready to implement

---

### 13. Relationship Access Methods

**Current State**: ❌ Not implemented
**Priority**: 🟢 Low
**Effort**: Large (~8 hours) - Requires API research

**Description**: Methods for accessing related resources. See `docs/api-methods-design.md` Phase 5.

**Examples**:
- `await company.fetch_contacts()`
- `await company.fetch_orders()`
- `await contact.fetch_activities()`

**Blockers**:
- Need to research Upsales API relationship capabilities
- Verify if API supports filtering by related resource IDs
- Check if nested writes are supported

**Status**: Exploratory - documented in API methods design doc

---

### 11. Domain-Specific Methods

**Current State**: Partial (e.g., `bulk_deactivate()` exists)
**Priority**: 🟢 Low
**Effort**: Variable per method

**Description**: Natural business operation methods. See `docs/api-methods-design.md` Phase 6.

**Examples**:
- **Campaigns**: `send()`, `schedule()`, `cancel()`, `add_recipients()`
- **Orders**: `approve()`, `reject()`, `fulfill()`, `cancel()`
- **Users**: `activate()`, `deactivate()`, `reset_password()`
- **Companies**: `activate()`, `deactivate()`, `monitor()`

**Implementation Pattern**:
```python
async def send(self) -> "Campaign":
    """Send this campaign now."""
    return await self.edit(status='sent', sent_date=datetime.now())

async def schedule(self, send_date: str) -> "Campaign":
    """Schedule campaign for later."""
    return await self.edit(status='scheduled', send_date=send_date)
```

**Status**: Documented in API methods design doc, implement as needed

---

## Developer Experience

### 12. Better Error Messages

**Current State**: Basic HTTP error handling
**Priority**: 🟡 Medium
**Effort**: Medium (~4 hours)

**Description**:

Current error messages could be more helpful:

```python
# Current
raise NotFoundError(f"Resource not found: {endpoint}")

# Improved
raise NotFoundError(
    f"User with ID {user_id} not found. "
    f"Verify the ID exists or check if you have permission to access it."
)
```

**Proposed Enhancements**:
1. **Context-aware messages**: Include resource type and ID
2. **Actionable suggestions**: What to check or try next
3. **Rate limit info**: Show remaining quota when hitting 429
4. **Validation details**: Which fields failed validation (parse API response)

**Example Implementation**:
```python
class NotFoundError(UpsalesError):
    def __init__(self, resource_type: str, resource_id: int, endpoint: str):
        super().__init__(
            f"{resource_type} with ID {resource_id} not found.\n"
            f"Endpoint: {endpoint}\n"
            f"Possible causes:\n"
            f"  - Resource doesn't exist\n"
            f"  - Resource was deleted\n"
            f"  - You don't have permission to access it"
        )
```

**Benefits**:
- Faster debugging
- Better developer experience
- Reduced support requests

---

### 13. Better Type Hints for Dynamic Methods

**Current State**: Some methods return `Any` or generic types
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Description**:

Improve type hints for better IDE support:

```python
# Current
async def search(self, **filters: Any) -> list[T]:
    ...

# Improved (with TypedDict)
class UserSearchFilters(TypedDict, total=False):
    name: str
    email: str
    active: int
    administrator: int

async def search(self, **filters: Unpack[UserSearchFilters]) -> list[User]:
    ...
```

**Benefits**:
- Full IDE autocomplete for search filters
- Type checking catches errors early
- Self-documenting code

---

### 14. CLI Tool: Discover Searchable Fields

**Current State**: Manual testing required to find searchable fields
**Priority**: 🟡 Medium
**Effort**: Medium (~6-8 hours)

**Description**:

Create CLI tool that automatically discovers which fields are searchable for each resource by testing all fields (including nested) against the API.

**Command**:
```bash
# Test all fields for a resource
uv run upsales discover-searchable users

# Test with all comparison operators
uv run upsales discover-searchable users --test-operators

# Test specific resource with output
uv run upsales discover-searchable accounts --test-operators --output searchable_fields.json

# Test nested fields only
uv run upsales discover-searchable accounts --nested-only

# Test all major resources
uv run upsales discover-searchable --all --test-operators

# Compare inconsistencies across resources (nested fields)
uv run upsales discover-searchable --all --check-consistency

# Verbose mode to see each test
uv run upsales discover-searchable users --test-operators -v

# Generate SearchFilters code
uv run upsales discover-searchable users --test-operators --generate-code
```

**Flags**:
- `--test-operators`: Test all comparison operators (eq, ne, gt, gte, lt, lte, in)
- `--nested-only`: Only test nested fields (e.g., role.id, user.name)
- `--output <file>`: Save JSON results to file
- `--all`: Test all major resources
- `--check-consistency`: Compare nested field support across resources
- `--generate-code`: Output Python code for SearchFilters
- `-v, --verbose`: Show detailed progress for each field tested
- `--sample-size <n>`: Number of items to fetch for testing (default: 10)

**How It Works**:

1. **Fetch sample data**:
   ```python
   # Get a few items from the endpoint
   response = await client.users.list(limit=10)
   ```

2. **Extract all fields recursively**:
   ```python
   # Top-level fields
   fields = ["id", "name", "email", "active", "administrator", ...]

   # Nested fields (test these too!)
   nested_fields = [
       "role.id",
       "role.name",
       "custom.fieldId",  # If applicable
       # etc.
   ]
   ```

3. **Test each field with ALL comparison operators**:
   ```python
   OPERATORS = ["eq", "ne", "gt", "gte", "lt", "lte"]

   for field in all_fields:
       field_results = {
           "field": field,
           "type": type(test_value).__name__,
           "operators": {}
       }

       # Test equality first (baseline)
       try:
           test_value = sample_data[0][field]
           result = await client.users.list(limit=1, **{field: test_value})
           field_results["operators"]["eq"] = {
               "supported": True,
               "matches": len(result)
           }
       except Exception as e:
           field_results["operators"]["eq"] = {
               "supported": False,
               "error": str(e)
           }
           continue  # Skip other operators if equals doesn't work

       # Test other operators (for numeric/date fields)
       if isinstance(test_value, (int, float, str)):  # str for dates
           for op in ["ne", "gt", "gte", "lt", "lte"]:
               try:
                   # Format: field="op:value"
                   filter_value = f"{op}:{test_value}"
                   result = await client.users.list(limit=1, **{field: filter_value})
                   field_results["operators"][op] = {
                       "supported": True,
                       "matches": len(result)
                   }
               except Exception as e:
                   field_results["operators"][op] = {
                       "supported": False,
                       "error": str(e)
                   }

       # Test multiple values (IN operator)
       try:
           # Get multiple test values from sample data
           values = [obj[field] for obj in sample_data[:3] if field in obj]
           if len(values) >= 2:
               filter_value = f"eq:{','.join(map(str, values))}"
               result = await client.users.list(limit=5, **{field: filter_value})
               field_results["operators"]["in"] = {
                   "supported": True,
                   "matches": len(result),
                   "values_tested": values
               }
       except Exception as e:
           field_results["operators"]["in"] = {
               "supported": False,
               "error": str(e)
           }

       all_field_results.append(field_results)
   ```

4. **Handle nested objects recursively**:
   ```python
   # Example: Companies have nested "users" array
   company = await client.companies.get(123)
   # company.users = [{"id": 1, "name": "John"}, ...]

   # Test nested fields with ALL operators:
   nested_fields = extract_nested_fields(company)
   # Returns: [("user.id", int, 1), ("user.name", str, "John"), ...]

   for nested_field, field_type, test_value in nested_fields:
       # Test different formats API might support:
       formats_to_test = [
           nested_field,              # "user.id"
           nested_field.replace(".", "_"),  # "user_id"
           nested_field.split(".")[-1],     # "id" (ambiguous, but test anyway)
       ]

       for format in formats_to_test:
           # Test equality
           try:
               result = await client.companies.list(limit=1, **{format: test_value})
               # Track which format works
           except:
               pass

           # Test operators (if equality worked)
           for op in ["ne", "gt", "gte", "lt", "lte"]:
               try:
                   filter_value = f"{op}:{test_value}"
                   result = await client.companies.list(limit=1, **{format: filter_value})
               except:
                   pass
   ```

5. **Detect inconsistencies across resources**:
   ```python
   # Track nested field searchability by model type
   nested_field_map = {}

   for resource in ["accounts", "orders", "activities", "contacts"]:
       results = await discover(resource)

       # Group by nested object model (e.g., PartialUser)
       for field_result in results["nested_fields"]:
           model_type = field_result["model"]  # "PartialUser"
           field_path = field_result["field"]  # "user.name"

           if model_type not in nested_field_map:
               nested_field_map[model_type] = {}

           if field_path not in nested_field_map[model_type]:
               nested_field_map[model_type][field_path] = {
                   "searchable_in": [],
                   "not_searchable_in": [],
                   "operators": {}
               }

           if field_result["searchable"]:
               nested_field_map[model_type][field_path]["searchable_in"].append(resource)
               nested_field_map[model_type][field_path]["operators"][resource] = \
                   field_result["supported_operators"]
           else:
               nested_field_map[model_type][field_path]["not_searchable_in"].append(resource)

   # Detect inconsistencies
   inconsistencies = []
   for model_type, fields in nested_field_map.items():
       for field, data in fields.items():
           if data["searchable_in"] and data["not_searchable_in"]:
               inconsistencies.append({
                   "model": model_type,
                   "field": field,
                   "searchable_in": data["searchable_in"],
                   "not_searchable_in": data["not_searchable_in"],
                   "severity": "high" if "id" in field else "medium",
                   "recommendation": f"Only include {field} in SearchFilters for: {data['searchable_in']}"
               })

           # Check operator consistency
           operators_by_resource = data.get("operators", {})
           if len(operators_by_resource) > 1:
               # Compare which operators work in each resource
               all_operators = set()
               for resource, ops in operators_by_resource.items():
                   all_operators.update(ops.keys())

               for op in all_operators:
                   resources_with_op = [r for r, ops in operators_by_resource.items() if op in ops]
                   resources_without_op = [r for r in operators_by_resource.keys() if op not in operators_by_resource[r]]

                   if resources_with_op and resources_without_op:
                       inconsistencies.append({
                           "model": model_type,
                           "field": field,
                           "operator": op,
                           "supported_in": resources_with_op,
                           "not_supported_in": resources_without_op,
                           "severity": "low",
                           "recommendation": f"Document that {field} supports '{op}' only in {resources_with_op}"
                       })
   ```

**Output Format**:

```json
{
  "resource": "users",
  "endpoint": "/users",
  "tested_at": "2025-01-02T10:30:00Z",
  "sample_size": 10,
  "fields_tested": 45,
  "operators_tested": ["eq", "ne", "gt", "gte", "lt", "lte", "in"],
  "searchable_fields": [
    {
      "field": "active",
      "type": "int",
      "tested_value": 1,
      "supported_operators": {
        "eq": {"supported": true, "matches": 8},
        "ne": {"supported": true, "matches": 2},
        "gt": {"supported": false, "error": "400: Comparison not supported for binary field"},
        "gte": {"supported": false, "error": "400: Comparison not supported for binary field"},
        "lt": {"supported": false, "error": "400: Comparison not supported for binary field"},
        "lte": {"supported": false, "error": "400: Comparison not supported for binary field"},
        "in": {"supported": true, "matches": 10, "values_tested": [0, 1]}
      },
      "recommended_operators": ["eq", "ne", "in"],
      "status": "confirmed"
    },
    {
      "field": "regDate",
      "type": "str",
      "tested_value": "2024-01-15",
      "supported_operators": {
        "eq": {"supported": true, "matches": 1},
        "ne": {"supported": true, "matches": 9},
        "gt": {"supported": true, "matches": 7},
        "gte": {"supported": true, "matches": 8},
        "lt": {"supported": true, "matches": 2},
        "lte": {"supported": true, "matches": 3},
        "in": {"supported": true, "matches": 5}
      },
      "recommended_operators": ["eq", "ne", "gt", "gte", "lt", "lte", "in"],
      "status": "confirmed",
      "note": "Date field - all operators supported for range queries"
    },
    {
      "field": "role.id",
      "type": "int",
      "nested": true,
      "model": "PartialRole",
      "tested_formats": {
        "role.id": {"supported": true, "preferred": true},
        "role_id": {"supported": false},
        "id": {"supported": false, "note": "Ambiguous, conflicts with user.id"}
      },
      "supported_operators": {
        "eq": {"supported": true, "matches": 3},
        "ne": {"supported": true, "matches": 7},
        "in": {"supported": true, "matches": 5}
      },
      "recommended_format": "role.id",
      "recommended_operators": ["eq", "ne", "in"],
      "status": "confirmed"
    }
  ],
  "non_searchable_fields": [
    {
      "field": "userPhone",
      "type": "str",
      "tested_value": "+123456789",
      "error": "400 Bad Request: Unknown filter parameter 'userPhone'",
      "status": "not_supported"
    }
  ],
  "nested_objects": [
    {
      "path": "role",
      "model": "PartialRole",
      "fields": [
        {
          "field": "role.id",
          "searchable": true,
          "operators": ["eq", "ne", "in"]
        },
        {
          "field": "role.name",
          "searchable": true,
          "operators": ["eq", "ne"]
        },
        {
          "field": "role.description",
          "searchable": false,
          "error": "400: Field not filterable"
        }
      ]
    }
  ]
}
```

**Consistency Report**:

```json
{
  "inconsistencies": [
    {
      "type": "field_availability",
      "nested_object": "user",
      "model": "PartialUser",
      "field": "name",
      "searchable_in": ["/accounts", "/contacts"],
      "not_searchable_in": ["/orders", "/activities"],
      "severity": "medium",
      "recommendation": "Only include user.name in CompanySearchFilters and ContactSearchFilters"
    },
    {
      "type": "field_availability",
      "nested_object": "user",
      "model": "PartialUser",
      "field": "email",
      "searchable_in": ["/accounts"],
      "not_searchable_in": ["/contacts", "/orders", "/activities"],
      "severity": "high",
      "recommendation": "Only include user.email in CompanySearchFilters"
    },
    {
      "type": "operator_support",
      "field": "regDate",
      "operator": "gt",
      "supported_in": ["/accounts", "/users"],
      "not_supported_in": ["/products"],
      "severity": "low",
      "recommendation": "Document that regDate supports 'gt' only in accounts and users"
    },
    {
      "type": "nested_format",
      "field": "user.id",
      "model": "PartialUser",
      "format_in_accounts": "user.id",
      "format_in_orders": "userId",
      "severity": "medium",
      "recommendation": "Normalize to single format or support both in SearchFilters"
    }
  ],
  "consistent_patterns": [
    {
      "nested_object": "user",
      "model": "PartialUser",
      "field": "id",
      "searchable_in_all": ["/accounts", "/contacts", "/orders", "/activities"],
      "supported_operators": ["eq", "ne", "in"],
      "consistent_format": "user.id",
      "recommendation": "Safe to include user.id in all SearchFilters with user relationship"
    },
    {
      "field_type": "binary_flags",
      "fields": ["active", "administrator", "isExternal"],
      "supported_operators_all": ["eq", "ne", "in"],
      "not_supported_operators": ["gt", "gte", "lt", "lte"],
      "recommendation": "Binary flags (0/1) only support eq, ne, in - never range operators"
    },
    {
      "field_type": "dates",
      "fields": ["regDate", "startDate", "endDate"],
      "supported_operators_all": ["eq", "ne", "gt", "gte", "lt", "lte", "in"],
      "recommendation": "Date fields support all operators - use gte/lte for date ranges"
    }
  ]
}
```

**Generated Documentation**:

The tool should auto-generate comprehensive field documentation:

```python
# Auto-generated from discovery tool
# Run: uv run upsales discover-searchable users --test-operators
# Date: 2025-01-02T10:30:00Z
# Tested against: https://power.upsales.com/api/v2/users
# Sample size: 10 users

class UsersResource(BaseResource[User, PartialUser]):
    async def search(self, **filters: Any) -> list[User]:
        """
        Search users with comparison operators.

        Searchable Fields (Auto-discovered):

        Top-level Fields:
            active: int or str
                - Operators: eq, ne, in
                - Example: active=1 or active="ne:0"
                - Note: Binary field (0/1), range operators not supported

            administrator: int or str
                - Operators: eq, ne, in
                - Example: administrator=1

            email: str
                - Operators: eq, ne
                - Example: email="john@example.com"
                - Note: Exact match only

            name: str
                - Operators: eq, ne
                - Example: name="John"
                - Note: May support partial matching (verify)

            regDate: str
                - Operators: eq, ne, gt, gte, lt, lte, in
                - Example: regDate="gte:2024-01-01"
                - Note: Full date operator support for range queries

        Nested Fields:
            role.id: int or str
                - Format: role.id (NOT role_id or id)
                - Operators: eq, ne, in
                - Example: **{"role.id": 5}** or **{"role.id": "eq:1,2,3"}**

            role.name: str
                - Format: role.name
                - Operators: eq, ne
                - Example: **{"role.name": "Manager"}**

        Custom Fields:
            custom: str
                - Format: "operator:fieldId:value"
                - Operators: eq, ne, gt, gte, lt, lte
                - Example: custom="eq:11:Technology"

        NOT Searchable (400 errors):
            - userPhone: Field not supported for filtering
            - userAddress: Field not supported for filtering
            - userCellPhone: Field not supported for filtering

        Example:
            >>> # Simple equality
            >>> active_users = await upsales.users.search(active=1)
            >>>
            >>> # With operators
            >>> recent_admins = await upsales.users.search(
            ...     active=1,
            ...     administrator=1,
            ...     regDate="gte:2024-01-01"
            ... )
            >>>
            >>> # Nested fields (use dict unpacking)
            >>> users_by_role = await upsales.users.search(
            ...     active=1,
            ...     **{"role.id": "eq:1,2,3"}
            ... )
            >>>
            >>> # Custom fields
            >>> senior_users = await upsales.users.search(
            ...     active=1,
            ...     custom="eq:11:Senior"
            ... )
        """
        return await self.list_all(**filters)
```

**Note on TypedDict**: With operators, values can be `int`, `str` with operator syntax (`"gt:100"`), or comma-separated (`"eq:1,2,3"`). TypedDict is less useful for type checking, but documentation becomes critical.

**Implementation Plan**:

```python
# upsales/cli.py

@app.command()
async def discover_searchable(
    resource: str = typer.Argument(..., help="Resource to test (e.g., 'users', 'accounts')"),
    output: Optional[str] = typer.Option(None, help="Output JSON file path"),
    all: bool = typer.Option(False, "--all", help="Test all major resources"),
    check_consistency: bool = typer.Option(False, help="Check for nested field inconsistencies"),
    sample_size: int = typer.Option(10, help="Number of items to fetch for testing"),
    verbose: bool = typer.Option(False, "-v", help="Show detailed progress"),
):
    """
    Discover which fields are searchable for a resource.

    Tests all fields (including nested) by making API requests with
    filter parameters and checking for errors.

    Examples:
        uv run upsales discover-searchable users
        uv run upsales discover-searchable accounts --output results.json
        uv run upsales discover-searchable --all --check-consistency
    """
    async with Upsales.from_env() as client:
        discoverer = SearchableFieldDiscoverer(client, verbose=verbose)

        if all:
            resources = ["users", "accounts", "products", "contacts", "orders", "activities"]
            results = {}
            for res in resources:
                typer.echo(f"\n🔍 Testing {res}...")
                results[res] = await discoverer.discover(res, sample_size)

            if check_consistency:
                typer.echo("\n📊 Checking for inconsistencies...")
                consistency_report = discoverer.check_consistency(results)
                typer.echo(json.dumps(consistency_report, indent=2))
        else:
            result = await discoverer.discover(resource, sample_size)

            if output:
                with open(output, "w") as f:
                    json.dump(result, f, indent=2)
                typer.echo(f"✅ Results saved to {output}")
            else:
                typer.echo(json.dumps(result, indent=2))


class SearchableFieldDiscoverer:
    """Discovers searchable fields by testing API."""

    def __init__(self, client: Upsales, verbose: bool = False):
        self.client = client
        self.verbose = verbose

    async def discover(self, resource: str, sample_size: int) -> dict:
        """Discover searchable fields for a resource."""
        # 1. Fetch sample data
        # 2. Extract all fields (recursive)
        # 3. Test each field individually
        # 4. Categorize: searchable, non-searchable, uncertain
        # 5. Return structured results
        pass

    def extract_all_fields(self, data: list[dict], prefix: str = "") -> list[tuple[str, str, Any]]:
        """
        Recursively extract all fields including nested.

        Returns: [(field_path, field_type, sample_value), ...]
        Example: [("name", "str", "John"), ("role.id", "int", 5), ...]
        """
        pass

    async def test_field(self, resource: str, field: str, value: Any) -> dict:
        """
        Test if a field is searchable.

        Returns: {
            "field": field,
            "searchable": True/False/None,
            "matches": int or None,
            "error": str or None
        }
        """
        pass

    def check_consistency(self, all_results: dict[str, dict]) -> dict:
        """
        Check for inconsistencies in nested field searchability.

        Example: user.name searchable in /accounts but not /orders
        """
        pass
```

**Benefits**:

- ✅ **Automated discovery** - No manual testing needed
- ✅ **Accurate SearchFilters** - Based on actual API behavior
- ✅ **Detects inconsistencies** - Find API quirks and edge cases
- ✅ **Generates code** - Auto-create TypedDict definitions
- ✅ **Saves time** - Test 50+ fields in minutes vs hours manually
- ✅ **Keeps docs updated** - Re-run when API changes

**Testing Strategy**:

1. Test with actual Upsales sandbox environment
2. **Handle rate limits intelligently**:
   - Read `X-RateLimit-Remaining` header after each test
   - When remaining < 20, wait for `X-RateLimit-Reset` seconds
   - Show progress: "Testing field 15/45... (175 requests remaining)"
   - Save progress to allow resuming if rate limited
3. Try multiple value types (int, str, bool, None)
4. Test different query param formats (camelCase vs snake_case, dot notation)
5. Document API error messages for better categorization
6. **Optimize testing order**:
   - Test most common fields first (active, name, email)
   - Batch similar field types together
   - Skip operator tests for fields where equality fails

**Edge Cases to Handle**:

- **Empty results**: Field might be searchable but no matches with test value
- **Rate limiting**: Add exponential backoff (200 req/10 sec), save progress between batches
- **Multiple formats**: Test `userId` vs `user_id` vs `user.id` for nested fields
- **Partial matches**: Some string fields might do partial vs exact match (test both)
- **Case sensitivity**: Test "John" vs "john" vs "JOHN"
- **Array fields**: Test filtering on array elements (e.g., `custom.fieldId=11`, `users.id=5`)
- **Operator support by field type**:
  - Binary flags (0/1): Only `eq`, `ne`, `in` (NO `gt`, `gte`, `lt`, `lte`)
  - Dates: All operators (use `gte`/`lte` for ranges)
  - Strings: Usually `eq`, `ne` (sometimes `gt`/`lt` for alphabetical?)
  - Numbers: All operators
- **Multiple values**: Test `"eq:1,2,3"` format for IN queries
- **Custom fields**: Test `custom="eq:fieldId:value"` format
- **Nested depth**: Test 2+ levels deep (e.g., `company.parent.id`)
- **Query param escaping**: Test special characters in values (spaces, quotes, etc.)

**Implementation Priorities**:

1. **Phase 1**: Basic field discovery (no operators) - ~4 hours
   - Test which top-level fields are searchable
   - Output JSON report
   - Generate basic documentation

2. **Phase 2**: Operator testing - ~2 hours
   - Test all comparison operators per field
   - Categorize by field type (binary, date, string, number)
   - Update output format

3. **Phase 3**: Nested field discovery - ~4 hours
   - Recursively extract nested fields
   - Test different query param formats
   - Track which format works

4. **Phase 4**: Consistency checking - ~2 hours
   - Compare nested fields across resources
   - Detect operator inconsistencies
   - Generate comprehensive report

5. **Phase 5**: Code generation - ~2 hours
   - Auto-generate search() docstrings
   - Output field documentation
   - Optionally generate TypedDict (if useful)

**Total Effort**: ~14 hours for full implementation

**Quick Win**: Phase 1 (4 hours) provides immediate value

**Dependencies**:
- ⚠️ **Recommended**: Implement Task #2 (Enhanced Rate Limit Handling) first
  - Provides rate limit header reading
  - Enables smart throttling during discovery
  - Or: Implement rate limit tracking directly in discovery tool

**Estimated API Requests**:

Testing single resource with full operator testing:
- Fetch sample: 1 request
- Top-level fields: ~30 fields × 7 operators = ~210 requests
- Nested fields: ~10 fields × 7 operators = ~70 requests
- **Total**: ~280 requests per resource

**Rate limit management crucial**: 280 requests = 1.4× the 10-second limit!

**Mitigation**:
1. Read headers and wait when needed (auto-pause at 180 requests)
2. Test operators only for relevant field types (binary flags don't need gt/lt)
3. Stop testing operators if equality fails
4. Add `--skip-operators` flag for quick discovery

**Status**: Design complete, ready for implementation (implement Task #2 first recommended)

---

### 15. CLI Tool Enhancements (General)

**Current State**: Basic commands (`generate-model`, `validate`, `init-resource`)
**Priority**: 🟢 Low
**Effort**: Variable

**Proposed Additions**:
- `upsales test-connection` - Verify API credentials
- `upsales list-endpoints` - Show available API endpoints
- `upsales inspect {resource} {id}` - View resource details from CLI
- `upsales export {resource}` - Export to JSON/CSV
- `upsales import {resource} {file}` - Bulk import from file
- `upsales count {resource}` - Quick count of resources

---

## Code Quality

### 15. Increase Test Coverage

**Current State**: Basic unit tests exist
**Priority**: 🟡 Medium
**Effort**: Ongoing

**Target Coverage**:
- Unit tests: 90%+
- Integration tests: Key workflows covered
- VCR.py cassettes for API interaction tests

**Focus Areas**:
- Edge cases (empty responses, rate limits, errors)
- All CRUD operations
- Bulk operations with exception handling
- Pydantic validation edge cases

---

### 16. Fix Remaining Mypy/Ruff Errors

**Current State**: 23 mypy errors, 87 ruff warnings
**Priority**: 🟡 Medium
**Effort**: Medium (~4 hours)

**Known Issues**:
- TypedDict edit() signatures (by design, but could add `# type: ignore`)
- CamelCase field names from API (could suppress with noqa)
- List iteration type inference in bulk operations

**See**: Recent linting session resolved majority of issues

---

### 17. Standardize Docstring Examples

**Current State**: 90%+ coverage, but examples vary in style
**Priority**: 🟢 Low
**Effort**: Small (~2 hours)

**Proposed Standard**:
```python
def method(self, arg: str) -> Result:
    """
    One-line summary.

    Detailed description paragraph explaining behavior,
    edge cases, and important considerations.

    Args:
        arg: Description of argument.

    Returns:
        Description of return value.

    Raises:
        ErrorType: When this error occurs.

    Example:
        >>> # Step 1: Setup
        >>> obj = await client.resource.get(123)
        >>>
        >>> # Step 2: Perform action
        >>> result = await obj.method("value")
        >>>
        >>> # Step 3: Verify
        >>> assert result.field == "expected"

    Note:
        Additional considerations, performance notes,
        or Python 3.13 free-threaded mode benefits.
    """
```

---

## Documentation

### 18. Add Quickstart Guide

**Current State**: README exists, but no dedicated quickstart
**Priority**: 🟡 Medium
**Effort**: Small (~2 hours)

**Proposed Content**:
1. Installation
2. First API call in 5 minutes
3. Common patterns (CRUD, bulk, search)
4. Error handling basics
5. Next steps (link to full docs)

**Location**: `docs/quickstart.md`

---

### 19. Add Architecture Decision Records (ADRs)

**Current State**: Decisions documented in CLAUDE.md and design docs
**Priority**: 🟢 Low
**Effort**: Small (~1 hour per ADR)

**Proposed ADRs**:
- ADR-001: Why `Upsales` not `UpsalesClient`
- ADR-002: Why `Company` not `Account`
- ADR-003: Why no caching layer
- ADR-004: Why `edit()` over `update()` for instances
- ADR-005: Why Python 3.13+ only
- ADR-006: TypedDict + Unpack for IDE autocomplete

**Location**: `docs/adr/`

---

### 20. Add Recipes/Cookbook

**Current State**: Examples scattered in docstrings
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Proposed Recipes**:
- Bulk import users from CSV
- Sync companies with external system
- Generate reports with async aggregation
- Handle rate limits gracefully
- Implement retry logic for transient failures
- Use free-threaded mode for maximum performance

**Location**: `docs/recipes/`

---

## Testing

### 21. Add Performance Benchmarks

**Current State**: No benchmarks
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Proposed Benchmarks**:
- Sequential vs parallel pagination (`list_all()`)
- Bulk operations scaling (10, 100, 1000 items)
- Free-threaded mode vs standard mode
- HTTP connection pooling impact
- Serialization performance (Pydantic v2 Rust core)

**Tool**: pytest-benchmark or custom async benchmark harness

**Location**: `tests/benchmarks/`

---

### 22. Add Integration Test Suite

**Current State**: Basic VCR.py tests exist
**Priority**: 🟡 Medium
**Effort**: Medium (~6 hours)

**Proposed Tests**:
- Full CRUD workflows for each resource
- Bulk operations end-to-end
- Error handling (401, 403, 404, 429, 500)
- Token refresh flow (for sandbox environments)
- Relationship traversal
- Complex filters and search

**Location**: `tests/integration/`

---

### 23. Add Sandbox Environment Test Runner

**Current State**: Manual testing with .env
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Proposed Feature**:

Script to run full test suite against Upsales sandbox environment:

```bash
# Run full integration tests against sandbox
uv run pytest tests/integration/ --sandbox

# Record new VCR cassettes
uv run pytest tests/integration/ --record-mode=all

# Run specific workflow test
uv run pytest tests/integration/test_user_workflow.py -v
```

**Benefits**:
- Catch API changes early
- Validate against real API
- Build confidence in SDK reliability

---

## Future Considerations

### 24. Async Iterator Support (Optional)

**Current State**: Returns full lists
**Priority**: 🟢 Low
**Effort**: Medium (~4 hours)

**Description**:

Discord.py uses async iterators for large collections:

```python
async for user in client.users.iter_all(batch_size=100):
    # Process one user at a time
    print(user.name)
```

**Pros**:
- Memory efficient for large datasets
- Can process items as they arrive
- Natural Python idiom

**Cons**:
- More complex API
- Requires understanding of async iteration
- Less common in REST API wrappers

**Recommendation**: Consider if users request it, but current `list_all()` is simpler

---

### 25. Webhook/Webhook Event Handling

**Current State**: Not applicable (Upsales doesn't have webhooks?)
**Priority**: ❓ Unknown - Need to research
**Effort**: Unknown

**Description**:

If Upsales API supports webhooks, add webhook handling:

```python
from upsales.webhooks import WebhookHandler

handler = WebhookHandler(secret_key="...")

@handler.on("user.created")
async def handle_user_created(event):
    print(f"New user: {event.data.name}")

# Use with web framework (FastAPI, etc.)
app.post("/webhooks")(handler.handle_request)
```

**Blocker**: Need to verify if Upsales API supports webhooks

---

## Completed Improvements

### ✅ 1. Implemented `create()` Method

**Completed**: 2025-01
**Priority**: 🔴 CRITICAL
**Location**: `upsales/resources/base.py:111`

**Description**: Added core CRUD operation for creating new resources. All writable resources (users, companies, products, campaigns, etc.) now support creation via `await upsales.{resource}.create(**data)`.

**Implementation**:
```python
async def create(self, **data: Any) -> T:
    """Create a new resource."""
    response = await self._http.post(self._endpoint, **data)
    return self._model_class(**response["data"], _client=self._http._upsales_client)
```

**Impact**: Core CRUD operation completed, SDK fully functional for all basic operations

---

### ✅ 2. Implemented `search()` Method with Comparison Operators

**Completed**: 2025-01
**Priority**: 🟡 Medium
**Location**: `upsales/resources/base.py:332`

**Description**: Added standardized search pattern supporting Upsales API comparison operators (eq, ne, gt, gte, lt, lte, IN) for all resources.

**Implementation**:
```python
async def search(self, **filters: Any) -> list[T]:
    """
    Search with comparison operators.

    Supports:
    - field=value (equals)
    - field="gt:value", "gte:value", "lt:value", "lte:value", "ne:value"
    - field="eq:1,2,3" (multiple values / IN)
    - custom="eq:fieldId:value" (custom fields)
    """
    return await self.list_all(**filters)
```

**Impact**: Powerful filtering capabilities across all resources, better than manual filtering

---

### ✅ 3. Fixed Import to TYPE_CHECKING Block

**Completed**: 2025-01-02
**Impact**: Resolved circular import issues in base.py

---

### ✅ 4. Renamed ID Parameters to Avoid Shadowing

**Completed**: 2025-01-02
**Impact**: Fixed 8 linting errors, improved code clarity

---

### ✅ 5. Fixed @computed_field Decorator Order

**Completed**: 2025-01-02
**Impact**: Fixed mypy prop-decorator errors in all models

---

### ✅ 6. Added Type Annotations Throughout

**Completed**: 2025-01-02
**Impact**: Reduced mypy errors from 51 to 23, improved type safety

---

## Contributing

To add new improvement ideas:

1. Choose appropriate section (Performance, Features, DX, etc.)
2. Use the template:
   ```markdown
   ### X. Improvement Title

   **Current State**: Brief description
   **Priority**: 🔴 Critical / 🟡 Medium / 🟢 Low
   **Effort**: Small/Medium/Large (with time estimate)

   **Description**: What needs to be done

   **Proposed Solution**: How to do it (with code examples)

   **Benefits**: Why it matters

   **Status**: Current state
   ```
3. Link to relevant docs/issues
4. Update when started/completed

---

**Document Status**: Active
**Last Updated**: 2025-11-06
**Maintainer**: Project Team
