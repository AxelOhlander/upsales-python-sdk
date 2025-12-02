"""List views model for custom list views stored in Redis.

This module provides models for managing custom list views for entities
in the Upsales CRM system.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel


class ListViewUpdateFields(TypedDict, total=False):
    """Available fields for updating a ListView.

    This TypedDict provides IDE autocomplete for all updatable fields.
    All fields are optional.

    Attributes:
        title: View title
        description: View description
        grouping: Grouping configuration
        columns: Column configuration
        sorting: Sort configuration
        filters: Filter configuration
        limit: Result limit
        default: Whether this is the default view
        roleId: Associated role ID
    """

    title: str
    description: str
    grouping: str
    columns: list[dict[str, Any]]
    sorting: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    limit: int
    default: bool
    roleId: int


class ListView(BaseModel):
    """Represents a custom list view in Upsales.

    List views allow customization of how entity lists are displayed,
    including columns, sorting, filtering, and grouping.

    Attributes:
        id: Unique identifier
        title: View title
        description: View description
        listType: Type of list (entity name)
        type: View type
        grouping: Grouping configuration
        columns: Column configuration
        sorting: Sort configuration
        filters: Filter configuration
        limit: Result limit
        users: Associated users
        roles: Associated roles
        default: Whether this is the default view
        regDate: Registration date
        modDate: Modification date
        regBy: Created by user

    Example:
        >>> view = ListView(
        ...     id=1,
        ...     title="Active Accounts",
        ...     listType="account",
        ...     type="custom"
        ... )
        >>> view.title
        'Active Accounts'
        >>> view.is_default
        False
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique identifier")
    listType: str = Field(frozen=True, description="Type of list (entity name)")
    type: str = Field(frozen=True, description="View type")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Modification date")
    regBy: dict[str, Any] | None = Field(None, frozen=True, description="Created by user")

    # Updatable fields
    title: str = Field(description="View title")
    description: str | None = Field(None, description="View description")
    grouping: str | None = Field(None, description="Grouping configuration")
    columns: list[dict[str, Any]] | None = Field(None, description="Column configuration")
    sorting: list[dict[str, Any]] | None = Field(None, description="Sort configuration")
    filters: list[dict[str, Any]] | None = Field(None, description="Filter configuration")
    limit: int | None = Field(None, description="Result limit")
    users: list[dict[str, Any]] | None = Field(None, description="Associated users")
    roles: list[dict[str, Any]] | None = Field(None, description="Associated roles")
    default: bool | None = Field(None, description="Whether this is the default view")

    @computed_field
    @property
    def is_default(self) -> bool:
        """Check if this is the default view.

        Returns:
            True if this is the default view, False otherwise.

        Example:
            >>> view = ListView(id=1, title="Test", listType="account", type="custom", default=True)
            >>> view.is_default
            True
        """
        return self.default is True

    async def edit(self, **kwargs: Unpack[ListViewUpdateFields]) -> "ListView":
        """Edit this list view with the given field updates.

        Args:
            **kwargs: Fields to update (title, description, grouping, columns,
                     sorting, filters, limit, default, roleId)

        Returns:
            Updated ListView instance with new values.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            UpsalesError: If the API request fails.

        Example:
            >>> view = await upsales.list_views.get("account", 1)
            >>> updated = await view.edit(
            ...     title="My Updated View",
            ...     default=True
            ... )
            >>> updated.title
            'My Updated View'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.list_views.update(
            self.listType, self.id, **self.to_api_dict(**kwargs)
        )


class PartialListView(PartialModel):
    """Partial representation of a ListView.

    Used when ListView appears as a nested object in API responses.
    Contains minimal fields for identification.

    Attributes:
        id: Unique identifier
        title: View title
        listType: Type of list (entity name)

    Example:
        >>> partial = PartialListView(id=1, title="Active Accounts", listType="account")
        >>> full_view = await partial.fetch_full()
        >>> full_view.description
        'Shows all active accounts'
    """

    id: int = Field(description="Unique identifier")
    title: str = Field(description="View title")
    listType: str | None = Field(None, description="Type of list (entity name)")

    async def fetch_full(self) -> ListView:
        """Fetch the complete ListView object.

        Returns:
            Full ListView instance with all fields populated.

        Raises:
            RuntimeError: If no client is available or listType is not set.
            NotFoundError: If the list view is not found.
            UpsalesError: If the API request fails.

        Example:
            >>> partial = PartialListView(id=1, title="Test", listType="account")
            >>> full = await partial.fetch_full()
            >>> isinstance(full, ListView)
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        if not self.listType:
            raise RuntimeError("listType is required to fetch full ListView")
        return await self._client.list_views.get(self.listType, self.id)

    async def edit(self, **kwargs: Unpack[ListViewUpdateFields]) -> ListView:
        """Edit this list view with the given field updates.

        Args:
            **kwargs: Fields to update (title, description, grouping, columns,
                     sorting, filters, limit, default, roleId)

        Returns:
            Updated ListView instance with new values.

        Raises:
            RuntimeError: If no client is available or listType is not set.
            ValidationError: If field validation fails.
            UpsalesError: If the API request fails.

        Example:
            >>> partial = PartialListView(id=1, title="Test", listType="account")
            >>> updated = await partial.edit(title="New Title")
            >>> updated.title
            'New Title'
        """
        if not self._client:
            raise RuntimeError("No client available")
        if not self.listType:
            raise RuntimeError("listType is required to edit ListView")
        return await self._client.list_views.update(self.listType, self.id, **kwargs)
