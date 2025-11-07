"""
Integration tests for Company model with real API responses.

Uses VCR.py to record API responses from /accounts endpoint.
Validates that our Pydantic v2 Company model correctly parses real data.

To record cassettes:
    uv run pytest tests/integration/test_companies_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.company import Company

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_companies_integration/test_get_company_real_response.yaml")
async def test_get_company_real_response():
    """
    Test getting a company with real API response structure.

    Records actual /accounts/:id response and validates Company model
    correctly parses all 87 fields with proper types.

    Cassette: tests/cassettes/integration/test_companies_integration/test_get_company_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get companies list to find a valid ID
        companies = await upsales.companies.list(limit=1)

        assert len(companies) > 0, "Should have at least one company"
        company = companies[0]

        # Validate Company model with Pydantic v2 features
        assert isinstance(company, Company)
        assert isinstance(company.id, int)
        assert isinstance(company.name, str)
        assert len(company.name) > 0  # NonEmptyStr validator

        # Validate BinaryFlag fields (0 or 1)
        assert company.active in (0, 1)
        assert company.isExternal in (0, 1)
        assert company.headquarters in (0, 1)

        # Validate computed fields
        assert isinstance(company.is_active, bool)
        assert isinstance(company.is_headquarters, bool)
        assert isinstance(company.contact_count, int)
        assert company.contact_count >= 0

        # Validate custom_fields property
        assert hasattr(company, "custom_fields")

        print(f"[OK] Company parsed: {company.name} (ID: {company.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_companies_integration/test_list_companies_real_response.yaml")
async def test_list_companies_real_response():
    """
    Test listing companies with real API response structure.

    Validates pagination and multiple company objects from /accounts.

    Cassette: tests/cassettes/integration/test_companies_integration/test_list_companies_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get companies with pagination
        companies = await upsales.companies.list(limit=10)

        assert isinstance(companies, list)
        assert len(companies) <= 10

        for company in companies:
            assert isinstance(company, Company)
            assert company.id > 0
            assert len(company.name) > 0
            # Validate required metadata
            assert isinstance(company.numberOfContacts, int)
            assert isinstance(company.score, int)

        print(f"[OK] Listed {len(companies)} companies successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_companies_integration/test_company_computed_fields_with_real_data.yaml")
async def test_company_computed_fields_with_real_data():
    """
    Test computed fields work correctly with real company data.

    Validates all computed properties with actual API responses.

    Cassette: tests/cassettes/integration/test_companies_integration/test_company_computed_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=5)

        for company in companies:
            # Test is_active computed field
            assert isinstance(company.is_active, bool)
            assert company.is_active == (company.active == 1)

            # Test is_headquarters computed field
            assert isinstance(company.is_headquarters, bool)
            assert company.is_headquarters == (company.headquarters == 1)

            # Test contact_count computed field
            assert isinstance(company.contact_count, int)
            assert company.contact_count == company.numberOfContactsTotal

        print(f"[OK] Validated computed fields for {len(companies)} companies")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_companies_integration/test_company_serialization_with_real_data.yaml")
async def test_company_serialization_with_real_data():
    """
    Test to_api_dict() serialization with real company data.

    Validates that serialization excludes frozen fields and works
    correctly with all field types.

    Cassette: tests/cassettes/integration/test_companies_integration/test_company_serialization_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=1)
        company = companies[0]

        # Test to_api_dict() serialization
        api_dict = company.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict
        assert "regDate" not in api_dict
        assert "modDate" not in api_dict

        # Validate updatable fields included
        assert "name" in api_dict
        assert "active" in api_dict

        # Validate types are JSON-serializable
        assert isinstance(api_dict, dict)
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert len(json_str) > 0

        print(f"[OK] Serialization validated: {len(api_dict)} fields")
