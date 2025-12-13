"""
Upsales Python SDK - Async wrapper for the Upsales CRM API.

This package provides a modern, type-safe Python interface to the Upsales CRM API,
leveraging Python 3.13+ features including:
- Native type hints (no typing imports needed)
- Type parameter syntax for clean generics
- Pattern matching for error handling
- Exception groups for bulk operations
- Asyncio for efficient concurrent I/O

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
    Uses asyncio for efficient concurrent operations, maximizing throughput
    within the Upsales API rate limits (200 req/10 sec). The bottleneck for
    bulk operations is typically network I/O and API rate limits, not the GIL.
"""

from upsales.client import Upsales
from upsales.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TransientError,
    UpsalesError,
    ValidationError,
)
from upsales.settings import UpsalesSettings, load_settings

# Dynamic version from package metadata (fallback for development installs)
try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("upsales")
except Exception:
    __version__ = "0.1.0"  # Fallback for development
__all__ = [
    "Upsales",
    "UpsalesSettings",
    "load_settings",
    "UpsalesError",
    "RateLimitError",
    "TransientError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
]
