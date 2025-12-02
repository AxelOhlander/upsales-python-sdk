"""
Provisioning models for Upsales API.

This endpoint is a pass-through/proxy to the provisioning service.
It does not follow standard CRUD patterns and forwards requests directly.

From API spec: /api/v2/provisioning
- GET: Forwards query params to provisioning service
- POST: Forwards request body to provisioning service
"""

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class ProvisioningRequest(BaseModel):
    """
    Provisioning request model.

    This is a generic container for provisioning operations.
    The actual structure depends on the provisioning service requirements.

    Note:
        This endpoint does not have a standard ID-based structure.
        It acts as a proxy to the provisioning service.

    Example:
        >>> request = ProvisioningRequest(data={"action": "provision"})
    """

    # No fixed ID field - this is a pass-through endpoint
    id: int = Field(default=0, frozen=True, strict=True, description="Not used for provisioning")

    # Generic data container
    data: dict[str, Any] = Field(default_factory=dict, description="Provisioning request data")


class PartialProvisioningRequest(PartialModel):
    """
    Partial provisioning request for nested responses.

    This is rarely used as provisioning is typically not nested.

    Example:
        >>> partial = PartialProvisioningRequest(id=0, data={})
        >>> # Provisioning doesn't support fetch_full in typical way
    """

    id: int = Field(default=0, frozen=True, strict=True, description="Not used for provisioning")
    data: dict[str, Any] = Field(default_factory=dict, description="Provisioning request data")

    async def fetch_full(self) -> ProvisioningRequest:
        """
        Fetch complete provisioning data.

        Note:
            Provisioning endpoint doesn't support standard GET by ID.
            This method exists for interface consistency but may not be functional.

        Returns:
            Full ProvisioningRequest object.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: If provisioning service doesn't support this operation.
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Provisioning endpoint is a pass-through service and doesn't support fetch_full"
        )

    async def edit(self, **kwargs: Any) -> ProvisioningRequest:
        """
        Edit provisioning request.

        Note:
            Provisioning endpoint doesn't support standard UPDATE operations.
            This method exists for interface consistency but may not be functional.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated ProvisioningRequest object.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: If provisioning service doesn't support this operation.
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Provisioning endpoint is a pass-through service and doesn't support edit"
        )
