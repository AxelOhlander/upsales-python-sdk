"""
Integration tests for Opportunities endpoint with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 Order models correctly parse real API data
from the /opportunities endpoint.

Opportunities are pipeline deals (probability 1-99%) that use the Order model.

To record cassettes:
    uv run pytest tests/integration/test_opportunities_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_opportunities_integration/*.yaml
    uv run pytest tests/integration/test_opportunities_integration.py -v
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
@my_vcr.use_cassette("test_opportunities_integration/test_list_opportunities_real_response.yaml")
async def test_list_opportunities_real_response():
    """
    Test listing opportunities with real API response structure.

    Validates pagination metadata and multiple opportunity objects.
    Ensures Order model correctly parses /opportunities endpoint data.

    Cassette: tests/cassettes/integration/test_opportunities_integration/test_list_opportunities_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get opportunities with limit
        opportunities = await upsales.opportunities.list(limit=5)

        assert isinstance(opportunities, list)
        assert len(opportunities) <= 5

        for opp in opportunities:
            assert isinstance(opp, Order)
            assert opp.id > 0
            assert isinstance(opp.description, str)
            assert isinstance(opp.value, int)
            assert isinstance(opp.probability, int)
            assert 0 <= opp.probability <= 100

            # Validate dates are strings
            assert isinstance(opp.date, str)
            if opp.closeDate:
                assert isinstance(opp.closeDate, str)

        print(f"[OK] Listed {len(opportunities)} opportunities successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunities_integration/test_get_opportunity_real_response.yaml")
async def test_get_opportunity_real_response():
    """
    Test getting a single opportunity with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Order
    model correctly parses real Upsales opportunities API data.

    Cassette: tests/cassettes/integration/test_opportunities_integration/test_get_opportunity_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First get a list to find a valid opportunity ID
        opportunities = await upsales.opportunities.list(limit=1)

        if not opportunities:
            pytest.skip("No opportunities available in test environment")

        opp_id = opportunities[0].id

        # Now get the specific opportunity
        opp = await upsales.opportunities.get(opp_id)

        # Validate Order model with Pydantic v2 features
        assert isinstance(opp, Order)
        assert opp.id == opp_id
        assert isinstance(opp.description, str)
        assert isinstance(opp.value, int)
        assert isinstance(opp.probability, int)
        assert 0 <= opp.probability <= 100

        # Validate monetary fields
        assert isinstance(opp.oneOffValue, int)
        assert isinstance(opp.monthlyValue, int)
        assert isinstance(opp.annualValue, int)
        assert isinstance(opp.contributionMargin, int)

        # Validate currency fields
        assert isinstance(opp.currency, str)
        assert isinstance(opp.currencyRate, int)

        # Validate dates
        assert isinstance(opp.date, str)
        assert isinstance(opp.regDate, str)
        assert isinstance(opp.modDate, str)

        # Validate configuration
        assert opp.locked in (0, 1)
        assert isinstance(opp.priceListId, int)
        assert isinstance(opp.recurringInterval, int)

        # Validate computed fields
        assert hasattr(opp, "custom_fields")
        assert isinstance(opp.is_locked, bool)
        assert isinstance(opp.expected_value, float)
        assert isinstance(opp.is_recurring, bool)
        assert isinstance(opp.margin_percentage, float)

        print(f"[OK] Opportunity parsed successfully: {opp.description} (ID: {opp.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunities_integration/test_opportunity_nested_objects.yaml")
async def test_opportunity_nested_objects():
    """
    Test nested objects in opportunity responses.

    Validates that PartialUser, PartialCompany, PartialContact, and
    PartialOrderStage are correctly parsed from nested data.

    Cassette: tests/cassettes/integration/test_opportunities_integration/test_opportunity_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        opportunities = await upsales.opportunities.list(limit=10)

        # Find an opportunity with nested objects
        opp_with_nested = None
        for opp in opportunities:
            if opp.client or opp.user or opp.contact or opp.stage:
                opp_with_nested = opp
                break

        if not opp_with_nested:
            pytest.skip("No opportunities with nested objects found")

        opp = opp_with_nested

        # Validate client (company) if present
        if opp.client:
            assert isinstance(opp.client, PartialCompany)
            assert isinstance(opp.client.id, int)
            assert hasattr(opp.client, "name")
            print(f"[OK] PartialCompany validated: {opp.client.name} (ID: {opp.client.id})")

        # Validate user if present
        if opp.user:
            assert isinstance(opp.user, PartialUser)
            assert isinstance(opp.user.id, int)
            assert hasattr(opp.user, "name")
            print(f"[OK] PartialUser validated: {opp.user.name} (ID: {opp.user.id})")

        # Validate contact if present
        if opp.contact:
            assert isinstance(opp.contact, PartialContact)
            assert isinstance(opp.contact.id, int)
            assert hasattr(opp.contact, "name")
            print(f"[OK] PartialContact validated: {opp.contact.name} (ID: {opp.contact.id})")

        # Validate stage if present
        if opp.stage:
            assert isinstance(opp.stage, PartialOrderStage)
            assert isinstance(opp.stage.id, int)
            assert hasattr(opp.stage, "name")
            print(f"[OK] PartialOrderStage validated: {opp.stage.name} (ID: {opp.stage.id})")

        # Validate regBy (user who registered) if present
        if opp.regBy:
            assert isinstance(opp.regBy, PartialUser)
            assert isinstance(opp.regBy.id, int)
            print(f"[OK] PartialUser (regBy) validated: ID {opp.regBy.id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunities_integration/test_opportunity_computed_fields.yaml")
async def test_opportunity_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates all computed properties return expected types and values:
    - is_locked (bool)
    - expected_value (float)
    - is_recurring (bool)
    - margin_percentage (float)

    Cassette: tests/cassettes/integration/test_opportunities_integration/test_opportunity_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        opportunities = await upsales.opportunities.list(limit=1)

        if not opportunities:
            pytest.skip("No opportunities available in test environment")

        opp = opportunities[0]

        # Test is_locked computed field
        assert isinstance(opp.is_locked, bool)
        assert opp.is_locked == (opp.locked == 1)

        # Test expected_value computed field
        assert isinstance(opp.expected_value, float)
        if opp.value and opp.probability is not None:
            expected = (opp.value * opp.probability) / 100
            assert abs(opp.expected_value - expected) < 0.01  # Float comparison with tolerance
            print(
                f"[OK] Expected value: ${opp.expected_value:.2f} "
                f"(${opp.value} × {opp.probability}%)"
            )

        # Test is_recurring computed field
        assert isinstance(opp.is_recurring, bool)
        assert opp.is_recurring == (opp.monthlyValue > 0 or opp.annualValue > 0)
        if opp.is_recurring:
            print(f"[OK] Recurring opportunity: MRR=${opp.monthlyValue}, ARR=${opp.annualValue}")

        # Test margin_percentage computed field
        assert isinstance(opp.margin_percentage, float)
        if opp.value > 0:
            expected_margin = (opp.contributionMargin / opp.value) * 100
            assert abs(opp.margin_percentage - expected_margin) < 0.01
            print(f"[OK] Margin percentage: {opp.margin_percentage:.1f}%")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_opportunities_integration/test_opportunity_custom_fields.yaml")
async def test_opportunity_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.
    Tests both field access by ID and the custom_fields property.

    Cassette: tests/cassettes/integration/test_opportunities_integration/test_opportunity_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        opportunities = await upsales.opportunities.list(limit=10)

        # Find an opportunity with custom fields
        opp_with_custom = None
        for opp in opportunities:
            if opp.custom:
                opp_with_custom = opp
                break

        if opp_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(opp_with_custom.custom, list)
            for field in opp_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = opp_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            # Test that custom_fields is accessible
            assert isinstance(cf._fields, list)

            print(
                f"[OK] Custom fields validated: {len(opp_with_custom.custom)} fields "
                f"on opportunity {opp_with_custom.id}"
            )
        else:
            print("[SKIP] No opportunities with custom fields found")
