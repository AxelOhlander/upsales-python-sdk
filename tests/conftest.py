"""
Shared test fixtures using Python 3.13 syntax.

Provides fixtures for testing the Upsales SDK.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from upsales import Upsales


@pytest.fixture
def base_url() -> str:
    """
    Base API URL for testing.

    Returns:
        The default Upsales API base URL.
    """
    return "https://power.upsales.com/api/v2"


@pytest.fixture
def mock_http_client() -> MagicMock:
    """
    Create a mock HTTP client for testing.

    Returns:
        Mock HTTP client with async methods.

    Example:
        >>> def test_with_mock(mock_http_client):
        ...     mock_http_client.get.return_value = {"id": 1}
    """
    return MagicMock()


@pytest.fixture
async def client() -> Upsales:
    """
    Create test client with mock token.

    Returns:
        Configured Upsales for testing.

    Example:
        >>> async def test_something(client):
        ...     user = await client.users.get(1)
    """
    async with Upsales(token="test_token_12345") as client:
        yield client


@pytest.fixture
def sample_user_response() -> dict[str, Any]:
    """
    Sample user API response.

    Returns:
        Mocked API response for a user.

    Example:
        >>> def test_parse_user(sample_user_response):
        ...     user = User(**sample_user_response["data"])
    """
    return {
        "error": None,
        "data": {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "administrator": 1,
            "role": {"id": 1, "name": "Admin"},
            "custom": [
                {"fieldId": 11, "value": "test_value"},
            ],
        },
    }


@pytest.fixture
def sample_user_list_response() -> dict[str, Any]:
    """
    Sample user list API response with metadata.

    Returns:
        Mocked API response for user list.
    """
    return {
        "error": None,
        "metadata": {
            "total": 2,
            "limit": 100,
            "offset": 0,
        },
        "data": [
            {
                "id": 1,
                "name": "User One",
                "email": "user1@example.com",
                "administrator": 1,
            },
            {
                "id": 2,
                "name": "User Two",
                "email": "user2@example.com",
                "administrator": 0,
            },
        ],
    }


@pytest.fixture
def sample_product_response() -> dict[str, Any]:
    """
    Sample product API response.

    Returns:
        Mocked API response for a product.
    """
    return {
        "error": None,
        "data": {
            "id": 1,
            "name": "Test Product",
            "description": "A test product",
            "price": 99.99,
            "active": 1,
            "custom": [],
        },
    }


@pytest.fixture
def sample_company_response() -> dict[str, Any]:
    """
    Sample company API response.

    Returns:
        Mocked API response for a company.

    Note:
        API endpoint is /accounts, but we use 'company' to match Upsales UI.
    """
    return {
        "error": None,
        "data": {
            "id": 1,
            "name": "Test Company",
            "custom": [],
        },
    }


@pytest.fixture
def sample_error_response() -> dict[str, Any]:
    """
    Sample error API response.

    Returns:
        Mocked API error response.
    """
    return {
        "error": "Validation failed: Invalid email format",
        "data": None,
    }


@pytest.fixture
def mock_custom_fields() -> list[dict[str, Any]]:
    """
    Sample custom fields data.

    Returns:
        List of custom field dicts.

    Example:
        >>> def test_custom_fields(mock_custom_fields):
        ...     cf = CustomFields(mock_custom_fields)
        ...     assert cf[11] == "value1"
    """
    return [
        {"fieldId": 11, "value": "value1"},
        {"fieldId": 12, "valueInteger": 123},
        {"fieldId": 13, "valueDate": "2024-01-01"},
    ]


@pytest.fixture
def field_schema() -> dict[str, int]:
    """
    Sample field schema mapping aliases to IDs.

    Returns:
        Dict mapping field aliases to field IDs.
    """
    return {
        "CUSTOM_FIELD_1": 11,
        "CUSTOM_FIELD_2": 12,
        "DATE_FIELD": 13,
    }


# ============================================================================
# VCR.py Configuration for Integration Tests
# ============================================================================


@pytest.fixture(scope="module")
def vcr_config():
    """
    VCR configuration for recording and replaying API responses.

    Records real API responses on first run, then replays them in future runs.
    This allows testing against real API structure without hitting the API.

    Returns:
        Dict with VCR configuration.

    Example:
        >>> @pytest.mark.vcr()
        >>> async def test_with_real_api():
        ...     # First run: calls real API and saves response
        ...     # Future runs: replays from saved cassette
        ...     user = await upsales.users.get(1)
    """
    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "once",  # Record once, then always replay
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        # Security: Filter sensitive data from cassettes
        "filter_headers": [
            ("cookie", "REDACTED"),  # Don't save API tokens
            ("authorization", "REDACTED"),
        ],
        "filter_post_data_parameters": [
            ("password", "REDACTED"),  # Don't save passwords
            ("email", "REDACTED"),  # Don't save email in auth requests
        ],
    }


@pytest.fixture
def vcr_cassette_dir(request, tmp_path):
    """
    Generate cassette directory based on test module/class/function.

    Returns:
        Path where cassette should be saved.

    Example:
        tests/integration/test_users.py::test_get_user
        -> tests/cassettes/test_users/test_get_user.yaml
    """
    # Get test location
    test_module = request.module.__name__.replace("tests.", "").replace(".", "/")
    test_name = request.node.name

    return f"{test_module}/{test_name}"
