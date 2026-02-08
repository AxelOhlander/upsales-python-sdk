"""
Form submission models for Upsales API.

Generated from /api/v2/formSubmits endpoint.
Analysis based on 253 samples.

Form submissions track when users fill out forms, including the submitted
data, associated contact/company, and processing status.

Requires admin or mailAdmin permission to access.
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from upsales.models.company import PartialCompany
    from upsales.models.contacts import PartialContact
    from upsales.models.forms import PartialForm


class FormSubmitUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a FormSubmit.

    All fields are optional. Note that userRemovable, userEditable,
    brandId, and id are read-only per API spec.
    """

    formId: int
    form: dict[str, Any]
    contact: dict[str, Any]
    client: dict[str, Any]
    score: int
    regDate: str
    processedDate: str
    fieldValues: list[dict[str, Any]]
    visit: dict[str, Any] | None


class FormSubmit(BaseModel):
    """
    Form submission model from /api/v2/formSubmits.

    Represents a single form submission with associated contact, company,
    field values, and processing metadata. Requires admin or mailAdmin
    permission to access.

    Attributes:
        id: Unique form submission ID (read-only)
        formId: ID of the form that was submitted
        form: Nested form object with id and name
        contact: Contact who submitted the form
        client: Company associated with the submission
        score: Lead score or submission score
        regDate: Registration date (when submitted)
        processedDate: Date when the submission was processed
        fieldValues: List of field value dictionaries
        visit: Associated visit tracking data (optional)
        userRemovable: Whether user can delete this submission (read-only, boolean from API)
        userEditable: Whether user can edit this submission (read-only, boolean from API)
        brandId: Brand identifier (read-only)

    Example:
        >>> submission = await upsales.form_submits.get(123)
        >>> print(f"Form: {submission.form['name']}")
        >>> print(f"Contact: {submission.contact.name}")
        >>> await submission.edit(score=85)
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique form submission ID")
    userRemovable: bool = Field(
        frozen=True, description="Whether user can delete this submission (boolean from API)"
    )
    userEditable: bool = Field(
        frozen=True, description="Whether user can edit this submission (boolean from API)"
    )
    brandId: int = Field(frozen=True, description="Brand identifier")
    regDate: str = Field(frozen=True, description="Registration date (when submitted)")

    # Updatable fields
    formId: int = Field(description="ID of the form that was submitted")
    form: "PartialForm | dict[str, Any]" = Field(description="Nested form object with id and name")
    contact: "PartialContact | dict[str, Any]" = Field(description="Contact who submitted the form")
    client: "PartialCompany | dict[str, Any]" = Field(
        description="Company associated with the submission"
    )
    score: int = Field(description="Lead score or submission score")
    processedDate: str = Field(description="Date when the submission was processed")
    fieldValues: list[dict[str, Any]] = Field(
        default_factory=list, description="List of field value dictionaries"
    )
    visit: dict[str, Any] | None = Field(None, description="Associated visit tracking data")

    @computed_field
    @property
    def is_removable(self) -> bool:
        """Check if user can delete this submission."""
        return self.userRemovable

    @computed_field
    @property
    def is_editable(self) -> bool:
        """Check if user can edit this submission."""
        return self.userEditable

    async def edit(self, **kwargs: Unpack[FormSubmitUpdateFields]) -> "FormSubmit":
        """
        Edit this form submission.

        Args:
            **kwargs: Fields to update (formId, form, contact, client, score,
                     processedDate, fieldValues, visit).

        Returns:
            Updated form submission.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> submission = await upsales.form_submits.get(123)
            >>> updated = await submission.edit(score=90, processedDate="2025-11-14")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.form_submits.update(self.id, **self.to_api_dict(**kwargs))


class PartialFormSubmit(PartialModel):
    """
    Partial FormSubmit for nested responses.

    Contains minimal form submission information when included as a
    nested object in other API responses.

    Attributes:
        id: Unique form submission ID

    Example:
        >>> partial = contact.last_form_submission  # hypothetical
        >>> full = await partial.fetch_full()
        >>> print(full.fieldValues)
    """

    id: int = Field(description="Unique form submission ID")

    async def fetch_full(self) -> FormSubmit:
        """
        Fetch full form submission data.

        Returns:
            Complete FormSubmit object with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialFormSubmit(id=123, _client=upsales)
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.form_submits.get(self.id)

    async def edit(self, **kwargs: Unpack[FormSubmitUpdateFields]) -> FormSubmit:
        """
        Edit this form submission.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated FormSubmit object.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialFormSubmit(id=123, _client=upsales)
            >>> updated = await partial.edit(score=95)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.form_submits.update(self.id, **kwargs)
