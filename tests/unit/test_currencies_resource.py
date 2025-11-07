"""
Unit tests for CurrenciesResource.

Note: Currencies endpoint is different from standard CRUD resources:
- No ID field (identified by ISO code)
- Read-only (no create/update/delete)
- Only supports list() and helper methods

Tests cover:
- list() - Get all currencies
- get_by_iso() - Get specific currency by ISO code
- get_master_currency() - Get the master currency
- get_active_currencies() - Get all active currencies
- convert() - Convert between currencies
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.currency import Currency, PartialCurrency
from upsales.resources.currencies import CurrenciesResource


class TestCurrenciesResource:
    """Test CurrenciesResource operations."""

    @pytest.fixture
    def sample_currencies(self):
        """Sample currencies data for testing."""
        return [
            {
                "iso": "SEK",
                "rate": 1.0,
                "masterCurrency": True,
                "active": True,
            },
            {
                "iso": "USD",
                "rate": 0.106791513,
                "masterCurrency": False,
                "active": True,
            },
            {
                "iso": "EUR",
                "rate": 0.091776799,
                "masterCurrency": False,
                "active": True,
            },
            {
                "iso": "GBP",
                "rate": 0.079123456,
                "masterCurrency": False,
                "active": False,
            },
        ]

    @pytest.fixture
    def sample_api_response(self, sample_currencies):
        """Sample API response."""
        return {"error": None, "data": sample_currencies}

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test listing all currencies."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            results = await resource.list()

            assert isinstance(results, list)
            assert len(results) == 4
            assert all(isinstance(item, Currency) for item in results)
            assert results[0].iso == "SEK"
            assert results[0].is_master is True
            assert results[1].iso == "USD"

    @pytest.mark.asyncio
    async def test_get_by_iso_found(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting a specific currency by ISO code (found)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            result = await resource.get_by_iso("USD")

            assert result is not None
            assert isinstance(result, Currency)
            assert result.iso == "USD"
            assert result.rate == 0.106791513
            assert result.masterCurrency is False

    @pytest.mark.asyncio
    async def test_get_by_iso_not_found(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting a specific currency by ISO code (not found)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            result = await resource.get_by_iso("ZZZ")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_master_currency(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting the master currency."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            result = await resource.get_master_currency()

            assert result is not None
            assert isinstance(result, Currency)
            assert result.iso == "SEK"
            assert result.is_master is True
            assert result.rate == 1.0

    @pytest.mark.asyncio
    async def test_get_active_currencies(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting all active currencies."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            results = await resource.get_active_currencies()

            assert isinstance(results, list)
            assert len(results) == 3  # SEK, USD, EUR (GBP is inactive)
            assert all(item.is_active for item in results)
            assert all(item.iso != "GBP" for item in results)

    @pytest.mark.asyncio
    async def test_convert_same_currency(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting between same currency."""
        # convert() calls get_by_iso() twice, each calling list()
        # So we need 2 mocked responses
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            result = await resource.convert(100, "USD", "USD")

            assert result == 100.0

    @pytest.mark.asyncio
    async def test_convert_to_master(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting from non-master to master currency."""
        # convert() calls get_by_iso() twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            # 100 USD * 0.106791513 = 10.6791513 SEK
            # Then 10.6791513 / 1.0 = 10.6791513 SEK
            result = await resource.convert(100, "USD", "SEK")

            assert result == pytest.approx(10.6791513, rel=1e-6)

    @pytest.mark.asyncio
    async def test_convert_from_master(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting from master to non-master currency."""
        # convert() calls get_by_iso() twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            # 100 SEK * 1.0 = 100 SEK (master)
            # Then 100 / 0.106791513 = 936.41 USD
            result = await resource.convert(100, "SEK", "USD")

            assert result == pytest.approx(936.41, rel=0.01)

    @pytest.mark.asyncio
    async def test_convert_between_non_masters(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting between two non-master currencies."""
        # convert() calls get_by_iso() twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            # 100 USD * 0.106791513 = 10.6791513 SEK
            # Then 10.6791513 / 0.091776799 = 116.37 EUR
            result = await resource.convert(100, "USD", "EUR")

            assert result == pytest.approx(116.37, rel=0.01)

    @pytest.mark.asyncio
    async def test_convert_invalid_from_currency(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting from invalid currency."""
        # convert() still calls get_by_iso() twice even if first currency not found
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            with pytest.raises(ValueError, match="Currency not found: ZZZ"):
                await resource.convert(100, "ZZZ", "USD")

    @pytest.mark.asyncio
    async def test_convert_invalid_to_currency(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test converting to invalid currency."""
        # convert() calls get_by_iso() twice - first succeeds, second fails
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/currencies",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = CurrenciesResource(http)
            with pytest.raises(ValueError, match="Currency not found: ZZZ"):
                await resource.convert(100, "USD", "ZZZ")


class TestCurrencyModel:
    """Test Currency model properties and methods."""

    @pytest.fixture
    def sample_currency(self):
        """Sample currency for testing."""
        return Currency(iso="USD", rate=0.106791513, masterCurrency=False, active=True)

    @pytest.fixture
    def master_currency(self):
        """Sample master currency for testing."""
        return Currency(iso="SEK", rate=1.0, masterCurrency=True, active=True)

    def test_is_master_property(self, master_currency, sample_currency):
        """Test is_master computed property."""
        assert master_currency.is_master is True
        assert sample_currency.is_master is False

    def test_is_active_property(self, sample_currency):
        """Test is_active computed property."""
        assert sample_currency.is_active is True

        inactive = Currency(iso="GBP", rate=0.079, masterCurrency=False, active=False)
        assert inactive.is_active is False


class TestPartialCurrencyModel:
    """Test PartialCurrency model."""

    def test_partial_currency_creation(self):
        """Test creating a PartialCurrency."""
        partial = PartialCurrency(iso="USD")

        assert partial.iso == "USD"
        assert isinstance(partial, PartialCurrency)
