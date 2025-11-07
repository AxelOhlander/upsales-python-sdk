"""
Tests for BaseResource - the foundation for all resource managers.

BaseResource provides CRUD operations that are inherited by all endpoint resources.
These tests ensure the foundation is solid before replicating to 20+ endpoints.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.http import HTTPClient
from upsales.models.user import User
from upsales.resources.users import UsersResource


class TestBaseResourceCRUD:
    """Test base CRUD operations inherited by all resources."""

    @pytest.fixture
    def sample_user(self):
        """Sample user data for testing."""
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01T00:00:00Z",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_create_resource(self, httpx_mock: HTTPXMock, sample_user):
        """Test create() creates new resource and returns full object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users",
            method="POST",
            json={"error": None, "data": sample_user},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.create(
                name="John Doe",
                email="john@example.com",
                active=1,
            )

            assert isinstance(result, User)
            assert result.id == 1
            assert result.name == "John Doe"
            assert result.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_get_single_resource(self, httpx_mock: HTTPXMock, sample_user):
        """Test get() retrieves single resource by ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={"error": None, "data": sample_user},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.get(1)

            assert isinstance(result, User)
            assert result.id == 1
            assert result.name == "John Doe"

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, httpx_mock: HTTPXMock, sample_user):
        """Test list() with pagination parameters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=10&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 10, "offset": 0},
                "data": [
                    sample_user,
                    {**sample_user, "id": 2, "name": "Jane Doe"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(user, User) for user in results)
            assert results[0].id == 1
            assert results[1].id == 2

    @pytest.mark.asyncio
    async def test_list_with_filters(self, httpx_mock: HTTPXMock, sample_user):
        """Test list() with additional filter parameters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&active=1",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, offset=0, active=1)

            assert len(results) == 1
            assert results[0].active == 1

    @pytest.mark.asyncio
    async def test_update_resource(self, httpx_mock: HTTPXMock, sample_user):
        """Test update() modifies resource and returns updated object."""
        updated_data = {**sample_user, "name": "John Updated"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.update(1, name="John Updated")

            assert isinstance(result, User)
            assert result.id == 1
            assert result.name == "John Updated"

    @pytest.mark.asyncio
    async def test_delete_resource(self, httpx_mock: HTTPXMock):
        """Test delete() removes resource."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.delete(1)

            # delete() returns the response from HTTPClient.delete()
            # which returns the full response dict with "error" and "data"
            assert isinstance(result, dict)
            assert result["data"]["success"] is True


class TestBaseResourceListAll:
    """Test list_all() auto-pagination functionality."""

    @pytest.fixture
    def sample_user(self):
        """Sample user for pagination tests."""
        return {
            "id": 1,
            "name": "User",
            "email": "user@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_user):
        """Test list_all() with single page (results < batch_size)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0",
            json={"error": None, "data": [sample_user] * 50},  # Less than 100
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list_all(batch_size=100)

            assert len(results) == 50
            # Should only make 1 request
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multiple_pages(self, httpx_mock: HTTPXMock, sample_user):
        """Test list_all() fetches multiple pages."""
        # Page 1: Full batch (100 items)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0",
            json={"error": None, "data": [{**sample_user, "id": i} for i in range(1, 101)]},
        )
        # Page 2: Partial batch (50 items - last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=100",
            json={"error": None, "data": [{**sample_user, "id": i} for i in range(101, 151)]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list_all(batch_size=100)

            assert len(results) == 150
            # Should make 2 requests
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_list_all_with_filters(self, httpx_mock: HTTPXMock, sample_user):
        """Test list_all() with filter parameters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&active=1",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list_all(active=1)

            assert len(results) == 1
            assert results[0].active == 1


class TestBaseResourceBulkOperations:
    """Test bulk operations with concurrency control."""

    @pytest.fixture
    def sample_user(self):
        """Sample user for bulk tests."""
        return {
            "id": 1,
            "name": "User",
            "email": "user@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_bulk_update_success(self, httpx_mock: HTTPXMock, sample_user):
        """Test bulk_update() with all successful updates."""
        # Mock 5 successful updates
        for i in range(1, 6):
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/users/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_user, "id": i, "active": 0}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3, 4, 5],
                data={"active": 0},
                max_concurrent=10,
            )

            assert len(results) == 5
            assert all(isinstance(user, User) for user in results)
            assert all(user.active == 0 for user in results)

    @pytest.mark.asyncio
    async def test_bulk_update_partial_failure(self, httpx_mock: HTTPXMock, sample_user):
        """Test bulk_update() with some failures raises ExceptionGroup."""
        from upsales.exceptions import NotFoundError

        # Mock 2 successful, 1 failure
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="PUT",
            json={"error": None, "data": {**sample_user, "id": 1}},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/2",
            method="PUT",
            status_code=404,
            json={"error": "User not found", "data": None},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/3",
            method="PUT",
            json={"error": None, "data": {**sample_user, "id": 3}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)

            # Should raise ExceptionGroup with errors
            with pytest.raises(ExceptionGroup) as exc_info:
                await resource.bulk_update(
                    ids=[1, 2, 3],
                    data={"active": 0},
                )

            # Verify exception group contains the failure
            assert len(exc_info.value.exceptions) == 1
            assert isinstance(exc_info.value.exceptions[0], NotFoundError)

    @pytest.mark.asyncio
    async def test_bulk_delete_success(self, httpx_mock: HTTPXMock):
        """Test bulk_delete() with all successful deletes."""
        # Mock 3 successful deletes
        for i in range(1, 4):
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/users/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3
            assert all(isinstance(r, dict) for r in results)
            assert all(r["data"]["success"] is True for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete_with_failures(self, httpx_mock: HTTPXMock):
        """Test bulk_delete() with failures raises ExceptionGroup."""
        from upsales.exceptions import NotFoundError

        # Mock 1 success, 1 failure
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/999",
            method="DELETE",
            status_code=404,
            json={"error": "User not found", "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)

            with pytest.raises(ExceptionGroup) as exc_info:
                await resource.bulk_delete(ids=[1, 999])

            assert len(exc_info.value.exceptions) == 1
            assert isinstance(exc_info.value.exceptions[0], NotFoundError)


class TestBaseResourceSearch:
    """Test search() functionality with filter operators."""

    @pytest.fixture
    def sample_user(self):
        """Sample user for search tests."""
        return {
            "id": 1,
            "name": "Active User",
            "email": "active@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_search_simple_filter(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with simple equality filter."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=1)

            assert len(results) == 1
            assert results[0].active == 1

    @pytest.mark.asyncio
    async def test_search_multiple_filters(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with multiple filter criteria."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&administrator=0&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=1, administrator=0)

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_no_results(self, httpx_mock: HTTPXMock):
        """Test search() returns empty list when no matches."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=999&limit=100&offset=0",
            json={"error": None, "data": []},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=999)

            assert results == []


class TestBaseResourceNaturalOperators:
    """Test natural operator syntax in search() method."""

    @pytest.fixture
    def sample_user(self):
        """Sample user for operator tests."""
        return {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_search_greater_than_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with > (greater than) natural operator."""
        # Natural operator ">" should transform to "gt:"
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=gt%3A5&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id=">5")

            assert len(results) == 1
            # Verify transformation happened correctly
            request = httpx_mock.get_requests()[0]
            assert "id=gt%3A5" in str(request.url)  # %3A is URL-encoded ":"

    @pytest.mark.asyncio
    async def test_search_greater_than_equals_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with >= (greater than or equals) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=gte%3A5&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id=">=5")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_less_than_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with < (less than) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=lt%3A10&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id="<10")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_less_than_equals_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with <= (less than or equals) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=lte%3A10&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id="<=10")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_equals_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with = (equals) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?name=eq%3AJohn&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(name="=John")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_not_equals_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with != (not equals) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?administrator=ne%3A1&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(administrator="!=1")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_natural_operators_with_dates(self, httpx_mock: HTTPXMock, sample_user):
        """Test natural operators work with date values."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?regDate=gte%3A2024-01-01&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(regDate=">=2024-01-01")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_natural_in_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test natural = operator with multiple values (IN)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=eq%3A1%2C2%2C3&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id="=1,2,3")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_backward_compatibility(self, httpx_mock: HTTPXMock, sample_user):
        """Test backward compatibility - API syntax still works."""
        # Old syntax should pass through unchanged
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=gt%3A5&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(id="gt:5")  # Old syntax

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_mixed_syntax(self, httpx_mock: HTTPXMock, sample_user):
        """Test mixing natural and API syntax in same search."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?id=gte%3A5&administrator=ne%3A1&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(
                id=">=5",  # Natural
                administrator="ne:1",  # API syntax
            )

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_substring_operator(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with * (substring) natural operator."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?name=src%3AJohn&limit=100&offset=0",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(name="*John")

            assert len(results) == 1
            # Verify transformation: "*John" → "src:John"
            request = httpx_mock.get_requests()[0]
            assert "name=src%3AJohn" in str(request.url)


class TestBaseResourceFieldSelection:
    """Test field selection feature for optimized queries."""

    @pytest.fixture
    def sample_user(self):
        """Sample user for field selection tests."""
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_list_with_field_selection(self, httpx_mock: HTTPXMock, sample_user):
        """Test list() with fields parameter."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&f%5B%5D=id&f%5B%5D=name",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, fields=["id", "name"])

            assert len(results) == 1
            # Verify f[] parameters added
            request = httpx_mock.get_requests()[0]
            assert "f%5B%5D=id" in str(request.url)  # f[]=id (URL encoded)
            assert "f%5B%5D=name" in str(request.url)

    @pytest.mark.asyncio
    async def test_list_with_field_selection_and_filters(self, httpx_mock: HTTPXMock, sample_user):
        """Test list() with both fields and filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&active=1&f%5B%5D=id&f%5B%5D=name",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, active=1, fields=["id", "name"])

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_list_all_with_field_selection(self, httpx_mock: HTTPXMock, sample_user):
        """Test list_all() with field selection."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&f%5B%5D=id&f%5B%5D=name",
            json={"error": None, "data": [sample_user] * 50},  # Less than batch_size
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list_all(fields=["id", "name"])

            assert len(results) == 50

    @pytest.mark.asyncio
    async def test_search_with_field_selection(self, httpx_mock: HTTPXMock, sample_user):
        """Test search() with field selection."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&limit=100&offset=0&f%5B%5D=id&f%5B%5D=name",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=1, fields=["id", "name"])

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_substring_with_field_selection(self, httpx_mock: HTTPXMock, sample_user):
        """Test combining substring search with field selection."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?name=src%3AJohn&limit=100&offset=0&f%5B%5D=id&f%5B%5D=name&f%5B%5D=email",
            json={"error": None, "data": [sample_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(name="*John", fields=["id", "name", "email"])

            assert len(results) == 1


class TestBaseResourceSorting:
    """Test sorting functionality."""

    @pytest.fixture
    def sample_users(self):
        """Sample users for sorting tests."""
        return [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": 1,
                "administrator": 0,
                "regDate": "2025-01-01",
                "custom": [],
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "active": 1,
                "administrator": 0,
                "regDate": "2025-01-02",
                "custom": [],
            },
        ]

    @pytest.mark.asyncio
    async def test_list_with_sort_ascending(self, httpx_mock: HTTPXMock, sample_users):
        """Test list() with ascending sort."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=name",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort="name")

            assert len(results) == 2
            # Verify sort parameter added
            request = httpx_mock.get_requests()[0]
            assert "sort=name" in str(request.url)

    @pytest.mark.asyncio
    async def test_list_with_sort_descending(self, httpx_mock: HTTPXMock, sample_users):
        """Test list() with descending sort."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=-regDate",
            json={"error": None, "data": sample_users[::-1]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort="-regDate")

            assert len(results) == 2
            # Verify descending sort parameter
            request = httpx_mock.get_requests()[0]
            assert "sort=-regDate" in str(request.url)

    @pytest.mark.asyncio
    async def test_list_with_multi_sort(self, httpx_mock: HTTPXMock, sample_users):
        """Test list() with multiple sort fields."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&sort=name&sort=-id",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, sort=["name", "-id"])

            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_with_sort(self, httpx_mock: HTTPXMock, sample_users):
        """Test search() with sorting."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&limit=100&offset=0&sort=-regDate",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.search(active=1, sort="-regDate")

            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_list_with_fields_and_sort(self, httpx_mock: HTTPXMock, sample_users):
        """Test list() with both field selection and sorting."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0&f%5B%5D=id&f%5B%5D=name&sort=-regDate",
            json={"error": None, "data": sample_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.list(limit=100, fields=["id", "name"], sort="-regDate")

            assert len(results) == 2


class TestBaseResourceClientReference:
    """Test that resources properly pass client reference to models."""

    @pytest.fixture
    def sample_user(self):
        """Sample user data."""
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": 1,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_returns_model_with_client(self, httpx_mock: HTTPXMock, sample_user):
        """Test that get() returns model with _client reference."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={"error": None, "data": sample_user},
        )

        async with Upsales(token="test_token") as upsales:
            user = await upsales.users.get(1)

            # Verify _client reference is set
            assert user._client is not None
            assert user._client == upsales

    @pytest.mark.asyncio
    async def test_list_returns_models_with_client(self, httpx_mock: HTTPXMock, sample_user):
        """Test that list() returns models with _client reference."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0",
            json={"error": None, "data": [sample_user, {**sample_user, "id": 2}]},
        )

        async with Upsales(token="test_token") as upsales:
            users = await upsales.users.list()

            # Verify all models have _client reference
            assert all(user._client is not None for user in users)
            assert all(user._client == upsales for user in users)


# Coverage verification
# Run: uv run pytest tests/unit/test_base_resource.py -v --cov=upsales/resources/base.py --cov-report=term-missing
# Target: 85%+ coverage
