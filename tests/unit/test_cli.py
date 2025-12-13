"""
Tests for CLI code generation.

Tests the generate-model command and helper functions.
"""

from upsales.cli import (
    _analyze_field_requirements,
    _generate_field_line,
    _python_type_from_value,
)


def test_python_type_from_value():
    """Test type inference from JSON values."""
    assert _python_type_from_value(123) == ("int", "")
    assert _python_type_from_value(123.45) == ("float", "")
    assert _python_type_from_value("text") == ("str", "")
    assert _python_type_from_value(True) == ("bool", "")
    assert _python_type_from_value(None) == ("Any", "  # Was None in samples")


def test_python_type_from_list():
    """Test type inference from lists."""
    assert _python_type_from_value([]) == ("list[Any]", "")
    assert _python_type_from_value([1, 2, 3]) == ("list[int]", "")
    assert _python_type_from_value(["a", "b"]) == ("list[str]", "")


def test_python_type_from_dict():
    """Test type inference from dicts."""
    assert _python_type_from_value({}) == ("dict[str, Any]", "")
    assert _python_type_from_value({"key": "value"}) == ("dict[str, Any]", "")


def test_python_type_from_nested_object():
    """Test detection of nested objects."""
    nested = {"id": 1, "name": "Test"}
    python_type, comment = _python_type_from_value(nested)

    assert python_type == "dict[str, Any]  # Has id+name - consider Partial model"
    assert "consider Partial model" in python_type


def test_analyze_field_requirements_all_required():
    """Test field analysis when all fields are required."""
    objects = [
        {"id": 1, "name": "User 1", "email": "user1@test.com"},
        {"id": 2, "name": "User 2", "email": "user2@test.com"},
        {"id": 3, "name": "User 3", "email": "user3@test.com"},
    ]

    analysis = _analyze_field_requirements(objects)

    # All fields should be required
    assert analysis["id"]["is_required"] is True
    assert analysis["name"]["is_required"] is True
    assert analysis["email"]["is_required"] is True

    # Check counts
    assert analysis["id"]["present_count"] == 3
    assert analysis["id"]["non_null_count"] == 3
    assert analysis["id"]["total_count"] == 3


def test_analyze_field_requirements_with_nulls():
    """Test field analysis when some fields are null."""
    objects = [
        {"id": 1, "name": "User 1", "title": "Manager"},
        {"id": 2, "name": "User 2", "title": None},  # ← null
        {"id": 3, "name": "User 3", "title": "Developer"},
    ]

    analysis = _analyze_field_requirements(objects)

    # id and name are required (never null)
    assert analysis["id"]["is_required"] is True
    assert analysis["name"]["is_required"] is True

    # title is optional (null in some)
    assert analysis["title"]["is_required"] is False
    assert analysis["title"]["present_count"] == 3
    assert analysis["title"]["non_null_count"] == 2  # Only 2 non-null


def test_analyze_field_requirements_with_missing():
    """Test field analysis when some fields are missing."""
    objects = [
        {"id": 1, "name": "User 1", "email": "user1@test.com"},
        {"id": 2, "name": "User 2"},  # ← email missing
        {"id": 3, "name": "User 3", "email": "user3@test.com"},
    ]

    analysis = _analyze_field_requirements(objects)

    # email is optional (missing in some)
    assert analysis["email"]["is_required"] is False
    assert analysis["email"]["present_count"] == 2
    assert analysis["email"]["total_count"] == 3


def test_analyze_field_requirements_empty_list():
    """Test field analysis with empty list."""
    objects = []

    analysis = _analyze_field_requirements(objects)

    assert analysis == {}


def test_generate_field_line_required():
    """Test field line generation for required field."""
    field_info = {
        "sample_value": "Test Name",
        "is_required": True,
        "present_count": 10,
        "non_null_count": 10,
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("name", field_info)

    assert field_line == "    name: str"
    assert "Present in 100% (10/10)" in comment
    assert "null" not in comment  # No null mention for required fields


def test_generate_field_line_optional_with_nulls():
    """Test field line generation for optional field (null in some)."""
    field_info = {
        "sample_value": "Some Title",
        "is_required": False,
        "present_count": 10,
        "non_null_count": 7,  # 3 are null
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("userTitle", field_info)

    assert field_line == "    userTitle: str | None = None"
    assert "Present in 100% (10/10)" in comment
    assert "null in 3" in comment  # Shows why it's optional!


def test_generate_field_line_optional_missing():
    """Test field line generation for optional field (missing in some)."""
    field_info = {
        "sample_value": "Description",
        "is_required": False,
        "present_count": 5,
        "non_null_count": 5,
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("description", field_info)

    assert field_line == "    description: str | None = None"
    assert "Present in 50% (5/10)" in comment


def test_generate_field_line_custom_field():
    """Test custom field always gets special handling."""
    field_info = {
        "sample_value": [{"fieldId": 11, "value": "test"}],
        "is_required": True,  # Even if "required"
        "present_count": 10,
        "non_null_count": 10,
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("custom", field_info)

    # Custom field always gets default_factory
    assert field_line == "    custom: list[dict] = Field(default_factory=list)"


def test_generate_field_line_list_required():
    """Test list field that's required."""
    field_info = {
        "sample_value": ["tag1", "tag2"],
        "is_required": True,
        "present_count": 10,
        "non_null_count": 10,
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("tags", field_info)

    assert field_line == "    tags: list[str] = Field(default_factory=list)"


def test_generate_field_line_dict_optional():
    """Test dict field that's optional."""
    field_info = {
        "sample_value": {"id": 1, "name": "Role"},
        "is_required": False,
        "present_count": 10,
        "non_null_count": 8,
        "total_count": 10,
    }

    field_line, comment = _generate_field_line("role", field_info)

    # role field with id+name is detected as PartialRole
    assert field_line == "    role: PartialRole | None = None"
    assert "null in 2" in comment
    assert "TODO: from upsales.models" in comment


def test_field_analysis_real_scenario():
    """Test complete field analysis with mixed data."""
    objects = [
        {
            "id": 1,
            "name": "User 1",
            "email": "user1@test.com",
            "title": "Manager",
            "role": {"id": 1, "name": "Admin"},
            "custom": [],
        },
        {
            "id": 2,
            "name": "User 2",
            "email": "user2@test.com",
            "title": None,  # ← null
            "role": None,  # ← null
            "custom": [],
        },
        {
            "id": 3,
            "name": "User 3",
            "email": "user3@test.com",
            # title missing
            "role": {"id": 2, "name": "User"},
            "custom": [{"fieldId": 11, "value": "test"}],
        },
    ]

    analysis = _analyze_field_requirements(objects)

    # id, name, email, custom: required (always present and non-null)
    assert analysis["id"]["is_required"] is True
    assert analysis["name"]["is_required"] is True
    assert analysis["email"]["is_required"] is True
    assert analysis["custom"]["is_required"] is True

    # title: optional (null in one, missing in one)
    assert analysis["title"]["is_required"] is False
    assert analysis["title"]["present_count"] == 2
    assert analysis["title"]["non_null_count"] == 1

    # role: optional (null in one)
    assert analysis["role"]["is_required"] is False
    assert analysis["role"]["present_count"] == 3
    assert analysis["role"]["non_null_count"] == 2


def test_comment_format_consistency():
    """Test that comments follow consistent format."""
    # Required field - no null mention
    required_field = {
        "sample_value": "test",
        "is_required": True,
        "present_count": 5,
        "non_null_count": 5,
        "total_count": 5,
    }

    _, comment = _generate_field_line("name", required_field)
    assert comment == "  # Present in 100% (5/5)"

    # Optional field with nulls - shows null count
    optional_field = {
        "sample_value": "test",
        "is_required": False,
        "present_count": 5,
        "non_null_count": 3,
        "total_count": 5,
    }

    _, comment = _generate_field_line("title", optional_field)
    assert comment == "  # Present in 100% (5/5), null in 2"
