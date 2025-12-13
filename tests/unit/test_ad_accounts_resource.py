"""Unit tests for AdAccounts resource manager."""

from unittest.mock import AsyncMock, Mock

import pytest

from upsales.http import HTTPClient
from upsales.models.ad_accounts import AdAccount, PartialAdAccount
from upsales.resources.ad_accounts import AdAccountsResource


@pytest.fixture
def mock_http():
    """Create a mock HTTP client."""
    http = Mock(spec=HTTPClient)
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.delete = AsyncMock()
    http._client = None  # Required for BaseResource
    http._upsales_client = None  # Required for model._client assignment
    return http


@pytest.fixture
def ad_accounts_resource(mock_http):
    """Create AdAccountsResource instance with mock HTTP client."""
    return AdAccountsResource(mock_http)


@pytest.fixture
def sample_account_data():
    """Sample account data matching API response structure."""
    return {
        "cpmAmount": 350.0,
        "active": True,
        "values": {"impressions": 10000, "clicks": 250},
    }


class TestAdAccountsResource:
    """Test suite for AdAccountsResource."""

    def test_initialization(self, mock_http):
        """Test resource initialization with correct endpoint."""
        resource = AdAccountsResource(mock_http)
        assert resource._endpoint == "/:customerId/engage/account"
        assert resource._model_class == AdAccount
        assert resource._partial_class == PartialAdAccount

    @pytest.mark.asyncio
    async def test_get_account(self, ad_accounts_resource, mock_http, sample_account_data):
        """Test getting account for a specific customer."""
        mock_http.get.return_value = {"data": sample_account_data}

        account = await ad_accounts_resource.get(customer_id=123)

        assert isinstance(account, AdAccount)
        assert account.cpmAmount == 350.0
        assert account.active is True
        mock_http.get.assert_called_once_with("/123/engage/account")

    @pytest.mark.asyncio
    async def test_create_account(self, ad_accounts_resource, mock_http, sample_account_data):
        """Test creating a new account for a customer."""
        mock_http.post.return_value = {"data": sample_account_data}

        account = await ad_accounts_resource.create(customer_id=123, cpmAmount=350.0, active=True)

        assert isinstance(account, AdAccount)
        assert account.cpmAmount == 350.0
        assert account.active is True
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/123/engage/account"

    @pytest.mark.asyncio
    async def test_update_account(self, ad_accounts_resource, mock_http, sample_account_data):
        """Test updating an existing account."""
        updated_data = sample_account_data.copy()
        updated_data["cpmAmount"] = 400.0
        mock_http.put.return_value = {"data": updated_data}

        account = await ad_accounts_resource.update(customer_id=123, cpmAmount=400.0)

        assert isinstance(account, AdAccount)
        assert account.cpmAmount == 400.0
        mock_http.put.assert_called_once()
        call_args = mock_http.put.call_args
        assert call_args[0][0] == "/123/engage/account"

    @pytest.mark.asyncio
    async def test_delete_account(self, ad_accounts_resource, mock_http):
        """Test deleting an account."""
        mock_http.delete.return_value = None

        await ad_accounts_resource.delete(customer_id=123)

        mock_http.delete.assert_called_once_with("/123/engage/account")


class TestAdAccountModel:
    """Test suite for AdAccount model."""

    def test_create_account_model(self, sample_account_data):
        """Test creating AdAccount model from data."""
        account = AdAccount(**sample_account_data)

        assert account.cpmAmount == 350.0
        assert account.active is True
        assert account.values == {"impressions": 10000, "clicks": 250}

    def test_default_values(self):
        """Test default values for fields."""
        account = AdAccount()

        assert account.cpmAmount == 300.0
        assert account.active is True
        assert account.values is None

    def test_computed_property_is_active(self, sample_account_data):
        """Test is_active computed property."""
        account = AdAccount(**sample_account_data)
        assert account.is_active is True

        # Test inactive account
        sample_account_data["active"] = False
        inactive_account = AdAccount(**sample_account_data)
        assert inactive_account.is_active is False

    def test_serialization(self, sample_account_data):
        """Test that to_api_dict works correctly."""
        account = AdAccount(**sample_account_data)

        api_dict = account.to_api_dict(cpmAmount=400.0)

        # All fields should be present (no frozen fields in this model)
        assert "cpmAmount" in api_dict
        assert api_dict["cpmAmount"] == 400.0
        assert "active" in api_dict


class TestPartialAdAccountModel:
    """Test suite for PartialAdAccount model."""

    def test_create_partial_account(self):
        """Test creating PartialAdAccount with minimal data."""
        partial = PartialAdAccount(cpmAmount=300.0, active=True)

        assert partial.cpmAmount == 300.0
        assert partial.active is True

    def test_default_values(self):
        """Test default values for partial model."""
        partial = PartialAdAccount()

        assert partial.cpmAmount == 300.0
        assert partial.active is True

    @pytest.mark.asyncio
    async def test_fetch_full_raises_not_implemented(self):
        """Test that fetch_full raises NotImplementedError."""
        # Mock the client
        mock_client = Mock()

        # Create partial with client reference
        partial = PartialAdAccount(cpmAmount=300.0, _client=mock_client)

        with pytest.raises(NotImplementedError, match="requires customer_id parameter"):
            await partial.fetch_full()

    @pytest.mark.asyncio
    async def test_edit_raises_not_implemented(self):
        """Test that edit raises NotImplementedError."""
        # Mock the client
        mock_client = Mock()

        # Create partial with client reference
        partial = PartialAdAccount(cpmAmount=300.0, _client=mock_client)

        with pytest.raises(NotImplementedError, match="requires customer_id parameter"):
            await partial.edit(active=False)
