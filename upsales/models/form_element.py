"""
Form element models for Upsales API.

Used in Form thankYouElement and thankYouElementOnDemand fields.
These represent custom elements displayed on form thank you pages.

Based on analysis of 11 populated samples from /api/v2/forms endpoint.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class FormElementUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a FormElement.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    type: str
    value: dict[str, Any]
    style: dict[str, Any]
    enabled: bool
    animation: str | None
    required: bool


class FormElement(BaseModel):
    """
    Form element model representing custom thank you page elements.

    Used in Form.thankYouElement and Form.thankYouElementOnDemand fields.
    Represents rich content displayed on form thank you pages after submission.

    Common types:
    - "text": HTML text content (stored in value.text)
    - "image": Image element (stored in value.src, value.opacity, value.shadow, value.align)

    Example:
        >>> # Text element
        >>> element = FormElement(
        ...     id=1539688745297,
        ...     type="text",
        ...     value={"text": "<h2>Thank you!</h2>"},
        ...     enabled=True,
        ...     style={},
        ... )
        >>> element.is_enabled
        True
        >>> element.is_text
        True
        >>> element.text_content
        '<h2>Thank you!</h2>'

        >>> # Image element
        >>> element = FormElement(
        ...     id=1625129300226,
        ...     type="image",
        ...     value={"src": "https://...", "opacity": 100},
        ...     enabled=True,
        ...     style={},
        ... )
        >>> element.is_image
        True
        >>> element.image_src
        'https://...'
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique element ID (timestamp)")

    # Required updatable fields
    type: str = Field(description="Element type (text, image, etc.)")
    value: dict[str, Any] = Field(
        description="Element value object (structure varies by type: "
        "text has 'text' field, image has 'src', 'opacity', 'shadow', 'align')"
    )
    style: dict[str, Any] = Field(default_factory=dict, description="CSS style properties")
    enabled: bool = Field(default=True, description="Whether element is enabled/visible")
    animation: str | None = Field(default=None, description="Animation effect name")
    required: bool = Field(default=False, description="Whether element is required")

    @property
    def is_enabled(self) -> bool:
        """
        Check if element is enabled.

        Returns:
            True if element is enabled and visible.

        Example:
            >>> element.is_enabled
            True
        """
        return self.enabled

    @property
    def is_text(self) -> bool:
        """
        Check if element is a text type.

        Returns:
            True if type is "text".

        Example:
            >>> element.is_text
            True
        """
        return self.type == "text"

    @property
    def is_image(self) -> bool:
        """
        Check if element is an image type.

        Returns:
            True if type is "image".

        Example:
            >>> element.is_image
            False
        """
        return self.type == "image"

    @property
    def text_content(self) -> str | None:
        """
        Get text content for text-type elements.

        Returns:
            HTML text content if type is "text", None otherwise.

        Example:
            >>> element.text_content
            '<h2>Thank you!</h2>'
        """
        if self.type == "text" and isinstance(self.value, dict):
            return self.value.get("text")
        return None

    @property
    def image_src(self) -> str | None:
        """
        Get image source URL for image-type elements.

        Returns:
            Image URL if type is "image", None otherwise.

        Example:
            >>> element.image_src
            'https://img.upsales.com/...'
        """
        if self.type == "image" and isinstance(self.value, dict):
            return self.value.get("src")
        return None

    async def edit(self, **kwargs: Unpack[FormElementUpdateFields]) -> "FormElement":
        """
        Edit this form element.

        Note: FormElement does not have its own endpoint. This method is provided
        for consistency but will raise RuntimeError. To update form elements,
        edit the parent Form object with the updated thankYouElement data.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated form element (not implemented).

        Raises:
            RuntimeError: Always raised - no direct endpoint for form elements.

        Example:
            >>> # To update, edit the parent form instead:
            >>> form = await upsales.forms.get(1)
            >>> form.thankYouElement.type = "text"
            >>> form.thankYouElement.value = {"text": "<h2>New content</h2>"}
            >>> await form.edit(thankYouElement=form.thankYouElement.model_dump())
        """
        raise RuntimeError(
            "FormElement does not have a direct API endpoint. "
            "To update, edit the parent Form with updated thankYouElement data."
        )


class PartialFormElement(PartialModel):
    """
    Partial form element model for minimal references.

    Contains core identifying information when form elements appear
    in simplified contexts.

    Example:
        >>> partial = PartialFormElement(
        ...     id=1539688745297,
        ...     type="text",
        ...     value={"text": "<h2>Thank you!</h2>"}
        ... )
        >>> partial.type
        'text'
    """

    id: int = Field(description="Unique element ID")
    type: str = Field(description="Element type (text, image, etc.)")
    value: dict[str, Any] = Field(description="Element value object")

    async def fetch_full(self) -> FormElement:
        """
        Fetch the complete form element object.

        Note: FormElement does not have its own endpoint. This method is provided
        for consistency but will raise RuntimeError. Access full elements through
        the parent Form object.

        Returns:
            Full FormElement object (not implemented).

        Raises:
            RuntimeError: Always raised - no direct endpoint for form elements.

        Example:
            >>> # To access full element, fetch the parent form:
            >>> form = await upsales.forms.get(form_id)
            >>> full_element = form.thankYouElement
        """
        raise RuntimeError(
            "FormElement does not have a direct API endpoint. "
            "Access full elements through the parent Form object."
        )

    async def edit(self, **kwargs: Unpack[FormElementUpdateFields]) -> FormElement:
        """
        Edit this form element and return the full updated object.

        Note: FormElement does not have its own endpoint. This method is provided
        for consistency but will raise RuntimeError. To update form elements,
        edit the parent Form object.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full FormElement object (not implemented).

        Raises:
            RuntimeError: Always raised - no direct endpoint for form elements.

        Example:
            >>> # To update, edit the parent form instead:
            >>> form = await upsales.forms.get(form_id)
            >>> form.thankYouElement.value = {"text": "<h2>New content</h2>"}
            >>> await form.edit(thankYouElement=form.thankYouElement.model_dump())
        """
        raise RuntimeError(
            "FormElement does not have a direct API endpoint. "
            "To update, edit the parent Form with updated thankYouElement data."
        )
