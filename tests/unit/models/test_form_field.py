"""
Unit tests for FormField and PartialFormField models.

Tests creation, validation, properties, and error handling for form field models.
"""

import pytest
from pydantic import ValidationError

from upsales.models.form_field import FormField, PartialFormField


class TestFormField:
    """Tests for the FormField model."""

    def test_create_minimal(self):
        """Test creating a FormField with minimal required fields."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.firstname",
            title="Förnamn",
            datatype="text",
        )
        assert field.id == 1
        assert field.formId == 7
        assert field.name == "Contact.firstname"
        assert field.title == "Förnamn"
        assert field.datatype == "text"
        assert field.sort == 0
        assert field.required == 0
        assert field.options == ""
        assert field.placeholder == ""
        assert field.info is None
        assert field.language is None

    def test_create_full(self):
        """Test creating a FormField with all fields."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.email",
            title="Email Address",
            datatype="email",
            sort=2,
            required=1,
            options="",
            placeholder="your@email.com",
            info="Enter your email address",
            language="en",
        )
        assert field.id == 1
        assert field.formId == 7
        assert field.name == "Contact.email"
        assert field.title == "Email Address"
        assert field.datatype == "email"
        assert field.sort == 2
        assert field.required == 1
        assert field.options == ""
        assert field.placeholder == "your@email.com"
        assert field.info == "Enter your email address"
        assert field.language == "en"

    def test_create_select_field_with_options(self):
        """Test creating a select field with options."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.country",
            title="Country",
            datatype="select",
            options="Sweden,Norway,Denmark,Finland",
        )
        assert field.datatype == "select"
        assert field.options == "Sweden,Norway,Denmark,Finland"

    def test_is_required_property(self):
        """Test is_required computed property."""
        optional_field = FormField(
            id=1,
            formId=7,
            name="Contact.phone",
            title="Phone",
            datatype="text",
            required=0,
        )
        assert optional_field.required == 0
        assert optional_field.is_required is False

        required_field = FormField(
            id=2,
            formId=7,
            name="Contact.email",
            title="Email",
            datatype="email",
            required=1,
        )
        assert required_field.required == 1
        assert required_field.is_required is True

    def test_name_validation_non_empty(self):
        """Test that name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1,
                formId=7,
                name="",
                title="Title",
                datatype="text",
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("name",)
        assert "empty" in error["msg"].lower()

    def test_name_validation_whitespace_only(self):
        """Test that name cannot be whitespace only."""
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1,
                formId=7,
                name="   ",
                title="Title",
                datatype="text",
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("name",)
        assert "empty" in error["msg"].lower()

    def test_name_strips_whitespace(self):
        """Test that name strips leading/trailing whitespace."""
        field = FormField(
            id=1,
            formId=7,
            name="  Contact.firstname  ",
            title="Title",
            datatype="text",
        )
        assert field.name == "Contact.firstname"

    def test_title_validation_non_empty(self):
        """Test that title cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1,
                formId=7,
                name="Contact.name",
                title="",
                datatype="text",
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("title",)
        assert "empty" in error["msg"].lower()

    def test_title_strips_whitespace(self):
        """Test that title strips leading/trailing whitespace."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.name",
            title="  Form Title  ",
            datatype="text",
        )
        assert field.title == "Form Title"

    def test_datatype_validation_non_empty(self):
        """Test that datatype cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1,
                formId=7,
                name="Contact.name",
                title="Title",
                datatype="",
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("datatype",)
        assert "empty" in error["msg"].lower()

    def test_datatype_strips_whitespace(self):
        """Test that datatype strips leading/trailing whitespace."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.name",
            title="Title",
            datatype="  text  ",
        )
        assert field.datatype == "text"

    def test_required_binary_flag(self):
        """Test that required accepts only 0 or 1."""
        # Valid values
        field_0 = FormField(
            id=1, formId=7, name="Contact.name", title="Title", datatype="text", required=0
        )
        assert field_0.required == 0

        field_1 = FormField(
            id=1, formId=7, name="Contact.name", title="Title", datatype="text", required=1
        )
        assert field_1.required == 1

        # Invalid values
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1, formId=7, name="Contact.name", title="Title", datatype="text", required=2
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("required",)
        assert "0 or 1" in error["msg"]

        # Boolean rejected (must be int)
        with pytest.raises(ValidationError) as exc_info:
            FormField(
                id=1,
                formId=7,
                name="Contact.name",
                title="Title",
                datatype="text",
                required=True,
            )
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("required",)
        assert "bool" in error["msg"].lower()

    def test_id_frozen(self):
        """Test that id cannot be changed after creation."""
        field = FormField(
            id=1,
            formId=7,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        with pytest.raises(ValidationError) as exc_info:
            field.id = 999
        assert "frozen" in str(exc_info.value).lower()

    def test_edit_not_implemented(self):
        """Test that edit() raises NotImplementedError."""
        import asyncio

        field = FormField(
            id=1,
            formId=7,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        with pytest.raises(NotImplementedError) as exc_info:
            asyncio.run(field.edit(title="New Title"))
        assert "cannot be edited independently" in str(exc_info.value).lower()
        assert "parent form" in str(exc_info.value).lower()

    def test_repr(self):
        """Test string representation."""
        field = FormField(
            id=123,
            formId=7,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        assert repr(field) == "<FormField id=123>"

    def test_common_datatypes(self):
        """Test common form field datatypes."""
        datatypes = ["text", "email", "number", "select", "textarea", "checkbox", "radio", "date"]

        for datatype in datatypes:
            field = FormField(
                id=1,
                formId=7,
                name=f"Contact.field_{datatype}",
                title=f"Test {datatype}",
                datatype=datatype,
            )
            assert field.datatype == datatype

    def test_sort_order(self):
        """Test sort field for ordering."""
        field1 = FormField(
            id=1, formId=7, name="Contact.name", title="Name", datatype="text", sort=1
        )
        field2 = FormField(
            id=2, formId=7, name="Contact.email", title="Email", datatype="email", sort=2
        )
        field3 = FormField(
            id=3, formId=7, name="Contact.phone", title="Phone", datatype="text", sort=3
        )

        assert field1.sort < field2.sort < field3.sort

    def test_localized_fields(self):
        """Test language field for localization."""
        en_field = FormField(
            id=1,
            formId=7,
            name="Contact.name",
            title="Name",
            datatype="text",
            language="en",
        )
        assert en_field.language == "en"

        sv_field = FormField(
            id=2,
            formId=7,
            name="Contact.name",
            title="Namn",
            datatype="text",
            language="sv",
        )
        assert sv_field.language == "sv"


class TestPartialFormField:
    """Tests for the PartialFormField model."""

    def test_create_minimal(self):
        """Test creating a PartialFormField with required fields."""
        partial = PartialFormField(
            id=1,
            name="Contact.firstname",
            title="Förnamn",
            datatype="text",
        )
        assert partial.id == 1
        assert partial.name == "Contact.firstname"
        assert partial.title == "Förnamn"
        assert partial.datatype == "text"

    def test_fetch_full_not_implemented(self):
        """Test that fetch_full() raises NotImplementedError."""
        import asyncio

        partial = PartialFormField(
            id=1,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        with pytest.raises(NotImplementedError) as exc_info:
            asyncio.run(partial.fetch_full())
        assert "cannot be fetched independently" in str(exc_info.value).lower()
        assert "parent form" in str(exc_info.value).lower()

    def test_edit_not_implemented(self):
        """Test that edit() raises NotImplementedError."""
        import asyncio

        partial = PartialFormField(
            id=1,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        with pytest.raises(NotImplementedError) as exc_info:
            asyncio.run(partial.edit(title="New Title"))
        assert "cannot be edited independently" in str(exc_info.value).lower()
        assert "parent form" in str(exc_info.value).lower()

    def test_repr(self):
        """Test string representation."""
        partial = PartialFormField(
            id=456,
            name="Contact.email",
            title="Email",
            datatype="email",
        )
        assert repr(partial) == "<PartialFormField id=456>"

    def test_all_fields_optional_strings(self):
        """Test that all string fields are optional in partial model."""
        # Only id is required
        partial = PartialFormField(
            id=1,
            name="Contact.name",
            title="Title",
            datatype="text",
        )
        assert partial.id == 1
        assert partial.name == "Contact.name"
