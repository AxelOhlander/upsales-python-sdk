"""
Custom exceptions for Upsales API.

All exceptions inherit from UpsalesError for easy catching.
Uses Python 3.13 native type hints throughout.

Example:
    >>> try:
    ...     user = await client.users.get(999)
    ... except NotFoundError:
    ...     print("User not found")
    ... except UpsalesError as e:
    ...     print(f"API error: {e}")
"""


class UpsalesError(Exception):
    """
    Base exception for all Upsales API errors.

    All other exceptions inherit from this, allowing you to catch
    any Upsales-related error with a single except clause.

    Example:
        >>> try:
        ...     await client.users.get(1)
        ... except UpsalesError:
        ...     # Handle any Upsales API error
        ...     pass
    """

    pass


class RateLimitError(UpsalesError):
    """
    Raised when API rate limit is exceeded (HTTP 429).

    The Upsales API enforces a limit of 200 requests per 10 seconds
    per API key. This exception is automatically retried with exponential
    backoff by the HTTP client.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header).

    Note:
        Use asyncio concurrency to maximize throughput up to the rate limit.
        The bottleneck is the API rate limit, not the GIL.

    Example:
        >>> try:
        ...     results = await client.products.bulk_update(ids, data)
        ... except RateLimitError as e:
        ...     # Rate limit exceeded even after retries
        ...     print(f"Too many requests, retry after {e.retry_after}s")
    """

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        """
        Initialize RateLimitError.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying (from Retry-After header).
        """
        super().__init__(message)
        self.retry_after = retry_after


class TransientError(UpsalesError):
    """
    Raised for transient network/transport errors that may succeed on retry.

    This includes connection timeouts, network failures, and other transport
    errors that are not permanent failures.

    Example:
        >>> try:
        ...     user = await client.users.get(1)
        ... except TransientError:
        ...     print("Network error, will retry automatically")
    """

    pass


class AuthenticationError(UpsalesError):
    """
    Raised when authentication fails (HTTP 401/403).

    This typically indicates an invalid or expired API token.

    Example:
        >>> try:
        ...     async with UpsalesClient(token="invalid") as client:
        ...         await client.users.get(1)
        ... except AuthenticationError:
        ...     print("Invalid API token")
    """

    pass


class NotFoundError(UpsalesError):
    """
    Raised when a resource is not found (HTTP 404).

    Example:
        >>> try:
        ...     user = await client.users.get(999999)
        ... except NotFoundError:
        ...     print("User does not exist")
    """

    pass


class ValidationError(UpsalesError):
    """
    Raised when request validation fails (HTTP 400).

    This indicates the request payload was invalid or missing required fields.

    Example:
        >>> try:
        ...     await client.users.update(1, email="invalid-email")
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")
    """

    pass


class ServerError(UpsalesError):
    """
    Raised when a server error occurs (HTTP 500+).

    This indicates an internal error on the Upsales API side.

    Example:
        >>> try:
        ...     await client.users.get(1)
        ... except ServerError:
        ...     print("Server error, try again later")
    """

    pass
