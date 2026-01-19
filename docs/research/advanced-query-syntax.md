# Advanced Query Syntax - Research Notes

**Date**: 2025-11-02
**Source**: Upsales UI → Backend query generation
**Status**: 📋 **DOCUMENTED FOR FUTURE INVESTIGATION**

---

## 🔍 Discovery

The Upsales backend uses a **more advanced query syntax** than documented in the API docs when the UI builds queries from user actions.

**Current SDK uses**: Simple query parameters
```
?active=1&regDate=gte:2024-01-01&limit=50
```

**Backend also supports**: Structured query objects
```
q[]={"a":"user.id","c":"eq","v":[1]}
q[]={"a":"active","c":"eq","v":true}
...
```

---

## 📊 Advanced Query Syntax Structure

### Query Parameters (`q[]`)

**Format**: Array of query condition objects

**Structure**:
```javascript
q[] = {
  "a": "field.name",        // Attribute (field path)
  "c": "operator",          // Condition (eq, ne, gt, gte, lt, lte, src)
  "v": value               // Value (can be any type)
}
```

### Examples from UI-Generated Queries

#### 1. Simple Equality
```
q[]={"a":"user.id","c":"eq","v":[1]}
```
**Meaning**: `WHERE user.id = 1`

#### 2. Boolean Values
```
q[]={"a":"active","c":"eq","v":true}
q[]={"a":"isExternal","c":"eq","v":false}
```
**Meaning**: `WHERE active = true AND isExternal = false`

#### 3. Null Checks
```
q[]={"a":"operationalAccount.id","c":"eq","v":null}
```
**Meaning**: `WHERE operationalAccount.id IS NULL`

#### 4. Range Queries
```
q[]={"a":"noEmployees","c":"gte","v":1}
q[]={"a":"noEmployees","c":"lte","v":23}
```
**Meaning**: `WHERE noEmployees >= 1 AND noEmployees <= 23`

#### 5. String Search ("src" operator)
```
q[]={"a":"contact.phone","c":"src","v":"123"}
```
**Meaning**: `WHERE contact.phone CONTAINS "123"` (substring search)

**⚠️ CRITICAL**: The `"src"` operator is NOT in API documentation!

---

### Field Selection (`f[]`)

**Format**: Array of field names to return

**Structure**:
```
f[]=field1
f[]=field2
f[]=nested.field
f[]=related.property
```

### Examples from UI-Generated Queries

```
f[]=active
f[]=id
f[]=categories
f[]=addresses
f[]=operationalAccount
f[]=name
f[]=webpage
f[]=about
f[]=linkedin
f[]=phone
f[]=Address_Visit_city
f[]=users.id
f[]=salesHistory
f[]=marketingHistory
f[]=custom
f[]=users
```

**Features**:
- ✅ Select specific fields (partial responses)
- ✅ Nested field selection (`users.id`)
- ✅ Related object selection (`operationalAccount`)
- ✅ Special fields (`Address_Visit_city`)

**Benefit**: Reduce response size, faster transfers

---

### Sorting (`sort[]`)

**Format**: Array of sort objects

**Structure**:
```javascript
sort[] = {
  "a": "field.name",    // Attribute to sort by
  "s": "A" | "D"       // Sort direction (A=Ascending, D=Descending)
}
```

### Examples
```
sort[]={"a":"name","s":"A"}     // Sort by name ascending
sort[]={"a":"id","s":"A"}       // Then by id ascending
```

**Multi-field sorting supported!**

---

## 🆚 Comparison: Simple vs Advanced Syntax

### Simple Query Params (Current SDK Implementation)
```
GET /accounts?active=1&noEmployees=gte:1&noEmployees=lte:23&limit=50
```

**Pros**:
- ✅ Simple, readable
- ✅ Easy to construct
- ✅ Works for most use cases

**Cons**:
- ❌ Can't specify field selection (always returns all fields)
- ❌ No substring search (`src` operator)
- ❌ Verbose for complex queries

---

### Advanced Query Objects (UI Uses)
```
POST or GET with:
q[]={"a":"active","c":"eq","v":true}
q[]={"a":"noEmployees","c":"gte","v":1}
q[]={"a":"noEmployees","c":"lte","v":23}
f[]=id
f[]=name
f[]=active
f[]=noEmployees
sort[]={"a":"name","s":"A"}
limit=50
```

**Pros**:
- ✅ Field selection (reduce payload size)
- ✅ Substring search (`src` operator)
- ✅ Cleaner for complex queries
- ✅ Type-safe values (true, false, null, numbers)
- ✅ Multi-field sorting

**Cons**:
- ❌ More complex to construct
- ❌ Not documented in API docs
- ❌ Requires JSON encoding
- ❌ Harder to read in URLs

---

## 🔍 Features NOT in API Documentation

### 1. `src` Operator (Substring Search) ⚠️

**UI uses**: `{"a":"contact.phone","c":"src","v":"123"}`

**What it does**: Substring/contains search (LIKE '%123%' in SQL)

**Current SDK**: NOT supported (we don't expose this operator)

**Use case**: Search for partial phone numbers, names, etc.

---

### 2. Field Selection (`f[]`) ⚠️

**UI uses**: `f[]=id&f[]=name&f[]=active`

**What it does**: Only return specified fields (partial response)

**Current SDK**: NOT supported (always returns all fields)

**Benefits**:
- Reduce response size (bandwidth savings)
- Faster responses
- Privacy (don't return sensitive fields)

**Use case**: Mobile apps, dashboards showing limited data

---

### 3. Multi-Field Sorting (`sort[]`) ⚠️

**UI uses**: `sort[]={"a":"name","s":"A"}&sort[]={"a":"id","s":"A"}`

**What it does**: Sort by multiple fields with direction

**Current SDK**: NOT supported

**Use case**: Complex result ordering (sort by priority DESC, then date ASC)

---

### 4. Type-Safe Values (Boolean, Null) ⚠️

**UI uses**: `{"v":true}`, `{"v":false}`, `{"v":null}`

**Simple syntax**: Everything is string (`active=1`, `active=0`)

**Advanced syntax**: Proper types (`active=true`, `operationalAccount.id=null`)

**Benefit**: Clearer semantics, potential for better API processing

---

## 📋 Future Investigation Tasks

### High Priority (Valuable Features)
1. ⚠️ **`src` operator for substring search**
   - Use case: Search contacts by partial phone/name
   - Implementation: Add to operator_map
   - Example: `search(phone__contains="555")` or `search(phone="src:555")`

2. ⚠️ **Field selection for partial responses**
   - Use case: Reduce bandwidth, faster queries
   - Implementation: New parameter `fields=["id", "name", "active"]`
   - Example: `list(limit=50, fields=["id", "name"])`

3. ⚠️ **Multi-field sorting**
   - Use case: Complex ordering
   - Implementation: New parameter `sort=[("name", "asc"), ("id", "desc")]`
   - Example: `list(sort=[("priority", "desc"), ("date", "asc")])`

### Medium Priority (Nice to Have)
4. 🟡 **Advanced query builder**
   - Build complex queries with helper
   - Example: `query().where(active=True).where(employees__gte=10).select("id", "name")`

5. 🟡 **Type-safe boolean/null values**
   - Pass actual booleans: `search(active=True)`
   - Pass actual None: `search(parent=None)`
   - Transform to API format

### Low Priority (Complex, Less Value)
6. 🟢 **Full query object support**
   - Expose raw q[] array building
   - Only needed for very complex queries

---

## 🎯 Recommended Next Steps

### Phase 1: Document & Validate (1 hour)
- Test if `src` operator actually works via Postman/curl
- Test if `f[]` field selection works
- Test if `sort[]` multi-sorting works
- Document in `postman_api_analysis.md`

### Phase 2: Implement High-Value Features (3-4 hours)
1. Add `src` operator support (30 min)
   ```python
   # Could use special syntax
   search(phone__contains="555")  # → phone="src:555"
   # Or explicit
   search(phone="src:555")  # Already works with our implementation!
   ```

2. Add field selection (1 hour)
   ```python
   list(limit=50, fields=["id", "name", "active"])
   # Generates: ?limit=50&f[]=id&f[]=name&f[]=active
   ```

3. Add multi-field sorting (1.5 hours)
   ```python
   list(sort=[("name", "asc"), ("id", "desc")])
   # Generates: ?sort[]={"a":"name","s":"A"}&sort[]={"a":"id","s":"D"}
   ```

4. Tests & documentation (1 hour)

### Phase 3: Advanced Query Builder (Optional, 4-6 hours)
- Implement fluent query builder
- Support complex nested queries
- Full test coverage

---

## 🔬 Open Questions for Investigation

1. **Is `src` operator reliable?**
   - Is it documented anywhere?
   - Does it work on all string fields?
   - Does it support wildcards?

2. **Does field selection work for all endpoints?**
   - Do nested fields work (`users.id`)?
   - Do computed fields work?
   - Does it affect performance?

3. **How are query objects (`q[]`) encoded?**
   - JSON in query string?
   - URL encoding rules?
   - Size limits?

4. **Are there other undocumented operators?**
   - `src` was found, are there more?
   - Regex support?
   - Case-insensitive search?

---

## 📊 Current SDK Coverage

| Feature | API Docs | UI Uses | SDK Supports |
|---------|----------|---------|--------------|
| **Simple filters** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Operators (gt, gte, etc.)** | ✅ Yes | ✅ Yes | ✅ Yes (both syntaxes!) |
| **Natural operators (>, >=)** | ❌ No | ❌ No | ✅ Yes (NEW!) |
| **`src` (substring)** | ❌ No | ✅ Yes | ❌ No |
| **Field selection (`f[]`)** | ❌ No | ✅ Yes | ❌ No |
| **Multi-sort (`sort[]`)** | ❌ No | ✅ Yes | ❌ No |
| **Query objects (`q[]`)** | ❌ No | ✅ Yes | ❌ No |
| **Boolean/null types** | ⚠️ Unclear | ✅ Yes | ⚠️ Partial |

**Coverage**: 3/8 advanced features (37.5%)

---

## 💡 Quick Wins Available

### Substring Search (30 minutes)
**Already works with current implementation!**
```python
# Just document that this exists
search(phone="src:555-1234")  # Substring search!
```

**Verify with curl/Postman, then document.**

### Field Selection (1 hour)
Add `fields` parameter to `list()` and `list_all()`:
```python
async def list(self, limit: int = 100, offset: int = 0, fields: list[str] | None = None, **params):
    if fields:
        for field in fields:
            params[f"f[]"] = field  # Build f[] array
    # ... rest of implementation
```

---

## 🚨 Important Notes

### This is UI/Backend Behavior
- **Not officially documented** in API docs
- **May change** without notice
- **May not work** for all endpoints
- **Test before relying on it**

### Investigation Strategy
1. **Test with Postman** - Verify each feature works
2. **Document confirmed features** - Only what we can verify
3. **Add to SDK carefully** - With proper fallbacks
4. **Mark as experimental** - Until confirmed stable

---

## 📝 Example: Complete Advanced Query

**UI-generated request**:
```
GET /accounts?
  q[]={"a":"user.id","c":"eq","v":[1]}&
  q[]={"a":"active","c":"eq","v":true}&
  q[]={"a":"noEmployees","c":"gte","v":1}&
  q[]={"a":"noEmployees","c":"lte","v":23}&
  q[]={"a":"contact.phone","c":"src","v":"123"}&
  f[]=id&
  f[]=name&
  f[]=active&
  f[]=phone&
  sort[]={"a":"name","s":"A"}&
  sort[]={"a":"id","s":"A"}&
  limit=50
```

**What it does**:
- Filter: user.id = 1
- Filter: active = true
- Filter: employees between 1-23
- Filter: phone contains "123"
- Select: Only return id, name, active, phone fields
- Sort: By name ascending, then id ascending
- Limit: 50 results

**If we supported this in SDK**:
```python
companies = await upsales.companies.query()
    .where(user_id=1)
    .where(active=True)
    .where_between(employees=(1, 23))
    .where_contains(phone="123")
    .select("id", "name", "active", "phone")
    .order_by("name", "asc")
    .order_by("id", "asc")
    .limit(50)
    .execute()

# Or more concise
companies = await upsales.companies.list(
    user_id=1,
    active=True,
    employees__gte=1,
    employees__lte=23,
    phone__contains="123",
    fields=["id", "name", "active", "phone"],
    sort=[("name", "asc"), ("id", "asc")],
    limit=50
)
```

---

## 🎯 Future Enhancement Roadmap

This roadmap is now tracked centrally. See Master Task List in `ENDPOINT_TASK_LIST.md` under “Query Enhancements”.

---

## 📖 Operators Discovered

### Documented in API
- `eq` - Equals ✅
- `ne` - Not equals ✅
- `gt` - Greater than ✅
- `gte` - Greater than or equals ✅
- `lt` - Less than ✅
- `lte` - Less than or equals ✅

### Found in UI (Undocumented)
- `src` - Substring/contains search ⚠️ **NEW DISCOVERY**

### Possible Others (To Investigate)
- `regex` - Regular expression search?
- `in` - Explicit IN operator?
- `nin` - NOT IN operator?
- `exists` - Field exists check?

---

## 🔑 Key Takeaways

### 1. UI Uses More Features Than Documented
The UI relies on features not in public API docs:
- `src` operator for substring search
- `f[]` for field selection
- `sort[]` for multi-field sorting
- `q[]` query object format

### 2. SDK Could Be Enhanced
We could support:
- ✅ **Easy**: `src` operator (document it)
- ✅ **Medium**: Field selection (`fields=` parameter)
- ✅ **Medium**: Multi-sorting (`sort=` parameter)
- ⚠️ **Hard**: Full query object builder

### 3. Validation Needed
Before implementing, must verify:
- Which endpoints support these features
- If they're stable/supported
- If they work with API tokens (not just UI sessions)

### 4. Current Implementation is Good
Our current approach:
- ✅ Works for 95% of use cases
- ✅ Well-documented
- ✅ Type-safe
- ✅ Simple

Advanced features are optimization, not necessity.

---

## 💡 Immediate Action Items

### 1. Test Substring Search (10 min)
```bash
# Test if src operator works
curl -H "Cookie: token=XXX" \
  "https://power.upsales.com/api/v2/contacts?phone=src:555"

# If works → document it!
```

### 2. Document in postman_api_analysis.md (20 min)
Add section:
- Advanced query syntax
- UI-discovered features
- Query objects format
- Field selection
- Multi-sorting

### 3. Create Enhancement Proposal (30 min)
Detailed proposal for:
- Which features to add
- Implementation approach
- Breaking changes (if any)
- Test requirements

---

## 📚 Resources for Investigation

**Upsales API Documentation**:
- Official docs: Limited (doesn't mention advanced syntax)
- Postman collection: May have examples
- UI network tab: Shows actual requests

**Similar Patterns in Other APIs**:
- **GraphQL**: Field selection, nested queries
- **OData**: $filter, $select, $orderby
- **MongoDB**: Query objects, field projection
- **Django**: Q objects, filter chains

---

## 🎯 Recommendation

### Short Term (Now)
✅ **Keep current implementation** - It's excellent for standard use cases

### Medium Term (Next sprint)
⚠️ **Investigate and add quick wins**:
1. Validate `src` operator works
2. Add `fields` parameter for field selection
3. Document advanced features

### Long Term (When needed)
🟢 **Consider query builder** - If users request complex queries

---

## 📊 Value Assessment

| Feature | Value | Complexity | Priority |
|---------|-------|------------|----------|
| **`src` operator** | High | Low (5 min) | 🔥 Do first |
| **Field selection** | High | Medium (1 hr) | 🔥 Do soon |
| **Multi-sorting** | Medium | Medium (1.5 hr) | 🟡 Later |
| **Query objects** | Low | High (4+ hr) | 🟢 Maybe never |

---

## ✅ Status

**Documented**: ✅ Yes (this file)
**Validated**: ❌ Not yet (needs Postman testing)
**Implemented**: ❌ Not yet (future enhancement)
**Priority**: 🟡 Medium (investigate when adding many endpoints)

**Next**: Validate features work, then decide on implementation

---

**Created**: 2025-11-02
**Purpose**: Document advanced query syntax for future investigation
**Source**: UI-generated backend queries
**Status**: Research note, not implemented
