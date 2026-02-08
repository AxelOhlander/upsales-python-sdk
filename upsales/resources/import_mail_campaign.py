"""Import mail campaign resource for Upsales API.

Imports historical or external mail campaign data with status SENT.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        campaign = await upsales.import_mail_campaign.create(
            name="Q4 Newsletter",
            subject="Your Q4 Update",
            from_address="marketing@example.com",
            fromName="Marketing Team",
            body="<html>...</html>",
            sendDate="2025-01-15",
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ImportMailCampaignResource:
    """Resource manager for importing mail campaigns.

    Admin-only endpoint at /import/mailcampaign. Always creates
    campaigns with status SENT.

    Example:
        ```python
        resource = ImportMailCampaignResource(http_client)
        campaign = await resource.create(name="Campaign", subject="Subject", ...)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize import mail campaign resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/import/mailcampaign"

    async def create(
        self,
        name: str,
        subject: str,
        from_address: str,
        fromName: str,
        body: str,
        sendDate: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Import a mail campaign.

        Creates a campaign with status SENT.

        Args:
            name: Campaign name.
            subject: Email subject line.
            from_address: Sender email address.
            fromName: Sender display name.
            body: HTML body content.
            sendDate: Date when campaign was sent (YYYY-MM-DD).
            **kwargs: Optional fields (user, category, attachments, segmentId,
                     flowId, brandId, externalId).

        Returns:
            Created campaign data.

        Example:
            ```python
            campaign = await upsales.import_mail_campaign.create(
                name="Newsletter",
                subject="Monthly Update",
                from_address="news@example.com",
                fromName="News Team",
                body="<h1>Hello</h1>",
                sendDate="2025-01-15",
            )
            ```
        """
        data: dict[str, Any] = {
            "name": name,
            "subject": subject,
            "from": from_address,
            "fromName": fromName,
            "body": body,
            "sendDate": sendDate,
        }
        data.update(kwargs)
        return await self._http.post(self._endpoint, **data)
