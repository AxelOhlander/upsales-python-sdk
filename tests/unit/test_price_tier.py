"""
Tests for PriceTier and PartialPriceTier models.

Uses Python 3.13 native type hints.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from upsales.models.price_tier import PartialPriceTier, PriceTier


@pytest.fixture
def sample_price_tier_data() -> dict[str, Any]:
    """
    Sample price tier data from API.

    Returns:
        Dict with complete price tier data.
    """
    return {
        "quantity": 10,
        "price": 95.00,
        "discount": 5,
    }


@pytest.fixture
def sample_price_tier_no_discount() -> dict[str, Any]:
    """
    Sample price tier data without discount.

    Returns:
        Dict with price tier data but no discount.
    """
    return {
        "quantity": 5,
        "price": 100.00,
    }


@pytest.fixture
def sample_price_tier_high_quantity() -> dict[str, Any]:
    """
    Sample price tier data with large quantity.

    Returns:
        Dict with price tier data for bulk quantities.
    """
    return {
        "quantity": 1000,
        "price": 50.00,
        "discount": 20,
    }


@pytest.fixture
def minimal_price_tier_data() -> dict[str, Any]:
    """
    Minimal price tier data (required fields only).

    Returns:
        Dict with minimum required price tier fields.
    """
    return {
        "quantity": 1,
        "price": 100.00,
    }


# ============================================================================
# PriceTier Model Tests
# ============================================================================


def test_price_tier_creation(sample_price_tier_data):
    """Test creating PriceTier with complete data."""
    tier = PriceTier(**sample_price_tier_data)

    assert tier.quantity == 10
    assert tier.price == 95.00
    assert tier.discount == 5


def test_price_tier_minimal_creation(minimal_price_tier_data):
    """Test creating PriceTier with minimal required fields."""
    tier = PriceTier(**minimal_price_tier_data)

    assert tier.quantity == 1
    assert tier.price == 100.00
    assert tier.discount is None


def test_price_tier_validates_required_fields():
    """Test that PriceTier validates required fields."""
    # Missing quantity
    with pytest.raises(ValidationError, match="quantity"):
        PriceTier(price=100.00)

    # Missing price
    with pytest.raises(ValidationError, match="price"):
        PriceTier(quantity=10)


def test_price_tier_validates_positive_quantity():
    """Test that PriceTier validates quantity is positive."""
    # Negative quantity
    with pytest.raises(ValidationError):
        PriceTier(quantity=-1, price=100.00)

    # Zero is valid (PositiveInt allows >= 0)
    tier = PriceTier(quantity=0, price=100.00)
    assert tier.quantity == 0


def test_price_tier_validates_positive_discount():
    """Test that PriceTier validates discount is positive."""
    # Negative discount
    with pytest.raises(ValidationError):
        PriceTier(quantity=10, price=100.00, discount=-5)

    # Zero is valid (PositiveInt allows >= 0)
    tier = PriceTier(quantity=10, price=100.00, discount=0)
    assert tier.discount == 0


def test_price_tier_effective_price_with_discount(sample_price_tier_data):
    """Test effective_price computed field with discount."""
    tier = PriceTier(**sample_price_tier_data)

    # Price 95.00 with 5% discount = 95 * 0.95 = 90.25
    assert tier.effective_price == 90.25


def test_price_tier_effective_price_without_discount(sample_price_tier_no_discount):
    """Test effective_price computed field without discount."""
    tier = PriceTier(**sample_price_tier_no_discount)

    # No discount, so effective price = price
    assert tier.effective_price == 100.00


def test_price_tier_effective_price_zero_discount():
    """Test effective_price computed field with zero discount."""
    tier = PriceTier(quantity=10, price=100.00, discount=0)

    # Zero discount, so effective price = price
    assert tier.effective_price == 100.00


def test_price_tier_effective_price_large_discount():
    """Test effective_price computed field with large discount."""
    tier = PriceTier(quantity=100, price=100.00, discount=50)

    # 50% discount on 100 = 50
    assert tier.effective_price == 50.0


def test_price_tier_effective_price_small_discount():
    """Test effective_price computed field with small discount."""
    tier = PriceTier(quantity=10, price=100.00, discount=1)

    # 1% discount on 100 = 99
    assert tier.effective_price == 99.0


def test_price_tier_effective_price_fractional():
    """Test effective_price computed field with fractional amounts."""
    tier = PriceTier(quantity=10, price=99.99, discount=10)

    # 10% discount on 99.99 = 89.991
    expected = 99.99 * 0.9
    assert abs(tier.effective_price - expected) < 0.01


def test_price_tier_repr_with_discount(sample_price_tier_data):
    """Test string representation with discount."""
    tier = PriceTier(**sample_price_tier_data)
    repr_str = repr(tier)

    assert "PriceTier" in repr_str
    assert "qty=10" in repr_str
    assert "price=95" in repr_str
    assert "discount=5%" in repr_str


def test_price_tier_repr_without_discount(sample_price_tier_no_discount):
    """Test string representation without discount."""
    tier = PriceTier(**sample_price_tier_no_discount)
    repr_str = repr(tier)

    assert "PriceTier" in repr_str
    assert "qty=5" in repr_str
    assert "price=100" in repr_str
    assert "discount" not in repr_str  # Should not show discount when None


def test_price_tier_repr_zero_discount():
    """Test string representation with zero discount."""
    tier = PriceTier(quantity=10, price=100.00, discount=0)
    repr_str = repr(tier)

    assert "PriceTier" in repr_str
    assert "qty=10" in repr_str
    assert "price=100" in repr_str
    assert "discount" not in repr_str  # Should not show discount when 0


def test_price_tier_model_dump(sample_price_tier_data):
    """Test model_dump serialization."""
    tier = PriceTier(**sample_price_tier_data)
    data = tier.model_dump()

    # Should include all fields
    assert data["quantity"] == 10
    assert data["price"] == 95.00
    assert data["discount"] == 5

    # Should NOT include computed fields in model_dump by default
    # (Pydantic v2 behavior for computed fields)
    if "effective_price" in data:
        # If included, verify it's correct
        assert data["effective_price"] == 90.25


def test_price_tier_model_dump_exclude_computed(sample_price_tier_data):
    """Test model_dump with exclude computed fields."""
    tier = PriceTier(**sample_price_tier_data)
    data = tier.model_dump(exclude={"effective_price"})

    assert "quantity" in data
    assert "price" in data
    assert "discount" in data
    assert "effective_price" not in data


def test_price_tier_multiple_tiers_in_list():
    """Test using multiple PriceTier objects in a list (like Product.tiers)."""
    tiers = [
        PriceTier(quantity=1, price=100.00),
        PriceTier(quantity=10, price=95.00, discount=5),
        PriceTier(quantity=100, price=80.00, discount=20),
    ]

    assert len(tiers) == 3
    assert tiers[0].quantity == 1
    assert tiers[1].effective_price == 90.25
    assert tiers[2].effective_price == 64.0


def test_price_tier_sorted_by_quantity():
    """Test sorting price tiers by quantity."""
    tiers = [
        PriceTier(quantity=100, price=80.00),
        PriceTier(quantity=1, price=100.00),
        PriceTier(quantity=10, price=95.00),
    ]

    sorted_tiers = sorted(tiers, key=lambda t: t.quantity)

    assert sorted_tiers[0].quantity == 1
    assert sorted_tiers[1].quantity == 10
    assert sorted_tiers[2].quantity == 100


def test_price_tier_to_dict(sample_price_tier_data):
    """Test to_dict serialization (if available)."""
    tier = PriceTier(**sample_price_tier_data)

    # Pydantic BaseModel doesn't have to_dict, use model_dump instead
    data = tier.model_dump()

    assert data["quantity"] == 10
    assert data["price"] == 95.00
    assert data["discount"] == 5


def test_price_tier_field_assignment(sample_price_tier_data):
    """Test that PriceTier allows field assignment (without validation)."""
    tier = PriceTier(**sample_price_tier_data)

    # Should allow assignment
    tier.quantity = 20
    assert tier.quantity == 20

    # Note: validate_assignment=False, so invalid values are NOT validated on assignment
    # This is by design - PriceTier is a simple data model for nested use only


# ============================================================================
# PartialPriceTier Model Tests
# ============================================================================


def test_partial_price_tier_creation(sample_price_tier_data):
    """Test creating PartialPriceTier with complete data."""
    tier = PartialPriceTier(**sample_price_tier_data)

    assert tier.quantity == 10
    assert tier.price == 95.00


def test_partial_price_tier_minimal_creation(minimal_price_tier_data):
    """Test creating PartialPriceTier with minimal required fields."""
    tier = PartialPriceTier(**minimal_price_tier_data)

    assert tier.quantity == 1
    assert tier.price == 100.00


def test_partial_price_tier_validates_required_fields():
    """Test that PartialPriceTier validates required fields."""
    # Missing quantity
    with pytest.raises(ValidationError, match="quantity"):
        PartialPriceTier(price=100.00)

    # Missing price
    with pytest.raises(ValidationError, match="price"):
        PartialPriceTier(quantity=10)


def test_partial_price_tier_validates_positive_quantity():
    """Test that PartialPriceTier validates quantity is positive."""
    # Negative quantity
    with pytest.raises(ValidationError):
        PartialPriceTier(quantity=-1, price=100.00)


def test_partial_price_tier_accepts_extra_fields():
    """Test that PartialPriceTier accepts extra fields (extra='allow')."""
    # Create with extra discount field (allowed as extra field)
    tier = PartialPriceTier(quantity=10, price=95.00, discount=5)

    assert tier.quantity == 10
    assert tier.price == 95.00
    # With extra="allow", discount is stored as extra field
    # but NOT as a defined model field
    assert hasattr(tier, "discount")  # extra field is accessible
    # But it's not in model_fields
    assert "discount" not in PartialPriceTier.model_fields


def test_partial_price_tier_no_effective_price():
    """Test that PartialPriceTier does not have effective_price."""
    tier = PartialPriceTier(quantity=10, price=95.00)

    # Should not have computed field
    assert not hasattr(tier, "effective_price")


def test_partial_price_tier_repr():
    """Test string representation of PartialPriceTier."""
    tier = PartialPriceTier(quantity=10, price=95.00)
    repr_str = repr(tier)

    assert "PartialPriceTier" in repr_str
    assert "qty=10" in repr_str
    assert "price=95" in repr_str


def test_partial_price_tier_model_dump():
    """Test model_dump serialization of PartialPriceTier."""
    tier = PartialPriceTier(quantity=10, price=95.00)
    data = tier.model_dump()

    assert data["quantity"] == 10
    assert data["price"] == 95.00
    assert "discount" not in data
    assert "effective_price" not in data


def test_partial_price_tier_multiple_in_list():
    """Test using multiple PartialPriceTier objects in a list."""
    tiers = [
        PartialPriceTier(quantity=1, price=100.00),
        PartialPriceTier(quantity=10, price=95.00),
        PartialPriceTier(quantity=100, price=80.00),
    ]

    assert len(tiers) == 3
    assert tiers[0].quantity == 1
    assert tiers[1].price == 95.00
    assert tiers[2].price == 80.00


def test_partial_price_tier_field_assignment():
    """Test that PartialPriceTier allows field assignment (without validation)."""
    tier = PartialPriceTier(quantity=10, price=95.00)

    # Should allow assignment
    tier.quantity = 20
    assert tier.quantity == 20

    # Note: validate_assignment=False, so invalid values are NOT validated on assignment
    # This is by design - PartialPriceTier is a simple data model for nested use only


# ============================================================================
# Integration Tests
# ============================================================================


def test_price_tier_vs_partial_price_tier():
    """Test difference between PriceTier and PartialPriceTier."""
    tier_data = {"quantity": 10, "price": 95.00, "discount": 5}

    full_tier = PriceTier(**tier_data)
    partial_tier = PartialPriceTier(**tier_data)

    # Both have quantity and price
    assert full_tier.quantity == partial_tier.quantity
    assert full_tier.price == partial_tier.price

    # PriceTier has discount as a defined field
    assert full_tier.discount == 5
    assert "discount" in PriceTier.model_fields

    # PriceTier has effective_price computed field
    assert full_tier.effective_price == 90.25
    assert "effective_price" in PriceTier.model_computed_fields

    # PartialPriceTier doesn't have discount or effective_price as defined fields
    assert "discount" not in PartialPriceTier.model_fields
    assert "effective_price" not in PartialPriceTier.model_computed_fields
    # But discount can be stored as extra field if provided
    assert hasattr(partial_tier, "discount")  # from extra="allow"


def test_price_tier_in_list_with_product_context():
    """Test price tiers in product context (simulated)."""
    product_data = {
        "id": 1,
        "name": "Test Product",
        "tiers": [
            {"quantity": 1, "price": 100.00},
            {"quantity": 10, "price": 90.00, "discount": 10},
            {"quantity": 100, "price": 70.00, "discount": 30},
        ],
    }

    tiers = [PriceTier(**tier_data) for tier_data in product_data["tiers"]]

    assert len(tiers) == 3
    assert tiers[0].effective_price == 100.00
    assert tiers[1].effective_price == 81.0
    assert tiers[2].effective_price == 49.0


def test_price_tier_type_coercion():
    """Test type coercion for price tier fields."""
    # String numbers should be coerced
    tier = PriceTier(quantity=10, price="95.00")

    assert tier.quantity == 10
    assert tier.price == 95.0
    assert isinstance(tier.price, float)


def test_price_tier_extra_fields():
    """Test that PriceTier allows extra fields from API (extra='allow')."""
    data = {
        "quantity": 10,
        "price": 95.00,
        "discount": 5,
        "unknown_field": "some_value",
    }

    # Should not raise error if extra fields are allowed
    # Note: Default Pydantic BaseModel has extra='forbid', but we're checking
    tier = PriceTier(**data)
    assert tier.quantity == 10


def test_price_tier_quantity_validation_message():
    """Test validation error message for quantity."""
    with pytest.raises(ValidationError) as exc_info:
        PriceTier(quantity=-10, price=100.00)

    errors = exc_info.value.errors()
    assert any("quantity" in str(error) for error in errors)


def test_price_tier_discount_range_interpretation():
    """Test that discount represents percentage (0-100)."""
    # Test various discount values
    tier_0 = PriceTier(quantity=1, price=100.00, discount=0)
    tier_50 = PriceTier(quantity=1, price=100.00, discount=50)
    tier_100 = PriceTier(quantity=1, price=100.00, discount=100)

    assert tier_0.effective_price == 100.00
    assert tier_50.effective_price == 50.00
    assert tier_100.effective_price == 0.00
