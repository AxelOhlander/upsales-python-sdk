"""
Mail templates resource manager for Upsales API.

Provides methods to interact with the /mail/templates endpoint using MailTemplate models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single template
    ...     template = await upsales.mail_templates.get(1)
    ...     print(template.name, template.is_active)
    ...
    ...     # List templates
    ...     templates = await upsales.mail_templates.list(limit=10)
    ...
    ...     # Get template by name
    ...     template = await upsales.mail_templates.get_by_name("Welcome Email")
    ...
    ...     # Get all active templates
    ...     active = await upsales.mail_templates.get_active()
"""

from upsales.http import HTTPClient
from upsales.models.mail_templates import MailTemplate, PartialMailTemplate
from upsales.resources.base import BaseResource


class MailTemplatesResource(BaseResource[MailTemplate, PartialMailTemplate]):
    """
    Resource manager for MailTemplate endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single template
    - list(limit, offset, **params) - List templates with pagination
    - list_all(**params) - Auto-paginated list of all templates
    - create(**data) - Create new template
    - update(id, **data) - Update template
    - delete(id) - Delete template
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_name(name) - Get template by name
    - get_active() - Get all active templates
    - get_inactive() - Get all inactive templates
    - get_private() - Get all private templates
    - get_public() - Get all public templates
    - get_editable() - Get all user-editable templates

    Example:
        >>> templates = MailTemplatesResource(http_client)
        >>> template = await templates.get(1)
        >>> welcome = await templates.get_by_name("Welcome Email")
        >>> all_active = await templates.get_active()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize mail templates resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/mail/templates",
            model_class=MailTemplate,
            partial_class=PartialMailTemplate,
        )

    async def get_by_name(self, name: str) -> MailTemplate | None:
        """
        Get template by name.

        Args:
            name: Template name to search for (case-insensitive).

        Returns:
            MailTemplate object if found, None otherwise.

        Example:
            >>> template = await upsales.mail_templates.get_by_name("Welcome Email")
            >>> if template:
            ...     print(template.subject)
        """
        all_templates: list[MailTemplate] = await self.list_all()
        for template in all_templates:
            if template.name.lower() == name.lower():
                return template
        return None

    async def get_active(self) -> list[MailTemplate]:
        """
        Get all active templates.

        Returns:
            List of templates with active=1.

        Example:
            >>> active = await upsales.mail_templates.get_active()
            >>> for template in active:
            ...     print(f"{template.name} - {template.subject}")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if t.is_active]

    async def get_inactive(self) -> list[MailTemplate]:
        """
        Get all inactive templates.

        Returns:
            List of templates with active=0.

        Example:
            >>> inactive = await upsales.mail_templates.get_inactive()
            >>> print(f"Found {len(inactive)} inactive templates")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if not t.is_active]

    async def get_private(self) -> list[MailTemplate]:
        """
        Get all private templates.

        Returns:
            List of templates with private=1.

        Example:
            >>> private = await upsales.mail_templates.get_private()
            >>> for template in private:
            ...     print(f"Private: {template.name}")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if t.is_private]

    async def get_public(self) -> list[MailTemplate]:
        """
        Get all public templates.

        Returns:
            List of templates with private=0.

        Example:
            >>> public = await upsales.mail_templates.get_public()
            >>> print(f"Found {len(public)} public templates")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if not t.is_private]

    async def get_editable(self) -> list[MailTemplate]:
        """
        Get all user-editable templates.

        Returns:
            List of templates with user_editable=True.

        Example:
            >>> editable = await upsales.mail_templates.get_editable()
            >>> for template in editable:
            ...     print(f"Editable: {template.name}")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if t.is_editable]

    async def get_removable(self) -> list[MailTemplate]:
        """
        Get all user-removable templates.

        Returns:
            List of templates with user_removable=True.

        Example:
            >>> removable = await upsales.mail_templates.get_removable()
            >>> print(f"Found {len(removable)} removable templates")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if t.is_removable]

    async def get_with_attachments(self) -> list[MailTemplate]:
        """
        Get all templates that have attachments.

        Returns:
            List of templates with non-empty attachments list.

        Example:
            >>> with_attachments = await upsales.mail_templates.get_with_attachments()
            >>> for template in with_attachments:
            ...     print(f"{template.name} has {template.attachment_count} attachments")
        """
        all_templates: list[MailTemplate] = await self.list_all()
        return [t for t in all_templates if t.has_attachments]
