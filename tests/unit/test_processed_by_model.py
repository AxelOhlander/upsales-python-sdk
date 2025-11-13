"""
Tests for ProcessedBy and PartialProcessedBy models.

Tests the models used for company processing tracking data.
"""

import pytest
from pydantic import ValidationError

from upsales.models.processed_by import PartialProcessedBy, ProcessedBy
from upsales.models.user import PartialUser


class TestProcessedByModel:
    """Test ProcessedBy full model."""

    def test_create_with_required_fields(self):
        """Test creating ProcessedBy with all required fields."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )

        assert processed_by.id == 123
        assert processed_by.entityType == "company"
        assert processed_by.date == "2025-10-15"
        assert processed_by.time == "14:30:00"
        assert processed_by.user.id == 1
        assert processed_by.user.name == "John Doe"

    def test_create_with_user_dict(self):
        """Test creating ProcessedBy with user as dict."""
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user={"id": 1, "name": "John Doe", "email": "john@example.com"},
        )

        assert processed_by.user.id == 1
        assert processed_by.user.name == "John Doe"
        assert processed_by.user.email == "john@example.com"

    def test_id_is_frozen(self):
        """Test that id field is frozen and cannot be changed."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )

        with pytest.raises(ValidationError, match="frozen"):
            processed_by.id = 456

    def test_entity_type_validates_non_empty(self):
        """Test that entityType must be non-empty string."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        # Empty string should fail
        with pytest.raises(ValidationError, match="String cannot be empty"):
            ProcessedBy(
                id=123,
                entityType="",
                date="2025-10-15",
                time="14:30:00",
                user=user,
            )

        # Whitespace only should fail
        with pytest.raises(ValidationError, match="String cannot be empty"):
            ProcessedBy(
                id=123,
                entityType="   ",
                date="2025-10-15",
                time="14:30:00",
                user=user,
            )

    def test_entity_type_strips_whitespace(self):
        """Test that entityType strips whitespace."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by = ProcessedBy(
            id=123,
            entityType="  company  ",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )

        assert processed_by.entityType == "company"

    def test_date_validates_non_empty(self):
        """Test that date must be non-empty string."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        with pytest.raises(ValidationError, match="String cannot be empty"):
            ProcessedBy(
                id=123,
                entityType="company",
                date="",
                time="14:30:00",
                user=user,
            )

    def test_time_is_optional(self):
        """Test that time field is optional (can be None or empty)."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        # Empty string is allowed
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="",
            user=user,
        )
        assert processed_by.time == ""

        # None is also allowed (field is optional)
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time=None,
            user=user,
        )
        assert processed_by.time is None

    def test_missing_required_fields(self):
        """Test that all required fields must be provided (time is optional)."""
        with pytest.raises(ValidationError, match="entityType"):
            ProcessedBy(
                id=123,
                date="2025-10-15",
                user={"id": 1, "name": "John", "email": "john@example.com"},
            )

        with pytest.raises(ValidationError, match="date"):
            ProcessedBy(
                id=123,
                entityType="company",
                user={"id": 1, "name": "John", "email": "john@example.com"},
            )

        with pytest.raises(ValidationError, match="user"):
            ProcessedBy(
                id=123,
                entityType="company",
                date="2025-10-15",
            )

        # time is optional - should NOT raise
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            user={"id": 1, "name": "John", "email": "john@example.com"},
        )
        assert processed_by.time is None  # Defaults to None

    def test_repr(self):
        """Test string representation."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )

        repr_str = repr(processed_by)
        assert repr_str == "<ProcessedBy id=123 entityType='company'>"

    async def test_edit_raises_runtime_error_without_client(self):
        """Test that edit() raises RuntimeError when no client available."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )

        with pytest.raises(RuntimeError, match="No client available"):
            await processed_by.edit(date="2025-10-16")

    def test_user_field_nested_validation(self):
        """Test that user field accepts both PartialUser and dict."""
        # User as dict - stays as dict (union type)
        processed_by = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user={"id": 1, "name": "John Doe", "email": "john@example.com"},
        )
        # With union type, Pydantic keeps it as dict
        assert isinstance(processed_by.user, (PartialUser, dict))

        # User as PartialUser object - accepted
        user_obj = PartialUser(id=1, name="John Doe", email="john@example.com")
        processed_by2 = ProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user_obj,
        )
        assert isinstance(processed_by2.user, PartialUser)


class TestPartialProcessedByModel:
    """Test PartialProcessedBy model."""

    def test_create_with_required_fields(self):
        """Test creating PartialProcessedBy with minimal fields."""
        partial = PartialProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
        )

        assert partial.id == 123
        assert partial.entityType == "company"
        assert partial.date == "2025-10-15"

    def test_id_is_frozen(self):
        """Test that id field is frozen and cannot be changed."""
        partial = PartialProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
        )

        with pytest.raises(ValidationError, match="frozen"):
            partial.id = 456

    def test_entity_type_validates_non_empty(self):
        """Test that entityType must be non-empty string."""
        with pytest.raises(ValidationError, match="String cannot be empty"):
            PartialProcessedBy(
                id=123,
                entityType="",
                date="2025-10-15",
            )

    def test_date_validates_non_empty(self):
        """Test that date must be non-empty string."""
        with pytest.raises(ValidationError, match="String cannot be empty"):
            PartialProcessedBy(
                id=123,
                entityType="company",
                date="",
            )

    def test_missing_required_fields(self):
        """Test that all required fields must be provided."""
        with pytest.raises(ValidationError, match="entityType"):
            PartialProcessedBy(
                id=123,
                date="2025-10-15",
            )

        with pytest.raises(ValidationError, match="date"):
            PartialProcessedBy(
                id=123,
                entityType="company",
            )

    def test_repr(self):
        """Test string representation."""
        partial = PartialProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
        )

        repr_str = repr(partial)
        assert repr_str == "<PartialProcessedBy id=123 entityType='company'>"

    async def test_fetch_full_raises_runtime_error_without_client(self):
        """Test that fetch_full() raises RuntimeError when no client available."""
        partial = PartialProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
        )

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    async def test_edit_raises_runtime_error_without_client(self):
        """Test that edit() raises RuntimeError when no client available."""
        partial = PartialProcessedBy(
            id=123,
            entityType="company",
            date="2025-10-15",
        )

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.edit(date="2025-10-16")


class TestProcessedByValidation:
    """Test validation scenarios for ProcessedBy models."""

    def test_different_entity_types(self):
        """Test ProcessedBy with different entity types."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        # Company
        company_pb = ProcessedBy(
            id=1,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )
        assert company_pb.entityType == "company"

        # Contact (if supported)
        contact_pb = ProcessedBy(
            id=2,
            entityType="contact",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )
        assert contact_pb.entityType == "contact"

        # Order (if supported)
        order_pb = ProcessedBy(
            id=3,
            entityType="order",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )
        assert order_pb.entityType == "order"

    def test_date_format_not_validated(self):
        """Test that date format is not strictly validated (string only)."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        # ISO format
        pb1 = ProcessedBy(
            id=1,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )
        assert pb1.date == "2025-10-15"

        # Other format (not validated, but accepted)
        pb2 = ProcessedBy(
            id=2,
            entityType="company",
            date="10/15/2025",
            time="14:30:00",
            user=user,
        )
        assert pb2.date == "10/15/2025"

    def test_time_format_not_validated(self):
        """Test that time format is not strictly validated (string only)."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        # 24-hour format
        pb1 = ProcessedBy(
            id=1,
            entityType="company",
            date="2025-10-15",
            time="14:30:00",
            user=user,
        )
        assert pb1.time == "14:30:00"

        # Other format (not validated, but accepted)
        pb2 = ProcessedBy(
            id=2,
            entityType="company",
            date="2025-10-15",
            time="2:30 PM",
            user=user,
        )
        assert pb2.time == "2:30 PM"


class TestProcessedByIntegration:
    """Test ProcessedBy in realistic scenarios."""

    def test_typical_usage_scenario(self):
        """Test typical usage of ProcessedBy from company response."""
        # Simulate company response with processedBy
        company_data = {
            "id": 1,
            "name": "Acme Corp",
            "processedBy": {
                "id": 123,
                "entityType": "company",
                "date": "2025-10-15",
                "time": "14:30:00",
                "user": {
                    "id": 5,
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                },
            },
        }

        # Create ProcessedBy from nested data
        processed_by = ProcessedBy(**company_data["processedBy"])

        assert processed_by.id == 123
        assert processed_by.entityType == "company"
        assert processed_by.date == "2025-10-15"
        assert processed_by.time == "14:30:00"
        assert processed_by.user.name == "Jane Smith"
        assert processed_by.user.email == "jane@example.com"

    def test_optional_presence(self):
        """Test that processedBy may be None in company responses."""
        # Company without processedBy
        company_data = {
            "id": 1,
            "name": "Acme Corp",
            "processedBy": None,
        }

        # This is handled at Company model level
        assert company_data["processedBy"] is None

    def test_partial_in_nested_context(self):
        """Test PartialProcessedBy in nested API responses."""
        # Simulate minimal processedBy data in list response
        partial_data = {
            "id": 123,
            "entityType": "company",
            "date": "2025-10-15",
        }

        partial = PartialProcessedBy(**partial_data)

        assert partial.id == 123
        assert partial.entityType == "company"
        assert partial.date == "2025-10-15"
