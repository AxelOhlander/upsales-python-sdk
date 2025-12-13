"""
Unit tests for multi-field sort parameter encoding (P2 #16).

This tests whether:
1. Single sort works: sort="name" → sort=name
2. Multi-sort with list works: sort=["name", "-id"] → sort=name&sort=-id
3. If needed, whether we should convert to comma-joined: sort="name,-id"
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.resources.users import UsersResource


class TestMultiSortEncoding:
    """Test sort parameter encoding for single and multi-field sorts."""

    @pytest.mark.asyncio
    async def test_single_sort_encoding(self, httpx_mock: HTTPXMock):
        """Test that single sort is passed correctly as sort=field."""
        sample_users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "regDate": "2025-01-01T00:00:00.000Z",
                "administrator": 0,
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "active": 1,
                "regDate": "2025-01-02T00:00:00.000Z",
                "administrator": 0,
            },
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=name",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort="name")

            assert len(results) == 2
            # Verify the correct URL was called
            request = httpx_mock.get_requests()[0]
            url_str = str(request.url)
            assert "sort=name" in url_str
            # Ensure there's only one sort parameter (no repeated sort)
            assert url_str.count("sort=") == 1

    @pytest.mark.asyncio
    async def test_multi_sort_repeated_params(self, httpx_mock: HTTPXMock):
        """Test that multi-sort with list creates repeated params: sort=name&sort=-id."""
        sample_users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "regDate": "2025-01-01T00:00:00.000Z",
                "administrator": 0,
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "active": 1,
                "regDate": "2025-01-02T00:00:00.000Z",
                "administrator": 0,
            },
        ]

        # Expected format: httpx passes list as repeated params
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=name&sort=-id",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort=["name", "-id"])

            assert len(results) == 2
            # Verify the URL has repeated sort params
            request = httpx_mock.get_requests()[0]
            url_str = str(request.url)
            assert "sort=name" in url_str
            assert "sort=-id" in url_str

    @pytest.mark.asyncio
    async def test_multi_sort_descending(self, httpx_mock: HTTPXMock):
        """Test multi-sort with descending order (- prefix)."""
        sample_users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "regDate": "2025-01-01T00:00:00.000Z",
                "administrator": 0,
            },
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=-name&sort=id",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort=["-name", "id"])

            assert len(results) == 1
            request = httpx_mock.get_requests()[0]
            url_str = str(request.url)
            assert "sort=-name" in url_str
            assert "sort=id" in url_str

    @pytest.mark.asyncio
    async def test_search_with_multi_sort(self, httpx_mock: HTTPXMock):
        """Test that search() also supports multi-sort."""
        sample_users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "regDate": "2025-01-01T00:00:00.000Z",
                "administrator": 0,
            },
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&limit=100&offset=0&sort=name&sort=-id",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=1, sort=["name", "-id"])

            assert len(results) == 1
            request = httpx_mock.get_requests()[0]
            url_str = str(request.url)
            assert "active=1" in url_str
            assert "sort=name" in url_str
            assert "sort=-id" in url_str

    @pytest.mark.asyncio
    async def test_list_all_with_multi_sort(self, httpx_mock: HTTPXMock):
        """Test that list_all() also supports multi-sort."""
        sample_users = [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "regDate": "2025-01-01T00:00:00.000Z",
                "administrator": 0,
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "active": 1,
                "regDate": "2025-01-02T00:00:00.000Z",
                "administrator": 0,
            },
        ]

        # Mock first page (returns 2 items with limit 100, so no more pages)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=name&sort=-id",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": sample_users,
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list_all(sort=["name", "-id"])

            assert len(results) == 2
            request = httpx_mock.get_requests()[0]
            url_str = str(request.url)
            assert "sort=name" in url_str
            assert "sort=-id" in url_str
