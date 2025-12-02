"""
Tests for SuggestionsResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.
This endpoint is special as it uses boxid instead of standard id parameter.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.client import Upsales
from upsales.models.suggestions import Suggestion


class TestSuggestionsResourceCustomMethods:
    """Test custom methods specific to SuggestionsResource."""

    @pytest.fixture
    def sample_suggestion(self):
        """Sample suggestion data."""
        return {
            "boxid": 123,
            "id": 456,
            "actions": [
                {"type": "call", "status": "pending"},
                {"type": "email", "status": "completed"},
            ],
        }

    @pytest.mark.asyncio
    async def test_get_by_boxid(self, httpx_mock: HTTPXMock, sample_suggestion):
        """Test get() retrieves suggestion by box ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/prospectingsuggestion/123",
            json={
                "error": None,
                "data": sample_suggestion,
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.suggestions.get(boxid=123)

            assert isinstance(result, Suggestion)
            assert result.boxid == 123
            assert result.id == 456
            assert len(result.actions) == 2
            assert result.has_actions is True

    @pytest.mark.asyncio
    async def test_update_suggestion(self, httpx_mock: HTTPXMock, sample_suggestion):
        """Test update() modifies suggestion actions."""
        updated_data = {**sample_suggestion, "actions": [{"type": "call", "status": "completed"}]}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/prospectingsuggestion/123",
            method="POST",
            json={
                "error": None,
                "data": updated_data,
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.suggestions.update(
                boxid=123, data={"actions": [{"type": "call", "status": "completed"}]}
            )

            assert isinstance(result, Suggestion)
            assert result.boxid == 123
            assert len(result.actions) == 1
            assert result.actions[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_create_suggestion(self, httpx_mock: HTTPXMock, sample_suggestion):
        """Test create() creates a new suggestion (calls update internally)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/prospectingsuggestion/999",
            method="POST",
            json={
                "error": None,
                "data": {**sample_suggestion, "boxid": 999},
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.suggestions.create(boxid=999, data={"actions": [{"type": "email"}]})

            assert isinstance(result, Suggestion)
            assert result.boxid == 999

    @pytest.mark.asyncio
    async def test_suggestion_without_actions(self, httpx_mock: HTTPXMock):
        """Test suggestion with empty actions list."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/prospectingsuggestion/789",
            json={
                "error": None,
                "data": {
                    "boxid": 789,
                    "id": 111,
                    "actions": [],
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            result = await upsales.suggestions.get(boxid=789)

            assert isinstance(result, Suggestion)
            assert result.has_actions is False
            assert len(result.actions) == 0


class TestSuggestionModel:
    """Test Suggestion model functionality."""

    @pytest.mark.asyncio
    async def test_suggestion_edit_method(self, httpx_mock: HTTPXMock):
        """Test Suggestion.edit() updates the suggestion."""
        initial_data = {
            "boxid": 123,
            "id": 456,
            "actions": [{"type": "call"}],
        }

        updated_data = {
            **initial_data,
            "actions": [{"type": "call"}, {"type": "email"}],
        }

        # Mock the update request
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/prospectingsuggestion/123",
            method="POST",
            json={
                "error": None,
                "data": updated_data,
            },
        )

        async with Upsales(token="test_token") as upsales:
            suggestion = Suggestion(**initial_data, _client=upsales)

            # Edit through model instance method
            updated = await suggestion.edit(actions=[{"type": "call"}, {"type": "email"}])

            assert updated.boxid == 123
            assert len(updated.actions) == 2

    def test_suggestion_has_actions_computed_field(self):
        """Test has_actions computed property."""
        suggestion_with_actions = Suggestion(boxid=123, actions=[{"type": "call"}])
        suggestion_without_actions = Suggestion(boxid=123, actions=[])

        assert suggestion_with_actions.has_actions is True
        assert suggestion_without_actions.has_actions is False

    def test_suggestion_frozen_fields(self):
        """Test that frozen fields cannot be modified."""
        suggestion = Suggestion(boxid=123, actions=[])

        # boxid is frozen
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            suggestion.boxid = 456

    def test_suggestion_to_api_dict(self):
        """Test serialization excludes frozen fields."""
        suggestion = Suggestion(boxid=123, id=456, actions=[{"type": "call"}])

        api_dict = suggestion.to_api_dict()

        # Frozen fields should be excluded
        assert "boxid" not in api_dict
        assert "id" not in api_dict
        assert "actions" in api_dict
