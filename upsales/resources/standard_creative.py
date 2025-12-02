"""Standard Creative resource manager for Upsales API.

This module provides resource management for the standardCreative endpoint,
which handles email/creative templates. This is a read-only endpoint.
"""

from __future__ import annotations

from upsales.http import HTTPClient  # noqa: TC001
from upsales.models.standard_creative import (
    PartialStandardCreative,
    StandardCreative,
)
from upsales.resources.base import BaseResource


class StandardCreativeResource(BaseResource[StandardCreative, PartialStandardCreative]):
    """Resource manager for standard creative templates.

    Provides read-only access to email and creative templates in Upsales.
    This endpoint does not support create, update, or delete operations.

    Example:
        >>> # List all templates
        >>> templates = await upsales.standard_creative.list()
        >>> for template in templates:
        ...     print(f"{template.name}: {template.subject}")
        >>>
        >>> # Get specific template
        >>> template = await upsales.standard_creative.get(1)
        >>> print(template.body)
        >>>
        >>> # Search for active templates
        >>> active = await upsales.standard_creative.search(active=1)
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the StandardCreative resource manager.

        Args:
            http: HTTP client for making API requests.
        """
        super().__init__(
            http=http,
            endpoint="/standardCreative",
            model_class=StandardCreative,
            partial_class=PartialStandardCreative,
        )
