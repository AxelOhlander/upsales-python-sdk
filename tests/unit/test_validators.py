"""
Tests for reusable Pydantic v2 validators.

Tests all validator functions and Annotated type aliases to ensure
proper validation and error messages.
"""

import pytest
from pydantic import BaseModel, ValidationError

from upsales.validators import (
    BinaryFlag,
    CustomFieldsList,
    EmailStr,
    NonEmptyStr,
    Percentage,
    PositiveInt,
    validate_binary_flag,
    validate_custom_fields_structure,
    validate_email,
    validate_non_empty_string,
    validate_positive_int,
)


class TestCustomFieldsValidator:
    """Test custom fields structure validation."""

    def test_valid_custom_fields(self):
        """Test valid custom fields pass validation."""
        fields = [
            {"fieldId": 11, "value": "test"},
            {"fieldId": 12, "valueInteger": 42},
            {"fieldId": 13, "valueDate": "2023-01-01"},
        ]
        result = validate_custom_fields_structure(fields)
        assert result == fields

    def test_empty_list(self):
        """Test empty list is valid."""
        result = validate_custom_fields_structure([])
        assert result == []

    def test_not_a_list(self):
        """Test non-list input raises ValueError."""
        with pytest.raises(ValueError, match="custom must be a list"):
            validate_custom_fields_structure("not a list")

        with pytest.raises(ValueError, match="custom must be a list"):
            validate_custom_fields_structure({"fieldId": 11})

    def test_item_not_dict(self):
        """Test non-dict item raises ValueError."""
        with pytest.raises(ValueError, match="Custom field item must be dict"):
            validate_custom_fields_structure([11, 12])

        with pytest.raises(ValueError, match="Custom field item must be dict"):
            validate_custom_fields_structure(["string"])

    def test_missing_field_id(self):
        """Test missing fieldId raises ValueError."""
        with pytest.raises(ValueError, match="Custom field missing 'fieldId'"):
            validate_custom_fields_structure([{"value": "test"}])

    def test_invalid_field_id_type(self):
        """Test non-integer fieldId raises ValueError."""
        with pytest.raises(ValueError, match="fieldId must be int"):
            validate_custom_fields_structure([{"fieldId": "11"}])

        with pytest.raises(ValueError, match="fieldId must be int"):
            validate_custom_fields_structure([{"fieldId": 11.5}])


class TestBinaryFlagValidator:
    """Test binary flag (0/1) validation."""

    def test_valid_zero(self):
        """Test 0 is valid."""
        assert validate_binary_flag(0) == 0

    def test_valid_one(self):
        """Test 1 is valid."""
        assert validate_binary_flag(1) == 1

    def test_invalid_value(self):
        """Test values other than 0/1 raise ValueError."""
        with pytest.raises(ValueError, match="Binary flag must be 0 or 1"):
            validate_binary_flag(2)

        with pytest.raises(ValueError, match="Binary flag must be 0 or 1"):
            validate_binary_flag(-1)

        with pytest.raises(ValueError, match="Binary flag must be 0 or 1"):
            validate_binary_flag(10)

    def test_invalid_type(self):
        """Test non-integer types raise ValueError."""
        with pytest.raises(ValueError, match="Binary flag must be int"):
            validate_binary_flag("1")

        with pytest.raises(ValueError, match="Binary flag must be int"):
            validate_binary_flag(1.0)

        # Booleans are rejected explicitly (bool is subclass of int)
        with pytest.raises(ValueError, match="Binary flag must be int \\(not bool\\)"):
            validate_binary_flag(True)


class TestNonEmptyStringValidator:
    """Test non-empty string validation."""

    def test_valid_string(self):
        """Test valid non-empty strings."""
        assert validate_non_empty_string("test") == "test"
        assert validate_non_empty_string("hello world") == "hello world"

    def test_strips_whitespace(self):
        """Test whitespace is stripped."""
        assert validate_non_empty_string("  test  ") == "test"
        assert validate_non_empty_string("\ttest\n") == "test"
        assert validate_non_empty_string("  hello  world  ") == "hello  world"

    def test_empty_string(self):
        """Test empty string raises ValueError."""
        with pytest.raises(ValueError, match="String cannot be empty"):
            validate_non_empty_string("")

    def test_whitespace_only(self):
        """Test whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="String cannot be empty"):
            validate_non_empty_string("   ")

        with pytest.raises(ValueError, match="String cannot be empty"):
            validate_non_empty_string("\t\n")

    def test_invalid_type(self):
        """Test non-string types raise ValueError."""
        with pytest.raises(ValueError, match="Must be string"):
            validate_non_empty_string(123)

        with pytest.raises(ValueError, match="Must be string"):
            validate_non_empty_string(None)


class TestEmailValidator:
    """Test email validation and normalization."""

    def test_valid_email(self):
        """Test valid emails pass validation."""
        assert validate_email("user@example.com") == "user@example.com"
        assert validate_email("test@test.com") == "test@test.com"

    def test_normalizes_to_lowercase(self):
        """Test email is converted to lowercase."""
        assert validate_email("User@Example.COM") == "user@example.com"
        assert validate_email("TEST@TEST.COM") == "test@test.com"

    def test_strips_whitespace(self):
        """Test whitespace is stripped."""
        assert validate_email("  user@example.com  ") == "user@example.com"
        assert validate_email("\ttest@test.com\n") == "test@test.com"

    def test_missing_at_sign(self):
        """Test email without @ raises ValueError."""
        with pytest.raises(ValueError, match="Email must contain '@'"):
            validate_email("invalid-email")

        with pytest.raises(ValueError, match="Email must contain '@'"):
            validate_email("test.com")

    def test_empty_email(self):
        """Test empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            validate_email("")

        with pytest.raises(ValueError, match="Email cannot be empty"):
            validate_email("   ")

    def test_invalid_type(self):
        """Test non-string types raise ValueError."""
        with pytest.raises(ValueError, match="Email must be string"):
            validate_email(123)

        with pytest.raises(ValueError, match="Email must be string"):
            validate_email(None)


class TestPositiveIntValidator:
    """Test positive integer validation."""

    def test_valid_positive_int(self):
        """Test valid positive integers."""
        assert validate_positive_int(0) == 0
        assert validate_positive_int(1) == 1
        assert validate_positive_int(42) == 42
        assert validate_positive_int(1000000) == 1000000

    def test_negative_int(self):
        """Test negative integers raise ValueError."""
        with pytest.raises(ValueError, match="Must be non-negative integer"):
            validate_positive_int(-1)

        with pytest.raises(ValueError, match="Must be non-negative integer"):
            validate_positive_int(-100)

    def test_invalid_type(self):
        """Test non-integer types raise ValueError."""
        with pytest.raises(ValueError, match="Must be integer"):
            validate_positive_int("10")

        with pytest.raises(ValueError, match="Must be integer"):
            validate_positive_int(10.5)


class TestAnnotatedTypeAliases:
    """Test Annotated type aliases in Pydantic models."""

    def test_custom_fields_list_in_model(self):
        """Test CustomFieldsList works in Pydantic models."""

        class TestModel(BaseModel):
            custom: CustomFieldsList = []

        # Valid
        model = TestModel(custom=[{"fieldId": 11, "value": "test"}])
        assert model.custom == [{"fieldId": 11, "value": "test"}]

        # Empty list is valid
        model = TestModel(custom=[])
        assert model.custom == []

        # Invalid - missing fieldId
        with pytest.raises(ValidationError) as exc_info:
            TestModel(custom=[{"value": "test"}])
        assert "Custom field missing 'fieldId'" in str(exc_info.value)

    def test_binary_flag_in_model(self):
        """Test BinaryFlag works in Pydantic models."""

        class TestModel(BaseModel):
            active: BinaryFlag = 0
            administrator: BinaryFlag = 0

        # Valid
        model = TestModel(active=1, administrator=0)
        assert model.active == 1
        assert model.administrator == 0

        # Invalid - not 0 or 1
        with pytest.raises(ValidationError) as exc_info:
            TestModel(active=2)
        assert "Binary flag must be 0 or 1" in str(exc_info.value)

    def test_non_empty_str_in_model(self):
        """Test NonEmptyStr works in Pydantic models."""

        class TestModel(BaseModel):
            name: NonEmptyStr

        # Valid
        model = TestModel(name="John Doe")
        assert model.name == "John Doe"

        # Strips whitespace
        model = TestModel(name="  Jane  ")
        assert model.name == "Jane"

        # Invalid - empty string
        with pytest.raises(ValidationError) as exc_info:
            TestModel(name="")
        assert "String cannot be empty" in str(exc_info.value)

    def test_email_str_in_model(self):
        """Test EmailStr works in Pydantic models."""

        class TestModel(BaseModel):
            email: EmailStr

        # Valid
        model = TestModel(email="user@example.com")
        assert model.email == "user@example.com"

        # Normalizes to lowercase
        model = TestModel(email="User@Example.COM")
        assert model.email == "user@example.com"

        # Invalid - no @ sign
        with pytest.raises(ValidationError) as exc_info:
            TestModel(email="invalid")
        assert "Email must contain '@'" in str(exc_info.value)

    def test_positive_int_in_model(self):
        """Test PositiveInt works in Pydantic models."""

        class TestModel(BaseModel):
            count: PositiveInt = 0

        # Valid
        model = TestModel(count=42)
        assert model.count == 42

        # Zero is valid
        model = TestModel(count=0)
        assert model.count == 0

        # Invalid - negative
        with pytest.raises(ValidationError) as exc_info:
            TestModel(count=-1)
        assert "Must be non-negative integer" in str(exc_info.value)


class TestValidatorsIntegration:
    """Test validators working together in realistic models."""

    def test_user_like_model(self):
        """Test validators in a User-like model."""

        class User(BaseModel):
            name: NonEmptyStr
            email: EmailStr
            administrator: BinaryFlag = 0
            active: BinaryFlag = 1
            custom: CustomFieldsList = []

        # Valid user
        user = User(
            name="  John Doe  ",
            email="John@Example.COM",
            administrator=1,
            custom=[{"fieldId": 11, "value": "test"}],
        )

        assert user.name == "John Doe"  # Stripped
        assert user.email == "john@example.com"  # Normalized
        assert user.administrator == 1
        assert user.active == 1
        assert user.custom == [{"fieldId": 11, "value": "test"}]

    def test_product_like_model(self):
        """Test validators in a Product-like model."""

        class Product(BaseModel):
            name: NonEmptyStr
            stock_count: PositiveInt = 0
            active: BinaryFlag = 1
            custom: CustomFieldsList = []

        # Valid product
        product = Product(
            name="Widget",
            stock_count=100,
            active=1,
        )

        assert product.name == "Widget"
        assert product.stock_count == 100
        assert product.active == 1

        # Invalid - negative stock
        with pytest.raises(ValidationError):
            Product(name="Widget", stock_count=-1)


class TestPercentage:
    """Test Percentage validator (1-100 range)."""

    def test_percentage_valid_values(self):
        """Test valid percentage values."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            value: Percentage

        # Minimum
        model = TestModel(value=1)
        assert model.value == 1

        # Middle values
        model = TestModel(value=50)
        assert model.value == 50

        model = TestModel(value=75)
        assert model.value == 75

        # Maximum
        model = TestModel(value=100)
        assert model.value == 100

    def test_percentage_too_low(self):
        """Test that values below 0 raise ValueError."""
        from pydantic import BaseModel, ValidationError

        class TestModel(BaseModel):
            value: Percentage

        # Zero is now valid (for "Lost" stages with 0% probability)
        assert TestModel(value=0).value == 0

        # Negative should still raise
        with pytest.raises(ValidationError) as exc_info:
            TestModel(value=-1)
        assert "between 0 and 100" in str(exc_info.value)

    def test_percentage_too_high(self):
        """Test that values above 100 raise ValueError."""
        from pydantic import BaseModel, ValidationError

        class TestModel(BaseModel):
            value: Percentage

        with pytest.raises(ValidationError) as exc_info:
            TestModel(value=101)
        assert "between 0 and 100" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            TestModel(value=200)
        assert "between 0 and 100" in str(exc_info.value)

    def test_percentage_edge_cases(self):
        """Test boundary values."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            value: Percentage

        # Boundaries should work
        assert TestModel(value=0).value == 0  # Minimum boundary (0%)
        assert TestModel(value=1).value == 1  # Low boundary
        assert TestModel(value=100).value == 100  # Maximum boundary

    def test_percentage_with_default(self):
        """Test Percentage with default value."""
        from pydantic import BaseModel, Field

        class OrderStage(BaseModel):
            probability: Percentage = Field(default=50, description="Win probability")

        stage = OrderStage()
        assert stage.probability == 50

        stage = OrderStage(probability=75)
        assert stage.probability == 75

    def test_percentage_realistic_usage(self):
        """Test Percentage in realistic model."""
        from pydantic import BaseModel, Field

        class OrderStage(BaseModel):
            id: int
            name: str
            probability: Percentage = Field(description="Win probability 0-100")

        # Valid - regular stage
        stage = OrderStage(id=1, name="Qualified", probability=75)
        assert stage.probability == 75

        # Valid - "Lost" stage with 0%
        lost_stage = OrderStage(id=2, name="Lost", probability=0)
        assert lost_stage.probability == 0

        # Invalid: too high
        with pytest.raises(Exception) as exc_info:
            OrderStage(id=1, name="Test", probability=101)
        assert "between 0 and 100" in str(exc_info.value).lower()
