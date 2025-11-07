"""
Upsales Python SDK - Async wrapper for the Upsales CRM API.

This package provides a modern, type-safe Python interface to the Upsales CRM API,
leveraging Python 3.13+ features including:
- Native type hints (no typing imports needed)
- Type parameter syntax for clean generics
- Pattern matching for error handling
- Exception groups for bulk operations
- Free-threaded mode support for true parallelism

Example:
    >>> import asyncio
    >>> from upsales import Upsales
    >>>
    >>> async def main():
    ...     async with Upsales(token="YOUR_TOKEN") as upsales:
    ...         user = await upsales.users.get(1)
    ...         print(f"{user.name = }")
    >>>
    >>> asyncio.run(main())

Requirements:
    - Python 3.13+
    - httpx
    - pydantic v2
    - tenacity

Note:
    With Python 3.13 free-threaded mode enabled, concurrent operations
    can achieve true parallelism without GIL contention, maximizing
    throughput within the Upsales API rate limits (200 req/10 sec).
"""

from upsales.client import Upsales
from upsales.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UpsalesError,
    ValidationError,
)
from upsales.settings import UpsalesSettings, load_settings

__version__ = "0.1.0"
__all__ = [
    "Upsales",
    "UpsalesSettings",
    "load_settings",
    "UpsalesError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
]
