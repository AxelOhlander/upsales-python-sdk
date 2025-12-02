"""Models for mail campaign mail import endpoint.

This module provides models for importing mail records for campaign contacts
into the Upsales CRM system.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImportMailCampaignMailRequest(BaseModel):
    """Request model for importing mail campaign mail records.

    This model represents the data required to import mail records for
    contacts in a mail campaign.

    Attributes:
        mailCampaignId: ID of the mail campaign.
        contactIds: List of contact IDs to import mail records for.

    Example:
        ```python
        request = ImportMailCampaignMailRequest(
            mailCampaignId=12345,
            contactIds=[1, 2, 3, 4, 5]
        )
        ```
    """

    mailCampaignId: int = Field(description="Mail campaign ID")
    contactIds: list[int] = Field(description="List of contact IDs")


class ImportMailCampaignMailResponse(BaseModel):
    """Response from the import mail campaign mail API.

    This model represents the response after importing mail campaign
    mail records. The actual response structure depends on the API.

    Attributes:
        success: Whether the import was successful.
        message: Optional message about the import result.

    Example:
        ```python
        response = ImportMailCampaignMailResponse(
            success=True,
            message="Successfully imported 5 mail records"
        )
        ```
    """

    success: bool = Field(default=True, description="Import success status")
    message: str | None = Field(None, description="Result message")
