"""Visit models for Upsales API.

This module defines models for visits (website visit tracking).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import VisitUpdateFields


class Visit(BaseModel):
    """Visit model.

    Represents a website visit from identified or anonymous users.

    Attributes:
        id: Unique visit ID (read-only).
        referer: Referrer URL.
        isFirst: Whether this is the first visit.
        client: Associated client object.
        contact: Associated contact object.
        score: Visit score.
        startDate: Visit start date (read-only).
        endDate: Visit end date (read-only).
        pages: List of visited pages.
        country: Visitor country (read-only).
        custom: Custom fields list.

    Example:
        ```python
        # Create visit (administrator or mailAdmin only)
        visit = await upsales.visits.create(
            referer="https://google.com",
            score=10
        )

        # Update visit
        visit.score = 20
        updated = await visit.edit()

        # Or use edit with parameters
        updated = await visit.edit(score=20, pages=[{"url": "/product"}])
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique visit ID")
    startDate: str | None = Field(None, frozen=True, description="Visit start date")
    endDate: str | None = Field(None, frozen=True, description="Visit end date")
    country: str | None = Field(None, frozen=True, description="Visitor country")

    # Updatable fields
    referer: str | None = Field(None, description="Referrer URL")
    isFirst: bool = Field(False, description="First visit flag")
    client: dict | None = Field(None, description="Associated client")
    contact: dict | None = Field(None, description="Associated contact")
    score: int = Field(0, description="Visit score")
    pages: list[dict] | None = Field(None, description="Visited pages")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            visit = await upsales.visits.get(1)
            value = visit.custom_fields.get(11)
            visit.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_first_visit(self) -> bool:
        """Check if this is the first visit.

        Returns:
            True if first visit, False otherwise.

        Example:
            ```python
            if visit.is_first_visit:
                print("First time visitor")
            ```
        """
        return self.isFirst is True

    async def edit(self, **kwargs: Unpack[VisitUpdateFields]) -> Visit:
        """Edit this visit with type-safe field updates.

        Args:
            **kwargs: Fields to update (referer, isFirst, client, contact,
                     score, pages, custom).

        Returns:
            Updated Visit instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If visit no longer exists.

        Example:
            ```python
            visit = await upsales.visits.get(1)

            # Update single field
            updated = await visit.edit(score=20)

            # Update multiple fields
            updated = await visit.edit(
                score=20,
                pages=[{"url": "/product", "duration": 60}]
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.visits.update(self.id, **self.to_api_dict(**kwargs))


class PartialVisit(PartialModel):
    """Partial visit model for nested responses.

    Used when visits appear as nested objects in API responses.

    Attributes:
        id: Unique visit ID.
        score: Visit score.

    Example:
        ```python
        # Fetch full visit from partial
        partial: PartialVisit = some_object.visit
        full: Visit = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(score=20)
        ```
    """

    id: int = Field(description="Unique visit ID")
    score: int | None = Field(None, description="Visit score")

    async def fetch_full(self) -> Visit:
        """Fetch complete visit data.

        Returns:
            Full Visit instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If visit not found.

        Example:
            ```python
            partial = PartialVisit(id=1, score=10)
            full = await partial.fetch_full()
            print(full.pages)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.visits.get(self.id)

    async def edit(self, **kwargs: Unpack[VisitUpdateFields]) -> Visit:
        """Edit this visit.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated Visit instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If visit not found.

        Example:
            ```python
            partial = PartialVisit(id=1, score=10)
            updated = await partial.edit(score=20)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.visits.update(self.id, **kwargs)
