"""
Reusable validators for Upsales API models.

Uses Pydantic v2 functional validators with Annotated types for consistent
validation across all models. Define validators once, use everywhere.

Example:
    >>> from upsales.validators import BinaryFlag, CustomFieldsList, NonEmptyStr
    >>> from pydantic import BaseModel
    >>>
    >>> class User(BaseModel):
    ...     name: NonEmptyStr
    ...     administrator: BinaryFlag = 0
    ...     custom: CustomFieldsList = []
"""

from typing import Annotated, Any

from pydantic import BeforeValidator


def validate_custom_fields_structure(v: Any) -> list[dict[str, Any]]:
    """
    Validate Upsales custom fields structure.

    Ensures each custom field has required 'fieldId' and proper structure.
    This validator is used across all models that support custom fields.

    Args:
        v: List of custom field dicts from API.

    Returns:
        Validated list of custom fields.

    Raises:
        ValueError: If structure is invalid or fieldId is missing.

    Example:
        >>> fields = [{"fieldId": 11, "value": "test"}]
        >>> validate_custom_fields_structure(fields)
        [{'fieldId': 11, 'value': 'test'}]

        >>> validate_custom_fields_structure("not a list")
        Traceback (most recent call last):
        ...
        ValueError: custom must be a list, got <class 'str'>

        >>> validate_custom_fields_structure([{"value": "test"}])
        Traceback (most recent call last):
        ...
        ValueError: Custom field missing 'fieldId': {'value': 'test'}
    """
    if not isinstance(v, list):
        raise ValueError(f"custom must be a list, got {type(v)}")

    for item in v:
        if not isinstance(item, dict):
            raise ValueError(f"Custom field item must be dict, got {type(item)}: {item}")
        if "fieldId" not in item:
            raise ValueError(f"Custom field missing 'fieldId': {item}")
        if not isinstance(item["fieldId"], int):
            raise ValueError(f"fieldId must be int, got {type(item['fieldId'])}: {item['fieldId']}")

    return v


def validate_binary_flag(v: Any) -> int:
    """
    Validate binary flag (0 or 1).

    Used for fields like 'administrator', 'active', 'hasDiscount' where
    Upsales API uses 0/1 integers as boolean flags.

    Args:
        v: Integer value to validate.

    Returns:
        Validated integer (0 or 1).

    Raises:
        ValueError: If value is not 0 or 1, or if it's a boolean.

    Example:
        >>> validate_binary_flag(0)
        0
        >>> validate_binary_flag(1)
        1
        >>> validate_binary_flag(2)
        Traceback (most recent call last):
        ...
        ValueError: Binary flag must be 0 or 1, got 2
        >>> validate_binary_flag("1")
        Traceback (most recent call last):
        ...
        ValueError: Binary flag must be int, got <class 'str'>
        >>> validate_binary_flag(True)
        Traceback (most recent call last):
        ...
        ValueError: Binary flag must be int (not bool), got <class 'bool'>
    """
    # Explicitly reject booleans (bool is subclass of int in Python)
    if isinstance(v, bool):
        raise ValueError(f"Binary flag must be int (not bool), got {type(v)}")
    if not isinstance(v, int):
        raise ValueError(f"Binary flag must be int, got {type(v)}")
    if v not in (0, 1):
        raise ValueError(f"Binary flag must be 0 or 1, got {v}")
    return v


def validate_non_empty_string(v: Any) -> str:
    """
    Validate and clean non-empty string.

    Strips whitespace and ensures the string is not empty. Useful for
    required string fields like names, emails, etc.

    Args:
        v: String value to validate.

    Returns:
        Stripped string.

    Raises:
        ValueError: If empty after stripping or not a string.

    Example:
        >>> validate_non_empty_string("  test  ")
        'test'
        >>> validate_non_empty_string("test")
        'test'
        >>> validate_non_empty_string("   ")
        Traceback (most recent call last):
        ...
        ValueError: String cannot be empty or whitespace-only
        >>> validate_non_empty_string("")
        Traceback (most recent call last):
        ...
        ValueError: String cannot be empty or whitespace-only
        >>> validate_non_empty_string(123)
        Traceback (most recent call last):
        ...
        ValueError: Must be string, got <class 'int'>
    """
    if not isinstance(v, str):
        raise ValueError(f"Must be string, got {type(v)}")
    stripped = v.strip()
    if not stripped:
        raise ValueError("String cannot be empty or whitespace-only")
    return stripped


def validate_email(v: Any) -> str:
    """
    Validate and normalize email address.

    Performs basic validation (must contain '@') and normalizes by
    converting to lowercase and stripping whitespace.

    Args:
        v: Email string to validate.

    Returns:
        Normalized email (lowercase, stripped).

    Raises:
        ValueError: If email format is invalid.

    Example:
        >>> validate_email("user@example.com")
        'user@example.com'
        >>> validate_email("  User@Example.COM  ")
        'user@example.com'
        >>> validate_email("invalid-email")
        Traceback (most recent call last):
        ...
        ValueError: Email must contain '@': invalid-email
        >>> validate_email("")
        Traceback (most recent call last):
        ...
        ValueError: Email cannot be empty
        >>> validate_email(123)
        Traceback (most recent call last):
        ...
        ValueError: Email must be string, got <class 'int'>
    """
    if not isinstance(v, str):
        raise ValueError(f"Email must be string, got {type(v)}")

    stripped = v.strip()
    if not stripped:
        raise ValueError("Email cannot be empty")

    if "@" not in stripped:
        raise ValueError(f"Email must contain '@': {stripped}")

    return stripped.lower()


def validate_positive_int(v: Any) -> int:
    """
    Validate positive integer (>= 0).

    Useful for counts, IDs, and other non-negative integer fields.

    Args:
        v: Integer value to validate.

    Returns:
        Validated positive integer.

    Raises:
        ValueError: If not an integer or negative.

    Example:
        >>> validate_positive_int(0)
        0
        >>> validate_positive_int(42)
        42
        >>> validate_positive_int(-1)
        Traceback (most recent call last):
        ...
        ValueError: Must be non-negative integer, got -1
        >>> validate_positive_int("10")
        Traceback (most recent call last):
        ...
        ValueError: Must be integer, got <class 'str'>
    """
    if not isinstance(v, int):
        raise ValueError(f"Must be integer, got {type(v)}")
    if v < 0:
        raise ValueError(f"Must be non-negative integer, got {v}")
    return v


# Reusable type aliases using Annotated + BeforeValidator
# Use these in model field definitions for consistent validation

CustomFieldsList = Annotated[
    list[dict[str, Any]],
    BeforeValidator(validate_custom_fields_structure),
]
"""
Type alias for Upsales custom fields list with validation.

Ensures each custom field has proper structure with required 'fieldId'.
Use this for any model's 'custom' field.

Example:
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     custom: CustomFieldsList = []
"""

BinaryFlag = Annotated[
    int,
    BeforeValidator(validate_binary_flag),
]
"""
Type alias for binary flag (0 or 1) with validation.

Use for fields like 'administrator', 'active', 'hasDiscount', etc.

Example:
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     administrator: BinaryFlag = 0
    ...     active: BinaryFlag = 1
"""

NonEmptyStr = Annotated[
    str,
    BeforeValidator(validate_non_empty_string),
]
"""
Type alias for non-empty string with whitespace stripping.

Use for required string fields that cannot be empty.

Example:
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     name: NonEmptyStr
    ...     email: NonEmptyStr
"""

EmailStr = Annotated[
    str,
    BeforeValidator(validate_email),
]
"""
Type alias for email with validation and normalization.

Validates basic email format and normalizes to lowercase.

Example:
    >>> from pydantic import BaseModel
    >>> class User(BaseModel):
    ...     email: EmailStr
"""

PositiveInt = Annotated[
    int,
    BeforeValidator(validate_positive_int),
]
"""
Type alias for positive integer (>= 0) with validation.

Use for counts, IDs, and other non-negative values.

Example:
    >>> from pydantic import BaseModel
    >>> class Product(BaseModel):
    ...     stock_count: PositiveInt = 0
"""


def validate_percentage(v: Any) -> int:
    """
    Validate percentage value (0-100).

    Used for probability, completion, progress fields that represent
    percentages in Upsales API. Range is 0-100 inclusive.

    Args:
        v: Integer value to validate.

    Returns:
        Validated percentage (0-100).

    Raises:
        ValueError: If not an integer or outside 0-100 range.

    Example:
        >>> validate_percentage(0)
        0
        >>> validate_percentage(1)
        1
        >>> validate_percentage(50)
        50
        >>> validate_percentage(100)
        100
        >>> validate_percentage(101)
        Traceback (most recent call last):
        ...
        ValueError: Percentage must be between 0 and 100, got 101
        >>> validate_percentage("50")
        Traceback (most recent call last):
        ...
        ValueError: Percentage must be an integer, got <class 'str'>
    """
    if not isinstance(v, int) or isinstance(v, bool):
        raise ValueError(f"Percentage must be an integer, got {type(v)}")
    if v < 0 or v > 100:
        raise ValueError(f"Percentage must be between 0 and 100, got {v}")
    return v


Percentage = Annotated[
    int,
    BeforeValidator(validate_percentage),
]
"""
Type alias for percentage (0-100) with validation.

Use for probability, completion, progress fields that are percentages.
Allows 0 for stages like "Lost" or "Cancelled" with 0% probability.

Example:
    >>> from pydantic import BaseModel
    >>> class OrderStage(BaseModel):
    ...     probability: Percentage = Field(description="Win probability 0-100")
    >>> class Opportunity(BaseModel):
    ...     probability: Percentage = 50
    ...     completion: Percentage = 75
"""
