"""Unit tests for client IP info resource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.client import Upsales
from upsales.models.client_ip_info import ClientIpInfo


@pytest.fixture
def client() -> Upsales:
    """Create test client."""
    return Upsales(token="test_token")


@pytest.mark.asyncio
async def test_check_client_ip_info(httpx_mock: HTTPXMock, client: Upsales) -> None:
    """Test checking client IP information."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/clientIpInfo",
        method="POST",
        json={
            "error": None,
            "data": {
                "target": ["192.168.1.1"],
                "allowed": True,
                "message": "IP is allowed",
            },
        },
    )

    result = await client.client_ip_info.check(target=["192.168.1.1"])

    assert isinstance(result, ClientIpInfo)
    assert result.allowed is True
    assert result.message == "IP is allowed"
    assert result.target == ["192.168.1.1"]


@pytest.mark.asyncio
async def test_check_client_ip_blocked(httpx_mock: HTTPXMock, client: Upsales) -> None:
    """Test checking blocked IP."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/clientIpInfo",
        method="POST",
        json={
            "error": None,
            "data": {
                "target": ["10.0.0.1"],
                "allowed": False,
                "message": "IP is blocked for tracking",
            },
        },
    )

    result = await client.client_ip_info.check(target=["10.0.0.1"])

    assert isinstance(result, ClientIpInfo)
    assert result.allowed is False
    assert result.message == "IP is blocked for tracking"


@pytest.mark.asyncio
async def test_check_multiple_ips(httpx_mock: HTTPXMock, client: Upsales) -> None:
    """Test checking multiple IPs at once."""
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/function/clientIpInfo",
        method="POST",
        json={
            "error": None,
            "data": {
                "target": ["192.168.1.1", "10.0.0.1", "172.16.0.1"],
                "allowed": True,
                "message": None,
            },
        },
    )

    result = await client.client_ip_info.check(target=["192.168.1.1", "10.0.0.1", "172.16.0.1"])

    assert isinstance(result, ClientIpInfo)
    assert result.allowed is True
    assert len(result.target) == 3


@pytest.mark.asyncio
async def test_create_not_supported(client: Upsales) -> None:
    """Test that create operation is not supported."""
    with pytest.raises(NotImplementedError, match="does not support create"):
        await client.client_ip_info.create(target=["192.168.1.1"])


@pytest.mark.asyncio
async def test_get_not_supported(client: Upsales) -> None:
    """Test that get operation is not supported."""
    with pytest.raises(NotImplementedError, match="does not support get"):
        await client.client_ip_info.get(1)


@pytest.mark.asyncio
async def test_list_not_supported(client: Upsales) -> None:
    """Test that list operation is not supported."""
    with pytest.raises(NotImplementedError, match="does not support list"):
        await client.client_ip_info.list()


@pytest.mark.asyncio
async def test_update_not_supported(client: Upsales) -> None:
    """Test that update operation is not supported."""
    with pytest.raises(NotImplementedError, match="does not support update"):
        await client.client_ip_info.update(1, allowed=False)


@pytest.mark.asyncio
async def test_delete_not_supported(client: Upsales) -> None:
    """Test that delete operation is not supported."""
    with pytest.raises(NotImplementedError, match="does not support delete"):
        await client.client_ip_info.delete(1)


@pytest.mark.asyncio
async def test_model_edit_not_supported(client: Upsales) -> None:
    """Test that model edit operation is not supported."""
    info = ClientIpInfo(target=["192.168.1.1"], allowed=True, message=None)

    with pytest.raises(NotImplementedError, match="does not support edit"):
        await info.edit()
