"""
User models for Upsales API.

Generated from /api/v2/users endpoint.
Analysis based on 10 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.models.role import PartialRole
from upsales.validators import BinaryFlag, CustomFieldsList, EmailStr, NonEmptyStr


class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    email: str
    active: int
    administrator: int
    billingAdmin: int
    crm: int
    service: int
    support: int
    supportAdmin: int
    export: int
    free: int
    ghost: int
    projectAdmin: int
    teamLeader: int
    userPhone: str
    userCellPhone: str
    userAddress: str
    userState: str
    userZipCode: str
    userTitle: str
    custom: list[dict[str, Any]]
    role: dict[str, Any]  # API accepts dict data


class User(BaseModel):
    """
    User model from /api/v2/users.

    Represents a user in the Upsales system with full data. Enhanced with
    Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 10 samples with field analysis.

    Example:
        >>> user = await upsales.users.get(1)
        >>> user.name
        'John Doe'
        >>> user.is_admin  # Computed property
        True
        >>> user.custom_fields[11]  # Access custom fields
        'value'
        >>> await user.edit(email="new@example.com")  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique user ID")
    regDate: str = Field(frozen=True, description="Registration date")

    # Required fields with validators
    name: NonEmptyStr = Field(description="User's full name")
    email: EmailStr = Field(description="User's email (normalized to lowercase)")

    # Binary flags (validated 0 or 1)
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    administrator: BinaryFlag = Field(default=0, description="Administrator flag (0=no, 1=yes)")
    billingAdmin: BinaryFlag = Field(default=0, description="Billing admin flag (0=no, 1=yes)")
    crm: BinaryFlag = Field(default=0, description="CRM access (0=no, 1=yes)")
    export: BinaryFlag = Field(default=0, description="Export permission (0=no, 1=yes)")
    free: BinaryFlag = Field(default=0, description="Free user (0=no, 1=yes)")
    ghost: BinaryFlag = Field(default=0, description="Ghost user (0=no, 1=yes)")
    projectAdmin: BinaryFlag = Field(default=0, description="Project admin (0=no, 1=yes)")
    service: BinaryFlag = Field(default=0, description="Service access (0=no, 1=yes)")
    support: BinaryFlag = Field(default=0, description="Support access (0=no, 1=yes)")
    supportAdmin: BinaryFlag = Field(default=0, description="Support admin (0=no, 1=yes)")
    teamLeader: BinaryFlag = Field(default=0, description="Team leader (0=no, 1=yes)")

    # Custom fields (validated structure)
    custom: CustomFieldsList = Field(
        default=[], description="Custom fields with validated structure"
    )

    # Optional fields
    role: PartialRole | None = Field(default=None, description="User's role")
    userAddress: str | None = Field(default=None, description="User's address")
    userCellPhone: str | None = Field(default=None, description="User's cell phone")
    userPhone: str | None = Field(default=None, description="User's phone")
    userState: str | None = Field(default=None, description="User's state")
    userTitle: str | None = Field(default=None, description="User's title")
    userZipCode: str | None = Field(default=None, description="User's ZIP code")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> user.custom_fields[11]  # By field ID
            'value'
            >>> user.custom_fields.get(11, "default")
            'value'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_admin(self) -> bool:
        """
        Check if user is an administrator.

        Returns:
            True if administrator flag is 1, False otherwise.

        Example:
            >>> user.is_admin
            True
        """
        return self.administrator == 1

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if user is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> user.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def is_api_key(self) -> bool:
        """
        Check if user is an API key (service account).

        User types:
        - API key: ghost=1, active=1
        - Active user: ghost=0, active=1
        - Inactive user: ghost=0, active=0

        Returns:
            True if user is an API key (ghost=1, active=1).

        Example:
            >>> user.is_api_key
            False  # Regular user
            >>> api_user.is_api_key
            True  # API key/service account
        """
        return self.ghost == 1 and self.active == 1

    @computed_field
    @property
    def user_type(self) -> str:
        """
        Get user type based on ghost and active flags.

        Returns:
            "api_key" - API key/service account (ghost=1, active=1)
            "active" - Active regular user (ghost=0, active=1)
            "inactive" - Inactive user (ghost=0, active=0)
            "invalid" - Invalid state (ghost=1, active=0)

        Example:
            >>> user.user_type
            'active'
            >>> api_user.user_type
            'api_key'
        """
        if self.ghost == 1 and self.active == 1:
            return "api_key"
        elif self.ghost == 0 and self.active == 1:
            return "active"
        elif self.ghost == 0 and self.active == 0:
            return "inactive"
        else:  # ghost=1, active=0
            return "invalid"  # Shouldn't exist normally

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get formatted display name.

        Returns:
            User's name with admin indicator if administrator.

        Example:
            >>> user.display_name
            'John Doe [ADMIN]'
        """
        return f"{self.name} [ADMIN]" if self.is_admin else self.name

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes any fields without values to keep API payloads clean.

        Args:
            custom: List of custom field dicts.

        Returns:
            Cleaned list with only fields that have values.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """
        Edit this user.

        Uses Pydantic v2's optimized serialization via to_api_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated user with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> user = await upsales.users.get(1)
            >>> updated = await user.edit(
            ...     name="Jane Doe",
            ...     email="jane@example.com",
            ...     administrator=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(self.id, **self.to_update_dict_minimal(**kwargs))


class PartialUser(PartialModel):
    """
    Partial User for nested responses.

    Contains minimal fields for when User appears nested in other
    API responses (e.g., as account owner, contact owner, etc.).

    Use fetch_full() to get complete User object with all fields.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> owner = company.owner  # PartialUser
        >>> full_user = await owner.fetch_full()  # Now User
    """

    id: int = Field(frozen=True, strict=True, description="Unique user ID")
    name: NonEmptyStr = Field(description="User's name")
    email: EmailStr = Field(description="User's email")
    role: dict[str, Any] | None = Field(None, description="User's role information")

    async def fetch_full(self) -> User:
        """
        Fetch complete user data.

        Returns:
            Full User object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = company.owner  # PartialUser
            >>> full = await partial.fetch_full()  # User
            >>> full.administrator  # Now available
            1
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.get(self.id)

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> User:
        """
        Edit this user.

        Returns full User object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full User object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = company.owner  # PartialUser
            >>> updated = await partial.edit(name="Jane")  # Returns User
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.users.update(self.id, **kwargs)
