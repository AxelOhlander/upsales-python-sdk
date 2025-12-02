"""
Unit tests for ClientIpsResource.

Tests the ClientIps resource manager's CRUD operations and custom methods.
Uses pytest-httpx for mocking HTTP calls.
"""

import pytest
from httpx import Response

from upsales import Upsales
from upsales.exceptions import NotFoundError
from upsales.models import ClientIp, PartialClientIp


@pytest.mark.asyncio
class TestClientIpsResource:
    """Test ClientIps resource CRUD operations."""

    async def test_get_client_ip(self, httpx_mock, base_url: str):
        """Test getting a single client IP rule."""
        # Mock successful response
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "allow",
                    "userId": 10,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            ip_rule = await upsales.client_ips.get(1)

            assert isinstance(ip_rule, ClientIp)
            assert ip_rule.id == 1
            assert ip_rule.ipAddress == "192.168.1.1"
            assert ip_rule.rule == "allow"
            assert ip_rule.userId == 10
            assert ip_rule.sortIdx == 0
            assert ip_rule.clientId == 100

    async def test_get_client_ip_not_found(self, httpx_mock, base_url: str):
        """Test getting non-existent client IP rule raises NotFoundError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps/999",
            status_code=404,
            json={"error": "Not found"},
        )

        async with Upsales(token="test_token") as upsales:
            with pytest.raises(NotFoundError):
                await upsales.client_ips.get(999)

    async def test_list_client_ips(self, httpx_mock, base_url: str):
        """Test listing client IP rules with pagination."""
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps?limit=10&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 10, "offset": 0},
                "data": [
                    {
                        "id": 1,
                        "ipAddress": "192.168.1.1",
                        "rule": "allow",
                        "userId": 10,
                        "sortIdx": 0,
                        "clientId": 100,
                    },
                    {
                        "id": 2,
                        "ipAddress": "10.0.0.1",
                        "rule": "deny",
                        "userId": 20,
                        "sortIdx": 1,
                        "clientId": 100,
                    },
                ],
            },
        )

        async with Upsales(token="test_token") as upsales:
            ip_rules = await upsales.client_ips.list(limit=10)

            assert len(ip_rules) == 2
            assert all(isinstance(rule, ClientIp) for rule in ip_rules)
            assert ip_rules[0].id == 1
            assert ip_rules[0].rule == "allow"
            assert ip_rules[1].id == 2
            assert ip_rules[1].rule == "deny"

    async def test_create_client_ip(self, httpx_mock, base_url: str):
        """Test creating a new client IP rule."""
        httpx_mock.add_response(
            method="POST",
            url=f"{base_url}/clientIps",
            json={
                "error": None,
                "data": {
                    "id": 3,
                    "ipAddress": "172.16.0.1",
                    "rule": "allow",
                    "userId": 30,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            new_ip = await upsales.client_ips.create(
                ipAddress="172.16.0.1",
                rule="allow",
                userId=30,
            )

            assert isinstance(new_ip, ClientIp)
            assert new_ip.id == 3
            assert new_ip.ipAddress == "172.16.0.1"
            assert new_ip.rule == "allow"
            assert new_ip.userId == 30

    async def test_update_client_ip(self, httpx_mock, base_url: str):
        """Test updating an existing client IP rule."""
        httpx_mock.add_response(
            method="PUT",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "deny",  # Changed
                    "userId": 10,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            updated_ip = await upsales.client_ips.update(1, rule="deny")

            assert isinstance(updated_ip, ClientIp)
            assert updated_ip.id == 1
            assert updated_ip.rule == "deny"

    async def test_delete_client_ip(self, httpx_mock, base_url: str):
        """Test deleting a client IP rule."""
        httpx_mock.add_response(
            method="DELETE",
            url=f"{base_url}/clientIps/1",
            json={"error": None, "data": {}},
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.client_ips.delete(1)
            assert result == {"error": None, "data": {}}

    async def test_get_by_user(self, httpx_mock, base_url: str):
        """Test getting all IP rules for a specific user."""
        # list_all starts with limit=100, offset=0
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps?userId=10&limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [
                    {
                        "id": 1,
                        "ipAddress": "192.168.1.1",
                        "rule": "allow",
                        "userId": 10,
                        "sortIdx": 0,
                        "clientId": 100,
                    },
                    {
                        "id": 4,
                        "ipAddress": "10.0.0.5",
                        "rule": "allow",
                        "userId": 10,
                        "sortIdx": 1,
                        "clientId": 100,
                    },
                ],
            },
        )

        async with Upsales(token="test_token") as upsales:
            user_ips = await upsales.client_ips.get_by_user(10)

            assert len(user_ips) == 2
            assert all(ip.userId == 10 for ip in user_ips)
            assert user_ips[0].ipAddress == "192.168.1.1"
            assert user_ips[1].ipAddress == "10.0.0.5"

    async def test_client_ip_edit_method(self, httpx_mock, base_url: str):
        """Test ClientIp.edit() instance method."""
        # Mock get
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "allow",
                    "userId": 10,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        # Mock update
        httpx_mock.add_response(
            method="PUT",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "deny",
                    "userId": 10,
                    "sortIdx": 5,
                    "clientId": 100,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            ip_rule = await upsales.client_ips.get(1)
            updated = await ip_rule.edit(rule="deny", sortIdx=5)

            assert isinstance(updated, ClientIp)
            assert updated.id == 1
            assert updated.rule == "deny"
            assert updated.sortIdx == 5

    async def test_partial_client_ip_fetch_full(self, httpx_mock, base_url: str):
        """Test PartialClientIp.fetch_full() method."""
        # Mock get full
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "allow",
                    "userId": 10,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            partial = PartialClientIp(id=1, ipAddress="192.168.1.1", _client=upsales)
            full = await partial.fetch_full()

            assert isinstance(full, ClientIp)
            assert full.id == 1
            assert full.rule == "allow"
            assert full.userId == 10

    async def test_frozen_fields_not_in_update(self, httpx_mock, base_url: str):
        """Test that frozen fields (id, clientId) are excluded from updates."""
        # Mock get
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/clientIps/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "ipAddress": "192.168.1.1",
                    "rule": "allow",
                    "userId": 10,
                    "sortIdx": 0,
                    "clientId": 100,
                },
            },
        )

        # Mock update - verify request doesn't include id or clientId
        def check_request(request):
            import json

            body = json.loads(request.content)
            assert "id" not in body
            assert "clientId" not in body
            return Response(
                200,
                json={
                    "error": None,
                    "data": {
                        "id": 1,
                        "ipAddress": "192.168.1.1",
                        "rule": "deny",
                        "userId": 10,
                        "sortIdx": 0,
                        "clientId": 100,
                    },
                },
            )

        httpx_mock.add_callback(check_request, url=f"{base_url}/clientIps/1")

        async with Upsales(token="test_token") as upsales:
            ip_rule = await upsales.client_ips.get(1)
            await ip_rule.edit(rule="deny")
