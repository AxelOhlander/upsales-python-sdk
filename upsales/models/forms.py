"""
Form models for Upsales API.

Web forms for capturing leads and submissions through Upsales.

Generated from /api/v2/forms endpoint.
Analysis based on 17 samples.

Example:
    >>> # Create a new form
    >>> form = await upsales.forms.create(
    ...     name="Contact Form",
    ...     internalName="contact_form",
    ...     title="Get in Touch",
    ...     description="Contact us for more information",
    ...     landingPage="https://example.com/contact",
    ...     buttonText="Submit",
    ...     thankYouTitle="Thank You!",
    ...     thankYouText="We'll be in touch soon."
    ... )
    >>>
    >>> # Update a form
    >>> await form.edit(title="Updated Contact Form")
    >>>
    >>> # Check form statistics
    >>> print(f"Form has {form.submits} submissions")
    >>> print(f"Form has {form.views} views")
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag

if TYPE_CHECKING:
    from upsales.models.user import PartialUser


class FormUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Form.

    All fields are optional. Read-only fields (id, uuid, submits, etc.) are excluded.
    """

    # Form identification
    name: str
    internalName: str
    title: str
    description: str

    # Form configuration
    formType: str
    fields: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    html: str
    isArchived: int

    # Landing page settings
    landingPage: str
    landingPageBody: dict[str, Any]
    backgroundColor: str
    backgroundColorOnDemand: str
    textColor: str
    linkColor: str
    buttonBgColor: str
    buttonTextColor: str
    buttonText: str
    showTitle: int
    domain: str
    urlName: str

    # Thank you page settings
    thankYouTitle: str
    thankYouText: str
    thankYouElement: dict[str, Any]
    thankYouTitleOnDemand: str
    thankYouTextOnDemand: str
    thankYouElementOnDemand: Any
    redirect: int

    # Additional settings
    labels: list[Any]
    projects: list[Any]
    socialEventId: int
    socialMediaTags: str
    supportEmailId: Any
    brandId: int
    score: int


class Form(BaseModel):
    """
    Web form for capturing leads and submissions.

    Forms can be embedded on web pages or hosted on Upsales landing pages.
    They support custom fields, actions (like creating contacts/companies),
    and can be configured with branding and thank you pages.

    Attributes:
        id: Unique form identifier (read-only).
        uuid: Unique form UUID (read-only).
        name: Form display name.
        internalName: Internal reference name.
        title: Form title shown to users.
        description: Form description.
        formType: Type of form (e.g., "lead", "contact").
        fields: List of form field definitions.
        actions: Actions to execute on form submission.
        html: Custom HTML for the form.
        isArchived: Whether form is archived (0=active, 1=archived).
        landingPage: Landing page URL.
        landingPageBody: Landing page body configuration.
        backgroundColor: Landing page background color.
        backgroundColorOnDemand: Alternative background color.
        textColor: Landing page text color.
        linkColor: Landing page link color.
        buttonBgColor: Submit button background color.
        buttonTextColor: Submit button text color.
        buttonText: Submit button text.
        showTitle: Whether to show form title (0=no, 1=yes).
        domain: Custom domain for form.
        urlName: URL-friendly form name.
        thankYouTitle: Thank you page title.
        thankYouText: Thank you page text.
        thankYouElement: Thank you page element configuration.
        thankYouTitleOnDemand: Alternative thank you title.
        thankYouTextOnDemand: Alternative thank you text.
        thankYouElementOnDemand: Alternative thank you element.
        redirect: Whether to redirect after submission (0=no, 1=yes).
        labels: Form labels/tags.
        projects: Associated projects.
        socialEventId: Associated social event ID.
        socialMediaTags: Social media meta tags.
        supportEmailId: Support email ID.
        brandId: Brand ID for styling.
        score: Form score/priority.
        submits: Total number of submissions (read-only).
        views: Total number of views (read-only).
        lastSubmitDate: Date of last submission (read-only).
        regDate: Registration date (read-only).
        modDate: Last modification date (read-only).
        user: User who created the form.
        userEditable: Whether current user can edit (read-only).
        userRemovable: Whether current user can delete (read-only).
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique form identifier")
    uuid: str = Field(frozen=True, description="Unique form UUID")
    submits: int = Field(frozen=True, description="Total number of submissions")
    views: int = Field(frozen=True, description="Total number of views")
    lastSubmitDate: str | None = Field(None, frozen=True, description="Date of last submission")
    regDate: str = Field(frozen=True, description="Registration date (YYYY-MM-DD HH:MM:SS)")
    modDate: str | None = Field(None, frozen=True, description="Last modification date")
    userEditable: bool = Field(frozen=True, description="Whether current user can edit")
    userRemovable: bool = Field(frozen=True, description="Whether current user can delete")

    # Form identification
    name: str = Field(description="Form display name")
    internalName: str = Field(description="Internal reference name")
    title: str = Field(description="Form title shown to users")
    description: str = Field(description="Form description")

    # Form configuration
    formType: str | None = Field(None, description="Type of form")
    fields: list[dict[str, Any]] = Field(default=[], description="Form field definitions")
    actions: list[dict[str, Any]] = Field(default=[], description="Actions on form submission")
    html: str | None = Field(None, description="Custom HTML for the form")
    isArchived: BinaryFlag = Field(default=0, description="Whether form is archived")

    # Landing page settings
    landingPage: str = Field(description="Landing page URL")
    landingPageBody: dict[str, Any] | None = Field(
        None, description="Landing page body configuration"
    )
    backgroundColor: str = Field(description="Landing page background color")
    backgroundColorOnDemand: str | None = Field(None, description="Alternative background color")
    textColor: str = Field(description="Landing page text color")
    linkColor: str = Field(description="Landing page link color")
    buttonBgColor: str = Field(description="Submit button background color")
    buttonTextColor: str = Field(description="Submit button text color")
    buttonText: str = Field(description="Submit button text")
    showTitle: BinaryFlag = Field(default=1, description="Whether to show form title")
    domain: str | None = Field(None, description="Custom domain for form")
    urlName: str | None = Field(None, description="URL-friendly form name")

    # Thank you page settings
    thankYouTitle: str = Field(description="Thank you page title")
    thankYouText: str = Field(description="Thank you page text")
    thankYouElement: dict[str, Any] | None = Field(
        None, description="Thank you page element configuration"
    )
    thankYouTitleOnDemand: str | None = Field(None, description="Alternative thank you title")
    thankYouTextOnDemand: str | None = Field(None, description="Alternative thank you text")
    thankYouElementOnDemand: Any | None = Field(None, description="Alternative thank you element")
    redirect: BinaryFlag = Field(default=0, description="Whether to redirect after submission")

    # Additional settings
    labels: list[Any] = Field(default=[], description="Form labels/tags")
    projects: list[Any] = Field(default=[], description="Associated projects")
    socialEventId: int | None = Field(None, description="Associated social event ID")
    socialMediaTags: str | None = Field(None, description="Social media meta tags")
    supportEmailId: Any | None = Field(None, description="Support email ID")
    brandId: int = Field(description="Brand ID for styling")
    score: int = Field(description="Form score/priority")

    # Relations
    user: "PartialUser" = Field(description="User who created the form")

    @computed_field
    @property
    def is_archived(self) -> bool:
        """Check if form is archived."""
        return self.isArchived == 1

    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if form is active (not archived)."""
        return self.isArchived == 0

    @computed_field
    @property
    def has_submissions(self) -> bool:
        """Check if form has any submissions."""
        return self.submits > 0

    @computed_field
    @property
    def submission_count(self) -> int:
        """Get total number of submissions (alias for submits)."""
        return self.submits

    @computed_field
    @property
    def view_count(self) -> int:
        """Human-friendly alias for total view counter."""
        return self.views

    @computed_field
    @property
    def conversion_rate(self) -> float:
        """Calculate form conversion rate (submits/views)."""
        if self.views == 0:
            return 0.0
        return (self.submits / self.views) * 100

    async def edit(self, **kwargs: Unpack[FormUpdateFields]) -> "Form":
        """
        Edit this form.

        Args:
            **kwargs: Fields to update. Available fields include:
                name: Form display name
                title: Form title
                description: Form description
                fields: Form field definitions
                actions: Actions on submission
                isArchived: Archive status (0 or 1)
                And many more styling/configuration options.

        Returns:
            Updated form instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> form = await upsales.forms.get(1)
            >>> await form.edit(
            ...     title="Updated Form Title",
            ...     description="New description",
            ...     isArchived=0
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.update(self.id, **self.to_api_dict(**kwargs))


class PartialForm(PartialModel):
    """
    Partial Form for nested responses.

    Contains minimal form information when forms appear in nested contexts
    (e.g., referenced from other objects).

    Attributes:
        id: Unique form identifier.
        name: Form display name.
        title: Form title shown to users.
    """

    id: int = Field(description="Unique form identifier")
    name: str = Field(description="Form display name")
    title: str = Field(description="Form title shown to users")

    async def fetch_full(self) -> Form:
        """
        Fetch complete form data.

        Returns:
            Full Form instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial_form = PartialForm(id=1, name="Contact", title="Contact Us")
            >>> full_form = await partial_form.fetch_full()
            >>> print(full_form.submits)  # Access full form data
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.get(self.id)

    async def edit(self, **kwargs: Unpack[FormUpdateFields]) -> Form:
        """
        Edit this form.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Form instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial_form = PartialForm(id=1, name="Contact", title="Contact Us")
            >>> updated_form = await partial_form.edit(title="New Title")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.forms.update(self.id, **kwargs)
