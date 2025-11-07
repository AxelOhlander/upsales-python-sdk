"""
Unit tests for FormElement model.

Tests cover:
- Model creation and validation
- Property methods (is_enabled, is_text, is_image, text_content, image_src)
- Edit method behavior
- PartialFormElement functionality
"""

import pytest
from pydantic import ValidationError

from upsales.models.form_element import FormElement, PartialFormElement


class TestFormElementCreation:
    """Tests for FormElement creation and validation."""

    def test_create_text_element(self):
        """Test creating a text-type form element."""
        element = FormElement(
            id=1539688745297,
            type="text",
            value={"text": "<h2>Thank you!</h2>"},
            style={},
            enabled=True,
        )

        assert element.id == 1539688745297
        assert element.type == "text"
        assert element.value == {"text": "<h2>Thank you!</h2>"}
        assert element.style == {}
        assert element.enabled is True
        assert element.animation is None
        assert element.required is False

    def test_create_image_element(self):
        """Test creating an image-type form element."""
        element = FormElement(
            id=1625129300226,
            type="image",
            value={
                "src": "https://img.upsales.com/test.png",
                "opacity": 100,
                "shadow": True,
                "align": "center",
            },
            style={},
            enabled=True,
        )

        assert element.id == 1625129300226
        assert element.type == "image"
        assert element.value["src"] == "https://img.upsales.com/test.png"
        assert element.value["opacity"] == 100
        assert element.enabled is True

    def test_create_with_defaults(self):
        """Test creating element with default values."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        assert element.style == {}
        assert element.enabled is True
        assert element.animation is None
        assert element.required is False

    def test_create_with_animation(self):
        """Test creating element with animation."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
            animation="fadeIn",
        )

        assert element.animation == "fadeIn"

    def test_id_is_frozen(self):
        """Test that id field is frozen and cannot be modified."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        with pytest.raises(ValidationError) as exc_info:
            element.id = 9999999999999

        assert "frozen" in str(exc_info.value).lower()

    def test_id_is_required(self):
        """Test that id field is required."""
        with pytest.raises(ValidationError) as exc_info:
            FormElement(
                type="text",
                value={"text": "Test"},
            )

        assert "id" in str(exc_info.value).lower()

    def test_type_is_required(self):
        """Test that type field is required."""
        with pytest.raises(ValidationError) as exc_info:
            FormElement(
                id=1234567890123,
                value={"text": "Test"},
            )

        assert "type" in str(exc_info.value).lower()

    def test_value_is_required(self):
        """Test that value field is required."""
        with pytest.raises(ValidationError) as exc_info:
            FormElement(
                id=1234567890123,
                type="text",
            )

        assert "value" in str(exc_info.value).lower()


class TestFormElementProperties:
    """Tests for FormElement property methods."""

    def test_is_enabled_true(self):
        """Test is_enabled property when enabled=True."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
            enabled=True,
        )

        assert element.is_enabled is True

    def test_is_enabled_false(self):
        """Test is_enabled property when enabled=False."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
            enabled=False,
        )

        assert element.is_enabled is False

    def test_is_text_true(self):
        """Test is_text property for text-type element."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        assert element.is_text is True
        assert element.is_image is False

    def test_is_image_true(self):
        """Test is_image property for image-type element."""
        element = FormElement(
            id=1234567890123,
            type="image",
            value={"src": "https://example.com/image.png"},
        )

        assert element.is_image is True
        assert element.is_text is False

    def test_text_content_for_text_element(self):
        """Test text_content property for text-type element."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "<h2>Thank you!</h2>"},
        )

        assert element.text_content == "<h2>Thank you!</h2>"

    def test_text_content_for_non_text_element(self):
        """Test text_content property returns None for non-text element."""
        element = FormElement(
            id=1234567890123,
            type="image",
            value={"src": "https://example.com/image.png"},
        )

        assert element.text_content is None

    def test_text_content_missing_text_key(self):
        """Test text_content property when value doesn't have text key."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"other": "data"},
        )

        assert element.text_content is None

    def test_image_src_for_image_element(self):
        """Test image_src property for image-type element."""
        element = FormElement(
            id=1234567890123,
            type="image",
            value={"src": "https://example.com/image.png", "opacity": 100},
        )

        assert element.image_src == "https://example.com/image.png"

    def test_image_src_for_non_image_element(self):
        """Test image_src property returns None for non-image element."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        assert element.image_src is None

    def test_image_src_missing_src_key(self):
        """Test image_src property when value doesn't have src key."""
        element = FormElement(
            id=1234567890123,
            type="image",
            value={"opacity": 100},
        )

        assert element.image_src is None


class TestFormElementEdit:
    """Tests for FormElement edit method."""

    @pytest.mark.anyio
    async def test_edit_raises_runtime_error(self):
        """Test that edit method raises RuntimeError (no endpoint)."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        with pytest.raises(RuntimeError) as exc_info:
            await element.edit(type="image")

        assert "does not have a direct API endpoint" in str(exc_info.value)


class TestPartialFormElement:
    """Tests for PartialFormElement model."""

    def test_create_partial(self):
        """Test creating a PartialFormElement."""
        partial = PartialFormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        assert partial.id == 1234567890123
        assert partial.type == "text"
        assert partial.value == {"text": "Test"}

    def test_partial_required_fields(self):
        """Test that PartialFormElement requires id, type, and value."""
        with pytest.raises(ValidationError):
            PartialFormElement(
                id=1234567890123,
                type="text",
            )

    @pytest.mark.anyio
    async def test_fetch_full_raises_runtime_error(self):
        """Test that fetch_full raises RuntimeError (no endpoint)."""
        partial = PartialFormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        with pytest.raises(RuntimeError) as exc_info:
            await partial.fetch_full()

        assert "does not have a direct API endpoint" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_edit_raises_runtime_error(self):
        """Test that edit raises RuntimeError (no endpoint)."""
        partial = PartialFormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        with pytest.raises(RuntimeError) as exc_info:
            await partial.edit(type="image")

        assert "does not have a direct API endpoint" in str(exc_info.value)


class TestFormElementSerialization:
    """Tests for FormElement serialization."""

    def test_model_dump(self):
        """Test model serialization with model_dump."""
        element = FormElement(
            id=1539688745297,
            type="text",
            value={"text": "<h2>Thank you!</h2>"},
            style={},
            enabled=True,
            animation=None,
            required=False,
        )

        data = element.model_dump()

        assert data["id"] == 1539688745297
        assert data["type"] == "text"
        assert data["value"] == {"text": "<h2>Thank you!</h2>"}
        assert data["style"] == {}
        assert data["enabled"] is True
        assert data["animation"] is None
        assert data["required"] is False

    def test_model_dump_exclude_none(self):
        """Test model serialization excluding None values."""
        element = FormElement(
            id=1234567890123,
            type="text",
            value={"text": "Test"},
        )

        data = element.model_dump(exclude_none=True)

        assert "id" in data
        assert "type" in data
        assert "value" in data
        assert "animation" not in data  # None excluded


class TestFormElementRealWorldData:
    """Tests using real-world data patterns from API."""

    def test_swedish_thank_you_text(self):
        """Test with actual Swedish thank you message from API."""
        element = FormElement(
            id=1539688745297,
            type="text",
            value={
                "text": "<h2>Tack</h2><p>Ett mail med inloggningsuppgifter skickas till din mailadress!</p>"
            },
            style={},
            enabled=True,
            animation=None,
            required=False,
        )

        assert element.is_text is True
        assert (
            element.text_content
            == "<h2>Tack</h2><p>Ett mail med inloggningsuppgifter skickas till din mailadress!</p>"
        )

    def test_image_with_full_properties(self):
        """Test with actual image element from API."""
        element = FormElement(
            id=1625129300226,
            type="image",
            value={
                "src": "https://img.upsales.com/RfYkyVcwMfeI1jeLapbY6w==/images/demobolaget_white(1).png",
                "opacity": 100,
                "shadow": True,
                "align": "center",
            },
            style={},
            enabled=True,
            animation=None,
            required=False,
        )

        assert element.is_image is True
        assert "demobolaget_white" in element.image_src
        assert element.value["opacity"] == 100
        assert element.value["shadow"] is True
        assert element.value["align"] == "center"

    def test_minimal_text_element(self):
        """Test with minimal text element."""
        element = FormElement(
            id=1629188144579,
            type="text",
            value={"text": "\n<p>Tack!&nbsp;</p>\n"},
            style={},
            enabled=True,
            animation=None,
            required=False,
        )

        assert element.is_text is True
        assert "Tack!" in element.text_content
