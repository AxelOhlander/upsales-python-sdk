"""Onboarding import models for Upsales API.

This module defines models for onboarding imports (standard integration import processes).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import OnboardingImportUpdateFields


class OnboardingImport(BaseModel):
    """Onboarding import model.

    Represents an onboarding import process for standard integrations.

    Attributes:
        id: Unique onboarding import ID (read-only).
        integrationId: Integration ID (required for creation, read-only after).
        stepId: Step ID (read-only).
        startDate: Import start date.
        endDate: Import end date.
        progress: Import progress percentage.
        clientCount: Number of clients imported.
        contactCount: Number of contacts imported.
        orderCount: Number of orders imported.
        custom: Custom fields list.

    Example:
        ```python
        # Create onboarding import
        import_job = await upsales.onboarding_imports.create(
            integrationId=1
        )

        # Update onboarding import
        import_job.progress = 50
        updated = await import_job.edit()

        # Or use edit with parameters
        updated = await import_job.edit(progress=75, clientCount=100)
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique onboarding import ID")
    integrationId: int = Field(frozen=True, description="Integration ID")
    stepId: int | None = Field(None, frozen=True, description="Step ID")

    # Updatable fields
    startDate: str | None = Field(None, description="Import start date")
    endDate: str | None = Field(None, description="Import end date")
    progress: int = Field(0, description="Import progress percentage")
    clientCount: int = Field(0, description="Number of clients imported")
    contactCount: int = Field(0, description="Number of contacts imported")
    orderCount: int = Field(0, description="Number of orders imported")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            import_job = await upsales.onboarding_imports.get(1)
            value = import_job.custom_fields.get(11)
            import_job.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if import is complete.

        Returns:
            True if progress is 100, False otherwise.

        Example:
            ```python
            if import_job.is_complete:
                print("Import finished")
            ```
        """
        return self.progress >= 100

    async def edit(self, **kwargs: Unpack[OnboardingImportUpdateFields]) -> OnboardingImport:
        """Edit this onboarding import with type-safe field updates.

        Args:
            **kwargs: Fields to update (startDate, endDate, progress,
                     clientCount, contactCount, orderCount, custom).

        Returns:
            Updated OnboardingImport instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If onboarding import no longer exists.

        Example:
            ```python
            import_job = await upsales.onboarding_imports.get(1)

            # Update single field
            updated = await import_job.edit(progress=50)

            # Update multiple fields
            updated = await import_job.edit(
                progress=75,
                clientCount=100,
                contactCount=250
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.onboarding_imports.update(self.id, **self.to_api_dict(**kwargs))


class PartialOnboardingImport(PartialModel):
    """Partial onboarding import model for nested responses.

    Used when onboarding imports appear as nested objects in API responses.

    Attributes:
        id: Unique onboarding import ID.
        integrationId: Integration ID.

    Example:
        ```python
        # Fetch full onboarding import from partial
        partial: PartialOnboardingImport = some_object.onboarding_import
        full: OnboardingImport = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(progress=50)
        ```
    """

    id: int = Field(description="Unique onboarding import ID")
    integrationId: int | None = Field(None, description="Integration ID")

    async def fetch_full(self) -> OnboardingImport:
        """Fetch complete onboarding import data.

        Returns:
            Full OnboardingImport instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If onboarding import not found.

        Example:
            ```python
            partial = PartialOnboardingImport(id=1, integrationId=1)
            full = await partial.fetch_full()
            print(full.progress)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.onboarding_imports.get(self.id)

    async def edit(self, **kwargs: Unpack[OnboardingImportUpdateFields]) -> OnboardingImport:
        """Edit this onboarding import.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated OnboardingImport instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If onboarding import not found.

        Example:
            ```python
            partial = PartialOnboardingImport(id=1, integrationId=1)
            updated = await partial.edit(progress=75)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.onboarding_imports.update(self.id, **kwargs)
