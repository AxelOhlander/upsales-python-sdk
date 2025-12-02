"""Unit tests for ActivityQuota resource manager."""

from unittest.mock import AsyncMock

import pytest

from upsales.client import Upsales
from upsales.http import HTTPClient
from upsales.models.activity_quota import ActivityQuota, PartialActivityQuota
from upsales.resources.activity_quota import ActivityQuotaResource


@pytest.fixture
def http_client():
    """Create a mock HTTP client."""
    client = AsyncMock(spec=HTTPClient)
    client._upsales_client = None  # Add missing attribute for model creation
    return client


@pytest.fixture
def resource(http_client):
    """Create an ActivityQuotaResource instance."""
    return ActivityQuotaResource(http_client)


@pytest.fixture
def sample_quota_data():
    """Sample activity quota data matching API response."""
    return {
        "id": 1,
        "year": 2025,
        "month": 11,
        "date": "2025-11-01",
        "performed": 15,
        "created": 10,
        "user": {"id": 123, "name": "John Doe", "email": "john@example.com"},
        "activityType": {"id": 5, "name": "Call"},
    }


@pytest.fixture
def sample_quota(sample_quota_data):
    """Create a sample ActivityQuota instance."""
    return ActivityQuota(**sample_quota_data)


class TestActivityQuotaResource:
    """Test ActivityQuotaResource methods."""

    @pytest.mark.asyncio
    async def test_init(self, resource):
        """Test resource initialization."""
        assert resource._endpoint == "/activityQuota"
        assert resource._model_class == ActivityQuota
        assert resource._partial_class == PartialActivityQuota

    @pytest.mark.asyncio
    async def test_get(self, resource, http_client, sample_quota_data):
        """Test getting a single activity quota."""
        http_client.get.return_value = {"data": sample_quota_data}

        result = await resource.get(1)

        assert isinstance(result, ActivityQuota)
        assert result.id == 1
        assert result.year == 2025
        assert result.month == 11
        assert result.performed == 15
        http_client.get.assert_called_once_with("/activityQuota/1")

    @pytest.mark.asyncio
    async def test_list(self, resource, http_client, sample_quota_data):
        """Test listing activity quotas."""
        http_client.get.return_value = {
            "data": [sample_quota_data],
            "metadata": {"total": 1, "limit": 100, "offset": 0},
        }

        result = await resource.list(limit=10, offset=0)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ActivityQuota)
        assert result[0].id == 1
        http_client.get.assert_called_once_with(
            "/activityQuota", limit=10, offset=0
        )

    @pytest.mark.asyncio
    async def test_create(self, resource, http_client, sample_quota_data):
        """Test creating an activity quota."""
        http_client.post.return_value = {"data": sample_quota_data}

        result = await resource.create(
            year=2025,
            month=11,
            user={"id": 123},
            activityType={"id": 5},
            performed=15,
            created=10,
        )

        assert isinstance(result, ActivityQuota)
        assert result.id == 1
        assert result.year == 2025
        assert result.month == 11
        http_client.post.assert_called_once_with(
            "/activityQuota",
            year=2025,
            month=11,
            user={"id": 123},
            activityType={"id": 5},
            performed=15,
            created=10,
        )

    @pytest.mark.asyncio
    async def test_update(self, resource, http_client, sample_quota_data):
        """Test updating an activity quota."""
        updated_data = {**sample_quota_data, "performed": 20, "created": 15}
        http_client.put.return_value = {"data": updated_data}

        result = await resource.update(1, performed=20, created=15)

        assert isinstance(result, ActivityQuota)
        assert result.id == 1
        assert result.performed == 20
        assert result.created == 15
        http_client.put.assert_called_once_with(
            "/activityQuota/1", performed=20, created=15
        )

    @pytest.mark.asyncio
    async def test_delete(self, resource, http_client):
        """Test deleting an activity quota."""
        http_client.delete.return_value = {"data": None}

        await resource.delete(1)

        http_client.delete.assert_called_once_with("/activityQuota/1")

    @pytest.mark.asyncio
    async def test_get_by_user(self, resource, http_client, sample_quota_data):
        """Test getting quotas by user ID."""
        http_client.get.return_value = {
            "data": [sample_quota_data],
            "metadata": {"total": 1},
        }

        result = await resource.get_by_user(123)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].user.id == 123
        http_client.get.assert_called_once_with(
            "/activityQuota", user__id=123, limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_by_user_with_year_month(
        self, resource, http_client, sample_quota_data
    ):
        """Test getting quotas by user with year and month filters."""
        http_client.get.return_value = {
            "data": [sample_quota_data],
            "metadata": {"total": 1},
        }

        result = await resource.get_by_user(123, year=2025, month=11)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].year == 2025
        assert result[0].month == 11
        http_client.get.assert_called_once_with(
            "/activityQuota", user__id=123, year=2025, month=11, limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_by_user_invalid_month(self, resource):
        """Test that invalid month raises ValueError."""
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            await resource.get_by_user(123, month=13)

        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            await resource.get_by_user(123, month=0)

    @pytest.mark.asyncio
    async def test_get_by_activity_type(
        self, resource, http_client, sample_quota_data
    ):
        """Test getting quotas by activity type ID."""
        http_client.get.return_value = {
            "data": [sample_quota_data],
            "metadata": {"total": 1},
        }

        result = await resource.get_by_activity_type(5)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].activityType.id == 5
        http_client.get.assert_called_once_with(
            "/activityQuota", activityType__id=5, limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_by_activity_type_with_filters(
        self, resource, http_client, sample_quota_data
    ):
        """Test getting quotas by activity type with year filter."""
        http_client.get.return_value = {
            "data": [sample_quota_data],
            "metadata": {"total": 1},
        }

        result = await resource.get_by_activity_type(5, year=2025)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].activityType.id == 5
        assert result[0].year == 2025
        http_client.get.assert_called_once_with(
            "/activityQuota", activityType__id=5, year=2025, limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_get_by_activity_type_invalid_month(self, resource):
        """Test that invalid month raises ValueError."""
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            await resource.get_by_activity_type(5, month=15)


class TestActivityQuotaModel:
    """Test ActivityQuota model."""

    def test_model_creation(self, sample_quota_data):
        """Test creating an ActivityQuota instance."""
        quota = ActivityQuota(**sample_quota_data)

        assert quota.id == 1
        assert quota.year == 2025
        assert quota.month == 11
        assert quota.date == "2025-11-01"
        assert quota.performed == 15
        assert quota.created == 10
        assert quota.user.id == 123
        assert quota.activityType.id == 5

    def test_month_validation_valid(self):
        """Test that valid months (1-12) are accepted."""
        for month in range(1, 13):
            quota = ActivityQuota(
                id=1,
                year=2025,
                month=month,
                user={"id": 123, "name": "John", "email": "john@example.com"},
                activityType={"id": 5, "name": "Call"},
            )
            assert quota.month == month

    def test_month_validation_invalid(self):
        """Test that invalid months raise ValueError."""
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            ActivityQuota(
                id=1,
                year=2025,
                month=13,
                user={"id": 123, "name": "John", "email": "john@example.com"},
                activityType={"id": 5, "name": "Call"},
            )

        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            ActivityQuota(
                id=1,
                year=2025,
                month=0,
                user={"id": 123, "name": "John", "email": "john@example.com"},
                activityType={"id": 5, "name": "Call"},
            )

    def test_frozen_fields(self, sample_quota):
        """Test that frozen fields cannot be modified."""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            sample_quota.id = 999

        with pytest.raises(Exception):
            sample_quota.date = "2026-01-01"

    def test_default_values(self):
        """Test that optional fields have correct defaults."""
        quota = ActivityQuota(
            id=1,
            year=2025,
            month=11,
            user={"id": 123, "name": "John", "email": "john@example.com"},
            activityType={"id": 5, "name": "Call"},
        )

        assert quota.performed == 0
        assert quota.created == 0

    @pytest.mark.asyncio
    async def test_edit_method(self, sample_quota):
        """Test the edit method."""
        mock_client = AsyncMock(spec=Upsales)
        mock_client.activity_quota = AsyncMock(spec=ActivityQuotaResource)
        mock_client.activity_quota.update.return_value = sample_quota

        sample_quota._client = mock_client

        result = await sample_quota.edit(performed=20, created=15)

        assert isinstance(result, ActivityQuota)
        mock_client.activity_quota.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_without_client(self, sample_quota):
        """Test that edit raises error without client."""
        sample_quota._client = None
        with pytest.raises(RuntimeError, match="No client available"):
            await sample_quota.edit(performed=20)


class TestPartialActivityQuotaModel:
    """Test PartialActivityQuota model."""

    def test_partial_model_creation(self):
        """Test creating a PartialActivityQuota instance."""
        partial = PartialActivityQuota(id=1)

        assert partial.id == 1

    @pytest.mark.asyncio
    async def test_fetch_full(self):
        """Test fetching full activity quota."""
        partial = PartialActivityQuota(id=1)
        mock_client = AsyncMock(spec=Upsales)
        mock_client.activity_quota = AsyncMock(spec=ActivityQuotaResource)
        full_quota = ActivityQuota(
            id=1,
            year=2025,
            month=11,
            user={"id": 123, "name": "John", "email": "john@example.com"},
            activityType={"id": 5, "name": "Call"},
        )
        mock_client.activity_quota.get.return_value = full_quota

        partial._client = mock_client

        result = await partial.fetch_full()

        assert isinstance(result, ActivityQuota)
        assert result.id == 1
        mock_client.activity_quota.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_fetch_full_without_client(self):
        """Test that fetch_full raises error without client."""
        partial = PartialActivityQuota(id=1)
        partial._client = None
        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    @pytest.mark.asyncio
    async def test_edit_method(self):
        """Test the edit method on partial model."""
        partial = PartialActivityQuota(id=1)
        mock_client = AsyncMock(spec=Upsales)
        mock_client.activity_quota = AsyncMock(spec=ActivityQuotaResource)
        full_quota = ActivityQuota(
            id=1,
            year=2025,
            month=11,
            user={"id": 123, "name": "John", "email": "john@example.com"},
            activityType={"id": 5, "name": "Call"},
            performed=20,
        )
        mock_client.activity_quota.update.return_value = full_quota

        partial._client = mock_client

        result = await partial.edit(performed=20)

        assert isinstance(result, ActivityQuota)
        assert result.performed == 20
        mock_client.activity_quota.update.assert_called_once_with(1, performed=20)

    @pytest.mark.asyncio
    async def test_edit_without_client(self):
        """Test that edit raises error without client."""
        partial = PartialActivityQuota(id=1)
        partial._client = None
        with pytest.raises(RuntimeError, match="No client available"):
            await partial.edit(performed=20)
