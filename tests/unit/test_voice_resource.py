"""Unit tests for VoiceResource."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from upsales.models.voice import VoiceOperation, VoiceRecording
from upsales.resources.voice import VoiceResource


@pytest.fixture
def mock_http():
    """Create mock HTTP client."""
    http = MagicMock()
    http.request = AsyncMock()
    http.get_bytes = AsyncMock()
    return http


@pytest.fixture
def voice_resource(mock_http):
    """Create VoiceResource instance."""
    return VoiceResource(mock_http)


class TestVoiceResource:
    """Test VoiceResource class."""

    def test_init(self, voice_resource):
        """Test VoiceResource initialization."""
        assert voice_resource._endpoint == "/function/voice"

    @pytest.mark.asyncio
    async def test_get_recording_bytes_response(self, voice_resource, mock_http):
        """Test get_recording with binary response."""
        # Arrange
        mock_http.get_bytes.return_value = b"audio_data"

        # Act
        result = await voice_resource.get_recording(integration_id="123", recording_id="456")

        # Assert
        assert isinstance(result, VoiceRecording)
        assert result.integration_id == "123"
        assert result.recording_id == "456"
        assert result.content == b"audio_data"

        mock_http.get_bytes.assert_called_once_with(
            "/function/voice/recording",
            type="recording",
            integrationId="123",
            id="456",
        )

    @pytest.mark.asyncio
    async def test_get_recording_wav_response(self, voice_resource, mock_http):
        """Test get_recording returns proper VoiceRecording with wav content."""
        # Arrange - get_bytes now returns raw bytes
        mock_http.get_bytes.return_value = b"\x00\x01\x02\x03audio_content"

        # Act
        result = await voice_resource.get_recording(integration_id="123", recording_id="456")

        # Assert
        assert isinstance(result, VoiceRecording)
        assert result.integration_id == "123"
        assert result.recording_id == "456"
        assert result.content == b"\x00\x01\x02\x03audio_content"

    @pytest.mark.asyncio
    async def test_initiate_call(self, voice_resource, mock_http):
        """Test initiate_call method."""
        # Arrange
        mock_http.request.return_value = {"callId": "abc123", "status": "initiated"}

        # Act
        result = await voice_resource.initiate_call(
            integration_id=789, data={"phoneNumber": "+1234567890", "userId": 1}
        )

        # Assert
        assert result == {"callId": "abc123", "status": "initiated"}

        mock_http.request.assert_called_once_with(
            "POST",
            "/function/voice",
            json={
                "type": "initiate",
                "integrationId": 789,
                "data": {"phoneNumber": "+1234567890", "userId": 1},
            },
        )

    @pytest.mark.asyncio
    async def test_initiate_call_no_data(self, voice_resource, mock_http):
        """Test initiate_call without data."""
        # Arrange
        mock_http.request.return_value = {"status": "ok"}

        # Act
        result = await voice_resource.initiate_call(integration_id=789)

        # Assert
        assert result == {"status": "ok"}

        mock_http.request.assert_called_once_with(
            "POST", "/function/voice", json={"type": "initiate", "integrationId": 789}
        )

    @pytest.mark.asyncio
    async def test_hangup_call(self, voice_resource, mock_http):
        """Test hangup_call method."""
        # Arrange
        mock_http.request.return_value = {"status": "hangup_success"}

        # Act
        result = await voice_resource.hangup_call(integration_id=789, data={"callId": "abc123"})

        # Assert
        assert result == {"status": "hangup_success"}

        mock_http.request.assert_called_once_with(
            "POST",
            "/function/voice",
            json={"type": "hangup", "integrationId": 789, "data": {"callId": "abc123"}},
        )

    @pytest.mark.asyncio
    async def test_ongoing_call(self, voice_resource, mock_http):
        """Test ongoing_call method."""
        # Arrange
        mock_http.request.return_value = {
            "callId": "abc123",
            "status": "in_progress",
            "duration": 120,
        }

        # Act
        result = await voice_resource.ongoing_call(integration_id=789, data={"callId": "abc123"})

        # Assert
        assert result == {"callId": "abc123", "status": "in_progress", "duration": 120}

        mock_http.request.assert_called_once_with(
            "POST",
            "/function/voice",
            json={"type": "ongoing", "integrationId": 789, "data": {"callId": "abc123"}},
        )

    @pytest.mark.asyncio
    async def test_call_event(self, voice_resource, mock_http):
        """Test call_event method."""
        # Arrange
        mock_http.request.return_value = {"status": "event_registered"}

        # Act
        result = await voice_resource.call_event(
            integration_id=789, data={"eventType": "connected", "callId": "abc123"}
        )

        # Assert
        assert result == {"status": "event_registered"}

        mock_http.request.assert_called_once_with(
            "POST",
            "/function/voice",
            json={
                "type": "call",
                "integrationId": 789,
                "data": {"eventType": "connected", "callId": "abc123"},
            },
        )

    @pytest.mark.asyncio
    async def test_call_operation_internal(self, voice_resource, mock_http):
        """Test _call_operation internal method."""
        # Arrange
        mock_http.request.return_value = {"result": "success"}

        # Act
        result = await voice_resource._call_operation(
            operation_type="call", integration_id=123, data={"test": "data"}
        )

        # Assert
        assert result == {"result": "success"}

        mock_http.request.assert_called_once_with(
            "POST",
            "/function/voice",
            json={"type": "call", "integrationId": 123, "data": {"test": "data"}},
        )

    @pytest.mark.asyncio
    async def test_call_operation_non_dict_response(self, voice_resource, mock_http):
        """Test _call_operation with non-dict response."""
        # Arrange
        mock_http.request.return_value = "success"

        # Act
        result = await voice_resource._call_operation(operation_type="hangup", integration_id=123)

        # Assert
        assert result == {}

        mock_http.request.assert_called_once_with(
            "POST", "/function/voice", json={"type": "hangup", "integrationId": 123}
        )


class TestVoiceOperation:
    """Test VoiceOperation model."""

    def test_voice_operation_creation(self):
        """Test VoiceOperation model creation."""
        operation = VoiceOperation(
            type="initiate", integrationId=123, data={"phoneNumber": "+1234567890"}
        )

        assert operation.type == "initiate"
        assert operation.integrationId == 123
        assert operation.data == {"phoneNumber": "+1234567890"}

    def test_voice_operation_without_data(self):
        """Test VoiceOperation without data field."""
        operation = VoiceOperation(type="hangup", integrationId=456)

        assert operation.type == "hangup"
        assert operation.integrationId == 456
        assert operation.data is None


class TestVoiceRecording:
    """Test VoiceRecording model."""

    def test_voice_recording_creation(self):
        """Test VoiceRecording model creation."""
        recording = VoiceRecording(
            integration_id="123",
            recording_id="456",
            content_type="audio/wav",
            content=b"audio_data",
        )

        assert recording.integration_id == "123"
        assert recording.recording_id == "456"
        assert recording.content_type == "audio/wav"
        assert recording.content == b"audio_data"

    def test_voice_recording_minimal(self):
        """Test VoiceRecording with minimal fields."""
        recording = VoiceRecording(integration_id="123", recording_id="456")

        assert recording.integration_id == "123"
        assert recording.recording_id == "456"
        assert recording.content_type is None
        assert recording.content is None
