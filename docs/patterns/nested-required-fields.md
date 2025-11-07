# Nested Required Fields Pattern

**Date**: 2025-11-06
**Applies To**: Orders, and potentially other endpoints with required relationships

---

## The Problem

When creating resources through the API, you often need to specify relationships to other entities (users, companies, products, stages, etc.). The API requires a **different structure for creation vs. what it returns in responses**.

### GET Response (Full Nested Objects)
```json
{
  "data": {
    "id": 1,
    "description": "Enterprise Deal",
    "user": {
      "id": 10,
      "name": "John Doe",
      "email": "john@example.com",
      "active": 1,
      "administrator": 0
    },
    "client": {
      "id": 123,
      "name": "ACME Corp",
      "phone": "+1-555-0123"
    },
    "stage": {
      "id": 3,
      "name": "Qualified",
      "probability": 50
    }
  }
}
```

### POST Request (Minimal Nested Structure)
```json
{
  "description": "Enterprise Deal",
  "date": "2025-01-15",
  "user": {"id": 10},         // Just ID!
  "client": {"id": 123},       // Just ID!
  "stage": {"id": 3},          // Just ID!
  "orderRow": [
    {"product": {"id": 5}}     // Nested just ID!
  ]
}
```

**Key Difference**: For creation, the API expects minimal nested objects with **just the `id` field**, NOT full nested objects.

---

## Verified Example: Orders

### Required Fields for Order Creation

Through manual testing, the following fields were **verified as required** for creating an Order:

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `orderRow` | `list[dict]` | `[{"product": {"id": int}}]` | `[{"product": {"id": 5}}]` |
| `date` | `str` | `"YYYY-MM-DD"` | `"2025-01-15"` |
| `user` | `dict` | `{"id": int}` | `{"id": 10}` |
| `stage` | `dict` | `{"id": int}` | `{"id": 3}` |
| `client` | `dict` | `{"id": int}` | `{"id": 123}` |

### Important Notes

1. **Not just "user is required"** - It's specifically `user.id` that's required
2. **Minimal nested structure** - `{"id": 10}` NOT the full `PartialUser` object
3. **Array with nested ID** - `orderRow` requires `[{"product": {"id": 5}}]` structure
4. **Date format strict** - Must be `YYYY-MM-DD` format

---

## Implementation Pattern

### 1. TypedDict for Creation

Create a separate TypedDict for creation that shows the minimal structure:

```python
class OrderCreateFields(TypedDict, total=False):
    """
    Required and optional fields for creating a new Order.

    REQUIRED fields (must be provided):
    - orderRow: List with at least one row containing product.id
    - date: Order date in 'YYYY-MM-DD' format
    - user: Dict with user.id (order owner)
    - stage: Dict with stage.id (pipeline stage)
    - client: Dict with client.id (company/account)

    IMPORTANT: Nested fields require minimal structure with just IDs.
    Example nested user: {"id": 10} NOT the full PartialUser object.
    """

    # REQUIRED fields for creation
    orderRow: list[dict[str, Any]]  # Required: [{"product": {"id": product_id}}]
    date: str  # Required: 'YYYY-MM-DD'
    user: dict[str, int]  # Required: {"id": user_id}
    stage: dict[str, int]  # Required: {"id": stage_id}
    client: dict[str, int]  # Required: {"id": client_id}

    # Optional fields
    description: str
    probability: int
    value: int
    # ... etc
```

### 2. Model Docstring Documentation

Document the creation requirements prominently in the model docstring:

```python
class Order(BaseModel):
    """
    Order model from /api/v2/orders.

    CREATING ORDERS:
        Use OrderCreateFields TypedDict for required field reference.
        Required fields use MINIMAL nested structure with just IDs:
        - orderRow: [{"product": {"id": product_id}}]
        - date: "YYYY-MM-DD"
        - user: {"id": user_id}
        - stage: {"id": stage_id}
        - client: {"id": client_id}

    Example Create:
        >>> new_order = await upsales.orders.create(
        ...     orderRow=[{"product": {"id": 5}}],
        ...     date="2025-01-15",
        ...     user={"id": 10},
        ...     stage={"id": 3},
        ...     client={"id": 123},
        ...     description="New Enterprise Deal",  # Optional
        ... )
    """
    # Model fields use full nested objects for responses
    user: PartialUser = Field(description="Order owner")
    client: PartialCompany = Field(description="Associated company")
    stage: PartialOrderStage | None = Field(default=None, description="Pipeline stage")
```

### 3. Resource Manager Examples

Add clear examples in the resource manager docstrings:

```python
class OrdersResource(BaseResource[Order, PartialOrder]):
    """
    Resource manager for Order endpoint.

    Example Create (with minimal nested structure):
        >>> new_order = await upsales.orders.create(
        ...     orderRow=[{"product": {"id": 5}}],
        ...     date="2025-01-15",
        ...     user={"id": 10},
        ...     stage={"id": 3},
        ...     client={"id": 123},
        ...     description="New Enterprise Deal",
        ...     probability=50,
        ...     value=100000,
        ... )
        >>> new_order.id
        456
        >>> new_order.user.name  # API returns full nested object
        'John Doe'
    """
```

---

## Testing Strategy

### 1. Manual Testing to Discover Requirements

Test with minimal fields to discover what's truly required:

```python
# Start with absolutely minimal
minimal_order = {
    "orderRow": [{"product": {"id": 5}}],
    "date": "2025-01-15",
}
# Try creating -> will fail with validation error
# Error tells you what's missing

# Add next field
minimal_order["user"] = {"id": 10}
# Try again -> still fails

# Continue until successful
minimal_order["stage"] = {"id": 3}
minimal_order["client"] = {"id": 123}
# Success! Now you know the exact requirements
```

### 2. Document Findings in TypedDict

Once requirements are discovered, document them:

```python
class OrderCreateFields(TypedDict, total=False):
    """
    REQUIRED fields (manually verified 2025-11-06):
    - orderRow: [{"product": {"id": product_id}}]
    - date: "YYYY-MM-DD"
    - user: {"id": user_id}
    - stage: {"id": stage_id}
    - client: {"id": client_id}
    """
```

### 3. Integration Tests

Create VCR-based integration test for creation:

```python
@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_create_order_minimal.yaml")
async def test_create_order_with_minimal_required_fields():
    """
    Test creating order with only required fields.

    Validates the minimal nested structure requirement.
    """
    async with Upsales.from_env() as upsales:
        new_order = await upsales.orders.create(
            orderRow=[{"product": {"id": 5}}],
            date="2025-01-15",
            user={"id": 10},
            stage={"id": 3},
            client={"id": 123},
        )

        # Verify creation succeeded
        assert isinstance(new_order, Order)
        assert new_order.id > 0

        # Verify API returns full nested objects
        assert isinstance(new_order.user, PartialUser)
        assert new_order.user.id == 10
        assert isinstance(new_order.user.name, str)

        assert isinstance(new_order.client, PartialCompany)
        assert new_order.client.id == 123

        print(f"✅ Created order {new_order.id} with minimal fields")
```

---

## Common Pitfalls

### ❌ Wrong: Using Full Nested Object

```python
# This will likely fail or cause unexpected behavior
user = await upsales.users.get(10)
new_order = await upsales.orders.create(
    user=user,  # ❌ Full PartialUser object
    # ...
)
```

### ✅ Correct: Using Minimal Structure

```python
# Use just the ID
new_order = await upsales.orders.create(
    user={"id": 10},  # ✅ Minimal structure
    # ...
)
```

### ❌ Wrong: Assuming Field Optional Because It Has Default

```python
# Model shows: user: PartialUser = Field(...)
# But this doesn't mean it's optional for creation!
new_order = await upsales.orders.create(
    date="2025-01-15",
    # user missing -> will fail!
)
```

### ✅ Correct: Verify Requirements Through Testing

```python
# Always test with minimal fields to discover true requirements
# Document findings in TypedDict with "total=False"
# Mark required fields with comments
```

### ❌ Wrong: Not Documenting Date Format

```python
date: str  # ❌ What format?
```

### ✅ Correct: Explicit Format Documentation

```python
date: str  # Required: 'YYYY-MM-DD' format
```

---

## When to Apply This Pattern

### Indicators That an Endpoint Uses This Pattern

1. **Has relationships** - References to users, companies, products, etc.
2. **Complex object structure** - Not just flat primitives
3. **Required relationships** - Can't create without linking to other entities
4. **Array fields with objects** - Like `orderRow` with products

### Endpoints Likely to Use This Pattern

- ✅ **Orders** - Verified (requires user, client, stage, orderRow)
- ⚠️ **Activities** - Likely (has user, client, contact relationships)
- ⚠️ **Appointments** - Likely (has user, client, contact relationships)
- ⚠️ **Contacts** - Maybe (has client relationship)
- ⚠️ **Projects** - Maybe (has relationships)

### Endpoints Unlikely to Use This Pattern

- ✅ **Users** - No required relationships (flat structure)
- ✅ **Products** - Optional category relationship only
- ✅ **Companies** - No required relationships
- ✅ **Order Stages** - Simple configuration (no relationships)

---

## Verification Checklist

When adding a new endpoint with relationships:

- [ ] Test CREATE with minimal fields to discover requirements
- [ ] Document exact required structure in `{Model}CreateFields` TypedDict
- [ ] Test nested fields specifically (not just "user required" but "user.id required")
- [ ] Document date/time format requirements
- [ ] Add integration test for creation with minimal fields
- [ ] Add integration test for creation with optional fields
- [ ] Document in model docstring with clear examples
- [ ] Add examples to resource manager docstring
- [ ] Update endpoint map with verified CREATE status
- [ ] Record VCR cassette for creation tests

---

## Example Implementation: Orders

### Complete Example

```python
from typing import Any, TypedDict
from upsales import Upsales

# TypedDict provides IDE autocomplete and documents requirements
class OrderCreateFields(TypedDict, total=False):
    # Required (verified through testing)
    orderRow: list[dict[str, Any]]
    date: str
    user: dict[str, int]
    stage: dict[str, int]
    client: dict[str, int]

    # Optional
    description: str
    probability: int
    value: int

async def create_order_example():
    """Complete example of creating an order."""
    async with Upsales.from_env() as upsales:
        # Create with minimal required fields
        new_order = await upsales.orders.create(
            orderRow=[{"product": {"id": 5}}],  # Product ID only
            date="2025-01-15",                   # YYYY-MM-DD
            user={"id": 10},                     # User ID only
            stage={"id": 3},                     # Stage ID only
            client={"id": 123},                  # Client ID only
        )

        print(f"Created order {new_order.id}")
        print(f"Owner: {new_order.user.name}")  # API returns full object

        # Create with optional fields
        detailed_order = await upsales.orders.create(
            orderRow=[
                {"product": {"id": 5}},
                {"product": {"id": 7}},
            ],
            date="2025-01-15",
            user={"id": 10},
            stage={"id": 3},
            client={"id": 123},
            description="Enterprise Software Deal",
            probability=75,
            value=250000,
            monthlyValue=5000,
            closeDate="2025-06-30",
        )

        print(f"Created detailed order {detailed_order.id}")
        print(f"Expected value: ${detailed_order.expected_value}")
```

---

## Summary

### Key Takeaways

1. **Different structures for CREATE vs GET** - API returns full nested objects but requires minimal structures with just IDs for creation
2. **Test to discover requirements** - Don't assume, test with minimal fields and document findings
3. **Specific nested field requirements** - It's not just "user required", it's "user.id required"
4. **TypedDict for documentation** - Use `{Model}CreateFields` to document the minimal structure
5. **Integration tests critical** - Verify creation works with real API using VCR

### Pattern Application

- ✅ Create separate `{Model}CreateFields` TypedDict
- ✅ Document minimal nested structure (e.g., `{"id": 10}`)
- ✅ Test with minimal fields to verify requirements
- ✅ Document date/time formats explicitly
- ✅ Add integration tests with VCR
- ✅ Update endpoint map with verification status

---

**Last Updated**: 2025-11-06
**Verified For**: Orders endpoint
**Pattern Status**: Production-ready, apply to other endpoints as needed
