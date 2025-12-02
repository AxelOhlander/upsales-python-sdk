"""
Tests for EventsResource.

Ensures complete CRUD coverage for events endpoint.
Note: Events do not support UPDATE operations.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.events import Event
from upsales.resources.events import EventsResource


class TestEventsResourceCRUD:
    """Test CRUD operations for EventsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample event data for testing."""
        return {
            "id": 1,
            "entityType": "manual",
            "score": 10,
            "subType": "note",
            "entityId": 5,
            "date": "2025-11-15T10:00:00Z",
            "value": "Important meeting scheduled",
            "client": {"id": 10, "name": "ACME Corp"},
            "contacts": [{"id": 1, "name": "John Doe"}],
            "users": [{"id": 5, "name": "Jane Smith", "email": "jane@example.com"}],
            "form": None,
            "marketingCustom": None,
            "opportunity": None,
            "activity": None,
            "appointment": None,
            "agreement": None,
            "mail": None,
            "mails": [],
            "order": None,
            "visit": None,
            "esign": None,
            "news": None,
            "socialEvent": None,
            "comment": None,
            "plan": None,
            "ticket": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "entityType": "marketingCustom"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an event."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/events",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            result = await resource.create(entityType="manual", score=10, client={"id": 10})

            assert isinstance(result, Event)
            assert result.id == 1
            assert result.entityType == "manual"
            assert result.score == 10
            assert result.is_manual is True

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing events with filter parameter."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/events?limit=100&offset=0&q=entityType%3Amanual",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            result = await resource.list(q="entityType:manual")

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, Event) for item in result)
            assert result[0].id == 1
            assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an event."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/events/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            await resource.delete(1)  # Should not raise

    @pytest.mark.asyncio
    async def test_update_not_supported(self):
        """Test that update raises NotImplementedError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            with pytest.raises(NotImplementedError, match="Events cannot be updated"):
                await resource.update(1, score=5)

    @pytest.mark.asyncio
    async def test_get_by_type(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting events by type."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/events?limit=100&offset=0&q=entityType%3Amanual",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            result = await resource.get_by_type("manual")

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, Event) for item in result)

    @pytest.mark.asyncio
    async def test_get_by_company(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting events by company ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/events?limit=100&offset=0&q=client.id%3A10",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = EventsResource(http)
            result = await resource.get_by_company(10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, Event) for item in result)


class TestEventModelFeatures:
    """Test Event model features."""

    @pytest.fixture
    def event_data(self):
        """Sample event data."""
        return {
            "id": 1,
            "entityType": "marketingCustom",
            "score": 15,
            "date": "2025-11-15T10:00:00Z",
            "value": "Campaign email sent",
            "client": {"id": 10, "name": "ACME Corp"},
            "contacts": [{"id": 1, "name": "John Doe"}],
            "users": [],
            "opportunity": {"id": 5, "description": "Q4 Deal"},
        }

    def test_computed_fields(self, event_data):
        """Test computed field properties."""
        event = Event(**event_data)

        assert event.is_marketing is True
        assert event.is_manual is False
        assert event.is_news is False
        assert event.has_company is True
        assert event.has_opportunity is True
        assert event.has_contacts is True

    def test_edit_not_supported(self, event_data):
        """Test that edit raises NotImplementedError."""
        event = Event(**event_data)

        with pytest.raises(NotImplementedError, match="Events cannot be edited"):
            # This is a sync call so we don't await
            import asyncio

            try:
                asyncio.run(event.edit(score=20))
            except RuntimeError as e:
                # If there's no event loop, create one
                if "no running event loop" in str(e).lower():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(event.edit(score=20))
                    finally:
                        loop.close()
                else:
                    raise

    def test_manual_event(self):
        """Test manual event type."""
        event = Event(id=1, entityType="manual", score=5)

        assert event.is_manual is True
        assert event.is_marketing is False
        assert event.is_news is False

    def test_news_event(self):
        """Test news event type."""
        event = Event(id=1, entityType="news", score=0)

        assert event.is_news is True
        assert event.is_manual is False
        assert event.is_marketing is False
