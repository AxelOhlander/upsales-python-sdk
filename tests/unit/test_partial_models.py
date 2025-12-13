"""
Tests for PartialModel implementations.

Tests PartialRole, PartialCategory, and PartialCampaign models which are
used for nested objects in API responses.

Coverage target: 90%+
"""

from upsales.models.campaign import PartialCampaign
from upsales.models.category import PartialCategory
from upsales.models.roles import PartialRole


class TestPartialRole:
    """Test PartialRole model used in User.role."""

    def test_create_partial_role(self):
        """Test creating PartialRole with minimal fields."""
        role = PartialRole(id=1, name="Administrator")

        assert role.id == 1
        assert role.name == "Administrator"

    def test_partial_role_repr(self):
        """Test string representation."""
        role = PartialRole(id=1, name="Administrator")

        repr_str = repr(role)
        assert "PartialRole" in repr_str
        assert "id=1" in repr_str

    def test_partial_role_with_optional_fields(self):
        """Test creating PartialRole with optional fields."""
        role = PartialRole(
            id=1,
            name="Administrator",
            description="Admin role",
            hasDiscount=0,
        )

        assert role.id == 1
        assert role.name == "Administrator"
        assert role.description == "Admin role"


class TestPartialCategory:
    """Test PartialCategory model used in Product.category."""

    def test_create_partial_category(self):
        """Test creating PartialCategory with minimal fields."""
        category = PartialCategory(id=1, name="Software")

        assert category.id == 1
        assert category.name == "Software"

    def test_partial_category_repr(self):
        """Test string representation."""
        category = PartialCategory(id=5, name="Hardware")

        repr_str = repr(category)
        assert "PartialCategory" in repr_str
        assert "id=5" in repr_str


class TestPartialCampaign:
    """Test PartialCampaign model used in Company.projects."""

    def test_create_partial_campaign(self):
        """Test creating PartialCampaign with minimal fields."""
        campaign = PartialCampaign(id=1, name="Q1 2025 Campaign")

        assert campaign.id == 1
        assert campaign.name == "Q1 2025 Campaign"

    def test_partial_campaign_repr(self):
        """Test string representation."""
        campaign = PartialCampaign(id=10, name="Spring Sale")

        repr_str = repr(campaign)
        assert "PartialCampaign" in repr_str
        assert "id=10" in repr_str

    def test_display_name_computed_field(self):
        """Test display_name computed field."""
        campaign = PartialCampaign(id=1, name="Q1 Campaign")

        assert campaign.display_name == "Q1 Campaign"


# Coverage check
# Run: uv run pytest tests/unit/test_partial_models.py -v --cov=upsales/models/role.py --cov=upsales/models/category.py --cov=upsales/models/campaign.py --cov-report=term-missing
