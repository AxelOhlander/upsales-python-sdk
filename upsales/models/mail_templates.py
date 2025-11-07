"""
Mail template models for Upsales API.

Generated from /api/v2/mail/templates endpoint.
Analysis based on 1 sample.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, NonEmptyStr)
- Computed fields (@computed_field)
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, NonEmptyStr


class MailTemplateUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a MailTemplate.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    from_address: str
    from_name: str
    subject: str
    body: str
    body_json: str
    active: int
    private: int
    user_editable: bool
    user_removable: bool
    attachments: list[Any]
    labels: list[Any]
    roles: list[Any]


class MailTemplate(BaseModel):
    """
    Mail template model from /api/v2/mail/templates.

    Represents an email template in the Upsales system. Enhanced with
    Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 1 sample with field analysis.

    Example:
        >>> template = await upsales.mail_templates.get(1)
        >>> template.name
        'test template'
        >>> template.is_active  # Computed property
        True
        >>> template.is_private  # Computed property
        False
        >>> await template.edit(subject="New Subject")  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique template ID")
    reg_date: str = Field(frozen=True, description="Registration date", alias="regDate")
    mod_date: str = Field(frozen=True, description="Last modification date", alias="modDate")
    version: int = Field(frozen=True, description="Template version")

    # Required fields with validators
    name: NonEmptyStr = Field(description="Template name")
    subject: NonEmptyStr = Field(description="Email subject line")
    body: str = Field(description="Email body HTML content")

    # Binary flags (validated 0 or 1)
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    private: BinaryFlag = Field(default=0, description="Private visibility (0=public, 1=private)")

    # Required fields
    from_address: str = Field(description="Sender email address", alias="from")
    from_name: str = Field(description="Sender display name", alias="fromName")
    body_json: str = Field(description="Email body JSON structure", alias="bodyJson")
    user_editable: bool = Field(
        description="Whether template is editable by users", alias="userEditable"
    )
    user_removable: bool = Field(
        description="Whether template can be removed by users", alias="userRemovable"
    )

    # Optional/list fields
    user: PartialUser | None = Field(default=None, description="Template creator/owner")
    used_counter: int | None = Field(
        default=None, description="Number of times template used", alias="usedCounter"
    )
    attachments: list[Any] = Field(default=[], description="Template attachments")
    labels: list[Any] = Field(default=[], description="Template labels/tags")
    roles: list[Any] = Field(default=[], description="Roles with access to template")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if template is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> template.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def is_private(self) -> bool:
        """
        Check if template is private.

        Returns:
            True if private flag is 1, False otherwise.

        Example:
            >>> template.is_private
            False
        """
        return self.private == 1

    @computed_field
    @property
    def is_editable(self) -> bool:
        """
        Check if template is editable by users.

        Returns:
            True if user_editable is True, False otherwise.

        Example:
            >>> template.is_editable
            True
        """
        return self.user_editable

    @computed_field
    @property
    def is_removable(self) -> bool:
        """
        Check if template can be removed by users.

        Returns:
            True if user_removable is True, False otherwise.

        Example:
            >>> template.is_removable
            True
        """
        return self.user_removable

    @computed_field
    @property
    def has_attachments(self) -> bool:
        """
        Check if template has attachments.

        Returns:
            True if attachments list is not empty, False otherwise.

        Example:
            >>> template.has_attachments
            False
        """
        return len(self.attachments) > 0

    @computed_field
    @property
    def attachment_count(self) -> int:
        """
        Get number of attachments.

        Returns:
            Number of attachments in the template.

        Example:
            >>> template.attachment_count
            0
        """
        return len(self.attachments)

    async def edit(self, **kwargs: Unpack[MailTemplateUpdateFields]) -> "MailTemplate":
        """
        Edit this mail template.

        Args:
            **kwargs: Fields to update. IDE provides autocomplete for all
                available fields (name, subject, body, active, etc.).

        Returns:
            Updated mail template with new values.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> template = await upsales.mail_templates.get(1)
            >>> updated = await template.edit(subject="New Subject", active=1)
            >>> updated.subject
            'New Subject'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_templates.update(self.id, **self.to_api_dict(**kwargs))


class PartialMailTemplate(PartialModel):
    """
    Partial mail template model for nested responses.

    Contains minimal data when a mail template appears in another object's response.
    Use fetch_full() to get complete data.

    Example:
        >>> partial_template = some_object.template  # PartialMailTemplate
        >>> full_template = await partial_template.fetch_full()  # MailTemplate
        >>> full_template.body  # Now has all fields
    """

    id: int = Field(description="Unique template ID")
    name: str = Field(description="Template name")

    async def fetch_full(self) -> MailTemplate:
        """
        Fetch the full mail template data.

        Returns:
            Complete MailTemplate object with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = some_object.template
            >>> full = await partial.fetch_full()
            >>> full.body  # Access full data
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_templates.get(self.id)

    async def edit(self, **kwargs: Unpack[MailTemplateUpdateFields]) -> MailTemplate:
        """
        Edit this mail template directly from partial model.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated MailTemplate with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = some_object.template
            >>> updated = await partial.edit(subject="New Subject")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_templates.update(self.id, **kwargs)
