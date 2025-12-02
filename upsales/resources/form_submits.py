"""
Form submissions resource manager for Upsales API.

Provides methods to interact with the /formSubmits endpoint.
Requires admin or mailAdmin permission to access.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     submission = await upsales.form_submits.get(1)
    ...     submissions_list = await upsales.form_submits.list(limit=10)
    ...     by_form = await upsales.form_submits.get_by_form_id(123)
"""

from upsales.http import HTTPClient
from upsales.models.form_submits import FormSubmit, PartialFormSubmit
from upsales.resources.base import BaseResource


class FormSubmitsResource(BaseResource[FormSubmit, PartialFormSubmit]):
    """
    Resource manager for FormSubmit endpoint.

    Handles form submission records including submitted data, associated
    contacts/companies, and processing status. Requires admin or mailAdmin
    permission to access.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single form submission
    - list(limit, offset, **params) - List submissions with pagination
    - list_all(**params) - Auto-paginated list of all submissions
    - update(id, **data) - Update submission
    - delete(id) - Delete submission
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = FormSubmitsResource(http_client)
        >>> submission = await resource.get(1)
        >>> recent = await resource.list(limit=20)
        >>> by_form = await resource.get_by_form_id(123)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize form submissions resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/formSubmits",
            model_class=FormSubmit,
            partial_class=PartialFormSubmit,
        )

    async def get_by_form_id(self, form_id: int) -> list[FormSubmit]:
        """
        Get all submissions for a specific form.

        Args:
            form_id: Form ID to filter by.

        Returns:
            List of form submissions for the specified form.

        Example:
            >>> submissions = await upsales.form_submits.get_by_form_id(123)
            >>> print(f"Found {len(submissions)} submissions")
        """
        return await self.list_all(formId=form_id)
