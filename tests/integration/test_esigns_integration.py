"""
Integration tests for Esign model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_esigns_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_esigns_integration/
    uv run pytest tests/integration/test_esigns_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.esigns import Esign

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
@my_vcr.use_cassette("test_esigns_integration/test_list_esigns_real_response.yaml")
async def test_list_esigns_real_response():
    """
    Test listing esigns with real API response structure.

    Validates that Esign model correctly parses real API data including
    Scrive integration fields.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_list_esigns_real_response.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        esigns = await upsales.esigns.list(limit=5)

        assert isinstance(esigns, list)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        for esign in esigns:
            assert isinstance(esign, Esign)
            assert isinstance(esign.id, int)
            assert esign.id > 0
            assert isinstance(esign.title, str)

            # Validate required fields
            assert isinstance(esign.userId, int)
            assert esign.userId > 0

            # Validate read-only fields (set by API)
            if esign.documentId is not None:
                assert isinstance(esign.documentId, str)
            if esign.upsalesStatus is not None:
                assert isinstance(esign.upsalesStatus, str)
            if esign.type is not None:
                assert isinstance(esign.type, str)

            # Validate updatable fields
            assert isinstance(esign.clientId, int)
            assert isinstance(esign.opportunityId, int)

        print(f"[OK] Listed {len(esigns)} esigns successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_esigns_integration/test_get_esign_real_response.yaml")
async def test_get_esign_real_response():
    """
    Test getting a single esign with real API response structure.

    Validates full Esign model including all Scrive integration fields.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_get_esign_real_response.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid esign ID
        esigns = await upsales.esigns.list(limit=1)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        esign_id = esigns[0].id

        # Now get the specific esign
        esign = await upsales.esigns.get(esign_id)

        assert isinstance(esign, Esign)
        assert esign.id == esign_id
        assert isinstance(esign.title, str)
        assert isinstance(esign.userId, int)

        print(f"[OK] Got esign {esign.id}: {esign.title}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_esigns_integration/test_esign_scrive_fields.yaml")
async def test_esign_scrive_fields():
    """
    Test that Scrive integration fields parse correctly.

    Validates documentId, upsalesStatus, type, state, signDate fields
    that are specific to the Scrive e-signature integration.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_esign_scrive_fields.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        esigns = await upsales.esigns.list(limit=10)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        # Check Scrive-specific fields
        found_document_id = False
        found_status = False
        found_type = False
        found_state = False
        found_sign_date = False
        found_involved = False

        for esign in esigns:
            if esign.documentId is not None:
                found_document_id = True
                assert isinstance(esign.documentId, str)
                print(f"  [OK] documentId: {esign.documentId}")

            if esign.upsalesStatus is not None:
                found_status = True
                assert isinstance(esign.upsalesStatus, str)
                print(f"  [OK] upsalesStatus: {esign.upsalesStatus}")

            if esign.type is not None:
                found_type = True
                assert isinstance(esign.type, str)
                print(f"  [OK] type: {esign.type}")

            if esign.state is not None:
                found_state = True
                assert isinstance(esign.state, str)
                print(f"  [OK] state: {esign.state}")

            if esign.signDate is not None:
                found_sign_date = True
                assert isinstance(esign.signDate, str)
                print(f"  [OK] signDate: {esign.signDate}")

            if esign.involved is not None:
                found_involved = True
                assert isinstance(esign.involved, list)
                print(f"  [OK] involved: {len(esign.involved)} parties")

        print(
            f"\n[OK] Scrive fields found - documentId:{found_document_id}, "
            f"upsalesStatus:{found_status}, type:{found_type}, state:{found_state}, "
            f"signDate:{found_sign_date}, involved:{found_involved}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_esigns_integration/test_esign_computed_fields.yaml")
async def test_esign_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates custom_fields computed property.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_esign_computed_fields.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        esigns = await upsales.esigns.list(limit=5)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        esign = esigns[0]

        # Test custom_fields property exists
        assert hasattr(esign, "custom_fields")

        # Validate custom fields structure
        assert isinstance(esign.custom, list)

        print(f"[OK] Computed field custom_fields exists with {len(esign.custom)} custom fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_esigns_integration/test_esign_custom_fields.yaml")
async def test_esign_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_esign_custom_fields.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        esigns = await upsales.esigns.list(limit=20)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        # Find an esign with custom fields
        esign_with_custom = None
        for esign in esigns:
            if esign.custom:
                esign_with_custom = esign
                break

        if esign_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(esign_with_custom.custom, list)
            for field in esign_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = esign_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(esign_with_custom.custom)} fields")
        else:
            print("[SKIP] No esigns with custom fields found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_esigns_integration/test_esign_relationships.yaml")
async def test_esign_relationships():
    """
    Test that relationship fields (clientId, opportunityId, fileId) work correctly.

    Validates foreign key relationships to other Upsales entities.

    Cassette: tests/cassettes/integration/test_esigns_integration/test_esign_relationships.yaml

    Note:
        May skip if esign module is not enabled in the Upsales account.
    """
    async with Upsales.from_env() as upsales:
        esigns = await upsales.esigns.list(limit=10)

        if len(esigns) == 0:
            pytest.skip("No esigns found in the system (esign module may not be enabled)")

        found_client = False
        found_opportunity = False
        found_file = False

        for esign in esigns:
            # clientId is always present (defaults to 0)
            assert isinstance(esign.clientId, int)
            if esign.clientId > 0:
                found_client = True
                print(f"  [OK] clientId: {esign.clientId}")

            # opportunityId is always present (defaults to 0)
            assert isinstance(esign.opportunityId, int)
            if esign.opportunityId > 0:
                found_opportunity = True
                print(f"  [OK] opportunityId: {esign.opportunityId}")

            if esign.fileId is not None and esign.fileId > 0:
                found_file = True
                print(f"  [OK] fileId: {esign.fileId}")

        print(
            f"\n[OK] Relationships found - client:{found_client}, "
            f"opportunity:{found_opportunity}, file:{found_file}"
        )
