"""
Project models for Upsales API.

Generated from /api/v2/projects endpoint.
Analysis based on 1 sample.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, NonEmptyStr, PositiveInt)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions (100% coverage)
- Optimized serialization via to_api_dict()
- TypedDict for IDE autocomplete

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, CustomFieldsList, NonEmptyStr, PositiveInt


class ProjectUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Project.

    All fields are optional. Use with Unpack for IDE autocomplete.
    Does not include read-only fields (id, regDate).
    """

    # Core project fields
    name: str
    startDate: str
    endDate: str
    quota: int
    notes: str

    # Status flags
    active: int
    isCallList: bool
    userEditable: bool
    userRemovable: bool

    # Relationships
    users: list[PartialUser]

    # Custom fields
    custom: list[Any]


class Project(BaseModel):
    """
    Project model from /api/v2/projects.

    Represents a project in the Upsales system with full data.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 1 sample with field analysis.

    Example:
        >>> project = await upsales.projects.get(1)
        >>> project.name
        'Q1 Campaign'
        >>> project.is_active  # Computed property
        True
        >>> project.custom_fields[11]  # Access custom fields
        'value'
        >>> await project.edit(name="Q2 Campaign", active=1)  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique project ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")

    # Core project fields
    name: NonEmptyStr = Field(description="Project name")
    startDate: str = Field(description="Project start date (ISO 8601)")
    endDate: str | None = Field(None, description="Project end date (ISO 8601)")
    quota: int = Field(default=0, description="Project quota/target")
    notes: str | None = Field(None, description="Project notes")

    # Status flags
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    isCallList: bool = Field(default=False, description="Whether project is a call list")
    userEditable: bool = Field(default=True, description="Whether users can edit project")
    userRemovable: bool = Field(default=True, description="Whether users can remove project")

    # Relationships
    users: list[PartialUser] = Field(
        default_factory=list, description="List of users assigned to project"
    )

    # Custom fields (always include for all models)
    custom: CustomFieldsList = Field(default_factory=list, description="Custom field values")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for accessing custom field values by ID or alias.

        Example:
            >>> project.custom_fields[11]  # By field ID
            'Marketing Campaign'
            >>> project.custom_fields["CAMPAIGN_TYPE"]  # By alias
            'Email'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if project is active.

        Returns:
            True if project is active (active=1), False otherwise.

        Example:
            >>> project.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def has_users(self) -> bool:
        """
        Check if project has assigned users.

        Returns:
            True if project has at least one assigned user, False otherwise.

        Example:
            >>> project.has_users
            True
        """
        return len(self.users) > 0

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Clean custom fields for API requests.

        Only includes fields with non-null values and removes extra metadata.
        Uses Pydantic v2 field serializer for automatic application during
        model_dump(mode='json').

        Args:
            custom: Raw custom fields list.

        Returns:
            Cleaned list with only fieldId and value.

        Example:
            >>> project.model_dump(mode='json')
            {'custom': [{'fieldId': 11, 'value': 'test'}]}
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[ProjectUpdateFields]) -> "Project":
        """
        Edit this project with type-safe field updates.

        Provides full IDE autocomplete for available fields via TypedDict.
        Automatically excludes read-only fields (id, regDate) using to_api_dict().

        Args:
            **kwargs: Fields to update (see ProjectUpdateFields for available options).

        Returns:
            Updated project with new values.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> project = await upsales.projects.get(1)
            >>> updated = await project.edit(
            ...     name="Q2 Campaign",
            ...     active=1,
            ...     quota=1000
            ... )
            >>> updated.name
            'Q2 Campaign'

        Note:
            Uses optimized Pydantic v2 serialization (5-50x faster than v1).
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.projects.update(self.id, **self.to_api_dict(**kwargs))


class PartialProject(PartialModel):
    """
    Partial Project for nested responses.

    Contains minimal project information when projects appear as nested
    objects in other API responses (e.g., in order.project).

    Example:
        >>> order = await upsales.orders.get(1)
        >>> if order.project:
        ...     print(order.project.name)  # Access partial data
        ...     full = await order.project.fetch_full()  # Fetch full details
    """

    id: PositiveInt = Field(description="Unique project ID")
    name: NonEmptyStr = Field(description="Project name")

    async def fetch_full(self) -> Project:
        """
        Fetch full project data from the API.

        Returns:
            Complete Project object with all fields.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> partial_project = order.project
            >>> full_project = await partial_project.fetch_full()
            >>> full_project.startDate
            '2025-01-01'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.projects.get(self.id)

    async def edit(self, **kwargs: Unpack[ProjectUpdateFields]) -> Project:
        """
        Edit this project directly from partial reference.

        Args:
            **kwargs: Fields to update (see ProjectUpdateFields for available options).

        Returns:
            Updated full Project object.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> partial_project = order.project
            >>> updated = await partial_project.edit(active=0)
            >>> updated.is_active
            False
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.projects.update(self.id, **kwargs)
