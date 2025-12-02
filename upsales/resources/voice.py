"""Voice/phone integration resource manager.

This module provides the VoiceResource class for managing voice operations
including call management and recording retrieval.

Example:
    >>> async with Upsales.from_env() as upsales:
    ...     # Get recording
    ...     recording = await upsales.voice.get_recording(
    ...         integration_id="123",
    ...         recording_id="456"
    ...     )
    ...
    ...     # Initiate call
    ...     await upsales.voice.initiate_call(
    ...         integration_id=789,
    ...         data={"phoneNumber": "+1234567890"}
    ...     )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from upsales.models.voice import VoiceRecording

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class VoiceResource:
    """Voice/phone integration operations.

    This resource provides methods for voice integration including
    call management (initiate, hangup, ongoing status) and recording retrieval.

    Note:
        Voice operations are function-based and don't follow the standard
        CRUD pattern. All operations use the /api/v2/function/voice endpoint.

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get recording
        ...     recording = await upsales.voice.get_recording(
        ...         integration_id="123",
        ...         recording_id="456"
        ...     )
        ...
        ...     # Initiate call
        ...     await upsales.voice.initiate_call(
        ...         integration_id=789,
        ...         data={"phoneNumber": "+1234567890", "userId": 1}
        ...     )
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize VoiceResource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/voice"

    async def get_recording(
        self,
        integration_id: str,
        recording_id: str,
    ) -> VoiceRecording:
        """Get voice recording.

        Retrieves a voice recording from the specified integration.

        Args:
            integration_id: Voice integration provider ID.
            recording_id: Unique recording identifier.

        Returns:
            VoiceRecording: Recording metadata and content.

        Raises:
            NotFoundError: If recording doesn't exist.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.

        Example:
            >>> recording = await upsales.voice.get_recording(
            ...     integration_id="123",
            ...     recording_id="456"
            ... )
            >>> print(recording.content_type)
            audio/wav
        """
        params = {
            "type": "recording",
            "integrationId": integration_id,
            "id": recording_id,
        }

        response = await self._http.request(
            "GET",
            f"{self._endpoint}/recording",
            params=params,
        )

        # For binary responses, response may be bytes
        if isinstance(response, bytes):
            return VoiceRecording(
                integration_id=integration_id,
                recording_id=recording_id,
                content=response,
            )

        # If API returns structured data
        if isinstance(response, dict):
            return VoiceRecording(
                integration_id=integration_id,
                recording_id=recording_id,
                content_type=response.get("contentType"),
                content=response.get("content"),
            )

        # Fallback
        return VoiceRecording(
            integration_id=integration_id,
            recording_id=recording_id,
        )

    async def _call_operation(
        self,
        operation_type: Literal["call", "hangup", "ongoing", "initiate"],
        integration_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute voice operation.

        Internal method for voice operations.

        Args:
            operation_type: Type of operation to perform.
            integration_id: Voice integration provider ID.
            data: Optional operation-specific data.

        Returns:
            dict[str, Any]: Operation response.

        Raises:
            ValidationError: If request data is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.
        """
        payload: dict[str, Any] = {
            "type": operation_type,
            "integrationId": integration_id,
        }

        if data is not None:
            payload["data"] = data

        response = await self._http.request(
            "POST",
            self._endpoint,
            json=payload,
        )

        return response if isinstance(response, dict) else {}

    async def initiate_call(
        self,
        integration_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Initiate outgoing call.

        Starts a new outgoing call through the voice integration.

        Args:
            integration_id: Voice integration provider ID.
            data: Call data (e.g., phone number, user ID, client ID).

        Returns:
            dict[str, Any]: Call initiation response.

        Raises:
            ValidationError: If call data is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.

        Example:
            >>> result = await upsales.voice.initiate_call(
            ...     integration_id=789,
            ...     data={
            ...         "phoneNumber": "+1234567890",
            ...         "userId": 1,
            ...         "clientId": 123
            ...     }
            ... )
        """
        return await self._call_operation("initiate", integration_id, data)

    async def hangup_call(
        self,
        integration_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Hangup/end active call.

        Terminates an active call through the voice integration.

        Args:
            integration_id: Voice integration provider ID.
            data: Hangup data (e.g., call ID).

        Returns:
            dict[str, Any]: Hangup response.

        Raises:
            ValidationError: If hangup data is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.

        Example:
            >>> result = await upsales.voice.hangup_call(
            ...     integration_id=789,
            ...     data={"callId": "abc123"}
            ... )
        """
        return await self._call_operation("hangup", integration_id, data)

    async def ongoing_call(
        self,
        integration_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get ongoing call status.

        Retrieves status information for an ongoing call.

        Args:
            integration_id: Voice integration provider ID.
            data: Status request data (e.g., call ID).

        Returns:
            dict[str, Any]: Call status information.

        Raises:
            ValidationError: If request data is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.

        Example:
            >>> status = await upsales.voice.ongoing_call(
            ...     integration_id=789,
            ...     data={"callId": "abc123"}
            ... )
        """
        return await self._call_operation("ongoing", integration_id, data)

    async def call_event(
        self,
        integration_id: int,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Register call event.

        Registers a general call event with the voice integration.

        Args:
            integration_id: Voice integration provider ID.
            data: Event data.

        Returns:
            dict[str, Any]: Event registration response.

        Raises:
            ValidationError: If event data is invalid.
            AuthenticationError: If authentication fails.
            ServerError: If server error occurs.

        Example:
            >>> result = await upsales.voice.call_event(
            ...     integration_id=789,
            ...     data={"eventType": "connected", "callId": "abc123"}
            ... )
        """
        return await self._call_operation("call", integration_id, data)


__all__ = ["VoiceResource"]
