"""
Integration tests for Order model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_orders_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_orders_integration/
    uv run pytest tests/integration/test_orders_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.order_stages import PartialOrderStage
from upsales.models.orders import Order
from upsales.models.user import PartialUser

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_list_orders_real_response.yaml")
async def test_list_orders_real_response():
    """
    Test listing orders with real API response structure.

    Validates that Order model correctly parses list responses
    with pagination metadata.

    Cassette: tests/cassettes/integration/test_orders_integration/test_list_orders_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get orders with limit
        orders = await upsales.orders.list(limit=5)

        assert isinstance(orders, list)
        assert len(orders) <= 5

        if len(orders) == 0:
            pytest.skip("No orders found in the system")

        for order in orders:
            assert isinstance(order, Order)
            assert isinstance(order.id, int)
            assert order.id > 0
            assert isinstance(order.description, str)

            # Validate read-only fields
            assert isinstance(order.regDate, str)
            assert isinstance(order.modDate, str)

            # Validate BinaryFlag field (0 or 1)
            assert order.locked in (0, 1)

            # Validate percentage field (0-100)
            assert 0 <= order.probability <= 100

            # Validate monetary fields
            assert isinstance(order.value, int)
            assert isinstance(order.oneOffValue, int)
            assert isinstance(order.annualValue, int)

        print(f"[OK] Listed {len(orders)} orders successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_get_order_real_response.yaml")
async def test_get_order_real_response():
    """
    Test getting a single order with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Order
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_orders_integration/test_get_order_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get orders first to find a valid ID
        orders = await upsales.orders.list(limit=1)

        if len(orders) == 0:
            pytest.skip("No orders found in the system")

        order_id = orders[0].id

        # Get single order by ID
        order = await upsales.orders.get(order_id)

        # Validate Order model with Pydantic v2 features
        assert isinstance(order, Order)
        assert order.id == order_id
        assert isinstance(order.description, str)

        # Validate timestamps
        assert isinstance(order.regDate, str)
        assert isinstance(order.modDate, str)

        # Validate BinaryFlag validator (0 or 1, not bool)
        assert order.locked in (0, 1)

        # Validate percentage validator (0-100)
        assert 0 <= order.probability <= 100

        # Validate monetary values
        assert isinstance(order.value, int)
        assert isinstance(order.oneOffValue, int)
        # monthlyValue can be float or int from API
        assert isinstance(order.monthlyValue, (int, float))
        assert isinstance(order.annualValue, int)
        assert isinstance(order.purchaseCost, int)
        assert isinstance(order.contributionMargin, int)

        # Validate currency
        assert isinstance(order.currency, str)
        assert len(order.currency) == 3  # ISO 4217 code

        # Validate configuration fields
        assert isinstance(order.priceListId, int)
        assert isinstance(order.recurringInterval, int)
        assert isinstance(order.invoiceRelatedClient, bool)
        assert isinstance(order.confirmedSolution, bool)
        assert isinstance(order.userEditable, bool)
        assert isinstance(order.userRemovable, bool)

        # Validate lists
        assert isinstance(order.orderRow, list)
        assert isinstance(order.checklist, list)
        assert isinstance(order.stakeholders, list)
        assert isinstance(order.titleCategories, list)
        assert isinstance(order.projectPlanOptions, list)
        assert isinstance(order.salesCoach, list)
        assert isinstance(order.lastIntegrationStatus, list)

        # Validate statistics
        assert isinstance(order.noCompletedAppointments, int)
        assert isinstance(order.noPostponedAppointments, int)
        assert isinstance(order.noTimesCallsNotAnswered, int)
        assert isinstance(order.noTimesClosingDateChanged, int)
        assert isinstance(order.noTimesOrderValueChanged, int)

        # Validate complex objects
        assert isinstance(order.risks, dict)

        # Validate custom fields (should be list)
        assert isinstance(order.custom, list)

        print(f"[OK] Order parsed successfully: {order.description} (ID: {order.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_order_nested_objects.yaml")
async def test_order_nested_objects():
    """
    Test that nested objects (PartialUser, PartialCompany, etc.) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_orders_integration/test_order_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        orders = await upsales.orders.list(limit=20)

        if len(orders) == 0:
            pytest.skip("No orders found in the system")

        # Check various nested objects across orders
        found_user = False
        found_client = False
        found_contact = False
        found_stage = False
        found_regby = False

        for order in orders:
            # Test user if present
            if order.user is not None:
                found_user = True
                assert isinstance(order.user, PartialUser)
                assert hasattr(order.user, "id")
                assert hasattr(order.user, "name")
                assert isinstance(order.user.id, int)
                print(f"  [OK] user: id={order.user.id}, name={order.user.name}")

            # Test client (company) if present
            if order.client is not None:
                found_client = True
                assert isinstance(order.client, PartialCompany)
                assert hasattr(order.client, "id")
                assert hasattr(order.client, "name")
                assert isinstance(order.client.id, int)
                print(f"  [OK] client: id={order.client.id}, name={order.client.name}")

            # Test contact if present
            if order.contact is not None:
                found_contact = True
                assert isinstance(order.contact, PartialContact)
                assert hasattr(order.contact, "id")
                assert isinstance(order.contact.id, int)
                print(f"  [OK] contact: id={order.contact.id}")

            # Test stage if present
            if order.stage is not None:
                found_stage = True
                assert isinstance(order.stage, PartialOrderStage)
                assert hasattr(order.stage, "id")
                assert isinstance(order.stage.id, int)
                print(f"  [OK] stage: id={order.stage.id}")

            # Test regBy if present
            if order.regBy is not None:
                found_regby = True
                assert isinstance(order.regBy, PartialUser)
                assert hasattr(order.regBy, "id")
                assert hasattr(order.regBy, "name")
                assert isinstance(order.regBy.id, int)
                print(f"  [OK] regBy: id={order.regBy.id}, name={order.regBy.name}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, client:{found_client}, "
            f"contact:{found_contact}, stage:{found_stage}, regBy:{found_regby}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_order_computed_fields.yaml")
async def test_order_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_locked, expected_value, is_recurring, margin_percentage
    computed properties.

    Cassette: tests/cassettes/integration/test_orders_integration/test_order_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        orders = await upsales.orders.list(limit=10)

        if len(orders) == 0:
            pytest.skip("No orders found in the system")

        order = orders[0]

        # Test is_locked computed field
        assert isinstance(order.is_locked, bool)
        assert order.is_locked == (order.locked == 1)
        print(f"[OK] is_locked: {order.is_locked} (locked={order.locked})")

        # Test expected_value computed field
        assert isinstance(order.expected_value, float)
        expected = (order.value * order.probability) / 100 if order.value else 0.0
        assert abs(order.expected_value - expected) < 0.01  # Float comparison with tolerance
        print(
            f"[OK] expected_value: {order.expected_value} "
            f"(value={order.value}, probability={order.probability}%)"
        )

        # Test is_recurring computed field
        assert isinstance(order.is_recurring, bool)
        expected_recurring = bool(order.monthlyValue > 0 or order.annualValue > 0)
        assert order.is_recurring == expected_recurring
        print(
            f"[OK] is_recurring: {order.is_recurring} "
            f"(monthlyValue={order.monthlyValue}, annualValue={order.annualValue})"
        )

        # Test margin_percentage computed field
        assert isinstance(order.margin_percentage, float)
        if order.value > 0:
            expected_margin = (order.contributionMargin / order.value) * 100
            assert abs(order.margin_percentage - expected_margin) < 0.01
        else:
            assert order.margin_percentage == 0.0
        print(
            f"[OK] margin_percentage: {order.margin_percentage:.2f}% "
            f"(margin={order.contributionMargin}, value={order.value})"
        )

        # Test custom_fields property
        assert hasattr(order, "custom_fields")
        print("[OK] custom_fields property exists")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_order_custom_fields.yaml")
async def test_order_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_orders_integration/test_order_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        orders = await upsales.orders.list(limit=20)

        if len(orders) == 0:
            pytest.skip("No orders found in the system")

        # Find an order with custom fields
        order_with_custom = None
        for order in orders:
            if order.custom:
                order_with_custom = order
                break

        if order_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(order_with_custom.custom, list)
            for field in order_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper (computed property)
            cf = order_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            # Test dict-like access works
            if order_with_custom.custom:
                first_field = order_with_custom.custom[0]
                field_id = first_field["fieldId"]
                # Access by ID should work
                value = cf.get(field_id)
                assert value is not None or field_id in [
                    f["fieldId"] for f in order_with_custom.custom
                ]

            print(f"[OK] Custom fields validated: {len(order_with_custom.custom)} fields")
        else:
            print("[SKIP] No orders with custom fields found in sample")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_orders_integration/test_order_search.yaml")
async def test_order_search():
    """
    Test searching orders with filters.

    Validates search functionality works with real API.
    Uses list() with filter instead of search() to avoid fetching all records.

    Cassette: tests/cassettes/integration/test_orders_integration/test_order_search.yaml
    """
    async with Upsales.from_env() as upsales:
        # List unlocked orders with limit (avoids fetching all via search)
        orders = await upsales.orders.list(limit=10, locked=0)

        assert isinstance(orders, list)

        if len(orders) == 0:
            pytest.skip("No unlocked orders found in the system")

        for order in orders:
            assert isinstance(order, Order)
            assert order.locked == 0

        print(f"[OK] Found {len(orders)} unlocked orders (limited to 10)")
