"""Resource manager for importing mail campaign mail records.

This module provides the ImportMailCampaignMailResource class for importing
mail records for campaign contacts into the Upsales CRM system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from upsales.models.import_mail_campaign_mail import (
    ImportMailCampaignMailRequest,
    ImportMailCampaignMailResponse,
)

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ImportMailCampaignMailResource:
    """Manager for mail campaign mail import operations.

    This resource handles importing mail records for contacts in a mail campaign.
    It creates or updates mail records linking contacts to a specific campaign.

    Attributes:
        http: HTTP client for API communication.
        endpoint: API endpoint path.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Import mail records for contacts in a campaign
            response = await upsales.import_mail_campaign_mail.import_mail(
                mail_campaign_id=12345,
                contact_ids=[1, 2, 3, 4, 5]
            )

            # Check if successful
            if response.success:
                print(f"Success: {response.message}")
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize the import mail campaign mail resource.

        Args:
            http: HTTP client for making API requests.
        """
        self.http = http
        self.endpoint = "/import/mailcampaign/mail"

    async def import_mail(
        self,
        mail_campaign_id: int,
        contact_ids: list[int],
    ) -> ImportMailCampaignMailResponse:
        """Import mail records for campaign contacts.

        This method creates or updates mail records linking the specified contacts
        to a mail campaign. This is typically used when importing contacts into
        a campaign from external sources.

        Args:
            mail_campaign_id: ID of the mail campaign.
            contact_ids: List of contact IDs to create mail records for.

        Returns:
            ImportMailCampaignMailResponse with success status and message.

        Raises:
            ValidationError: If input data is invalid (400).
            AuthenticationError: If authentication fails (401/403).
            NotFoundError: If mail campaign or contacts not found (404).
            ServerError: If server error occurs (500+).

        Example:
            ```python
            # Import mail records for specific contacts
            response = await upsales.import_mail_campaign_mail.import_mail(
                mail_campaign_id=12345,
                contact_ids=[1, 2, 3, 4, 5]
            )

            if response.success:
                print("Mail records imported successfully")
            ```

        Note:
            - This endpoint is useful for bulk importing contacts into campaigns
            - It creates mail records without sending actual emails
            - Contact IDs must exist in the system
            - The mail campaign must already exist
        """
        # Create request payload
        request = ImportMailCampaignMailRequest(
            mailCampaignId=mail_campaign_id,
            contactIds=contact_ids,
        )

        # Convert to dict for API
        payload = request.model_dump(mode="json")

        # Make request
        response = await self.http.post(self.endpoint, json=payload)

        # Parse response - adjust based on actual API response structure
        if isinstance(response, dict):
            return ImportMailCampaignMailResponse.model_validate(response)
        else:
            # If API returns simple success, create success response
            return ImportMailCampaignMailResponse(
                success=True, message="Mail records imported successfully"
            )

    async def import_mail_from_request(
        self,
        request: ImportMailCampaignMailRequest | dict[str, Any],
    ) -> ImportMailCampaignMailResponse:
        """Import mail records using a request object.

        This is an alternative method that accepts a full request object,
        useful when you've already constructed the request model.

        Args:
            request: ImportMailCampaignMailRequest object or dictionary.

        Returns:
            ImportMailCampaignMailResponse with success status and message.

        Raises:
            ValidationError: If request data is invalid (400).
            AuthenticationError: If authentication fails (401/403).
            NotFoundError: If mail campaign or contacts not found (404).
            ServerError: If server error occurs (500+).

        Example:
            ```python
            # Using request object
            request = ImportMailCampaignMailRequest(
                mailCampaignId=12345,
                contactIds=[1, 2, 3, 4, 5]
            )
            response = await upsales.import_mail_campaign_mail.import_mail_from_request(request)

            # Using dictionary
            response = await upsales.import_mail_campaign_mail.import_mail_from_request({
                "mailCampaignId": 12345,
                "contactIds": [1, 2, 3, 4, 5]
            })
            ```
        """
        # Convert to dict if needed
        if isinstance(request, ImportMailCampaignMailRequest):
            payload = request.model_dump(mode="json")
        else:
            # Validate dict through model first
            validated = ImportMailCampaignMailRequest.model_validate(request)
            payload = validated.model_dump(mode="json")

        # Make request
        response = await self.http.post(self.endpoint, json=payload)

        # Parse response
        if isinstance(response, dict):
            return ImportMailCampaignMailResponse.model_validate(response)
        else:
            return ImportMailCampaignMailResponse(
                success=True, message="Mail records imported successfully"
            )
