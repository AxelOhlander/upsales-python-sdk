"""Unit tests for StandardIntegrationDataResource."""

from unittest.mock import AsyncMock, Mock

import pytest

from upsales.resources.standard_integration_data import StandardIntegrationDataResource


@pytest.fixture
def mock_http():
    """Create mock HTTP client."""
    http = Mock()
    http.post = AsyncMock()
    return http


@pytest.fixture
def resource(mock_http):
    """Create StandardIntegrationDataResource instance."""
    return StandardIntegrationDataResource(mock_http)


class TestStandardIntegrationDataResource:
    """Test StandardIntegrationDataResource methods."""

    @pytest.mark.asyncio
    async def test_execute_test_operation(self, resource, mock_http):
        """Test execute with test operation."""
        mock_http.post.return_value = {"status": "success"}

        result = await resource.execute(type="test", integrationId=123, data={"key": "value"})

        assert result == {"status": "success"}
        mock_http.post.assert_called_once_with(
            "/function/standardIntegrationData",
            json={"type": "test", "integrationId": 123, "data": {"key": "value"}},
        )

    @pytest.mark.asyncio
    async def test_execute_oauth_operation(self, resource, mock_http):
        """Test execute with OAuth operation."""
        mock_http.post.return_value = {"oauth_token": "abc123"}

        result = await resource.execute(type="oauth", integrationId=456)

        assert result == {"oauth_token": "abc123"}
        mock_http.post.assert_called_once_with(
            "/function/standardIntegrationData", json={"type": "oauth", "integrationId": 456}
        )

    @pytest.mark.asyncio
    async def test_execute_with_user_ids(self, resource, mock_http):
        """Test execute with userIds."""
        mock_http.post.return_value = {"users": [1, 2, 3]}

        result = await resource.execute(type="events", integrationId=789, userIds=[1, 2, 3])

        assert result == {"users": [1, 2, 3]}
        mock_http.post.assert_called_once_with(
            "/function/standardIntegrationData",
            json={"type": "events", "integrationId": 789, "userIds": [1, 2, 3]},
        )

    @pytest.mark.asyncio
    async def test_test_method(self, resource, mock_http):
        """Test test() convenience method."""
        mock_http.post.return_value = {"test": "passed"}

        result = await resource.test(integrationId=123, data={"param": "value"})

        assert result == {"test": "passed"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "test"
        assert call_args[1]["json"]["integrationId"] == 123

    @pytest.mark.asyncio
    async def test_get_values_method(self, resource, mock_http):
        """Test get_values() convenience method."""
        mock_http.post.return_value = {"values": ["a", "b", "c"]}

        result = await resource.get_values(integrationId=123)

        assert result == {"values": ["a", "b", "c"]}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "values"

    @pytest.mark.asyncio
    async def test_config_button_method(self, resource, mock_http):
        """Test config_button() convenience method."""
        mock_http.post.return_value = {"config": "updated"}

        result = await resource.config_button(integrationId=123, data={"setting": "value"})

        assert result == {"config": "updated"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "configButton"

    @pytest.mark.asyncio
    async def test_oauth_method(self, resource, mock_http):
        """Test oauth() convenience method."""
        mock_http.post.return_value = {"access_token": "token123"}

        result = await resource.oauth(integrationId=123, data={"code": "auth_code"})

        assert result == {"access_token": "token123"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "oauth"

    @pytest.mark.asyncio
    async def test_get_events_method(self, resource, mock_http):
        """Test get_events() convenience method."""
        mock_http.post.return_value = {"events": []}

        result = await resource.get_events(integrationId=123)

        assert result == {"events": []}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "events"

    @pytest.mark.asyncio
    async def test_test_user_method(self, resource, mock_http):
        """Test test_user() convenience method."""
        mock_http.post.return_value = {"result": "ok"}

        result = await resource.test_user(
            integrationId=123, userIds=[1, 2], data={"param": "value"}
        )

        assert result == {"result": "ok"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "testUser"
        assert call_args[1]["json"]["userIds"] == [1, 2]

    @pytest.mark.asyncio
    async def test_get_values_user_method(self, resource, mock_http):
        """Test get_values_user() convenience method."""
        mock_http.post.return_value = {"values": {"1": "a", "2": "b"}}

        result = await resource.get_values_user(integrationId=123, userIds=[1, 2])

        assert result == {"values": {"1": "a", "2": "b"}}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "valuesUser"

    @pytest.mark.asyncio
    async def test_user_config_button_method(self, resource, mock_http):
        """Test user_config_button() convenience method."""
        mock_http.post.return_value = {"config": "saved"}

        result = await resource.user_config_button(
            integrationId=123, userIds=[1], data={"setting": "value"}
        )

        assert result == {"config": "saved"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[1]["json"]["type"] == "userConfigButton"
        assert call_args[1]["json"]["userIds"] == [1]

    @pytest.mark.asyncio
    async def test_execute_minimal_params(self, resource, mock_http):
        """Test execute with only required type parameter."""
        mock_http.post.return_value = {"status": "ok"}

        result = await resource.execute(type="test")

        assert result == {"status": "ok"}
        mock_http.post.assert_called_once_with(
            "/function/standardIntegrationData", json={"type": "test"}
        )

    @pytest.mark.asyncio
    async def test_execute_all_operation_types(self, resource, mock_http):
        """Test execute with all operation types."""
        operation_types = [
            "test",
            "values",
            "configButton",
            "testUser",
            "valuesUser",
            "userConfigButton",
            "oauth",
            "events",
        ]

        for op_type in operation_types:
            mock_http.post.return_value = {"type": op_type}
            result = await resource.execute(type=op_type, integrationId=123)  # type: ignore
            assert result == {"type": op_type}

        assert mock_http.post.call_count == len(operation_types)
