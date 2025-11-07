"""
Integration tests for all models together - cross-model validation.

Tests relationships between User, Company, and Product models using
real API responses recorded with VCR.py.

To record cassettes:
    uv run pytest tests/integration/test_all_models_integration.py -v --vcr-record=once
"""

import pytest
import vcr

from upsales import Upsales

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_all_models_integration/test_all_resources_available.yaml")
async def test_all_resources_available():
    """
    Test that all resource managers are properly registered.

    Validates upsales.users, upsales.companies, upsales.products all exist
    and return correct model types.

    Cassette: tests/cassettes/integration/test_all_models_integration/test_all_resources_available.yaml
    """
    async with Upsales.from_env() as upsales:
        # Validate all resources exist
        assert hasattr(upsales, "users")
        assert hasattr(upsales, "companies")
        assert hasattr(upsales, "products")

        # Test each resource returns correct model type
        users = await upsales.users.list(limit=1)
        assert len(users) > 0
        assert users[0].__class__.__name__ == "User"

        companies = await upsales.companies.list(limit=1)
        assert len(companies) > 0
        assert companies[0].__class__.__name__ == "Company"

        products = await upsales.products.list(limit=1)
        assert len(products) > 0
        assert products[0].__class__.__name__ == "Product"

        print("[OK] All resources registered and returning correct model types")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_all_models_integration/test_pydantic_v2_validators_across_models.yaml")
async def test_pydantic_v2_validators_across_models():
    """
    Test that Pydantic v2 validators work consistently across all models.

    Validates BinaryFlag, CustomFieldsList, and other validators work
    correctly with real API data in all models.

    Cassette: tests/cassettes/integration/test_all_models_integration/test_pydantic_v2_validators_across_models.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get one of each model
        user = (await upsales.users.list(limit=1))[0]
        company = (await upsales.companies.list(limit=1))[0]
        product = (await upsales.products.list(limit=1))[0]

        # Validate BinaryFlag validator works (all should be 0 or 1)
        assert user.active in (0, 1)
        assert user.administrator in (0, 1)
        assert company.active in (0, 1)
        assert product.active in (0, 1)

        # Validate CustomFieldsList validator works (all should be valid structure)
        for cf in user.custom:
            assert "fieldId" in cf
        for cf in company.custom:
            assert "fieldId" in cf
        for cf in product.custom:
            assert "fieldId" in cf

        # Validate custom_fields helper works
        assert hasattr(user, "custom_fields")
        assert hasattr(company, "custom_fields")
        assert hasattr(product, "custom_fields")

        print("[OK] Pydantic v2 validators work consistently across all models")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_all_models_integration/test_computed_fields_across_models.yaml")
async def test_computed_fields_across_models():
    """
    Test that computed fields work correctly in all models.

    Validates all models have custom_fields and is_active computed properties.

    Cassette: tests/cassettes/integration/test_all_models_integration/test_computed_fields_across_models.yaml
    """
    async with Upsales.from_env() as upsales:
        user = (await upsales.users.list(limit=1))[0]
        company = (await upsales.companies.list(limit=1))[0]
        product = (await upsales.products.list(limit=1))[0]

        # All models should have custom_fields computed field
        assert hasattr(user, "custom_fields")
        assert hasattr(company, "custom_fields")
        assert hasattr(product, "custom_fields")

        # All models should have is_active computed field
        assert isinstance(user.is_active, bool)
        assert isinstance(company.is_active, bool)
        assert isinstance(product.is_active, bool)

        # Validate computed fields return correct values
        assert user.is_active == (user.active == 1)
        assert company.is_active == (company.active == 1)
        assert product.is_active == (product.active == 1)

        print("[OK] Computed fields work consistently across all models")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_all_models_integration/test_serialization_excludes_frozen_fields.yaml")
async def test_serialization_excludes_frozen_fields():
    """
    Test that to_api_dict() excludes frozen fields in all models.

    Validates Pydantic v2 optimized serialization works correctly.

    Cassette: tests/cassettes/integration/test_all_models_integration/test_serialization_excludes_frozen_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        user = (await upsales.users.list(limit=1))[0]
        company = (await upsales.companies.list(limit=1))[0]
        product = (await upsales.products.list(limit=1))[0]

        # Test each model's serialization
        user_dict = user.to_api_dict()
        assert "id" not in user_dict
        assert "regDate" not in user_dict

        company_dict = company.to_api_dict()
        assert "id" not in company_dict
        assert "regDate" not in company_dict
        assert "modDate" not in company_dict

        product_dict = product.to_api_dict()
        assert "id" not in product_dict

        print("[OK] All models properly exclude frozen fields in serialization")
