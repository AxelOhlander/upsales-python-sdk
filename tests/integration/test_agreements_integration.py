"""
Integration tests for Agreement model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_agreements_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_agreements_integration/
    uv run pytest tests/integration/test_agreements_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.agreements import Agreement
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
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
@my_vcr.use_cassette("test_agreements_integration/test_list_agreements_real_response.yaml")
async def test_list_agreements_real_response():
    """
    Test listing agreements with real API response structure.

    Validates that Agreement model correctly parses real API data including
    nested objects like PartialUser, PartialCompany, PartialContact.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_list_agreements_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        agreements = await upsales.agreements.list(limit=5)

        assert isinstance(agreements, list)

        if len(agreements) == 0:
            pytest.skip("No agreements found in the system")

        for agreement in agreements:
            assert isinstance(agreement, Agreement)
            assert isinstance(agreement.id, int)
            assert agreement.id > 0
            assert isinstance(agreement.description, str)

            # Validate read-only fields are present
            assert isinstance(agreement.regDate, str)
            assert isinstance(agreement.modDate, str)

            # Validate monetary fields
            assert isinstance(agreement.value, int)
            assert isinstance(agreement.contributionMargin, int)
            assert isinstance(agreement.yearlyValue, int)

            # Validate currency
            assert isinstance(agreement.currency, str)
            assert len(agreement.currency) == 3  # ISO 4217 code

            # Validate configuration fields
            assert isinstance(agreement.priceListId, int)
            assert isinstance(agreement.invoiceRelatedClient, bool)
            assert isinstance(agreement.userEditable, bool)
            assert isinstance(agreement.userRemovable, bool)

            # Validate lists
            assert isinstance(agreement.orderRow, list)
            assert isinstance(agreement.custom, list)
            assert isinstance(agreement.children, list)

            # Validate complex objects
            assert isinstance(agreement.metadata, dict)
            assert isinstance(agreement.stage, dict)

        print(f"[OK] Listed {len(agreements)} agreements successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_agreements_integration/test_get_agreement_real_response.yaml")
async def test_get_agreement_real_response():
    """
    Test getting a single agreement with real API response structure.

    Validates full Agreement model including all nested objects.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_get_agreement_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid agreement ID
        agreements = await upsales.agreements.list(limit=1)

        if len(agreements) == 0:
            pytest.skip("No agreements found in the system")

        agreement_id = agreements[0].id

        # Now get the specific agreement
        agreement = await upsales.agreements.get(agreement_id)

        assert isinstance(agreement, Agreement)
        assert agreement.id == agreement_id
        assert isinstance(agreement.description, str)

        # Validate timestamps
        assert isinstance(agreement.regDate, str)
        assert isinstance(agreement.modDate, str)

        # Validate monetary fields
        assert isinstance(agreement.value, int)
        assert isinstance(agreement.orderValue, int)
        assert isinstance(agreement.contributionMargin, int)
        assert isinstance(agreement.contributionMarginInAgreementCurrency, int)
        assert isinstance(agreement.valueInMasterCurrency, int)
        assert isinstance(agreement.yearlyValue, int)
        assert isinstance(agreement.yearlyValueInMasterCurrency, int)
        assert isinstance(agreement.yearlyContributionMargin, int)
        assert isinstance(agreement.yearlyContributionMarginInAgreementCurrency, int)
        assert isinstance(agreement.purchaseCost, int)

        # Validate currency
        assert isinstance(agreement.currency, str)
        assert len(agreement.currency) == 3  # ISO 4217 code
        assert isinstance(agreement.currencyRate, int)

        # Validate configuration fields
        assert isinstance(agreement.priceListId, int)
        assert isinstance(agreement.invoiceRelatedClient, bool)
        assert isinstance(agreement.userEditable, bool)
        assert isinstance(agreement.userRemovable, bool)
        assert isinstance(agreement.isParent, bool)

        # Validate lists
        assert isinstance(agreement.orderRow, list)
        assert isinstance(agreement.custom, list)
        assert isinstance(agreement.children, list)

        # Validate complex objects
        assert isinstance(agreement.metadata, dict)
        assert isinstance(agreement.stage, dict)
        assert "id" in agreement.stage

        print(f"[OK] Got agreement {agreement.id}: {agreement.description}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_agreements_integration/test_agreement_nested_objects.yaml")
async def test_agreement_nested_objects():
    """
    Test that nested objects (PartialUser, PartialCompany, etc.) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_agreement_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        agreements = await upsales.agreements.list(limit=10)

        if len(agreements) == 0:
            pytest.skip("No agreements found in the system")

        # Check various nested objects across agreements
        found_user = False
        found_client = False
        found_contact = False
        found_regby = False

        for agreement in agreements:
            if agreement.user is not None:
                found_user = True
                assert isinstance(agreement.user, PartialUser)
                assert hasattr(agreement.user, "id")
                assert hasattr(agreement.user, "name")
                print(f"  [OK] user: id={agreement.user.id}, name={agreement.user.name}")

            if agreement.client is not None:
                found_client = True
                assert isinstance(agreement.client, PartialCompany)
                assert hasattr(agreement.client, "id")
                assert hasattr(agreement.client, "name")
                print(f"  [OK] client: id={agreement.client.id}, name={agreement.client.name}")

            if agreement.contact is not None:
                found_contact = True
                assert isinstance(agreement.contact, PartialContact)
                assert hasattr(agreement.contact, "id")
                print(f"  [OK] contact: id={agreement.contact.id}")

            if agreement.regBy is not None:
                found_regby = True
                assert isinstance(agreement.regBy, PartialUser)
                assert hasattr(agreement.regBy, "id")
                assert hasattr(agreement.regBy, "name")
                print(f"  [OK] regBy: id={agreement.regBy.id}, name={agreement.regBy.name}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, client:{found_client}, "
            f"contact:{found_contact}, regBy:{found_regby}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_agreements_integration/test_agreement_computed_fields.yaml")
async def test_agreement_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates custom_fields computed property.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_agreement_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        agreements = await upsales.agreements.list(limit=5)

        if len(agreements) == 0:
            pytest.skip("No agreements found in the system")

        agreement = agreements[0]

        # Test custom_fields property
        assert hasattr(agreement, "custom_fields")
        print("[OK] custom_fields property exists")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_agreements_integration/test_agreement_custom_fields.yaml")
async def test_agreement_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_agreement_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        agreements = await upsales.agreements.list(limit=20)

        if len(agreements) == 0:
            pytest.skip("No agreements found in the system")

        # Find an agreement with custom fields
        agreement_with_custom = None
        for agreement in agreements:
            if agreement.custom:
                agreement_with_custom = agreement
                break

        if agreement_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(agreement_with_custom.custom, list)
            for field in agreement_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = agreement_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(agreement_with_custom.custom)} fields")
        else:
            print("[SKIP] No agreements with custom fields found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_agreements_integration/test_agreement_search.yaml")
async def test_agreement_search():
    """
    Test listing agreements with filters.

    Validates list functionality works with real API.

    Cassette: tests/cassettes/integration/test_agreements_integration/test_agreement_search.yaml
    """
    async with Upsales.from_env() as upsales:
        # List agreements with limit
        agreements = await upsales.agreements.list(limit=10)

        assert isinstance(agreements, list)

        for agreement in agreements:
            assert isinstance(agreement, Agreement)

        print(f"[OK] Found {len(agreements)} agreements (limited to 10)")
