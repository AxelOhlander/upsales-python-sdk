"""Unit tests for SendBeamResource."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from upsales.resources.send_beam import SendBeamResource


@pytest.fixture
def http_client():
    """Create mock HTTP client."""
    client = MagicMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def resource(http_client):
    """Create SendBeamResource instance."""
    return SendBeamResource(http_client)


class TestSendBeamResource:
    """Test SendBeamResource methods."""

    async def test_init(self, resource):
        """Test resource initialization."""
        assert resource.endpoint == "/function/sendbeam"
        assert resource.http is not None

    async def test_send_minimal(self, resource, http_client):
        """Test sending notification with only required field."""
        http_client.post.return_value = {"success": True}

        result = await resource.send(loc_key="NEW_MESSAGE")

        http_client.post.assert_called_once_with(
            "/function/sendbeam", json={"loc-key": "NEW_MESSAGE"}
        )
        assert result == {"success": True}

    async def test_send_with_all_fields(self, resource, http_client):
        """Test sending notification with all fields."""
        http_client.post.return_value = {"success": True}

        result = await resource.send(
            loc_key="NEW_MESSAGE",
            loc_args=["John Doe", "Sales Team"],
            sound="notification.wav",
            category="message",
        )

        http_client.post.assert_called_once_with(
            "/function/sendbeam",
            json={
                "loc-key": "NEW_MESSAGE",
                "loc-args": ["John Doe", "Sales Team"],
                "sound": "notification.wav",
                "category": "message",
            },
        )
        assert result == {"success": True}

    async def test_send_with_loc_args(self, resource, http_client):
        """Test sending notification with localization arguments."""
        http_client.post.return_value = {"success": True}

        result = await resource.send(
            loc_key="TASK_ASSIGNED", loc_args=["Task #123", "Project Alpha"]
        )

        http_client.post.assert_called_once_with(
            "/function/sendbeam",
            json={"loc-key": "TASK_ASSIGNED", "loc-args": ["Task #123", "Project Alpha"]},
        )
        assert result == {"success": True}

    async def test_send_with_sound(self, resource, http_client):
        """Test sending notification with custom sound."""
        http_client.post.return_value = {"success": True}

        result = await resource.send(loc_key="ALERT", sound="alert.wav")

        http_client.post.assert_called_once_with(
            "/function/sendbeam", json={"loc-key": "ALERT", "sound": "alert.wav"}
        )
        assert result == {"success": True}

    async def test_send_with_category(self, resource, http_client):
        """Test sending notification with category."""
        http_client.post.return_value = {"success": True}

        result = await resource.send(loc_key="NEW_LEAD", category="lead")

        http_client.post.assert_called_once_with(
            "/function/sendbeam", json={"loc-key": "NEW_LEAD", "category": "lead"}
        )
        assert result == {"success": True}
