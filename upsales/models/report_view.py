"""Report view models for Upsales API.

This module defines models for report views (custom report configurations).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import ReportViewUpdateFields


class ReportView(BaseModel):
    """Report view model.

    Represents a custom report configuration stored in Redis.

    Attributes:
        id: Unique report view ID (read-only).
        description: Report view description.
        type: View type (own, role, public).
        title: Report view title.
        default: Whether this is the default view.
        editable: Whether this view can be edited.
        private: Whether this view is private.
        sorting: Sorting configuration.
        grouping: Grouping configuration.
        tableGrouping: Table grouping configuration.
        filters: Filter configuration.
        roleId: Associated role ID (required when type is 'role').
        custom: Custom fields list.

    Example:
        ```python
        # Create report view
        view = await upsales.report_views.create(
            title="My Custom View",
            type="own",
            filters=[]
        )

        # Update report view
        view.title = "Updated View"
        updated = await view.edit()

        # Or use edit with parameters
        updated = await view.edit(title="New Title", default=True)
        ```
    """

    # Read-only fields
    id: str = Field(frozen=True, strict=True, description="Unique report view ID (UUID)")

    # Updatable fields
    description: str | None = Field(None, description="Report view description")
    type: str | None = Field(None, description="View type (own, role, public)")
    title: str | None = Field(None, description="Report view title")
    default: bool = Field(False, description="Default view status")
    editable: bool = Field(True, description="Editable status")
    private: bool = Field(False, description="Private status")
    sorting: list[dict] | None = Field(None, description="Sorting configuration")
    grouping: str | None = Field(None, description="Grouping configuration")
    tableGrouping: str | None = Field(None, description="Table grouping")
    filters: list[dict] | None = Field(None, description="Filter configuration")
    roleId: int | None = Field(None, description="Associated role ID")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            view = await upsales.report_views.get("uuid")
            value = view.custom_fields.get(11)
            view.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_default(self) -> bool:
        """Check if report view is the default view.

        Returns:
            True if default, False otherwise.

        Example:
            ```python
            if view.is_default:
                print("This is the default view")
            ```
        """
        return self.default is True

    @computed_field
    @property
    def is_private(self) -> bool:
        """Check if report view is private.

        Returns:
            True if private, False otherwise.

        Example:
            ```python
            if view.is_private:
                print("This is a private view")
            ```
        """
        return self.private is True

    async def edit(self, **kwargs: Unpack[ReportViewUpdateFields]) -> ReportView:
        """Edit this report view with type-safe field updates.

        Args:
            **kwargs: Fields to update (description, type, title, default,
                     editable, private, sorting, grouping, tableGrouping,
                     filters, roleId, custom).

        Returns:
            Updated ReportView instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If report view no longer exists.

        Example:
            ```python
            view = await upsales.report_views.get("uuid")

            # Update single field
            updated = await view.edit(title="New Title")

            # Update multiple fields
            updated = await view.edit(
                title="New Title",
                default=True,
                private=False
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.report_views.update(self.id, **self.to_api_dict(**kwargs))


class PartialReportView(PartialModel):
    """Partial report view model for nested responses.

    Used when report views appear as nested objects in API responses.

    Attributes:
        id: Unique report view ID.
        title: Report view title.

    Example:
        ```python
        # Fetch full report view from partial
        partial: PartialReportView = some_object.report_view
        full: ReportView = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(title="New Title")
        ```
    """

    id: str = Field(description="Unique report view ID")
    title: str | None = Field(None, description="Report view title")

    async def fetch_full(self) -> ReportView:
        """Fetch complete report view data.

        Returns:
            Full ReportView instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If report view not found.

        Example:
            ```python
            partial = PartialReportView(id="uuid", title="My View")
            full = await partial.fetch_full()
            print(full.description)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.report_views.get(self.id)

    async def edit(self, **kwargs: Unpack[ReportViewUpdateFields]) -> ReportView:
        """Edit this report view.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated ReportView instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If report view not found.

        Example:
            ```python
            partial = PartialReportView(id="uuid", title="My View")
            updated = await partial.edit(default=True)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.report_views.update(self.id, **kwargs)
