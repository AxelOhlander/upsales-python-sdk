"""User invite models for the Upsales API.

This module provides Pydantic models for managing user invitations stored in Redis.
User invites represent pending user account creations with temporary storage.
"""

from __future__ import annotations

from typing import TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import BinaryFlag, CustomFieldsList, EmailStr


class UserInviteUpdateFields(TypedDict, total=False):
    """Available fields for updating a UserInvite.

    All fields are optional. Only provided fields will be updated.
    """

    name: str
    administrator: int
    export: int
    language: str
    role: dict[str, int] | None
    email: str
    active: int
    ghost: int
    crm: int
    support: int
    custom: list[dict[str, int | str]]


class UserInvite(BaseModel):
    """Represents a user invitation in the Upsales system.

    User invites are stored in Redis with expiration and represent pending
    user account creations. Once accepted, they are converted to full User accounts.

    Attributes:
        id: Unique identifier (UUID string in Redis).
        name: Full name of the invited user.
        administrator: Administrator status (0 or 1).
        export: Export permission status (0 or 1).
        language: Preferred language code (e.g., 'en', 'sv').
        role: Role object with nested structure.
        email: Email address for the invitation.
        killDate: Expiration date for the invitation.
        custom: Custom field values as list of dicts.
        active: Active status (0 or 1).
        ghost: Ghost user status (0 or 1).
        crm: CRM access (0 or 1).
        support: Support access (0 or 1).

    Examples:
        Create a new user invite:
        >>> invite = UserInvite(
        ...     id="invite-uuid-123",
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     administrator=0,
        ...     active=1
        ... )
        >>> print(invite.name)
        John Doe

        Check if invite is for an administrator:
        >>> print(invite.is_admin)
        False

        Access custom fields:
        >>> invite.custom = [{"fieldId": 1, "value": "Sales"}]
        >>> print(invite.custom_fields.get(1))
        Sales
    """

    # Read-only fields (frozen)
    # Note: userInvites uses UUID strings as IDs (not integers like other resources)
    id: str = Field(frozen=True, strict=True, description="Unique invite identifier (UUID)")  # type: ignore[assignment]
    killDate: str | None = Field(None, frozen=True, description="Invitation expiration date")

    # Required fields
    name: str = Field(description="Full name of invited user")
    email: EmailStr = Field(description="Email address for invitation")

    # Optional fields with defaults
    administrator: BinaryFlag = Field(default=0, description="Administrator status (0 or 1)")
    export: BinaryFlag = Field(default=0, description="Export permission (0 or 1)")
    language: str | None = Field(None, description="Preferred language code")
    role: dict[str, int] | None = Field(None, description="Role object with nested structure")
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")
    ghost: BinaryFlag = Field(default=0, description="Ghost user status (0 or 1)")
    crm: BinaryFlag = Field(default=1, description="CRM access (0 or 1)")
    support: BinaryFlag = Field(default=0, description="Support access (0 or 1)")
    custom: CustomFieldsList = Field(default=[], description="Custom field values")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with a dict-like interface.

        Returns:
            CustomFields: Helper object for accessing custom fields.

        Examples:
            >>> invite.custom = [{"fieldId": 1, "value": "Sales"}]
            >>> print(invite.custom_fields.get(1))
            Sales
            >>> invite.custom_fields.set(2, "Manager")
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_admin(self) -> bool:
        """Check if the invited user will be an administrator.

        Returns:
            bool: True if administrator flag is set.

        Examples:
            >>> invite = UserInvite(id="1", name="Admin", email="admin@ex.com", administrator=1)
            >>> print(invite.is_admin)
            True
        """
        return self.administrator == 1

    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if the invitation is active.

        Returns:
            bool: True if active flag is set.

        Examples:
            >>> invite = UserInvite(id="1", name="User", email="user@ex.com", active=1)
            >>> print(invite.is_active)
            True
        """
        return self.active == 1

    @computed_field
    @property
    def has_crm_access(self) -> bool:
        """Check if the invited user will have CRM access.

        Returns:
            bool: True if CRM access is granted.

        Examples:
            >>> invite = UserInvite(id="1", name="User", email="user@ex.com", crm=1)
            >>> print(invite.has_crm_access)
            True
        """
        return self.crm == 1

    @computed_field
    @property
    def has_support_access(self) -> bool:
        """Check if the invited user will have support access.

        Returns:
            bool: True if support access is granted.

        Examples:
            >>> invite = UserInvite(id="1", name="User", email="user@ex.com", support=1)
            >>> print(invite.has_support_access)
            True
        """
        return self.support == 1

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(
        self, custom: list[dict[str, int | str]]
    ) -> list[dict[str, int | str]]:
        """Clean custom fields for API requests.

        Removes empty values and includes only fieldId and value.

        Args:
            custom: List of custom field dictionaries.

        Returns:
            list[dict]: Cleaned custom field data.
        """
        return [
            {"fieldId": item["fieldId"], "value": item["value"]}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[UserInviteUpdateFields]) -> UserInvite:
        """Edit this user invite with type-safe field updates.

        This method provides full IDE autocomplete for all updatable fields.
        Only the provided fields will be updated.

        Args:
            **kwargs: Fields to update (see UserInviteUpdateFields for available options).

        Returns:
            UserInvite: Updated user invite instance.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            >>> invite = await upsales.user_invites.get("invite-123")
            >>> updated = await invite.edit(
            ...     name="Jane Doe",
            ...     administrator=1
            ... )
            >>> print(updated.name)
            Jane Doe
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.user_invites.update(self.id, **self.to_api_dict(**kwargs))  # type: ignore[arg-type]


class PartialUserInvite(PartialModel):
    """Minimal user invite representation for nested API responses.

    Used when user invites appear as nested objects in other resources.

    Attributes:
        id: Unique invite identifier (UUID).
        name: Full name of invited user.
        email: Email address for invitation.

    Examples:
        Fetch full details from a partial:
        >>> partial = PartialUserInvite(id="invite-123", name="John", email="john@ex.com")
        >>> full = await partial.fetch_full()
        >>> print(full.administrator)
        0
    """

    id: str = Field(description="Unique invite identifier (UUID)")  # type: ignore[assignment]
    name: str = Field(description="Full name of invited user")
    email: EmailStr = Field(description="Email address for invitation")

    async def fetch_full(self) -> UserInvite:
        """Fetch the complete UserInvite object.

        Returns:
            UserInvite: Full user invite with all fields.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            >>> partial = PartialUserInvite(id="invite-123", name="John", email="john@ex.com")
            >>> full = await partial.fetch_full()
            >>> print(full.custom_fields)
            <CustomFields object>
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.user_invites.get(self.id)  # type: ignore[arg-type]

    async def edit(self, **kwargs: Unpack[UserInviteUpdateFields]) -> UserInvite:
        """Edit this user invite and return the updated full object.

        Args:
            **kwargs: Fields to update (see UserInviteUpdateFields).

        Returns:
            UserInvite: Updated full user invite.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            >>> partial = PartialUserInvite(id="invite-123", name="John", email="john@ex.com")
            >>> updated = await partial.edit(name="Jane Doe")
            >>> print(updated.name)
            Jane Doe
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.user_invites.update(self.id, **kwargs)  # type: ignore[arg-type]
