"""Unit tests for MailDomainsResource.

Tests CRUD operations for mail domains endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.mail_domains import MailDomain
from upsales.resources.mail_domains import MailDomainsResource


class TestMailDomainsResourceCRUD:
    """Test CRUD operations for MailDomainsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample mail domain data for testing."""
        return {
            "domain": "example.com",
            "dns": "valid",
            "valid": 1,
            "msg": "Domain verified successfully",
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "domain": "test.com", "valid": 0, "msg": "DNS not configured"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a mail domain."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.create(domain="example.com")

            assert isinstance(result, MailDomain)
            assert result.domain == "example.com"
            assert result.dns == "valid"
            assert result.valid == 1
            assert result.msg == "Domain verified successfully"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single mail domain by name."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains/example.com",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.get("example.com")

            assert isinstance(result, MailDomain)
            assert result.domain == "example.com"
            assert result.dns == "valid"
            assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting domain by name (convenience method)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains/example.com",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.get_by_name("example.com")

            assert isinstance(result, MailDomain)
            assert result.domain == "example.com"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing mail domains with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.list(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, MailDomain) for item in result)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a mail domain."""
        updated_data = {**sample_data, "msg": "Updated validation message"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains/example.com",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.update("example.com", msg="Updated validation message")

            assert isinstance(result, MailDomain)
            assert result.domain == "example.com"
            assert result.msg == "Updated validation message"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a mail domain."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains/example.com",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            await resource.delete("example.com")

            # No exception means success

    @pytest.mark.asyncio
    async def test_get_verified(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting verified domains."""
        page1_data = [{**sample_data, "domain": f"domain{i}.com", "valid": 1} for i in range(1, 51)]
        page2_data = [
            {**sample_data, "domain": f"domain{i}.com", "valid": 1 if i % 2 == 0 else 0}
            for i in range(51, 101)
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 100, "limit": 100, "offset": 0},
                "data": page1_data,
            },
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains?limit=100&offset=100",
            json={
                "error": None,
                "metadata": {"total": 100, "limit": 100, "offset": 100},
                "data": page2_data,
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MailDomainsResource(http)
            result = await resource.get_verified()

            assert isinstance(result, list)
            # 50 from page 1, 25 from page 2 (every other one)
            assert len(result) == 75
            assert all(isinstance(item, MailDomain) for item in result)
            assert all(item.is_valid for item in result)


class TestMailDomainModel:
    """Test MailDomain model features."""

    def test_is_valid_property(self):
        """Test is_valid computed property."""
        domain = MailDomain(
            domain="example.com",
            dns="valid",
            valid=1,
        )
        assert domain.is_valid is True

        invalid_domain = MailDomain(
            domain="test.com",
            dns="pending",
            valid=0,
        )
        assert invalid_domain.is_valid is False

    def test_default_values(self):
        """Test default values for optional fields."""
        domain = MailDomain(
            domain="example.com",
            dns="pending",
        )
        assert domain.valid == 0
        assert domain.msg is None

    @pytest.mark.asyncio
    async def test_edit_method(self, httpx_mock: HTTPXMock):
        """Test model edit method."""
        from upsales import Upsales

        updated_data = {
            "domain": "example.com",
            "dns": "valid",
            "valid": 1,
            "msg": "Updated message",
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/mail/domains/example.com",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with Upsales(token="test_token") as upsales:
            domain = MailDomain(
                domain="example.com",
                dns="valid",
                valid=1,
                msg="Old message",
                _client=upsales,
            )

            updated = await domain.edit(msg="Updated message")
            assert updated.msg == "Updated message"
            assert updated.domain == "example.com"
