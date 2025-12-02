"""Standard Creative models for Upsales API.

This module provides Pydantic models for the standardCreative endpoint,
which represents email/creative templates in Upsales. This is a read-only
endpoint with no create, update, or delete operations.
"""

from __future__ import annotations

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag  # noqa: TC001


class StandardCreative(BaseModel):
    """Standard creative template model.

    Represents an email or creative template in Upsales. This is a read-only
    resource with no update capabilities.

    Attributes:
        id: Unique identifier for the standard creative.
        name: Name of the creative template.
        subject: Email subject line template.
        body: Email body content template.
        active: Active status (0 = inactive, 1 = active).

    Example:
        >>> creative = await upsales.standard_creative.get(1)
        >>> print(creative.name)
        "Welcome Email Template"
        >>> print(creative.is_active)
        True
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique creative ID")

    # Template fields
    name: str = Field(description="Template name")
    subject: str | None = Field(None, description="Email subject line")
    body: str | None = Field(None, description="Email body content")
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")

    @property
    def is_active(self) -> bool:
        """Check if the creative is active.

        Returns:
            True if active (1), False if inactive (0).

        Example:
            >>> creative.active = 1
            >>> creative.is_active
            True
        """
        return self.active == 1


class PartialStandardCreative(PartialModel):
    """Partial standard creative model for nested references.

    Used when standard creative appears as a nested object in other API responses.

    Attributes:
        id: Unique identifier for the standard creative.
        name: Name of the creative template.

    Example:
        >>> partial = PartialStandardCreative(id=1, name="Welcome Email")
        >>> full = await partial.fetch_full()
    """

    id: int = Field(description="Unique creative ID")
    name: str = Field(description="Template name")

    async def fetch_full(self) -> StandardCreative:
        """Fetch the complete StandardCreative object.

        Returns:
            Complete StandardCreative instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialStandardCreative(id=1, name="Welcome")
            >>> full = await partial.fetch_full()
            >>> print(full.subject)
            "Welcome to our platform!"
        """
        if not self._client:
            raise RuntimeError("No client available for fetch_full")
        return await self._client.standard_creative.get(self.id)
