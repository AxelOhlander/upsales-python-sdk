"""Unit tests for EngageCreditTransactionsResource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.models import EngageCreditTransaction, PartialEngageCreditTransaction


@pytest.fixture
def mock_transaction_data() -> dict:
    """Mock transaction data for testing."""
    return {
        "id": 1,
        "value": 100.0,
        "description": "Ad credit purchase",
        "date": "2025-01-15",
        "campaignId": 456,
        "custom": [{"fieldId": 11, "value": "test"}],
    }


@pytest.fixture
def mock_transaction_list_data(mock_transaction_data: dict) -> list[dict]:
    """Mock transaction list data for testing."""
    return [
        mock_transaction_data,
        {
            "id": 2,
            "value": 200.0,
            "description": "Second transaction",
            "date": "2025-01-16",
            "campaignId": 457,
            "custom": [],
        },
    ]


class TestEngageCreditTransactionsResource:
    """Tests for EngageCreditTransactionsResource."""

    @pytest.mark.asyncio
    async def test_get_transaction(
        self, client: Upsales, httpx_mock: HTTPXMock, mock_transaction_data: dict
    ):
        """Test getting a single transaction."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": mock_transaction_data, "error": None},
        )

        transaction = await client.engage_credit_transactions.get(1)

        assert isinstance(transaction, EngageCreditTransaction)
        assert transaction.id == 1
        assert transaction.value == 100.0
        assert transaction.description == "Ad credit purchase"
        assert transaction.date == "2025-01-15"
        assert transaction.campaignId == 456
        assert len(transaction.custom) == 1

    @pytest.mark.asyncio
    async def test_list_transactions(
        self,
        client: Upsales,
        httpx_mock: HTTPXMock,
        mock_transaction_list_data: list[dict],
    ):
        """Test listing transactions."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction?limit=100&offset=0",
            json={
                "data": mock_transaction_list_data,
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
            },
        )

        transactions = await client.engage_credit_transactions.list()

        assert len(transactions) == 2
        assert all(isinstance(t, EngageCreditTransaction) for t in transactions)
        assert transactions[0].id == 1
        assert transactions[1].id == 2

    @pytest.mark.asyncio
    async def test_create_transaction(
        self, client: Upsales, httpx_mock: HTTPXMock, mock_transaction_data: dict
    ):
        """Test creating a transaction."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction",
            json={"data": mock_transaction_data, "error": None},
        )

        transaction = await client.engage_credit_transactions.create(
            value=100.0, description="Ad credit purchase"
        )

        assert isinstance(transaction, EngageCreditTransaction)
        assert transaction.id == 1
        assert transaction.value == 100.0
        assert transaction.description == "Ad credit purchase"

    @pytest.mark.asyncio
    async def test_update_transaction(
        self, client: Upsales, httpx_mock: HTTPXMock, mock_transaction_data: dict
    ):
        """Test updating a transaction."""
        updated_data = {**mock_transaction_data, "description": "Updated description"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": updated_data, "error": None},
        )

        transaction = await client.engage_credit_transactions.update(
            1, description="Updated description"
        )

        assert isinstance(transaction, EngageCreditTransaction)
        assert transaction.id == 1
        assert transaction.description == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_transaction(
        self, client: Upsales, httpx_mock: HTTPXMock
    ):
        """Test deleting a transaction."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": {}, "error": None},
        )

        result = await client.engage_credit_transactions.delete(1)

        # Delete returns the raw response
        assert result is not None

    @pytest.mark.asyncio
    async def test_transaction_edit_method(
        self, client: Upsales, httpx_mock: HTTPXMock, mock_transaction_data: dict
    ):
        """Test transaction.edit() instance method."""
        # Mock GET
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": mock_transaction_data, "error": None},
        )

        transaction = await client.engage_credit_transactions.get(1)
        transaction._client = client

        # Mock UPDATE
        updated_data = {**mock_transaction_data, "value": 150.0}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": updated_data, "error": None},
        )

        updated = await transaction.edit(value=150.0)

        assert isinstance(updated, EngageCreditTransaction)
        assert updated.value == 150.0

    @pytest.mark.asyncio
    async def test_custom_fields_access(
        self, client: Upsales, httpx_mock: HTTPXMock, mock_transaction_data: dict
    ):
        """Test accessing custom fields."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/engage/creditTransaction/1",
            json={"data": mock_transaction_data, "error": None},
        )

        transaction = await client.engage_credit_transactions.get(1)

        assert transaction.custom_fields[11] == "test"


class TestPartialEngageCreditTransaction:
    """Tests for PartialEngageCreditTransaction."""

    def test_partial_creation(self):
        """Test creating a partial transaction."""
        partial = PartialEngageCreditTransaction(
            id=1, value=100.0, description="Ad credit purchase"
        )

        assert partial.id == 1
        assert partial.value == 100.0
        assert partial.description == "Ad credit purchase"
