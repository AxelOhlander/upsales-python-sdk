"""Unit tests for Unsub resource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.unsub import Unsub
from upsales.resources.unsub import UnsubsResource


class TestUnsubResource:
    """Test cases for UnsubsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample unsub data for testing."""
        return {"id": 123}

    @pytest.mark.asyncio
    async def test_unsubscribe(self, httpx_mock: HTTPXMock, sample_data):
        """Test unsubscribing a contact."""
        contact_id = 123
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/unsub",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UnsubsResource(http)
            result = await resource.unsubscribe(contact_id=contact_id)

            assert isinstance(result, Unsub)
            assert result.id == contact_id

    @pytest.mark.asyncio
    async def test_resubscribe(self, httpx_mock: HTTPXMock):
        """Test resubscribing a contact."""
        contact_id = 123
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/unsub/123",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UnsubsResource(http)
            result = await resource.resubscribe(contact_id=contact_id)

            assert result is None

    @pytest.mark.asyncio
    async def test_create_directly(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating unsub record directly."""
        contact_id = 456
        sample_data = {"id": contact_id}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/unsub",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UnsubsResource(http)
            result = await resource.create(id=contact_id)

            assert isinstance(result, Unsub)
            assert result.id == contact_id

    @pytest.mark.asyncio
    async def test_delete_directly(self, httpx_mock: HTTPXMock):
        """Test deleting unsub record directly."""
        contact_id = 456
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/function/unsub/456",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UnsubsResource(http)
            result = await resource.delete(contact_id)

            # DELETE returns the response dict
            assert result == {"error": None, "data": None}


class TestUnsubModel:
    """Test cases for Unsub model."""

    def test_unsub_model_creation(self):
        """Test creating an Unsub model."""
        unsub = Unsub(id=123)
        assert unsub.id == 123

    def test_unsub_model_frozen_id(self):
        """Test that id field is frozen."""
        unsub = Unsub(id=123)
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            unsub.id = 456

    @pytest.mark.asyncio
    async def test_edit_raises_not_implemented(self):
        """Test that edit() raises NotImplementedError."""
        unsub = Unsub(id=123)
        with pytest.raises(NotImplementedError) as exc_info:
            await unsub.edit()
        assert "does not support updates" in str(exc_info.value)
