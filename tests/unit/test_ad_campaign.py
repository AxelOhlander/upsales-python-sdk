"""
Unit tests for AdCampaign models.

Tests cover:
- Model validation with correct data
- Validator behavior (BinaryFlag, PositiveInt)
- Computed fields (is_active)
- Error cases (invalid data, unsupported operations)
- Frozen field immutability
- Partial model behavior
"""

import pytest
from pydantic import ValidationError

from upsales.models.ad_campaign import AdCampaign, PartialAdCampaign


class TestAdCampaign:
    """Test suite for AdCampaign model."""

    def test_create_valid_campaign(self):
        """Test creating a valid ad campaign."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=150,
            impressions=5000,
            grade="A",
            hasIp=True,
            lastTimestamp="2025-10-01T12:00:00.000Z",
        )

        assert campaign.id == 1
        assert campaign.active == 1
        assert campaign.brandId == 100
        assert campaign.clicks == 150
        assert campaign.impressions == 5000
        assert campaign.grade == "A"
        assert campaign.hasIp is True
        assert campaign.lastTimestamp == "2025-10-01T12:00:00.000Z"

    def test_create_campaign_optional_timestamp(self):
        """Test creating campaign with optional lastTimestamp."""
        campaign = AdCampaign(
            id=1,
            active=0,
            brandId=100,
            clicks=0,
            impressions=0,
            grade="F",
            hasIp=False,
        )

        assert campaign.id == 1
        assert campaign.lastTimestamp is None

    def test_computed_field_is_active(self):
        """Test is_active computed field."""
        active_campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=100,
            impressions=1000,
            grade="A",
            hasIp=True,
        )
        assert active_campaign.is_active is True

        inactive_campaign = AdCampaign(
            id=2,
            active=0,
            brandId=100,
            clicks=0,
            impressions=0,
            grade="F",
            hasIp=False,
        )
        assert inactive_campaign.is_active is False

    def test_active_validates_boolean(self):
        """Test active field validates as boolean (API returns bool true/false)."""
        # Valid values - booleans
        campaign_false = AdCampaign(
            id=1, active=False, brandId=1, clicks=0, impressions=0, grade="F", hasIp=False
        )
        assert campaign_false.active is False
        assert campaign_false.is_active is False

        campaign_true = AdCampaign(
            id=1, active=True, brandId=1, clicks=100, impressions=1000, grade="A", hasIp=True
        )
        assert campaign_true.active is True
        assert campaign_true.is_active is True

        # Pydantic coerces 0/1 to bool
        campaign_0 = AdCampaign(
            id=1, active=0, brandId=1, clicks=0, impressions=0, grade="F", hasIp=False
        )
        assert campaign_0.active is False

        campaign_1 = AdCampaign(
            id=1, active=1, brandId=1, clicks=100, impressions=1000, grade="A", hasIp=True
        )
        assert campaign_1.active is True

    def test_clicks_validates_positive_int(self):
        """Test clicks field validates as positive integer."""
        # Valid: zero and positive
        campaign_0 = AdCampaign(
            id=1, active=1, brandId=1, clicks=0, impressions=0, grade="F", hasIp=False
        )
        assert campaign_0.clicks == 0

        campaign_positive = AdCampaign(
            id=1, active=1, brandId=1, clicks=150, impressions=1000, grade="A", hasIp=True
        )
        assert campaign_positive.clicks == 150

        # Invalid: negative
        with pytest.raises(ValidationError) as exc_info:
            AdCampaign(id=1, active=1, brandId=1, clicks=-1, impressions=0, grade="F", hasIp=False)
        assert "Must be non-negative integer" in str(exc_info.value)

        # Invalid: not integer
        with pytest.raises(ValidationError) as exc_info:
            AdCampaign(
                id=1, active=1, brandId=1, clicks="100", impressions=0, grade="F", hasIp=False
            )
        assert "Must be integer" in str(exc_info.value)

    def test_impressions_validates_positive_int(self):
        """Test impressions field validates as positive integer."""
        # Valid: zero and positive
        campaign_0 = AdCampaign(
            id=1, active=1, brandId=1, clicks=0, impressions=0, grade="F", hasIp=False
        )
        assert campaign_0.impressions == 0

        campaign_positive = AdCampaign(
            id=1, active=1, brandId=1, clicks=100, impressions=5000, grade="A", hasIp=True
        )
        assert campaign_positive.impressions == 5000

        # Invalid: negative
        with pytest.raises(ValidationError) as exc_info:
            AdCampaign(id=1, active=1, brandId=1, clicks=0, impressions=-1, grade="F", hasIp=False)
        assert "Must be non-negative integer" in str(exc_info.value)

    def test_frozen_fields_immutable(self):
        """Test that all fields are frozen (read-only)."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=150,
            impressions=5000,
            grade="A",
            hasIp=True,
        )

        # All fields should be frozen
        with pytest.raises(ValidationError) as exc_info:
            campaign.id = 2
        assert "frozen" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            campaign.active = 0
        assert "frozen" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            campaign.clicks = 200
        assert "frozen" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_edit_not_supported(self):
        """Test that edit() raises NotImplementedError."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=150,
            impressions=5000,
            grade="A",
            hasIp=True,
        )

        with pytest.raises(NotImplementedError) as exc_info:
            await campaign.edit(active=0)
        assert "read-only nested data" in str(exc_info.value)

    def test_to_api_dict_excludes_frozen_fields(self):
        """Test that to_api_dict() excludes all frozen fields."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=150,
            impressions=5000,
            grade="A",
            hasIp=True,
        )

        api_dict = campaign.to_api_dict()

        # All fields are frozen, so should be empty except _client
        # (but _client is also excluded)
        assert api_dict == {}

    def test_repr(self):
        """Test string representation."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=150,
            impressions=5000,
            grade="A",
            hasIp=True,
        )

        assert repr(campaign) == "<AdCampaign id=1>"


class TestPartialAdCampaign:
    """Test suite for PartialAdCampaign model."""

    def test_create_valid_partial(self):
        """Test creating a valid partial ad campaign."""
        partial = PartialAdCampaign(
            id=1,
            active=1,
            clicks=150,
            impressions=5000,
        )

        assert partial.id == 1
        assert partial.active == 1
        assert partial.clicks == 150
        assert partial.impressions == 5000

    def test_computed_field_is_active(self):
        """Test is_active computed field."""
        active = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
        assert active.is_active is True

        inactive = PartialAdCampaign(id=2, active=0, clicks=0, impressions=0)
        assert inactive.is_active is False

    def test_active_validates_binary_flag(self):
        """Test active field validates as binary flag."""
        # Valid
        partial_0 = PartialAdCampaign(id=1, active=0, clicks=0, impressions=0)
        assert partial_0.active == 0

        partial_1 = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
        assert partial_1.active == 1

        # Invalid
        with pytest.raises(ValidationError) as exc_info:
            PartialAdCampaign(id=1, active=2, clicks=0, impressions=0)
        assert "Binary flag must be 0 or 1" in str(exc_info.value)

    def test_clicks_validates_positive_int(self):
        """Test clicks field validates as positive integer."""
        # Valid
        partial = PartialAdCampaign(id=1, active=1, clicks=150, impressions=1000)
        assert partial.clicks == 150

        # Invalid
        with pytest.raises(ValidationError) as exc_info:
            PartialAdCampaign(id=1, active=1, clicks=-1, impressions=0)
        assert "Must be non-negative integer" in str(exc_info.value)

    def test_impressions_validates_positive_int(self):
        """Test impressions field validates as positive integer."""
        # Valid
        partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=5000)
        assert partial.impressions == 5000

        # Invalid
        with pytest.raises(ValidationError) as exc_info:
            PartialAdCampaign(id=1, active=1, clicks=0, impressions=-1)
        assert "Must be non-negative integer" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_full_not_supported(self):
        """Test that fetch_full() raises NotImplementedError."""
        partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)

        with pytest.raises(NotImplementedError) as exc_info:
            await partial.fetch_full()
        assert "no dedicated endpoint" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_edit_not_supported(self):
        """Test that edit() raises NotImplementedError."""
        partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)

        with pytest.raises(NotImplementedError) as exc_info:
            await partial.edit(active=0)
        assert "read-only nested data" in str(exc_info.value)

    def test_repr(self):
        """Test string representation."""
        partial = PartialAdCampaign(id=1, active=1, clicks=100, impressions=1000)
        assert repr(partial) == "<PartialAdCampaign id=1>"


class TestAdCampaignEdgeCases:
    """Test edge cases for AdCampaign models."""

    def test_zero_clicks_and_impressions(self):
        """Test campaign with zero metrics."""
        campaign = AdCampaign(
            id=1,
            active=0,
            brandId=100,
            clicks=0,
            impressions=0,
            grade="F",
            hasIp=False,
        )

        assert campaign.clicks == 0
        assert campaign.impressions == 0
        assert campaign.is_active is False

    def test_large_metrics(self):
        """Test campaign with large click/impression counts."""
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=1_000_000,
            impressions=50_000_000,
            grade="A",
            hasIp=True,
        )

        assert campaign.clicks == 1_000_000
        assert campaign.impressions == 50_000_000

    def test_extra_fields_allowed(self):
        """Test that extra fields from API are allowed."""
        # BaseModel has extra="allow" in config
        campaign = AdCampaign(
            id=1,
            active=1,
            brandId=100,
            clicks=100,
            impressions=1000,
            grade="A",
            hasIp=True,
            unknown_field="extra_data",  # Extra field
        )

        # Should not raise error
        assert campaign.id == 1
        assert hasattr(campaign, "unknown_field")

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            AdCampaign(
                id=1,
                active=1,
                # Missing: brandId, clicks, impressions, grade, hasIp
            )
        assert "Field required" in str(exc_info.value)
