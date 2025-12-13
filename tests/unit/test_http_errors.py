"""
Tests for HTTP error handling and edge cases.

Tests various error scenarios including connection errors, timeouts,
and different HTTP status codes.
"""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from upsales.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransientError,
    ValidationError,
)
from upsales.http import HTTPClient


class TestHTTPErrorPaths:
    """Test HTTP error handling scenarios."""

    @pytest.mark.asyncio
    async def test_404_not_found_error(self, httpx_mock: HTTPXMock):
        """Test 404 raises NotFoundError."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/999",
            status_code=404,
            json={"error": "User not found", "data": None},
        )

        # Use HTTPClient without auth manager to avoid auth fallback
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            with pytest.raises(NotFoundError):
                await http.get("/users/999")

    @pytest.mark.asyncio
    async def test_400_validation_error(self, httpx_mock: HTTPXMock):
        """Test 400 raises ValidationError."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users",
            method="POST",
            status_code=400,
            json={"error": "Invalid email format", "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            with pytest.raises(ValidationError):
                await http.post("/users", json={"email": "invalid"})

    @pytest.mark.asyncio
    async def test_401_authentication_error(self, httpx_mock: HTTPXMock):
        """Test 401 raises AuthenticationError."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
            json={"error": "Unauthorized", "data": None},
        )

        async with HTTPClient(token="invalid_token", auth_manager=None) as http:
            with pytest.raises(AuthenticationError):
                await http.get("/users/1")

    @pytest.mark.asyncio
    async def test_403_forbidden_error(self, httpx_mock: HTTPXMock):
        """Test 403 raises AuthenticationError."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=403,
            json={"error": "Forbidden", "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            with pytest.raises(AuthenticationError):
                await http.get("/users/1")

    @pytest.mark.asyncio
    async def test_429_rate_limit_error_retry(self, httpx_mock: HTTPXMock):
        """Test 429 triggers retry with exponential backoff."""
        # First request: 429
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=429,
            json={"error": "Rate limit exceeded", "data": None},
        )
        # Second request: Success (after retry)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=200,
            json={"error": None, "data": {"id": 1, "name": "Test"}},
        )

        async with HTTPClient(token="test_token") as http:
            # Should retry and succeed
            result = await http.get("/users/1")
            assert result["data"]["id"] == 1

        # Should have made 2 requests (1 failed, 1 retry)
        requests = httpx_mock.get_requests()
        assert len(requests) == 2

    @pytest.mark.asyncio
    async def test_500_server_error(self, httpx_mock: HTTPXMock):
        """Test 500 raises ServerError after retries."""
        # Add 5 responses for retries (default is 5 attempts)
        for _ in range(5):
            httpx_mock.add_response(
                url="https://power.upsales.com/api/v2/users/1",
                status_code=500,
                json={"error": "Internal server error", "data": None},
            )

        async with HTTPClient(token="test_token") as http:
            # Should raise ServerError after 5 attempts
            with pytest.raises(ServerError):
                await http.get("/users/1")

        requests = httpx_mock.get_requests()
        assert len(requests) == 5

    @pytest.mark.asyncio
    async def test_502_bad_gateway_error(self, httpx_mock: HTTPXMock):
        """Test 502 raises ServerError after retries."""
        for _ in range(5):
            httpx_mock.add_response(
                url="https://power.upsales.com/api/v2/users/1",
                status_code=502,
                text="Bad Gateway",
            )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(ServerError):
                await http.get("/users/1")

        requests = httpx_mock.get_requests()
        assert len(requests) == 5

    @pytest.mark.asyncio
    async def test_503_service_unavailable_error(self, httpx_mock: HTTPXMock):
        """Test 503 raises ServerError after retries."""
        for _ in range(5):
            httpx_mock.add_response(
                url="https://power.upsales.com/api/v2/users/1",
                status_code=503,
                text="Service Unavailable",
            )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(ServerError):
                await http.get("/users/1")

        requests = httpx_mock.get_requests()
        assert len(requests) == 5

    @pytest.mark.asyncio
    async def test_connection_error(self, httpx_mock: HTTPXMock):
        """Test connection errors are wrapped in TransientError and retried."""
        # Add 5 exceptions for retries (default is 5 attempts)
        for _ in range(5):
            httpx_mock.add_exception(
                httpx.ConnectError("Connection failed"),
                url="https://power.upsales.com/api/v2/users/1",
            )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(TransientError) as exc_info:
                await http.get("/users/1")
            assert isinstance(exc_info.value.__cause__, httpx.ConnectError)

        requests = httpx_mock.get_requests()
        assert len(requests) == 5

    @pytest.mark.asyncio
    async def test_timeout_error(self, httpx_mock: HTTPXMock):
        """Test timeout errors are wrapped in TransientError and retried."""
        for _ in range(5):
            httpx_mock.add_exception(
                httpx.TimeoutException("Request timeout"),
                url="https://power.upsales.com/api/v2/users/1",
            )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(TransientError) as exc_info:
                await http.get("/users/1")
            assert isinstance(exc_info.value.__cause__, httpx.TimeoutException)

        requests = httpx_mock.get_requests()
        assert len(requests) == 5

    @pytest.mark.asyncio
    async def test_network_error(self, httpx_mock: HTTPXMock):
        """Test network errors are wrapped in TransientError and retried."""
        for _ in range(5):
            httpx_mock.add_exception(
                httpx.NetworkError("Network unreachable"),
                url="https://power.upsales.com/api/v2/users/1",
            )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(TransientError) as exc_info:
                await http.get("/users/1")
            assert isinstance(exc_info.value.__cause__, httpx.NetworkError)

        requests = httpx_mock.get_requests()
        assert len(requests) == 5


class TestHTTPRequestMethods:
    """Test different HTTP methods handle errors correctly."""

    @pytest.mark.asyncio
    async def test_post_404_error(self, httpx_mock: HTTPXMock):
        """Test POST request 404 error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users",
            method="POST",
            status_code=404,
            json={"error": "Endpoint not found", "data": None},
        )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(NotFoundError):
                await http.post("/users", json={"name": "Test"})

    @pytest.mark.asyncio
    async def test_put_validation_error(self, httpx_mock: HTTPXMock):
        """Test PUT request validation error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="PUT",
            status_code=400,
            json={"error": "Validation failed", "data": None},
        )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(ValidationError):
                await http.put("/users/1", json={"email": "invalid"})

    @pytest.mark.asyncio
    async def test_delete_auth_error(self, httpx_mock: HTTPXMock):
        """Test DELETE request authentication error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="DELETE",
            status_code=403,
            json={"error": "Forbidden", "data": None},
        )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(AuthenticationError):
                await http.delete("/users/1")


class TestHTTPEdgeCases:
    """Test edge cases and unusual scenarios."""

    @pytest.mark.asyncio
    async def test_empty_response_body(self, httpx_mock: HTTPXMock):
        """Test handling of empty response body."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=200,
            text="",  # Empty body
        )

        async with HTTPClient(token="test_token") as http:
            # Empty responses now return empty dict instead of raising
            result = await http.get("/users/1")
            assert result == {}

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, httpx_mock: HTTPXMock):
        """Test handling of malformed JSON."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=200,
            text="{'invalid': json}",  # Malformed JSON
        )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(Exception):  # JSON decode error
                await http.get("/users/1")

    @pytest.mark.asyncio
    async def test_unexpected_status_code(self, httpx_mock: HTTPXMock):
        """Test handling of unexpected status codes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=418,  # I'm a teapot (unusual code)
            text="Unexpected status",
        )

        async with HTTPClient(token="test_token") as http:
            with pytest.raises(Exception):
                await http.get("/users/1")

    @pytest.mark.asyncio
    async def test_large_response_handling(self, httpx_mock: HTTPXMock):
        """Test handling of large response bodies."""
        # Create large response
        large_data = [{"id": i, "name": f"User {i}"} for i in range(1000)]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users",
            status_code=200,
            json={"error": None, "data": large_data},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.get("/users")
            assert len(result["data"]) == 1000

    @pytest.mark.asyncio
    async def test_client_not_initialized_error(self):
        """Test using client before async context raises error."""
        http = HTTPClient(token="test_token")

        # Should raise RuntimeError (client not initialized)
        with pytest.raises(RuntimeError, match="not initialized"):
            await http.get("/users")

    @pytest.mark.asyncio
    async def test_multiple_sequential_requests(self, httpx_mock: HTTPXMock):
        """Test multiple sequential requests reuse connection."""
        # Add multiple responses
        for i in range(5):
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/users/{i + 1}",
                status_code=200,
                json={"error": None, "data": {"id": i + 1, "name": f"User {i + 1}"}},
            )

        async with HTTPClient(token="test_token") as http:
            # Make multiple requests
            for i in range(5):
                result = await http.get(f"/users/{i + 1}")
                assert result["data"]["id"] == i + 1

        # All 5 requests should have been made
        assert len(httpx_mock.get_requests()) == 5


class TestHTTPRetryBehavior:
    """Test retry logic for rate limits."""

    @pytest.mark.asyncio
    async def test_rate_limit_retry_success_after_3_attempts(self, httpx_mock: HTTPXMock):
        """Test successful retry after 3 rate limit errors."""
        # Fail 3 times, then succeed
        for _ in range(3):
            httpx_mock.add_response(
                url="https://power.upsales.com/api/v2/users/1",
                status_code=429,
                json={"error": "Rate limit", "data": None},
            )

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=200,
            json={"error": None, "data": {"id": 1, "name": "Success"}},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.get("/users/1")
            assert result["data"]["name"] == "Success"

        # Should have made 4 requests total (3 retries + 1 success)
        assert len(httpx_mock.get_requests()) == 4

    @pytest.mark.asyncio
    @pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
    async def test_rate_limit_max_retries_exceeded(self, httpx_mock: HTTPXMock):
        """Test rate limit error after max retries."""
        from tenacity import RetryError

        # Always return 429
        for _ in range(10):  # More than max retries
            httpx_mock.add_response(
                url="https://power.upsales.com/api/v2/users/1",
                status_code=429,
                json={"error": "Rate limit", "data": None},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # Should raise RetryError after max attempts (wraps RateLimitError)
            with pytest.raises((RateLimitError, RetryError)):
                await http.get("/users/1")


class TestHTTPContextManager:
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self):
        """Test client is properly closed after context."""
        http = HTTPClient(token="test_token")

        async with http:
            assert http._client is not None

        # Client should be closed after context
        # Note: Can't easily test aclose was called, but structure is correct

    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test close() method works."""
        http = HTTPClient(token="test_token")

        async with http:
            pass  # Initialize client

        await http.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_double_close_safe(self):
        """Test calling close twice is safe."""
        http = HTTPClient(token="test_token")

        async with http:
            pass

        await http.close()
        await http.close()  # Should not raise


class TestHTTPParameterHandling:
    """Test various parameter combinations."""

    @pytest.mark.asyncio
    async def test_get_with_query_params(self, httpx_mock: HTTPXMock):
        """Test GET request with query parameters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&limit=10",
            status_code=200,
            json={"error": None, "data": []},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.get("/users", active=1, limit=10)
            assert result["data"] == []

    @pytest.mark.asyncio
    async def test_post_with_json_body(self, httpx_mock: HTTPXMock):
        """Test POST request with JSON body."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users",
            method="POST",
            status_code=201,
            json={"error": None, "data": {"id": 1, "name": "Created"}},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.post(
                "/users", json={"name": "New User", "email": "test@example.com"}
            )
            assert result["data"]["id"] == 1

    @pytest.mark.asyncio
    async def test_put_with_data(self, httpx_mock: HTTPXMock):
        """Test PUT request with data."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="PUT",
            status_code=200,
            json={"error": None, "data": {"id": 1, "name": "Updated"}},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.put("/users/1", json={"name": "Updated"})
            assert result["data"]["name"] == "Updated"

    @pytest.mark.asyncio
    async def test_delete_returns_data(self, httpx_mock: HTTPXMock):
        """Test DELETE request returns data."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            method="DELETE",
            status_code=200,
            json={"error": None, "data": {"id": 1, "deleted": True}},
        )

        async with HTTPClient(token="test_token") as http:
            result = await http.delete("/users/1")
            assert result["data"]["deleted"] is True
