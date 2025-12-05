"""
Integration tests for CustomField model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

Note: Custom fields are entity-specific. This resource does NOT extend BaseResource.

To record cassettes:
    uv run pytest tests/integration/test_custom_fields_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_custom_fields_integration/
    uv run pytest tests/integration/test_custom_fields_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.custom_field import CustomField

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
@my_vcr.use_cassette("test_custom_fields_integration/test_list_account_custom_fields.yaml")
async def test_list_account_custom_fields():
    """
    Test listing custom fields for accounts entity.

    Validates that CustomField model correctly parses real API data
    for account custom field definitions.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_list_account_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        fields = await upsales.custom_fields.list_for_entity("account")

        assert isinstance(fields, list)

        if len(fields) == 0:
            pytest.skip("No custom fields found for accounts entity")

        for field in fields:
            assert isinstance(field, CustomField)
            assert isinstance(field.id, int)
            assert field.id > 0
            assert isinstance(field.name, str)
            assert isinstance(field.datatype, str)
            # alias can be None per model definition
            if field.alias is not None:
                assert isinstance(field.alias, str)

            # Validate binary flags (should be 0 or 1)
            assert field.visible in [0, 1]
            assert field.editable in [0, 1]
            assert field.locked in [0, 1]
            assert field.viewonly in [0, 1]
            assert field.obligatoryField in [0, 1]
            assert field.searchable in [0, 1]
            assert field.lookupField in [0, 1]

        print(f"[OK] Listed {len(fields)} custom fields for accounts successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_list_contact_custom_fields.yaml")
async def test_list_contact_custom_fields():
    """
    Test listing custom fields for contacts entity.

    Validates that CustomField model correctly parses real API data
    for contact custom field definitions.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_list_contact_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        fields = await upsales.custom_fields.list_for_entity("contact")

        assert isinstance(fields, list)

        if len(fields) == 0:
            pytest.skip("No custom fields found for contacts entity")

        for field in fields:
            assert isinstance(field, CustomField)
            assert isinstance(field.id, int)
            assert field.id > 0
            assert isinstance(field.name, str)
            assert isinstance(field.datatype, str)

        print(f"[OK] Listed {len(fields)} custom fields for contacts successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_list_order_custom_fields.yaml")
async def test_list_order_custom_fields():
    """
    Test listing custom fields for orders entity.

    Orders may have entity-specific fields like formula and stages.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_list_order_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        fields = await upsales.custom_fields.list_for_entity("order")

        assert isinstance(fields, list)

        if len(fields) == 0:
            pytest.skip("No custom fields found for orders entity")

        # Check for order-specific fields (formula, formulaVisible, stages)
        found_calculation = False
        for field in fields:
            assert isinstance(field, CustomField)
            if field.datatype == "Calculation":
                found_calculation = True
                # Calculation fields may have formula
                if field.formula is not None:
                    assert isinstance(field.formula, str)
                    print(f"  [OK] Found Calculation field: {field.name}, formula={field.formula}")

        print(f"[OK] Listed {len(fields)} custom fields for orders successfully")
        if found_calculation:
            print("  [INFO] Found Calculation field type (order-specific)")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_list_product_custom_fields.yaml")
async def test_list_product_custom_fields():
    """
    Test listing custom fields for products entity.

    Products may have entity-specific fields like categories.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_list_product_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        fields = await upsales.custom_fields.list_for_entity("product")

        assert isinstance(fields, list)

        if len(fields) == 0:
            pytest.skip("No custom fields found for products entity")

        for field in fields:
            assert isinstance(field, CustomField)
            # Products have categories field
            if field.categories:
                assert isinstance(field.categories, list)
                print(f"  [OK] Field '{field.name}' has categories: {len(field.categories)}")

        print(f"[OK] Listed {len(fields)} custom fields for products successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_get_custom_field_by_id.yaml")
async def test_get_custom_field_by_id():
    """
    Test getting a specific custom field by ID.

    Uses list to find a valid field ID, then gets it specifically.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_get_custom_field_by_id.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid field ID
        fields = await upsales.custom_fields.list_for_entity("account")

        if len(fields) == 0:
            pytest.skip("No custom fields found for accounts entity")

        field_id = fields[0].id

        # Now get the specific field
        field = await upsales.custom_fields.get(field_id, entity="account")

        assert isinstance(field, CustomField)
        assert field.id == field_id
        assert isinstance(field.name, str)
        assert isinstance(field.datatype, str)

        print(f"[OK] Got custom field {field.id}: {field.name} ({field.datatype})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_custom_field_types.yaml")
async def test_custom_field_types():
    """
    Test different custom field types (String, Select, Boolean, etc.).

    Validates that various field types parse correctly.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_custom_field_types.yaml
    """
    async with Upsales.from_env() as upsales:
        # Check multiple entities for variety
        all_fields = []
        for entity in ["account", "contact", "order", "product"]:
            fields = await upsales.custom_fields.list_for_entity(entity)
            all_fields.extend(fields)

        if len(all_fields) == 0:
            pytest.skip("No custom fields found in any entity")

        # Track which field types we found
        found_types = set()
        for field in all_fields:
            found_types.add(field.datatype)

            # Validate type-specific fields
            if field.datatype in ["String", "Text"]:
                assert isinstance(field.maxLength, int)
                print(f"  [OK] {field.datatype} field: maxLength={field.maxLength}")

            elif field.datatype in ["Select", "MultiSelect"]:
                # Select fields may have options in 'default'
                if field.default is not None:
                    print(f"  [OK] {field.datatype} field: options={field.default}")

            elif field.datatype == "Boolean":
                # Boolean fields just need validation
                print(f"  [OK] Boolean field: {field.name}")

            elif field.datatype == "Calculation":
                # Calculation fields may have formula
                if field.formula is not None:
                    print(f"  [OK] Calculation field: formula={field.formula}")

        print(f"[OK] Found {len(found_types)} different field types: {sorted(found_types)}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_get_by_alias.yaml")
async def test_get_by_alias():
    """
    Test getting custom field by alias.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_get_by_alias.yaml
    """
    async with Upsales.from_env() as upsales:
        fields = await upsales.custom_fields.list_for_entity("account")

        if len(fields) == 0:
            pytest.skip("No custom fields found for accounts entity")

        # Find a field with an alias
        field_with_alias = None
        for field in fields:
            if field.alias:
                field_with_alias = field
                break

        if not field_with_alias:
            pytest.skip("No custom fields with aliases found")

        # Get by alias
        found = await upsales.custom_fields.get_by_alias(field_with_alias.alias, entity="account")

        assert found is not None
        assert isinstance(found, CustomField)
        assert found.id == field_with_alias.id
        assert found.alias == field_with_alias.alias

        print(f"[OK] Found field by alias '{found.alias}': {found.name} (id={found.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_custom_fields_integration/test_list_by_type.yaml")
async def test_list_by_type():
    """
    Test listing custom fields filtered by type.

    Cassette: tests/cassettes/integration/test_custom_fields_integration/test_list_by_type.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all account fields
        all_fields = await upsales.custom_fields.list_for_entity("account")

        if len(all_fields) == 0:
            pytest.skip("No custom fields found for accounts entity")

        # Find what types exist
        existing_types = {f.datatype for f in all_fields}

        # Test filtering by a type that exists
        test_type = existing_types.pop() if existing_types else "String"
        filtered_fields = await upsales.custom_fields.list_by_type(
            entity="account", datatype=test_type
        )

        assert isinstance(filtered_fields, list)

        # All returned fields should be of the requested type
        for field in filtered_fields:
            assert field.datatype == test_type

        print(
            f"[OK] Found {len(filtered_fields)} fields of type '{test_type}' "
            f"(out of {len(all_fields)} total)"
        )
