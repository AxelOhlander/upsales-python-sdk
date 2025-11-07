"""
Unit tests for Assignment models.

Tests cover:
- Assignment model creation and validation
- PartialAssignment model creation and validation
- Field validation and constraints
- No edit() or fetch_full() support (nested only)
- String representation
"""

import pytest
from pydantic import ValidationError

from upsales.models.assignment import Assignment, PartialAssignment
from upsales.models.user import PartialUser


class TestAssignment:
    """Tests for Assignment model."""

    def test_assignment_creation_valid(self):
        """Test creating a valid Assignment."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        assert assignment.user.id == 1
        assert assignment.user.name == "John Doe"
        assert assignment.user.email == "john@example.com"
        assert assignment.regDate == "2025-01-01T00:00:00.000Z"
        assert assignment.id == 0  # Assignments don't have their own IDs

    def test_assignment_creation_with_dict(self):
        """Test creating Assignment from dict (API response format)."""
        data = {
            "user": {"id": 1, "name": "John Doe", "email": "john@example.com"},
            "regDate": "2025-01-01T00:00:00.000Z",
        }
        assignment = Assignment(**data)

        assert assignment.user.id == 1
        assert assignment.user.name == "John Doe"
        assert assignment.regDate == "2025-01-01T00:00:00.000Z"

    def test_assignment_regdate_frozen(self):
        """Test that regDate is frozen after creation."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        with pytest.raises(ValidationError) as exc_info:
            assignment.regDate = "2025-02-01T00:00:00.000Z"

        assert "frozen" in str(exc_info.value).lower()

    def test_assignment_id_frozen(self):
        """Test that id is frozen after creation."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z", id=123)

        with pytest.raises(ValidationError) as exc_info:
            assignment.id = 456

        assert "frozen" in str(exc_info.value).lower()

    def test_assignment_user_mutable(self):
        """Test that user field can be updated."""
        user1 = PartialUser(id=1, name="John Doe", email="john@example.com")
        user2 = PartialUser(id=2, name="Jane Smith", email="jane@example.com")
        assignment = Assignment(user=user1, regDate="2025-01-01T00:00:00.000Z")

        assignment.user = user2

        assert assignment.user.id == 2
        assert assignment.user.name == "Jane Smith"

    async def test_assignment_edit_not_supported(self):
        """Test that edit() raises NotImplementedError."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        with pytest.raises(NotImplementedError) as exc_info:
            await assignment.edit(user=user)

        assert "nested" in str(exc_info.value).lower()
        assert "cannot be edited directly" in str(exc_info.value).lower()

    def test_assignment_repr(self):
        """Test string representation of Assignment."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        repr_str = repr(assignment)

        assert "Assignment" in repr_str
        assert "John Doe" in repr_str
        assert "2025-01-01T00:00:00.000Z" in repr_str

    def test_assignment_missing_user(self):
        """Test that user field is required."""
        with pytest.raises(ValidationError) as exc_info:
            Assignment(regDate="2025-01-01T00:00:00.000Z")

        assert "user" in str(exc_info.value).lower()

    def test_assignment_missing_regdate(self):
        """Test that regDate field is required."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")

        with pytest.raises(ValidationError) as exc_info:
            Assignment(user=user)

        assert "regdate" in str(exc_info.value).lower()

    def test_assignment_with_client_reference(self):
        """Test Assignment with client reference (for user.fetch_full())."""
        from unittest.mock import AsyncMock, MagicMock

        mock_client = MagicMock()
        mock_client.users = AsyncMock()

        user = PartialUser(id=1, name="John Doe", email="john@example.com", _client=mock_client)
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        # User should have client reference
        assert assignment.user._client is mock_client


class TestPartialAssignment:
    """Tests for PartialAssignment model."""

    def test_partial_assignment_creation_valid(self):
        """Test creating a valid PartialAssignment."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        partial = PartialAssignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        assert partial.user.id == 1
        assert partial.user.name == "John Doe"
        assert partial.regDate == "2025-01-01T00:00:00.000Z"
        assert partial.id == 0

    async def test_partial_assignment_fetch_full_not_supported(self):
        """Test that fetch_full() raises NotImplementedError."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        partial = PartialAssignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        with pytest.raises(NotImplementedError) as exc_info:
            await partial.fetch_full()

        assert "nested" in str(exc_info.value).lower()
        assert "no dedicated endpoint" in str(exc_info.value).lower()

    async def test_partial_assignment_edit_not_supported(self):
        """Test that edit() raises NotImplementedError."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        partial = PartialAssignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        with pytest.raises(NotImplementedError) as exc_info:
            await partial.edit(user=user)

        assert "nested" in str(exc_info.value).lower()
        assert "cannot be edited directly" in str(exc_info.value).lower()

    def test_partial_assignment_repr(self):
        """Test string representation of PartialAssignment."""
        user = PartialUser(id=1, name="Jane Smith", email="jane@example.com")
        partial = PartialAssignment(user=user, regDate="2025-02-15T12:30:00.000Z")

        repr_str = repr(partial)

        assert "PartialAssignment" in repr_str
        assert "Jane Smith" in repr_str
        assert "2025-02-15T12:30:00.000Z" in repr_str

    def test_partial_assignment_convert_to_full(self):
        """Test converting PartialAssignment to full Assignment."""
        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        partial = PartialAssignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        # Convert to full Assignment
        full = Assignment(**partial.model_dump())

        assert full.user.id == partial.user.id
        assert full.user.name == partial.user.name
        assert full.regDate == partial.regDate
        assert isinstance(full, Assignment)

    def test_partial_assignment_with_role(self):
        """Test PartialAssignment with user role data."""
        user = PartialUser(
            id=1,
            name="John Doe",
            email="john@example.com",
            role={"id": 5, "name": "Sales Manager"},
        )
        partial = PartialAssignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        assert partial.user.role is not None
        assert partial.user.role["id"] == 5
        assert partial.user.role["name"] == "Sales Manager"


class TestAssignmentIntegration:
    """Integration tests for Assignment with other models."""

    def test_assignment_in_company_context(self):
        """Test Assignment as it would appear in a Company object."""
        # Simulate API response structure
        company_data = {
            "assigned": {
                "user": {
                    "id": 10,
                    "name": "Sarah Johnson",
                    "email": "sarah@example.com",
                    "role": {"id": 3, "name": "Account Manager"},
                },
                "regDate": "2025-01-15T09:00:00.000Z",
            }
        }

        # Parse the assignment
        assignment = Assignment(**company_data["assigned"])

        assert assignment.user.id == 10
        assert assignment.user.name == "Sarah Johnson"
        assert assignment.user.email == "sarah@example.com"
        assert assignment.user.role["id"] == 3
        assert assignment.regDate == "2025-01-15T09:00:00.000Z"

    def test_assignment_serialization(self):
        """Test serializing Assignment back to dict."""
        user = PartialUser(
            id=1,
            name="John Doe",
            email="john@example.com",
            role={"id": 5, "name": "Sales Rep"},
        )
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        # Serialize to dict
        data = assignment.model_dump()

        assert data["user"]["id"] == 1
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["email"] == "john@example.com"
        assert data["user"]["role"]["id"] == 5
        assert data["regDate"] == "2025-01-01T00:00:00.000Z"
        assert data["id"] == 0

    def test_assignment_json_serialization(self):
        """Test JSON serialization of Assignment."""
        import json

        user = PartialUser(id=1, name="John Doe", email="john@example.com")
        assignment = Assignment(user=user, regDate="2025-01-01T00:00:00.000Z")

        # Serialize to JSON
        json_str = assignment.model_dump_json()
        data = json.loads(json_str)

        assert data["user"]["id"] == 1
        assert data["user"]["name"] == "John Doe"
        assert data["regDate"] == "2025-01-01T00:00:00.000Z"

    def test_assignment_extra_fields_allowed(self):
        """Test that extra fields from API are allowed."""
        data = {
            "user": {"id": 1, "name": "John Doe", "email": "john@example.com"},
            "regDate": "2025-01-01T00:00:00.000Z",
            "extraField": "some_value",  # Extra field not in model
        }

        # Should not raise (extra="allow" in base config)
        assignment = Assignment(**data)

        assert assignment.user.id == 1
        assert assignment.regDate == "2025-01-01T00:00:00.000Z"
