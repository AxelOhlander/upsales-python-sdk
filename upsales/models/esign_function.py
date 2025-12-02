"""
E-signature function models for Upsales API.

This endpoint provides e-signature integration settings and document download
capabilities. Note: This is a special function endpoint, not a standard CRUD resource.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from upsales.client import Upsales


class EsignFunctionSettingsFields(dict[str, Any]):
    """
    Fields for requesting e-signature settings.

    This is a flexible dict since the API accepts various settings parameters.
    Required fields:
    - type: Must be "settings"
    - integrationId: The integration identifier
    """


class EsignFunctionSettings(BaseModel):
    """
    E-signature integration settings response.

    This model represents the settings returned from the e-signature
    integration endpoint. These settings control document delivery,
    signing capabilities, and available languages.

    Attributes:
        delivery: Delivery method configuration
        allowDraft: Whether draft documents are allowed
        documentType: Type of document for e-signature
        languages: Available languages for the signature interface
        bankIdCountries: Countries where BankID is available
        multiSign: Whether multiple signatures are supported
        userCanSign: Whether the current user can sign documents
        fields: Custom fields configuration for the signature process

    Example:
        >>> settings = await upsales.esign_function.get_settings(
        ...     integration_id=123
        ... )
        >>> print(settings.languages)
        ['en', 'sv', 'no']
        >>> print(settings.multiSign)
        True
    """

    # All fields are optional as the API doesn't specify which are guaranteed
    delivery: str | None = Field(None, description="Delivery method configuration")
    allowDraft: int | None = Field(None, description="Whether draft documents are allowed (0 or 1)")
    documentType: str | None = Field(None, description="Type of document for e-signature")
    languages: list[str] | None = Field(
        None, description="Available languages for signature interface"
    )
    bankIdCountries: list[str] | None = Field(
        None, description="Countries where BankID is available"
    )
    multiSign: int | None = Field(
        None, description="Whether multiple signatures are supported (0 or 1)"
    )
    userCanSign: int | None = Field(
        None, description="Whether current user can sign documents (0 or 1)"
    )
    fields: list[dict[str, Any]] | None = Field(
        None, description="Custom fields configuration for signature process"
    )

    # Store client reference for instance methods
    _client: "Upsales | None" = None

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


# Note: This endpoint does not follow standard CRUD patterns
# - No list/get/update/delete operations
# - Only POST for settings and GET for download
# - No PartialModel needed as objects are not nested in other responses
