"""Unit tests for AdCampaigns resource manager."""

from unittest.mock import AsyncMock, Mock

import pytest

from upsales.http import HTTPClient
from upsales.models.ad_campaigns import AdCampaign, PartialAdCampaign
from upsales.resources.ad_campaigns import AdCampaignsResource


@pytest.fixture
def mock_http():
    """Create a mock HTTP client."""
    http = Mock(spec=HTTPClient)
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.delete = AsyncMock()
    http._upsales_client = None  # Required for BaseResource
    return http


@pytest.fixture
def ad_campaigns_resource(mock_http):
    """Create AdCampaignsResource instance with mock HTTP client."""
    return AdCampaignsResource(mock_http)


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data matching API response structure."""
    return {
        "id": 1,
        "name": "Q4 Campaign",
        "type": "email",
        "budget": 10000.0,
        "spent": 3500.50,
        "startDate": "2024-10-01",
        "endDate": "2024-12-31",
        "status": "active",
        "impressions": 50000,
        "clicks": 1250,
        "conversions": 125,
        "cpm": 70.01,
        "externalId": "ext-123",
        "useRange": True,
        "targetAbm": 0,
        "creative": [{"id": 1, "name": "Creative 1"}],
        "target": [{"id": 1, "criteria": "age>25"}],
        "siteTemplate": [{"id": 1, "name": "Template 1"}],
        "custom": [],
    }


class TestAdCampaignsResource:
    """Test suite for AdCampaignsResource."""

    def test_initialization(self, mock_http):
        """Test resource initialization with correct endpoint."""
        resource = AdCampaignsResource(mock_http)
        assert resource._endpoint == "/engage/campaign"
        assert resource._model_class == AdCampaign
        assert resource._partial_class == PartialAdCampaign

    @pytest.mark.asyncio
    async def test_get_campaign(self, ad_campaigns_resource, mock_http, sample_campaign_data):
        """Test getting a single campaign by ID."""
        mock_http.get.return_value = {"data": sample_campaign_data}

        campaign = await ad_campaigns_resource.get(1)

        assert isinstance(campaign, AdCampaign)
        assert campaign.id == 1
        assert campaign.name == "Q4 Campaign"
        assert campaign.budget == 10000.0
        assert campaign.status == "active"
        mock_http.get.assert_called_once_with("/engage/campaign/1")

    @pytest.mark.asyncio
    async def test_list_campaigns(self, ad_campaigns_resource, mock_http, sample_campaign_data):
        """Test listing campaigns with pagination."""
        mock_http.get.return_value = {
            "data": [sample_campaign_data],
            "metadata": {"total": 1, "limit": 100, "offset": 0},
        }

        campaigns = await ad_campaigns_resource.list(limit=10)

        assert len(campaigns) == 1
        assert isinstance(campaigns[0], AdCampaign)
        assert campaigns[0].name == "Q4 Campaign"
        mock_http.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_campaign(self, ad_campaigns_resource, mock_http, sample_campaign_data):
        """Test creating a new campaign."""
        mock_http.post.return_value = {"data": sample_campaign_data}

        campaign = await ad_campaigns_resource.create(
            name="Q4 Campaign",
            startDate="2024-10-01",
            endDate="2024-12-31",
            budget=10000.0,
        )

        assert isinstance(campaign, AdCampaign)
        assert campaign.name == "Q4 Campaign"
        assert campaign.budget == 10000.0
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        assert call_args[0][0] == "/engage/campaign"

    @pytest.mark.asyncio
    async def test_update_campaign(self, ad_campaigns_resource, mock_http, sample_campaign_data):
        """Test updating an existing campaign."""
        updated_data = sample_campaign_data.copy()
        updated_data["budget"] = 15000.0
        mock_http.put.return_value = {"data": updated_data}

        campaign = await ad_campaigns_resource.update(1, budget=15000.0)

        assert isinstance(campaign, AdCampaign)
        assert campaign.budget == 15000.0
        mock_http.put.assert_called_once_with("/engage/campaign/1", budget=15000.0)

    @pytest.mark.asyncio
    async def test_delete_campaign(self, ad_campaigns_resource, mock_http):
        """Test deleting a campaign."""
        mock_http.delete.return_value = None

        await ad_campaigns_resource.delete(1)

        mock_http.delete.assert_called_once_with("/engage/campaign/1")

    @pytest.mark.asyncio
    async def test_get_active_campaigns(
        self, ad_campaigns_resource, mock_http, sample_campaign_data
    ):
        """Test getting active campaigns using custom method."""
        mock_http.get.return_value = {
            "data": [sample_campaign_data],
            "metadata": {"total": 1, "limit": 100, "offset": 0},
        }

        campaigns = await ad_campaigns_resource.get_active()

        assert len(campaigns) == 1
        assert campaigns[0].status == "active"
        # Verify it called list_all with status filter
        mock_http.get.assert_called()


class TestAdCampaignModel:
    """Test suite for AdCampaign model."""

    def test_create_campaign_model(self, sample_campaign_data):
        """Test creating AdCampaign model from data."""
        campaign = AdCampaign(**sample_campaign_data)

        assert campaign.id == 1
        assert campaign.name == "Q4 Campaign"
        assert campaign.budget == 10000.0
        assert campaign.spent == 3500.50
        assert campaign.status == "active"
        assert campaign.impressions == 50000
        assert campaign.clicks == 1250

    def test_frozen_fields(self, sample_campaign_data):
        """Test that read-only fields are frozen."""
        campaign = AdCampaign(**sample_campaign_data)

        # These should raise ValidationError when trying to modify
        with pytest.raises(Exception):  # Pydantic ValidationError
            campaign.id = 999

        with pytest.raises(Exception):
            campaign.spent = 5000.0

        with pytest.raises(Exception):
            campaign.impressions = 100000

    def test_computed_field_is_active(self, sample_campaign_data):
        """Test is_active computed property."""
        campaign = AdCampaign(**sample_campaign_data)
        assert campaign.is_active is True

        # Test inactive campaign
        sample_campaign_data["status"] = "paused"
        inactive_campaign = AdCampaign(**sample_campaign_data)
        assert inactive_campaign.is_active is False

    def test_computed_field_ctr(self, sample_campaign_data):
        """Test CTR (click-through rate) computed property."""
        campaign = AdCampaign(**sample_campaign_data)

        # CTR = (clicks / impressions) * 100
        # 1250 / 50000 * 100 = 2.5%
        assert campaign.ctr == 2.5

        # Test with zero impressions
        sample_campaign_data["impressions"] = 0
        zero_campaign = AdCampaign(**sample_campaign_data)
        assert zero_campaign.ctr == 0.0

    def test_computed_field_budget_remaining(self, sample_campaign_data):
        """Test budget_remaining computed property."""
        campaign = AdCampaign(**sample_campaign_data)

        # Remaining = budget - spent
        # 10000 - 3500.50 = 6499.50
        assert campaign.budget_remaining == 6499.50

    def test_custom_fields_access(self, sample_campaign_data):
        """Test custom fields access through computed property."""
        sample_campaign_data["custom"] = [
            {"fieldId": 11, "value": "email"},
            {"fieldId": 12, "value": "premium"},
        ]
        campaign = AdCampaign(**sample_campaign_data)

        assert campaign.custom_fields[11] == "email"
        assert campaign.custom_fields[12] == "premium"

    def test_serialization_excludes_frozen_fields(self, sample_campaign_data):
        """Test that to_api_dict excludes frozen fields."""
        campaign = AdCampaign(**sample_campaign_data)

        api_dict = campaign.to_api_dict(budget=12000.0)

        # Frozen fields should not be in output
        assert "id" not in api_dict
        assert "spent" not in api_dict
        assert "impressions" not in api_dict
        assert "clicks" not in api_dict
        assert "conversions" not in api_dict
        assert "cpm" not in api_dict
        assert "externalId" not in api_dict

        # Updatable fields should be present
        assert "name" in api_dict
        assert "budget" in api_dict
        assert api_dict["budget"] == 12000.0

    @pytest.mark.asyncio
    async def test_edit_method(self, sample_campaign_data):
        """Test edit method on AdCampaign instance."""
        # Mock the client
        mock_client = Mock()
        mock_client.ad_campaigns = Mock()
        updated_campaign = AdCampaign(**sample_campaign_data)
        mock_client.ad_campaigns.update = AsyncMock(return_value=updated_campaign)

        # Create campaign with client reference
        campaign = AdCampaign(**sample_campaign_data, _client=mock_client)

        await campaign.edit(budget=15000.0, status="paused")

        mock_client.ad_campaigns.update.assert_called_once()
        call_args = mock_client.ad_campaigns.update.call_args
        assert call_args[0][0] == 1  # campaign ID


class TestPartialAdCampaignModel:
    """Test suite for PartialAdCampaign model."""

    def test_create_partial_campaign(self):
        """Test creating PartialAdCampaign with minimal data."""
        partial = PartialAdCampaign(id=1, name="Q4 Campaign")

        assert partial.id == 1
        assert partial.name == "Q4 Campaign"

    @pytest.mark.asyncio
    async def test_fetch_full(self):
        """Test fetching full campaign from partial."""
        # Mock the client
        mock_client = Mock()
        full_campaign = Mock(spec=AdCampaign)
        mock_client.ad_campaigns = Mock()
        mock_client.ad_campaigns.get = AsyncMock(return_value=full_campaign)

        # Create partial with client reference
        partial = PartialAdCampaign(id=1, name="Q4 Campaign", _client=mock_client)

        result = await partial.fetch_full()

        assert result == full_campaign
        mock_client.ad_campaigns.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_edit_from_partial(self):
        """Test editing campaign from partial instance."""
        # Mock the client
        mock_client = Mock()
        updated_campaign = Mock(spec=AdCampaign)
        mock_client.ad_campaigns = Mock()
        mock_client.ad_campaigns.update = AsyncMock(return_value=updated_campaign)

        # Create partial with client reference
        partial = PartialAdCampaign(id=1, name="Q4 Campaign", _client=mock_client)

        result = await partial.edit(budget=15000.0)

        assert result == updated_campaign
        mock_client.ad_campaigns.update.assert_called_once_with(1, budget=15000.0)
