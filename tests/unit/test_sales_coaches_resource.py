"""
Unit tests for SalesCoachesResource.

Tests CRUD operations and custom methods for sales coaches endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.salesCoaches import SalesCoach
from upsales.resources.sales_coaches import SalesCoachesResource


class TestSalesCoachesResourceCRUD:
    """Test CRUD operations for SalesCoachesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample sales coach data for testing."""
        return {
            "id": 1,
            "name": "Enterprise Sales Coach",
            "active": True,
            "budgetActive": True,
            "budgetStages": [{"id": 1, "name": "Budget Confirmed"}],
            "decisionMakersActive": True,
            "decisionMakersStages": [{"id": 1, "name": "CEO Engaged"}],
            "decisionMakersTitles": [{"title": "CEO"}, {"title": "CFO"}],
            "decisionMakersType": "required",
            "decisionMakers": [],
            "solutionActive": True,
            "solutionStages": [{"id": 1, "name": "Solution Proposed"}],
            "timeframeActive": True,
            "timeframeStages": [{"id": 1, "name": "Q1 Decision"}],
            "nextStepActive": True,
            "nextStepOnlyAppointments": False,
            "checklist": [{"item": "Verify budget"}],
            "users": [10, 20],
            "roles": [5],
            "regBy": 1,
            "regDate": "2024-01-01T00:00:00Z",
            "modBy": 1,
            "modDate": None,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {
                    **sample_data,
                    "id": 2,
                    "name": "SMB Sales Coach",
                    "active": False,
                    "budgetActive": False,
                    "decisionMakersActive": False,
                    "solutionActive": False,
                    "timeframeActive": False,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a sales coach."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.create(
                name="Enterprise Sales Coach",
                active=True,
                budgetActive=True,
                decisionMakersActive=True,
                solutionActive=True,
                timeframeActive=True,
            )

            assert isinstance(result, SalesCoach)
            assert result.id == 1
            assert result.name == "Enterprise Sales Coach"
            assert result.active is True
            assert result.budgetActive is True
            assert result.decisionMakersActive is True
            assert result.solutionActive is True
            assert result.timeframeActive is True

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single sales coach."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.get(1)

            assert isinstance(result, SalesCoach)
            assert result.id == 1
            assert result.name == "Enterprise Sales Coach"
            assert result.budgetActive is True
            assert len(result.users) == 2
            assert 10 in result.users
            assert 20 in result.users

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing sales coaches with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "SMB Sales Coach"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a sales coach."""
        updated_data = {
            **sample_data,
            "name": "Updated Enterprise Coach",
            "budgetActive": False,
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.update(1, name="Updated Enterprise Coach", budgetActive=False)

            assert isinstance(result, SalesCoach)
            assert result.id == 1
            assert result.name == "Updated Enterprise Coach"
            assert result.budgetActive is False

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a sales coach."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        # Mock responses for each update
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/salesCoaches/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i, "active": False}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"active": False},
            )

            assert len(results) == 3
            assert all(isinstance(item, SalesCoach) for item in results)
            assert all(not r.active for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        # Mock responses for each delete
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/salesCoaches/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestSalesCoachesResourceCustomMethods:
    """Test custom methods specific to SalesCoachesResource."""

    @pytest.fixture
    def sample_coaches(self):
        """Sample sales coaches for custom method testing."""
        return [
            {
                "id": 1,
                "name": "Enterprise Sales Coach",
                "active": True,
                "budgetActive": True,
                "budgetStages": [],
                "decisionMakersActive": True,
                "decisionMakersStages": [],
                "decisionMakersTitles": [],
                "decisionMakersType": None,
                "decisionMakers": [],
                "solutionActive": True,
                "solutionStages": [],
                "timeframeActive": True,
                "timeframeStages": [],
                "nextStepActive": True,
                "nextStepOnlyAppointments": False,
                "checklist": [],
                "users": [10, 20],
                "roles": [5],
                "regBy": 1,
                "regDate": "2024-01-01T00:00:00Z",
                "modBy": 1,
                "modDate": None,
            },
            {
                "id": 2,
                "name": "SMB Sales Coach",
                "active": False,
                "budgetActive": True,
                "budgetStages": [],
                "decisionMakersActive": False,
                "decisionMakersStages": [],
                "decisionMakersTitles": [],
                "decisionMakersType": None,
                "decisionMakers": [],
                "solutionActive": False,
                "solutionStages": [],
                "timeframeActive": False,
                "timeframeStages": [],
                "nextStepActive": False,
                "nextStepOnlyAppointments": False,
                "checklist": [],
                "users": [30],
                "roles": [6],
                "regBy": 1,
                "regDate": "2024-01-01T00:00:00Z",
                "modBy": 1,
                "modDate": None,
            },
            {
                "id": 3,
                "name": "Partner Sales Coach",
                "active": True,
                "budgetActive": False,
                "budgetStages": [],
                "decisionMakersActive": True,
                "decisionMakersStages": [],
                "decisionMakersTitles": [],
                "decisionMakersType": None,
                "decisionMakers": [],
                "solutionActive": False,
                "solutionStages": [],
                "timeframeActive": False,
                "timeframeStages": [],
                "nextStepActive": False,
                "nextStepOnlyAppointments": False,
                "checklist": [],
                "users": [10],
                "roles": [5, 7],
                "regBy": 1,
                "regDate": "2024-01-01T00:00:00Z",
                "modBy": 1,
                "modDate": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_list_active(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_active() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_active()

            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert all(r.active for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "Partner Sales Coach"

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test get_by_name() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.get_by_name("Enterprise Sales Coach")

            assert result is not None
            assert isinstance(result, SalesCoach)
            assert result.id == 1
            assert result.name == "Enterprise Sales Coach"

    @pytest.mark.asyncio
    async def test_get_by_name_case_insensitive(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test get_by_name() is case-insensitive."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.get_by_name("ENTERPRISE SALES COACH")

            assert result is not None
            assert result.name == "Enterprise Sales Coach"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test get_by_name() when coach not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            result = await resource.get_by_name("Nonexistent Coach")

            assert result is None

    @pytest.mark.asyncio
    async def test_list_with_budget_tracking(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_with_budget_tracking() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_with_budget_tracking()

            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert all(r.budgetActive for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "SMB Sales Coach"

    @pytest.mark.asyncio
    async def test_list_with_decision_maker_tracking(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_with_decision_maker_tracking() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_with_decision_maker_tracking()

            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert all(r.decisionMakersActive for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "Partner Sales Coach"

    @pytest.mark.asyncio
    async def test_list_with_full_bant(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_with_full_bant() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_with_full_bant()

            # Only Enterprise Sales Coach has all BANT dimensions enabled
            assert len(results) == 1
            assert isinstance(results[0], SalesCoach)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[0].budgetActive
            assert results[0].decisionMakersActive
            assert results[0].solutionActive
            assert results[0].timeframeActive

    @pytest.mark.asyncio
    async def test_list_assigned_to_user(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_assigned_to_user() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_assigned_to_user(10)

            # User 10 is in coaches 1 and 3
            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert all(10 in r.users for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "Partner Sales Coach"

    @pytest.mark.asyncio
    async def test_list_assigned_to_user_not_found(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_assigned_to_user() when user has no coaches."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_assigned_to_user(999)

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_list_assigned_to_role(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_assigned_to_role() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_assigned_to_role(5)

            # Role 5 is in coaches 1 and 3
            assert len(results) == 2
            assert all(isinstance(r, SalesCoach) for r in results)
            assert all(5 in r.roles for r in results)
            assert results[0].name == "Enterprise Sales Coach"
            assert results[1].name == "Partner Sales Coach"

    @pytest.mark.asyncio
    async def test_list_assigned_to_role_not_found(self, httpx_mock: HTTPXMock, sample_coaches):
        """Test list_assigned_to_role() when role has no coaches."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/salesCoaches?limit=100&offset=0",
            json={"error": None, "data": sample_coaches},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = SalesCoachesResource(http)
            results = await resource.list_assigned_to_role(999)

            assert len(results) == 0
