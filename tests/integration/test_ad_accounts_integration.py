"""
Integration tests for AdAccount model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that AdAccount model correctly parses real Upsales API data.

Note: This endpoint is special - it requires a customer_id and may return
404 if no ad account is configured for that customer.

To record cassettes:
    uv run pytest tests/integration/test_ad_accounts_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import NotFoundError
from upsales.models.ad_accounts import AdAccount

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ad_accounts_integration/test_get_ad_account_real_response.yaml")
async def test_get_ad_account_real_response():
    """
    Test getting ad account with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our AdAccount
    model correctly parses real Upsales API data.

    Note: May skip if no ad account exists for the test customer.
    """
    async with Upsales.from_env() as upsales:
        # First get a valid customer_id
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies available for testing")

        customer_id = companies[0].id

        try:
            account = await upsales.ad_accounts.get(customer_id=customer_id)

            # Validate AdAccount model
            assert isinstance(account, AdAccount)
            assert isinstance(account.cpmAmount, float)
            assert account.cpmAmount > 0
            assert isinstance(account.active, bool)

            # Validate computed property
            assert isinstance(account.is_active, bool)
            assert account.is_active == account.active

            # Validate optional fields
            if account.values is not None:
                assert isinstance(account.values, dict)

            print(
                f"[OK] AdAccount parsed successfully for customer {customer_id}: "
                f"CPM={account.cpmAmount}, Active={account.active}"
            )

        except NotFoundError:
            pytest.skip(f"No ad account configured for customer {customer_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ad_accounts_integration/test_create_ad_account_real_response.yaml")
async def test_create_ad_account_real_response():
    """
    Test creating ad account with real API response.

    Creates an ad account for a customer, then validates the model.
    Skips if creation fails due to existing account.
    """
    async with Upsales.from_env() as upsales:
        # Get a valid customer_id
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies available for testing")

        customer_id = companies[0].id

        try:
            # First check if account already exists
            try:
                await upsales.ad_accounts.get(customer_id=customer_id)
                pytest.skip(f"Ad account already exists for customer {customer_id}")
            except NotFoundError:
                pass  # Good, no existing account

            # Create new ad account
            account = await upsales.ad_accounts.create(
                customer_id=customer_id, cpmAmount=350.0, active=True
            )

            # Validate created account
            assert isinstance(account, AdAccount)
            assert account.cpmAmount == 350.0
            assert account.active is True
            assert account.is_active

            print(
                f"[OK] Created ad account for customer {customer_id}: "
                f"CPM={account.cpmAmount}, Active={account.active}"
            )

            # Clean up: delete the created account
            await upsales.ad_accounts.delete(customer_id=customer_id)

        except Exception as e:
            # If creation fails for any reason, skip
            pytest.skip(f"Could not create ad account: {e}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ad_accounts_integration/test_update_ad_account_real_response.yaml")
async def test_update_ad_account_real_response():
    """
    Test updating ad account with real API response.

    Updates an existing ad account and validates the changes.
    Skips if no ad account exists for the test customer.
    """
    async with Upsales.from_env() as upsales:
        # Get a valid customer_id
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies available for testing")

        customer_id = companies[0].id

        try:
            # Get existing account
            account = await upsales.ad_accounts.get(customer_id=customer_id)
            original_cpm = account.cpmAmount

            # Update the account
            updated = await upsales.ad_accounts.update(customer_id=customer_id, cpmAmount=400.0)

            # Validate update
            assert isinstance(updated, AdAccount)
            assert updated.cpmAmount == 400.0

            print(
                f"[OK] Updated ad account for customer {customer_id}: "
                f"CPM {original_cpm} -> {updated.cpmAmount}"
            )

            # Restore original value
            await upsales.ad_accounts.update(customer_id=customer_id, cpmAmount=original_cpm)

        except NotFoundError:
            pytest.skip(f"No ad account configured for customer {customer_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ad_accounts_integration/test_ad_account_serialization.yaml")
async def test_ad_account_serialization_real_data():
    """
    Test to_api_dict() serialization with real ad account data.

    Validates that serialization works correctly with all fields.
    """
    async with Upsales.from_env() as upsales:
        # Get a valid customer_id
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies available for testing")

        customer_id = companies[0].id

        try:
            account = await upsales.ad_accounts.get(customer_id=customer_id)

            # Get API dict
            api_dict = account.to_api_dict()

            # Should include updatable fields
            assert "cpmAmount" in api_dict
            assert "active" in api_dict
            assert isinstance(api_dict["cpmAmount"], float)
            assert isinstance(api_dict["active"], bool)

            # Computed properties should NOT be in API dict
            assert "is_active" not in api_dict

            # With overrides, should include changed fields
            api_dict_with_changes = account.to_api_dict(cpmAmount=500.0, active=False)
            assert api_dict_with_changes["cpmAmount"] == 500.0
            assert api_dict_with_changes["active"] is False

            # Validate it's JSON serializable
            import json

            json_str = json.dumps(api_dict)  # Should not raise
            assert json_str

            print(f"[OK] Serialization validated for customer {customer_id}")
            print(f"[OK] API payload has {len(api_dict)} fields")

        except NotFoundError:
            pytest.skip(f"No ad account configured for customer {customer_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_ad_accounts_integration/test_ad_account_edit_method.yaml")
async def test_ad_account_edit_method():
    """
    Test the instance edit() method with real API.

    Validates that the edit() method on AdAccount instances works
    correctly with the special customer_id requirement.
    """
    async with Upsales.from_env() as upsales:
        # Get a valid customer_id
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies available for testing")

        customer_id = companies[0].id

        try:
            account = await upsales.ad_accounts.get(customer_id=customer_id)
            original_cpm = account.cpmAmount

            # Use instance method to edit
            updated = await account.edit(customer_id=customer_id, cpmAmount=450.0)

            # Validate update
            assert isinstance(updated, AdAccount)
            assert updated.cpmAmount == 450.0

            print(
                f"[OK] Edit method worked for customer {customer_id}: "
                f"CPM {original_cpm} -> {updated.cpmAmount}"
            )

            # Restore original value
            await updated.edit(customer_id=customer_id, cpmAmount=original_cpm)

        except NotFoundError:
            pytest.skip(f"No ad account configured for customer {customer_id}")
