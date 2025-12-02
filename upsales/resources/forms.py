"""
Forms resource manager for Upsales API.

Provides methods to interact with the /forms endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     form = await upsales.forms.get(1)
    ...     forms_list = await upsales.forms.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.forms import Form, PartialForm
from upsales.resources.base import BaseResource


class FormsResource(BaseResource[Form, PartialForm]):
    """
    Resource manager for Form endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single form
    - list(limit, offset, **params) - List forms with pagination
    - list_all(**params) - Auto-paginated list of all forms
    - update(id, **data) - Update form
    - delete(id) - Delete form
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = FormsResource(http_client)
        >>> form = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize forms resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/forms",
            model_class=Form,
            partial_class=PartialForm,
        )

    async def get_active(self) -> list[Form]:
        """
        Get all active (non-archived) forms.

        Returns:
            List of active forms.

        Example:
            >>> active_forms = await upsales.forms.get_active()
            >>> for form in active_forms:
            ...     print(f"{form.name}: {form.submits} submissions")
        """
        forms = await self.list_all()
        return [form for form in forms if not form.is_archived]

    async def get_archived(self) -> list[Form]:
        """
        Get all archived forms.

        Returns:
            List of archived forms.

        Example:
            >>> archived_forms = await upsales.forms.get_archived()
        """
        forms = await self.list_all()
        return [form for form in forms if form.is_archived]

    async def get_with_submissions(self) -> list[Form]:
        """
        Get all forms that have at least one submission.

        Returns:
            List of forms with submissions > 0.

        Example:
            >>> forms_with_data = await upsales.forms.get_with_submissions()
            >>> for form in forms_with_data:
            ...     print(f"{form.name}: {form.submits} submissions")
        """
        all_forms: list[Form] = await self.list_all()
        return [form for form in all_forms if form.submits > 0]

    async def get_by_name(self, name: str) -> Form | None:
        """
        Get a form by its name field.

        Args:
            name: The form name to search for.

        Returns:
            The form with matching name, or None if not found.

        Example:
            >>> form = await upsales.forms.get_by_name("contact_form")
            >>> if form:
            ...     print(f"Found: {form.title}")
        """
        all_forms: list[Form] = await self.list_all()
        for form in all_forms:
            if form.name == name:
                return form
        return None

    async def get_by_title(self, title: str) -> Form | None:
        """
        Get a form by its title field (case-insensitive).

        Args:
            title: The form title to search for (case-insensitive).

        Returns:
            The form with matching title, or None if not found.

        Example:
            >>> form = await upsales.forms.get_by_title("Contact Us")
            >>> if form:
            ...     print(f"Found: {form.name}")
        """
        all_forms: list[Form] = await self.list_all()
        title_lower = title.lower()
        for form in all_forms:
            if form.title.lower() == title_lower:
                return form
        return None
