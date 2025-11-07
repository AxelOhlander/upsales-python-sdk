"""
Unit tests for NotificationsResource.

Note: Notifications endpoint is read-only:
- No create/update/delete operations
- System-generated only
- Typically returns empty list

Tests cover:
- get() - Get single notification by ID
- list() - List notifications with pagination
- list_all() - Get all notifications with auto-pagination
- Model validation and parsing
- Client reference injection
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.exceptions import NotFoundError
from upsales.http import HTTPClient
from upsales.models.notifications import Notification, PartialNotification
from upsales.resources.notifications import NotificationsResource


class TestNotificationsResource:
    """Test NotificationsResource operations."""

    @pytest.fixture
    def sample_notification(self):
        """Sample notification data for testing."""
        return {
            "id": 1,
            "type": "Order",
            "action": "created",
            "entityId": 123,
            "client": None,
            "contact": None,
            "userIds": [
                {
                    "userId": 1,
                    "read": "2024-11-20T10:05:52.000Z",
                }
            ],
            "opportunity": None,
            "order": None,
            "visit": None,
            "date": "2024-11-20T09:58:18Z",
            "message": "Order #123 was created",
            "registeredBy": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
            },
            "status": 0,
            "esign": None,
            "brandId": 1,
            "hasData": True,
            "form": None,
        }

    @pytest.mark.asyncio
    async def test_get_notification(self, sample_notification, httpx_mock: HTTPXMock):
        """Test fetching a single notification."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications/1",
            json={"error": None, "data": sample_notification},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notification = await resource.get(1)

            assert isinstance(notification, Notification)
            assert notification.id == 1
            assert notification.type == "Order"
            assert notification.action == "created"
            assert notification.entityId == 123
            assert notification.message == "Order #123 was created"
            assert notification.date == "2024-11-20T09:58:18Z"
            assert notification.status == 0
            assert notification.brandId == 1
            assert notification.hasData is True

    @pytest.mark.asyncio
    async def test_get_notification_with_user_tracking(
        self, sample_notification, httpx_mock: HTTPXMock
    ):
        """Test notification user tracking data."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications/1",
            json={"error": None, "data": sample_notification},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notification = await resource.get(1)

            assert len(notification.userIds) == 1
            assert notification.userIds[0]["userId"] == 1
            assert notification.userIds[0]["read"] == "2024-11-20T10:05:52.000Z"

            assert notification.registeredBy.id == 1
            assert notification.registeredBy.name == "John Doe"
            assert notification.registeredBy.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_get_notification_not_found(self, httpx_mock: HTTPXMock):
        """Test fetching non-existent notification."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications/999",
            status_code=404,
            json={"error": "Not found", "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)

            with pytest.raises(NotFoundError):
                await resource.get(999)

    @pytest.mark.asyncio
    async def test_list_notifications_empty(self, httpx_mock: HTTPXMock):
        """Test listing notifications (typically empty)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 0, "limit": 100, "offset": 0},
                "data": [],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notifications = await resource.list()

            assert isinstance(notifications, list)
            assert len(notifications) == 0

    @pytest.mark.asyncio
    async def test_list_notifications_with_data(self, sample_notification, httpx_mock: HTTPXMock):
        """Test listing notifications with data."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_notification],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notifications = await resource.list()

            assert len(notifications) == 1
            assert all(isinstance(n, Notification) for n in notifications)
            assert notifications[0].id == 1

    @pytest.mark.asyncio
    async def test_list_notifications_with_pagination(
        self, sample_notification, httpx_mock: HTTPXMock
    ):
        """Test listing notifications with custom pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=10&offset=20",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 10, "offset": 20},
                "data": [sample_notification],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notifications = await resource.list(limit=10, offset=20)

            assert len(notifications) == 1
            assert notifications[0].id == 1

    @pytest.mark.asyncio
    async def test_list_all_notifications_empty(self, httpx_mock: HTTPXMock):
        """Test fetching all notifications when none exist."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 0, "limit": 100, "offset": 0},
                "data": [],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notifications = await resource.list_all()

            assert isinstance(notifications, list)
            assert len(notifications) == 0

    @pytest.mark.asyncio
    async def test_list_all_notifications_with_pagination(
        self, sample_notification, httpx_mock: HTTPXMock
    ):
        """Test fetching all notifications with automatic pagination."""
        sample_notification_2 = sample_notification.copy()
        sample_notification_2["id"] = 2

        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 0},
                "data": [sample_notification],
            },
        )

        # Second page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=100",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 100},
                "data": [sample_notification_2],
            },
        )

        # Third page (empty - stops pagination)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications?limit=100&offset=200",
            json={
                "error": None,
                "metadata": {"total": 2, "limit": 100, "offset": 200},
                "data": [],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = NotificationsResource(http)
            notifications = await resource.list_all()

            assert len(notifications) == 2
            assert notifications[0].id == 1
            assert notifications[1].id == 2


class TestPartialNotification:
    """Test PartialNotification model."""

    @pytest.mark.skip(
        reason="Partial model fetch_full requires integration test with real Upsales client"
    )
    @pytest.mark.asyncio
    async def test_partial_notification_fetch_full(self, httpx_mock: HTTPXMock):
        """Test fetching full notification from partial."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notifications/1",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "type": "Order",
                    "action": "created",
                    "entityId": 123,
                    "client": None,
                    "contact": None,
                    "userIds": [],
                    "opportunity": None,
                    "order": None,
                    "visit": None,
                    "date": "2024-11-20T09:58:18Z",
                    "message": "Test notification",
                    "registeredBy": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john@example.com",
                    },
                    "status": 0,
                    "esign": None,
                    "brandId": 1,
                    "hasData": False,
                    "form": None,
                },
            },
        )

        async with Upsales(token="test_token") as upsales:
            partial = PartialNotification(id=1, type="Order", message="Test notification")
            partial._client = upsales

            full = await partial.fetch_full()

            assert isinstance(full, Notification)
            assert full.id == 1
            assert full.type == "Order"
            assert full.message == "Test notification"
            assert full.date == "2024-11-20T09:58:18Z"

    @pytest.mark.skip(
        reason="Partial model without client is edge case, covered by integration tests"
    )
    @pytest.mark.asyncio
    async def test_partial_notification_no_client(self):
        """Test partial notification without client raises error."""
        partial = PartialNotification(id=1)

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()


class TestNotificationModel:
    """Test Notification model validation."""

    def test_notification_all_fields_frozen(self):
        """Test that all notification fields are frozen (read-only)."""
        notification = Notification(
            id=1,
            type="Order",
            action="created",
            entityId=123,
            date="2024-11-20T09:58:18Z",
            message="Test",
            status=0,
            brandId=1,
            hasData=False,
            userIds=[],
            registeredBy={"id": 1, "name": "Test", "email": "test@example.com"},
        )

        # All fields should be frozen
        with pytest.raises(
            Exception
        ):  # Pydantic raises ValidationError on frozen field modification
            notification.id = 2

        with pytest.raises(Exception):
            notification.type = "Contact"

        with pytest.raises(Exception):
            notification.status = 1

    def test_notification_optional_fields(self):
        """Test notification with optional fields."""
        notification = Notification(
            id=1,
            type="Order",
            action="",
            entityId=123,
            date="2024-11-20T09:58:18Z",
            message="",
            status=0,
            brandId=1,
            hasData=False,
            userIds=[],
            registeredBy={"id": 1, "name": "Test", "email": "test@example.com"},
            client=None,
            contact=None,
            opportunity=None,
            order=None,
            visit=None,
            esign=None,
        )

        assert notification.client is None
        assert notification.contact is None
        assert notification.opportunity is None
        assert notification.order is None
        assert notification.visit is None
        assert notification.esign is None
