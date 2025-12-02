"""ResetScore resource manager for Upsales API.

This module provides methods to reset marketing scores for clients or contacts.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     result = await upsales.reset_score.reset(userId=1, clientId=100)
    ...     result = await upsales.reset_score.reset(userId=1, contactId=200, sync=True)
"""

from upsales.http import HTTPClient
from upsales.models.reset_score import (
    ResetScoreResponse,
)


class ResetScoreResource:
    """Resource manager for resetScore endpoint.

    This is an action-only endpoint that resets marketing scores.
    It doesn't support standard CRUD operations.

    Example:
        >>> resource = ResetScoreResource(http_client)
        >>> result = await resource.reset(userId=1, clientId=100)
        >>> result = await resource.reset(userId=1, contactId=200, sync=True)
    """

    def __init__(self, http: HTTPClient):
        """Initialize resetScore resource manager.

        Args:
            http: HTTP client for API requests
        """
        self.http = http
        self.endpoint = "/function/resetScore"

    async def reset(  # noqa: N803
        self,
        userId: int,  # noqa: N803
        clientId: int | None = None,  # noqa: N803
        contactId: int | None = None,  # noqa: N803
        sync: bool = False,
    ) -> ResetScoreResponse:
        """Reset marketing score for a client or contact.

        Args:
            userId: User ID performing the reset
            clientId: Client ID to reset score for (optional)
            contactId: Contact ID to reset score for (optional)
            sync: Whether to synchronize the operation (defaults to False)

        Returns:
            Response indicating success or failure

        Raises:
            ValidationError: If neither clientId nor contactId is provided,
                or if both are provided
            AuthenticationError: If authentication fails (401/403)
            ServerError: If server error occurs (500+)

        Example:
            >>> # Reset score for a client
            >>> result = await resource.reset(userId=1, clientId=100)
            >>> print(result.success)  # True
            >>>
            >>> # Reset score for a contact with sync
            >>> result = await resource.reset(userId=1, contactId=200, sync=True)

        Note:
            Either clientId or contactId must be provided, but not both.
        """
        # Validate that exactly one of clientId or contactId is provided
        if clientId is None and contactId is None:
            raise ValueError("Either clientId or contactId must be provided")
        if clientId is not None and contactId is not None:
            raise ValueError("Cannot specify both clientId and contactId")

        # Build request data
        request_data = {
            "userId": userId,
            "sync": sync,
        }

        if clientId is not None:
            request_data["clientId"] = clientId
        if contactId is not None:
            request_data["contactId"] = contactId

        # Make API request
        response = await self.http.request("POST", self.endpoint, json=request_data)

        # Parse response
        return ResetScoreResponse.model_validate(response)
