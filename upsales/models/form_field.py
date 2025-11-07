"""
Form field models for Upsales API.

Form fields define the structure of form inputs in Upsales forms.
They are nested within Form objects and do not have their own endpoint.

API Structure:
    Form fields appear in Form.fields as a list of dicts with the following structure:
    {
        "name": "Contact.firstname",
        "title": "Förnamn",
        "required": false,
        "datatype": "text",
        "options": "",
        "sort": 1,
        "placeholder": "",
        "info": null,
        "language": null,
        "formId": 7
    }

Enhanced with Pydantic v2 features:
- NonEmptyStr validator for required string fields
- Field descriptions for all fields
- Strict type checking
- No edit() or fetch_full() methods (nested only, no standalone endpoint)
"""

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, NonEmptyStr


class FormField(BaseModel):
    """
    Form field definition model.

    Represents a single field in an Upsales form, defining its structure,
    validation, appearance, and behavior. Form fields are nested within
    Form objects and do not exist as standalone API resources.

    Note:
        This model does not have edit() or fetch_full() methods since
        form fields are only accessible as nested data within forms.
        To update a form field, you must update the parent form's
        fields list.

    Example:
        >>> form = await upsales.forms.get(1)
        >>> for field in form.fields:
        ...     print(f"{field.title}: {field.datatype}")
        'Förnamn: text'
        'Email: email'
        >>> field = form.fields[0]
        >>> field.title
        'Förnamn'
        >>> field.is_required
        False
    """

    # Primary fields (always present)
    id: int = Field(frozen=True, strict=True, description="Unique form field ID")
    formId: int = Field(description="ID of the parent form this field belongs to")
    name: NonEmptyStr = Field(
        description="Field name/identifier (e.g., 'Contact.firstname', 'Company.name')"
    )
    title: NonEmptyStr = Field(description="Display title shown to users")
    datatype: NonEmptyStr = Field(
        description="Field data type (e.g., 'text', 'email', 'number', 'select')"
    )
    sort: int = Field(default=0, description="Sort order for field display (lower = earlier)")
    required: BinaryFlag = Field(default=0, description="Whether field is required (0=no, 1=yes)")

    # Optional fields
    options: str = Field(
        default="",
        description="Options for select/radio fields (comma-separated or JSON)",
    )
    placeholder: str = Field(default="", description="Placeholder text shown in empty field")
    info: str | None = Field(default=None, description="Help text or description for users")
    language: str | None = Field(
        default=None, description="Language code for localized fields (e.g., 'sv', 'en')"
    )

    @property
    def is_required(self) -> bool:
        """
        Check if field is required.

        Returns:
            True if required flag is 1, False otherwise.

        Example:
            >>> field.required
            1
            >>> field.is_required
            True
        """
        return self.required == 1

    async def edit(self, **kwargs: Any) -> "FormField":
        """
        Edit not supported for form fields.

        Form fields are nested within forms and cannot be edited independently.
        To update a form field, update the parent form's fields list.

        Raises:
            NotImplementedError: Always, as form fields have no standalone endpoint.

        Example:
            >>> form = await upsales.forms.get(1)
            >>> # Update field in parent form
            >>> form.fields[0]["title"] = "New Title"
            >>> await form.edit(fields=form.fields)
        """
        raise NotImplementedError(
            "FormField cannot be edited independently. "
            "Update the parent form's fields list instead."
        )


class PartialFormField(PartialModel):
    """
    Partial form field model for minimal nested references.

    Contains only essential form field data when form fields appear
    in extremely nested contexts or summary views.

    Note:
        Like FormField, this model does not have edit() or fetch_full()
        methods since form fields are only accessible via their parent form.

    Example:
        >>> # If a nested object references a form field
        >>> partial_field = some_object.field
        >>> partial_field.name
        'Contact.firstname'
        >>> partial_field.title
        'Förnamn'
    """

    id: int = Field(description="Unique form field ID")
    name: str = Field(description="Field name/identifier")
    title: str = Field(description="Display title")
    datatype: str = Field(description="Field data type")

    async def fetch_full(self) -> FormField:
        """
        Fetch full not supported for form fields.

        Form fields are nested within forms and cannot be fetched independently.
        To get the full form field data, fetch the parent form.

        Raises:
            NotImplementedError: Always, as form fields have no standalone endpoint.

        Example:
            >>> # Get form field through parent form
            >>> form = await upsales.forms.get(field.formId)
            >>> full_field = next(f for f in form.fields if f.id == field.id)
        """
        raise NotImplementedError(
            "FormField cannot be fetched independently. "
            "Fetch the parent form and access its fields list."
        )

    async def edit(self, **kwargs: Any) -> FormField:
        """
        Edit not supported for form fields.

        Form fields are nested within forms and cannot be edited independently.
        To update a form field, update the parent form's fields list.

        Raises:
            NotImplementedError: Always, as form fields have no standalone endpoint.

        Example:
            >>> # Update field through parent form
            >>> form = await upsales.forms.get(field.formId)
            >>> for f in form.fields:
            ...     if f["id"] == field.id:
            ...         f["title"] = "New Title"
            >>> await form.edit(fields=form.fields)
        """
        raise NotImplementedError(
            "FormField cannot be edited independently. "
            "Update the parent form's fields list instead."
        )
