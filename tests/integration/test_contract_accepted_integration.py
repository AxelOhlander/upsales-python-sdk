"""
Integration tests for ContractAccepted model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_contract_accepted_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_contract_accepted_integration/
    uv run pytest tests/integration/test_contract_accepted_integration.py -v

Note:
    The /contractAccepted endpoint may return 500 errors in some test environments.
    Tests are designed to skip gracefully if the endpoint is unavailable.
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import AuthenticationError, ServerError
from upsales.models.contract_accepted import ContractAccepted

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
@my_vcr.use_cassette(
    "test_contract_accepted_integration/test_list_contract_accepted_real_response.yaml"
)
async def test_list_contract_accepted_real_response():
    """
    Test listing contract accepted records with real API response structure.

    Validates that ContractAccepted model correctly parses real API data
    including auto-populated fields like date, userId, customerId, etc.

    Cassette: tests/cassettes/integration/test_contract_accepted_integration/test_list_contract_accepted_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            contracts = await upsales.contract_accepted.list(limit=10)
        except (ServerError, AuthenticationError) as e:
            # The contractAccepted endpoint may return 500 errors in some environments
            if "500" in str(e) or "Server error" in str(e):
                pytest.skip(f"contractAccepted endpoint not available: {e}")
            raise

        assert isinstance(contracts, list)

        if len(contracts) == 0:
            pytest.skip("No contract acceptance records found in the system")

        for contract in contracts:
            assert isinstance(contract, ContractAccepted)
            assert isinstance(contract.id, int)
            assert contract.id > 0
            assert isinstance(contract.contractId, int)

            # Validate optional auto-populated fields
            if contract.customerId is not None:
                assert isinstance(contract.customerId, int)
            if contract.userId is not None:
                assert isinstance(contract.userId, int)
            if contract.body is not None:
                assert isinstance(contract.body, str)
            if contract.version is not None:
                assert isinstance(contract.version, str)
            if contract.date is not None:
                assert isinstance(contract.date, str)

        print(f"[OK] Listed {len(contracts)} contract acceptance records successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_contract_accepted_integration/test_get_contract_accepted_real_response.yaml"
)
async def test_get_contract_accepted_real_response():
    """
    Test getting a single contract accepted record with real API response structure.

    Validates full ContractAccepted model with all fields.

    Cassette: tests/cassettes/integration/test_contract_accepted_integration/test_get_contract_accepted_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid contract acceptance ID
        try:
            contracts = await upsales.contract_accepted.list(limit=1)
        except (ServerError, AuthenticationError) as e:
            if "500" in str(e) or "Server error" in str(e):
                pytest.skip(f"contractAccepted endpoint not available: {e}")
            raise

        if len(contracts) == 0:
            pytest.skip("No contract acceptance records found in the system")

        contract_id = contracts[0].id

        # Now get the specific contract acceptance record
        contract = await upsales.contract_accepted.get(contract_id)

        assert isinstance(contract, ContractAccepted)
        assert contract.id == contract_id
        assert isinstance(contract.contractId, int)

        print(
            f"[OK] Got contract acceptance record {contract.id} for contract {contract.contractId}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_contract_accepted_integration/test_contract_accepted_computed_fields.yaml"
)
async def test_contract_accepted_computed_fields():
    """
    Test computed field has_date works correctly with real API data.

    Validates the has_date computed property.

    Cassette: tests/cassettes/integration/test_contract_accepted_integration/test_contract_accepted_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            contracts = await upsales.contract_accepted.list(limit=5)
        except (ServerError, AuthenticationError) as e:
            if "500" in str(e) or "Server error" in str(e):
                pytest.skip(f"contractAccepted endpoint not available: {e}")
            raise

        if len(contracts) == 0:
            pytest.skip("No contract acceptance records found in the system")

        contract = contracts[0]

        # Test computed field exists and returns correct type
        assert isinstance(contract.has_date, bool)
        assert contract.has_date == bool(contract.date)

        if contract.date:
            assert contract.has_date is True
            print(f"[OK] Computed field has_date=True, date={contract.date}")
        else:
            assert contract.has_date is False
            print("[OK] Computed field has_date=False, date=None")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contract_accepted_integration/test_contract_accepted_fields.yaml")
async def test_contract_accepted_fields():
    """
    Test that all fields parse correctly with real API data.

    Validates required and optional fields are properly structured.

    Cassette: tests/cassettes/integration/test_contract_accepted_integration/test_contract_accepted_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            contracts = await upsales.contract_accepted.list(limit=10)
        except (ServerError, AuthenticationError) as e:
            if "500" in str(e) or "Server error" in str(e):
                pytest.skip(f"contractAccepted endpoint not available: {e}")
            raise

        if len(contracts) == 0:
            pytest.skip("No contract acceptance records found in the system")

        # Track which optional fields we've seen
        found_customer_id = False
        found_user_id = False
        found_body = False
        found_version = False
        found_date = False

        for contract in contracts:
            # All contracts should have these required fields
            assert isinstance(contract.id, int)
            assert isinstance(contract.contractId, int)

            # Check optional fields
            if contract.customerId is not None:
                found_customer_id = True
                assert isinstance(contract.customerId, int)
                print(f"  [OK] customerId: {contract.customerId}")

            if contract.userId is not None:
                found_user_id = True
                assert isinstance(contract.userId, int)
                print(f"  [OK] userId: {contract.userId}")

            if contract.body is not None:
                found_body = True
                assert isinstance(contract.body, str)
                print(f"  [OK] body: {len(contract.body)} chars")

            if contract.version is not None:
                found_version = True
                assert isinstance(contract.version, str)
                print(f"  [OK] version: {contract.version}")

            if contract.date is not None:
                found_date = True
                assert isinstance(contract.date, str)
                print(f"  [OK] date: {contract.date}")

        print(
            f"\n[OK] Optional fields found - customerId:{found_customer_id}, "
            f"userId:{found_user_id}, body:{found_body}, version:{found_version}, "
            f"date:{found_date}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contract_accepted_integration/test_contract_accepted_search.yaml")
async def test_contract_accepted_search():
    """
    Test searching contract acceptance records with filters.

    Validates search functionality works with real API.

    Cassette: tests/cassettes/integration/test_contract_accepted_integration/test_contract_accepted_search.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a contract ID from the list
        try:
            all_contracts = await upsales.contract_accepted.list(limit=1)
        except (ServerError, AuthenticationError) as e:
            if "500" in str(e) or "Server error" in str(e):
                pytest.skip(f"contractAccepted endpoint not available: {e}")
            raise

        if len(all_contracts) == 0:
            pytest.skip("No contract acceptance records found in the system")

        contract_id = all_contracts[0].contractId

        # Search for records with this specific contract ID
        contracts = await upsales.contract_accepted.search(contractId=contract_id)

        assert isinstance(contracts, list)

        for contract in contracts:
            assert isinstance(contract, ContractAccepted)
            assert contract.contractId == contract_id

        print(f"[OK] Found {len(contracts)} contract acceptance records for contract {contract_id}")
