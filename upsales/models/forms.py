"""
Form models for Upsales API.

Generated from /api/v2/forms endpoint.
Analysis based on API data.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for boolean helpers
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.form_action import FormAction
from upsales.models.form_element import FormElement
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, NonEmptyStr


class FormUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Form.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    title: str
    name: str
    internalName: str
    description: str
    landingPage: str
    buttonText: str
    thankYouTitle: str
    thankYouTitleOnDemand: str | None
    thankYouText: str
    thankYouTextOnDemand: str | None
    formType: str | None
    supportEmailId: int | None
    buttonBgColor: str
    buttonTextColor: str
    backgroundColor: str
    backgroundColorOnDemand: str | None
    textColor: str
    linkColor: str
    score: int
    redirect: int
    showTitle: int
    fields: list[dict[str, Any]]
    actions: list[FormAction]
    isArchived: int
    landingPageBody: str | None
    socialEventId: int | None
    domain: str | None
    urlName: str | None


class Form(BaseModel):
    """
    Form model from /api/v2/forms.

    Represents a form (landing page) in Upsales for lead capture.
    Forms can be embedded on websites or used as standalone landing pages.

    Example:
        >>> form = await upsales.forms.get(1)
        >>> form.title
        'Contact Us'
        >>> form.is_archived
        False
        >>> form.submission_count
        42
        >>> await form.edit(title="New Title")
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique form ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")
    uuid: str = Field(frozen=True, description="Unique form UUID for public URL")
    html: str = Field(frozen=True, description="Generated HTML for the form (read-only)")
    socialMediaTags: str = Field(
        frozen=True, description="Generated social media tags JSON (read-only)"
    )
    user: PartialUser = Field(frozen=True, description="User who created this form (read-only)")
    submits: int = Field(
        frozen=True, default=0, description="Total number of form submissions (read-only)"
    )
    views: int = Field(frozen=True, default=0, description="Total number of form views (read-only)")
    lastSubmitDate: str | None = Field(
        frozen=True, default=None, description="Date of last submission (ISO 8601, read-only)"
    )
    userEditable: bool = Field(
        frozen=True, default=True, description="Whether user can edit this form (read-only)"
    )
    userRemovable: bool = Field(
        frozen=True,
        default=True,
        description="Whether user can remove this form (read-only)",
    )
    brandId: int = Field(frozen=True, description="Brand ID (read-only)")

    # Required updatable fields
    title: NonEmptyStr = Field(description="Form display title")
    name: NonEmptyStr = Field(description="Internal form name")
    internalName: str = Field(default="", description="Additional internal identifier")
    description: str = Field(default="", description="Form description/subtitle")
    buttonText: str = Field(default="Submit", description="Submit button text")
    thankYouTitle: str = Field(default="Thank you", description="Thank you page title")
    thankYouTitleOnDemand: str | None = Field(
        default=None, description="Thank you title for on-demand events"
    )
    thankYouText: str = Field(default="", description="Thank you page message")
    thankYouTextOnDemand: str | None = Field(
        default=None, description="Thank you message for on-demand events"
    )
    buttonBgColor: str = Field(default="#000000", description="Submit button background color")
    buttonTextColor: str = Field(default="#ffffff", description="Submit button text color (hex)")
    backgroundColor: str = Field(default="#ffffff", description="Form background color (hex)")
    backgroundColorOnDemand: str | None = Field(
        default=None, description="Background color for on-demand events (hex)"
    )
    textColor: str = Field(default="#000000", description="Form text color (hex)")
    linkColor: str = Field(default="#4A90E2", description="Form link color (hex)")
    landingPage: str = Field(default="", description="Landing page URL")
    score: int = Field(default=0, description="Form score value")
    redirect: BinaryFlag = Field(default=0, description="Redirect after submission (0=no, 1=yes)")
    showTitle: BinaryFlag = Field(default=1, description="Show form title (0=no, 1=yes)")
    isArchived: BinaryFlag = Field(default=0, description="Archived status (0=active, 1=archived)")
    fields: list[dict[str, Any]] = Field(
        default=[], description="Form field definitions (name, title, required, datatype, etc.)"
    )
    actions: list[FormAction] = Field(default=[], description="Form actions/triggers")
    labels: list[Any] = Field(default=[], description="Form labels/tags")
    projects: list[Any] = Field(default=[], description="Associated projects")

    # Optional fields
    formType: str | None = Field(default=None, description="Form type identifier")
    supportEmailId: int | None = Field(default=None, description="Support email ID for routing")
    landingPageBody: str | None = Field(default=None, description="Custom landing page HTML body")
    thankYouElement: FormElement | None = Field(
        default=None, description="Custom thank you page element (text, image, etc.)"
    )
    thankYouElementOnDemand: FormElement | None = Field(
        default=None, description="Custom thank you element for on-demand events"
    )
    socialEventId: int | None = Field(default=None, description="Associated social event ID")
    domain: str | None = Field(default=None, description="Custom domain for form")
    urlName: str | None = Field(default=None, description="Custom URL slug")

    @computed_field
    @property
    def is_archived(self) -> bool:
        """
        Check if form is archived.

        Returns:
            True if isArchived flag is 1, False otherwise.

        Example:
            >>> form.is_archived
            False
        """
        return self.isArchived == 1

    @computed_field
    @property
    def has_submissions(self) -> bool:
        """
        Check if form has any submissions.

        Returns:
            True if submits > 0, False otherwise.

        Example:
            >>> form.has_submissions
            True
        """
        return self.submits > 0

    @computed_field
    @property
    def submission_count(self) -> int:
        """
        Get total number of form submissions.

        Returns:
            Number of submissions.

        Example:
            >>> form.submission_count
            42
        """
        return self.submits

    @computed_field
    @property
    def view_count(self) -> int:
        """
        Get total number of form views.

        Returns:
            Number of views.

        Example:
            >>> form.view_count
            150
        """
        return self.views

    async def edit(self, **kwargs: Unpack[FormUpdateFields]) -> "Form":
        """
        Edit this form.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated form with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> form = await upsales.forms.get(1)
            >>> updated = await form.edit(
            ...     title="New Form Title",
            ...     description="Updated description"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.update(self.id, **self.to_api_dict(**kwargs))


class PartialForm(PartialModel):
    """
    Partial form model for nested references.

    Contains minimal form data when forms appear nested in other objects.

    Example:
        >>> partial = contact.form  # If contact has form reference
        >>> full = await partial.fetch_full()
    """

    id: int = Field(description="Unique form ID")
    name: str = Field(description="Form name")
    title: str | None = Field(default=None, description="Form display title")

    async def fetch_full(self) -> Form:
        """
        Fetch the complete form object.

        Returns:
            Full Form object with all fields.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial_form = contact.form
            >>> full_form = await partial_form.fetch_full()
            >>> full_form.description
            'Contact form for leads'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.get(self.id)

    async def edit(self, **kwargs: Unpack[FormUpdateFields]) -> Form:
        """
        Edit this form and return the full updated object.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Form object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial_form = contact.form
            >>> updated = await partial_form.edit(title="New Title")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.update(self.id, **kwargs)
