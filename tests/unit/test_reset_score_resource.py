"""Unit tests for ResetScore resource."""

import pytest

from upsales.models.reset_score import ResetScoreResponse


class TestResetScoreResource:
    """Tests for ResetScoreResource."""

    @pytest.fixture
    def resource(self, client):
        """Create ResetScore resource instance."""
        return client.reset_score

    @pytest.mark.asyncio
    async def test_reset_with_client_id(self, resource, httpx_mock):
        """Test resetting score for a client."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/resetScore",
            method="POST",
            json={"success": True, "message": "Score reset successfully"},
        )

        result = await resource.reset(userId=1, clientId=100)

        assert isinstance(result, ResetScoreResponse)
        assert result.success is True
        assert result.message == "Score reset successfully"

        # Verify request
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path == "/api/v2/function/resetScore"
        request_data = request.read()
        assert b'"userId":1' in request_data or b'"userId": 1' in request_data
        assert b'"clientId":100' in request_data or b'"clientId": 100' in request_data

    @pytest.mark.asyncio
    async def test_reset_with_contact_id(self, resource, httpx_mock):
        """Test resetting score for a contact."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/resetScore",
            method="POST",
            json={"success": True},
        )

        result = await resource.reset(userId=1, contactId=200)

        assert isinstance(result, ResetScoreResponse)
        assert result.success is True

        # Verify request
        request = httpx_mock.get_request()
        request_data = request.read()
        assert b'"userId":1' in request_data or b'"userId": 1' in request_data
        assert b'"contactId":200' in request_data or b'"contactId": 200' in request_data

    @pytest.mark.asyncio
    async def test_reset_with_sync(self, resource, httpx_mock):
        """Test resetting score with sync enabled."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/resetScore",
            method="POST",
            json={"success": True},
        )

        result = await resource.reset(userId=1, clientId=100, sync=True)

        assert result.success is True

        # Verify request
        request = httpx_mock.get_request()
        request_data = request.read()
        assert b'"sync":true' in request_data or b'"sync": true' in request_data

    @pytest.mark.asyncio
    async def test_reset_missing_both_ids(self, resource):
        """Test that error is raised when neither clientId nor contactId is provided."""
        with pytest.raises(ValueError, match="Either clientId or contactId must be provided"):
            await resource.reset(userId=1)

    @pytest.mark.asyncio
    async def test_reset_both_ids_provided(self, resource):
        """Test that error is raised when both clientId and contactId are provided."""
        with pytest.raises(ValueError, match="Cannot specify both clientId and contactId"):
            await resource.reset(userId=1, clientId=100, contactId=200)

    @pytest.mark.asyncio
    async def test_reset_failure(self, resource, httpx_mock):
        """Test handling of reset failure."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/resetScore",
            method="POST",
            json={"success": False, "message": "Invalid client ID"},
        )

        result = await resource.reset(userId=1, clientId=999)

        assert result.success is False
        assert result.message == "Invalid client ID"
