"""
Unit tests for OpportunityAIResource.

Tests READ-ONLY operations for opportunity AI analysis endpoint.
This endpoint does NOT support create/update/delete operations.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.exceptions import UpsalesError
from upsales.http import HTTPClient
from upsales.models.opportunity_ai import OpportunityAI
from upsales.resources.opportunity_ai import OpportunityAIResource


class TestOpportunityAIResourceGet:
    """Test GET operations for OpportunityAIResource."""

    @pytest.fixture
    def sample_opportunity_data(self):
        """Sample complete opportunity data."""
        return {
            "id": 45,
            "description": "Test Opportunity",
            "date": "2024-04-02T00:00:00.000Z",
            "value": 300,
            "probability": 100,
            "stage": {"id": 12, "name": "Closed Won"},
            "client": {"id": 24, "name": "Test Company"},
            "user": {"id": 1, "name": "Test User", "email": "test@example.com"},
        }

    @pytest.fixture
    def sample_ai_data(self, sample_opportunity_data):
        """Sample AI analysis data for testing."""
        return {
            "appointment": {"id": 102, "date": "2025-05-21T22:00:00.000Z"},
            "activity": {"lastContact": "2025-05-20"},
            "allActivity": {"totalContacts": 5},
            "isDecisionMakerInvolved": True,
            "decisionMakerId": 10,
            "avg": 4.5,
            "checklist": [{"item": "Follow up", "done": True}],
            "opportunity": sample_opportunity_data,
        }

    @pytest.fixture
    def sample_get_all_response(self):
        """Sample get_all response structure."""
        return {
            "error": None,
            "data": [
                {
                    "45": {
                        "meeting": {
                            "id": 102,
                            "date": "2025-05-21T22:00:00.000Z",
                            "description": "Test Meeting",
                        },
                        "activity": {},
                        "allActivity": {},
                        "notOld": None,
                        "confirmedDate": None,
                        "confirmedBudget": False,
                        "confirmedSolution": False,
                        "notPassedDate": False,
                        "todo": None,
                        "phonecall": None,
                        "futurePhonecall": None,
                        "checklist": [],
                    },
                    "46": {
                        "meeting": {},
                        "activity": {"lastContact": "2025-05-20"},
                        "allActivity": {},
                        "notOld": None,
                        "confirmedDate": None,
                        "confirmedBudget": True,
                        "confirmedSolution": True,
                        "notPassedDate": False,
                        "todo": {"id": 5, "description": "Call client"},
                        "phonecall": None,
                        "futurePhonecall": None,
                        "checklist": [],
                    },
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_ai_data):
        """Test getting AI analysis for a specific opportunity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI/45",
            json={"error": None, "data": sample_ai_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get(45)

            assert isinstance(result, OpportunityAI)
            assert result.id == 45
            assert result.opportunity_description == "Test Opportunity"
            assert result.opportunity_value == 300
            assert result.isDecisionMakerInvolved is True
            assert result.decisionMakerId == 10
            assert result.avg == 4.5

    @pytest.mark.asyncio
    async def test_get_computed_properties(self, httpx_mock: HTTPXMock, sample_ai_data):
        """Test computed properties on OpportunityAI model."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI/45",
            json={"error": None, "data": sample_ai_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get(45)

            # Test computed fields
            assert result.id == 45
            assert result.opportunity_description == "Test Opportunity"
            assert result.opportunity_value == 300
            assert result.opportunity_stage == {"id": 12, "name": "Closed Won"}

            # Test boolean helpers
            assert result.has_appointment is True
            assert result.has_activity is True

    @pytest.mark.asyncio
    async def test_get_empty_activity(self, httpx_mock: HTTPXMock, sample_opportunity_data):
        """Test AI data with no activity."""
        data = {
            "appointment": {},
            "activity": {},
            "allActivity": {},
            "isDecisionMakerInvolved": False,
            "decisionMakerId": None,
            "avg": None,
            "checklist": [],
            "opportunity": sample_opportunity_data,
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI/45",
            json={"error": None, "data": data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get(45)

            assert result.has_appointment is False
            assert result.has_activity is False
            assert result.isDecisionMakerInvolved is False
            assert result.decisionMakerId is None

    @pytest.mark.asyncio
    async def test_get_all(self, httpx_mock: HTTPXMock, sample_get_all_response):
        """Test getting AI analysis for all opportunities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI",
            json=sample_get_all_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get_all()

            # Check result structure
            assert isinstance(result, dict)
            assert len(result) == 2
            assert 45 in result
            assert 46 in result

            # Check opportunity 45 data
            opp_45 = result[45]
            assert opp_45["meeting"]["id"] == 102
            assert opp_45["confirmedBudget"] is False

            # Check opportunity 46 data
            opp_46 = result[46]
            assert opp_46["confirmedBudget"] is True
            assert opp_46["todo"]["id"] == 5

    @pytest.mark.asyncio
    async def test_get_all_empty_list(self, httpx_mock: HTTPXMock):
        """Test get_all with empty data list raises error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI",
            json={"error": None, "data": []},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)

            with pytest.raises(UpsalesError, match="expected list with one item"):
                await resource.get_all()

    @pytest.mark.asyncio
    async def test_get_all_wrong_type(self, httpx_mock: HTTPXMock):
        """Test get_all with wrong data type raises error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI",
            json={"error": None, "data": {"not": "a list"}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)

            with pytest.raises(UpsalesError, match="expected list with one item"):
                await resource.get_all()

    @pytest.mark.asyncio
    async def test_get_all_wrong_inner_type(self, httpx_mock: HTTPXMock):
        """Test get_all with wrong inner data type raises error."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI",
            json={"error": None, "data": ["not a dict"]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)

            with pytest.raises(UpsalesError, match="expected dict"):
                await resource.get_all()


class TestOpportunityAIResourceReadOnly:
    """Test that OpportunityAI resource is read-only."""

    @pytest.mark.asyncio
    async def test_no_create_method(self):
        """Test that resource has no create method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "create")

    @pytest.mark.asyncio
    async def test_no_update_method(self):
        """Test that resource has no update method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "update")

    @pytest.mark.asyncio
    async def test_no_delete_method(self):
        """Test that resource has no delete method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "delete")

    @pytest.mark.asyncio
    async def test_no_list_method(self):
        """Test that resource has no standard list method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "list")

    @pytest.mark.asyncio
    async def test_no_list_all_method(self):
        """Test that resource has no list_all method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "list_all")

    @pytest.mark.asyncio
    async def test_no_search_method(self):
        """Test that resource has no search method."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            assert not hasattr(resource, "search")


class TestOpportunityAIResourceEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def minimal_ai_data(self):
        """Minimal valid AI data."""
        return {
            "appointment": {},
            "activity": {},
            "allActivity": {},
            "isDecisionMakerInvolved": False,
            "decisionMakerId": None,
            "avg": None,
            "checklist": [],
            "opportunity": {"id": 1, "description": "Minimal", "value": 0},
        }

    @pytest.mark.asyncio
    async def test_get_with_minimal_data(self, httpx_mock: HTTPXMock, minimal_ai_data):
        """Test get with minimal valid data."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI/1",
            json={"error": None, "data": minimal_ai_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get(1)

            assert isinstance(result, OpportunityAI)
            assert result.id == 1
            assert result.opportunity_description == "Minimal"
            assert result.opportunity_value == 0

    @pytest.mark.asyncio
    async def test_get_all_with_single_opportunity(self, httpx_mock: HTTPXMock):
        """Test get_all with only one opportunity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/opportunityAI",
            json={
                "error": None,
                "data": [
                    {
                        "100": {
                            "meeting": {},
                            "activity": {},
                            "allActivity": {},
                            "confirmedBudget": False,
                        }
                    }
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = OpportunityAIResource(http)
            result = await resource.get_all()

            assert len(result) == 1
            assert 100 in result
            assert result[100]["confirmedBudget"] is False
