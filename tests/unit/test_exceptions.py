"""
Tests for exception classes.

Uses Python 3.13 native type hints.
"""

import pytest

from upsales.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UpsalesError,
    ValidationError,
)


def test_upsales_error():
    """Test base UpsalesError."""
    error = UpsalesError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_rate_limit_error():
    """Test RateLimitError inherits from UpsalesError."""
    error = RateLimitError("Rate limit exceeded")
    assert isinstance(error, UpsalesError)
    assert isinstance(error, Exception)


def test_authentication_error():
    """Test AuthenticationError inherits from UpsalesError."""
    error = AuthenticationError("Invalid token")
    assert isinstance(error, UpsalesError)


def test_not_found_error():
    """Test NotFoundError inherits from UpsalesError."""
    error = NotFoundError("Resource not found")
    assert isinstance(error, UpsalesError)


def test_validation_error():
    """Test ValidationError inherits from UpsalesError."""
    error = ValidationError("Validation failed")
    assert isinstance(error, UpsalesError)


def test_server_error():
    """Test ServerError inherits from UpsalesError."""
    error = ServerError("Internal server error")
    assert isinstance(error, UpsalesError)


def test_catch_all_upsales_errors():
    """Test catching all errors with base UpsalesError."""
    errors: list[Exception] = [
        RateLimitError("rate"),
        AuthenticationError("auth"),
        NotFoundError("not found"),
        ValidationError("validation"),
        ServerError("server"),
    ]

    for error in errors:
        with pytest.raises(UpsalesError):
            raise error


def test_specific_error_catching():
    """Test catching specific error types."""
    with pytest.raises(NotFoundError):
        raise NotFoundError("Resource not found")

    with pytest.raises(RateLimitError):
        raise RateLimitError("Rate limit")
