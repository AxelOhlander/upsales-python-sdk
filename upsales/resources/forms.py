"""
Forms resource manager for Upsales API.

Provides methods to interact with the /forms endpoint using Form models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single form
    ...     form = await upsales.forms.get(1)
    ...     print(form.title, form.submission_count)
    ...
    ...     # List forms
    ...     forms = await upsales.forms.list(limit=10)
    ...
    ...     # Get active forms (not archived)
    ...     active = await upsales.forms.get_active()
    ...
    ...     # Get forms with submissions
    ...     with_submissions = await upsales.forms.get_with_submissions()
"""

from upsales.http import HTTPClient
from upsales.models.forms import Form, PartialForm
from upsales.resources.base import BaseResource


class FormsResource(BaseResource[Form, PartialForm]):
    """
    Resource manager for Forms endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single form
    - list(limit, offset, **params) - List forms with pagination
    - list_all(**params) - Auto-paginated list of all forms
    - create(**data) - Create new form
    - update(id, **data) - Update form
    - delete(id) - Delete form
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active (non-archived) forms
    - get_archived() - Get all archived forms
    - get_with_submissions() - Get forms that have submissions
    - get_by_name(name) - Get form by name

    Example:
        >>> forms = FormsResource(http_client)
        >>> form = await forms.get(1)
        >>> active = await forms.get_active()
        >>> with_submissions = await forms.get_with_submissions()
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
            List of forms with isArchived=0.

        Example:
            >>> active_forms = await upsales.forms.get_active()
            >>> for form in active_forms:
            ...     print(f"{form.title} - {form.submission_count} submissions")
        """
        all_forms: list[Form] = await self.list_all()
        return [form for form in all_forms if not form.is_archived]

    async def get_archived(self) -> list[Form]:
        """
        Get all archived forms.

        Returns:
            List of forms with isArchived=1.

        Example:
            >>> archived_forms = await upsales.forms.get_archived()
            >>> for form in archived_forms:
            ...     print(f"{form.title} - Archived on {form.modDate}")
        """
        all_forms: list[Form] = await self.list_all()
        return [form for form in all_forms if form.is_archived]

    async def get_with_submissions(self) -> list[Form]:
        """
        Get all forms that have received submissions.

        Returns:
            List of forms where submits > 0.

        Example:
            >>> forms_with_data = await upsales.forms.get_with_submissions()
            >>> for form in forms_with_data:
            ...     print(f"{form.title} - {form.submission_count} submissions")
        """
        all_forms: list[Form] = await self.list_all()
        return [form for form in all_forms if form.has_submissions]

    async def get_by_name(self, name: str) -> Form | None:
        """
        Get form by name.

        Args:
            name: Form name to search for (case-insensitive).

        Returns:
            Form object if found, None otherwise.

        Example:
            >>> form = await upsales.forms.get_by_name("Contact Us")
            >>> if form:
            ...     print(f"Form ID: {form.id}, Submissions: {form.submission_count}")
        """
        all_forms: list[Form] = await self.list_all()
        for form in all_forms:
            if form.name.lower() == name.lower():
                return form
        return None

    async def get_by_title(self, title: str) -> Form | None:
        """
        Get form by display title.

        Args:
            title: Form title to search for (case-insensitive).

        Returns:
            Form object if found, None otherwise.

        Example:
            >>> form = await upsales.forms.get_by_title("Kontakta oss")
            >>> if form:
            ...     print(f"Internal name: {form.name}")
        """
        all_forms: list[Form] = await self.list_all()
        for form in all_forms:
            if form.title.lower() == title.lower():
                return form
        return None
