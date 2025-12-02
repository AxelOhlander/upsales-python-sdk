"""Voice/phone integration models for Upsales API.

This module provides models for voice operations including call management
and recording retrieval.

Example:
    Voice operations are typically handled through the VoiceResource:

    >>> # Get recording
    >>> recording = await upsales.voice.get_recording(
    ...     integration_id="123",
    ...     recording_id="456"
    ... )

    >>> # Initiate call
    >>> await upsales.voice.initiate_call(
    ...     integration_id=789,
    ...     data={"phoneNumber": "+1234567890"}
    ... )
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from upsales.models.base import PartialModel


class VoiceCallData(TypedDict, total=False):
    """Data payload for voice operations.

    The structure of this data depends on the operation type and
    the voice integration provider being used.
    """

    phoneNumber: str
    """Phone number for the call."""

    userId: int
    """User ID associated with the call."""

    clientId: int
    """Client/account ID for the call."""

    contactId: int
    """Contact ID for the call."""


class VoiceOperation(PydanticBaseModel):
    """Voice operation request/response.

    This model represents various voice operations including call initiation,
    hangup, ongoing call status, and general call events.

    Example:
        >>> operation = VoiceOperation(
        ...     type="initiate",
        ...     integrationId=123,
        ...     data={"phoneNumber": "+1234567890"}
        ... )
    """

    type: Literal["call", "hangup", "ongoing", "initiate"] = Field(
        description="Type of voice operation to perform"
    )
    integrationId: int = Field(description="Voice integration provider ID")
    data: dict[str, Any] | None = Field(default=None, description="Operation-specific data payload")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "initiate",
                    "integrationId": 123,
                    "data": {"phoneNumber": "+1234567890", "userId": 1},
                },
                {"type": "hangup", "integrationId": 123, "data": {"callId": "abc123"}},
            ]
        }
    }


class VoiceRecording(PydanticBaseModel):
    """Voice recording metadata and stream.

    This model represents a voice recording retrieved from the API.
    The actual audio data is typically returned as a binary stream.

    Example:
        >>> recording = await upsales.voice.get_recording(
        ...     integration_id="123",
        ...     recording_id="456"
        ... )
    """

    integration_id: str = Field(description="Voice integration provider ID")
    recording_id: str = Field(description="Unique recording identifier")
    content_type: str | None = Field(
        default=None, description="MIME type of the recording (e.g., audio/wav)"
    )
    content: bytes | None = Field(default=None, description="Binary audio data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"integration_id": "123", "recording_id": "456", "content_type": "audio/wav"}
            ]
        }
    }


class PartialVoiceOperation(PartialModel):
    """Partial voice operation model.

    Minimal representation of a voice operation used in nested responses.

    Example:
        >>> partial = PartialVoiceOperation(type="call", integrationId=123)
        >>> # Fetch full details
        >>> full = await partial.fetch_full()
    """

    type: str = Field(description="Operation type")
    integrationId: int = Field(description="Integration ID")

    async def fetch_full(self) -> VoiceOperation:
        """Fetch full voice operation details.

        Note: Voice operations are stateless function calls,
        so this returns a new VoiceOperation instance with the same data.

        Returns:
            VoiceOperation: Full operation details.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")

        # Voice operations are stateless, return as-is
        return VoiceOperation(
            type=self.type,  # type: ignore[arg-type]
            integrationId=self.integrationId,
        )

    async def edit(self, **kwargs: Any) -> VoiceOperation:
        """Edit voice operation.

        Note: Voice operations are stateless and cannot be edited.
        This method exists for interface compatibility but will raise an error.

        Args:
            **kwargs: Arbitrary keyword arguments (ignored).

        Raises:
            NotImplementedError: Voice operations cannot be edited.
        """
        raise NotImplementedError("Voice operations are stateless and cannot be edited")


__all__ = [
    "VoiceCallData",
    "VoiceOperation",
    "VoiceRecording",
    "PartialVoiceOperation",
]
