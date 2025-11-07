"""
Custom fields helper class for Upsales API.

Uses Python 3.13 native type hints throughout.

The Upsales API stores custom fields as a list of objects with fieldId
and value. This helper class provides dict-like access by field ID or alias.

Example:
    >>> custom = CustomFields([
    ...     {"fieldId": 11, "value": "test"},
    ...     {"fieldId": 12, "valueInteger": 123},
    ... ])
    >>> custom[11]  # Access by ID
    'test'
    >>> custom[11] = "new value"  # Update value
    >>> custom.to_api_format()  # Convert back for API
    [{'fieldId': 11, 'value': 'new value'}, {'fieldId': 12, 'value': None}]
"""

from typing import Any


class CustomFields:
    """
    Helper class for managing Upsales custom fields.

    Provides dict-like access to custom fields by field ID or alias.
    Handles the conversion between Upsales API format and a more
    Pythonic interface.

    Args:
        data: List of custom field dicts from the API.
        field_schema: Optional mapping of field aliases to field IDs.

    Attributes:
        _data: Internal storage of custom fields keyed by field ID.
        _schema: Mapping of aliases to field IDs for convenient access.

    Example:
        >>> # From API response
        >>> custom = CustomFields([
        ...     {"fieldId": 11, "value": "test", "valueInteger": None},
        ... ])
        >>>
        >>> # Access by ID
        >>> print(custom[11])
        'test'
        >>>
        >>> # Update value
        >>> custom[11] = "new value"
        >>>
        >>> # With schema for alias access
        >>> schema = {"MY_FIELD": 11}
        >>> custom = CustomFields([...], field_schema=schema)
        >>> custom["MY_FIELD"] = "value"
        >>>
        >>> # Convert back to API format
        >>> api_data = custom.to_api_format()

    Note:
        The Upsales API uses different value fields based on data type:
        - value: String values
        - valueInteger: Integer values
        - valueDate: Date values
        - valueArray: Array values

        This helper currently focuses on the 'value' field for simplicity.
    """

    def __init__(
        self,
        data: list[dict[str, Any]],
        field_schema: dict[int | str, int] | None = None,
    ) -> None:
        """
        Initialize custom fields helper.

        Args:
            data: List of custom field data from API response.
            field_schema: Optional mapping of field aliases to IDs for
                convenient access (e.g., {"MY_FIELD": 11}).
        """
        self._data: dict[int, dict[str, Any]] = {item["fieldId"]: item for item in data}
        self._schema: dict[int | str, int] = field_schema or {}

    def __getitem__(self, key: int | str) -> Any:
        """
        Get field value by ID or alias.

        Args:
            key: Field ID (int) or alias (str).

        Returns:
            The field value.

        Raises:
            KeyError: If field ID or alias not found.

        Example:
            >>> custom[11]  # By ID
            'value'
            >>> custom["MY_FIELD"]  # By alias (requires schema)
            'value'
        """
        field_id = self._resolve_key(key)

        # Check if field exists first
        if field_id not in self._data:
            raise KeyError(f"Custom field {key} (ID: {field_id}) not found")

        field_data = self._data[field_id]

        # Return the first non-None value field
        # Upsales uses different fields based on data type
        return (
            field_data.get("value")
            or field_data.get("valueInteger")
            or field_data.get("valueDate")
            or field_data.get("valueArray")
        )

    def __setitem__(self, key: int | str, value: Any) -> None:
        """
        Set field value by ID or alias.

        Args:
            key: Field ID (int) or alias (str).
            value: Value to set.

        Example:
            >>> custom[11] = "new value"
            >>> custom["MY_FIELD"] = "another value"
        """
        field_id = self._resolve_key(key)
        if field_id not in self._data:
            self._data[field_id] = {"fieldId": field_id}
        self._data[field_id]["value"] = value

    def __contains__(self, key: int | str) -> bool:
        """
        Check if field exists.

        Args:
            key: Field ID (int) or alias (str).

        Returns:
            True if field exists, False otherwise.

        Example:
            >>> 11 in custom
            True
            >>> "MY_FIELD" in custom
            True
        """
        try:
            field_id = self._resolve_key(key)
            return field_id in self._data
        except KeyError:
            return False

    def get(self, key: int | str, default: Any = None) -> Any:
        """
        Get field value with default fallback.

        Args:
            key: Field ID (int) or alias (str).
            default: Default value if field not found.

        Returns:
            Field value or default.

        Example:
            >>> custom.get(11, "default")
            'value'
            >>> custom.get(999, "default")
            'default'
        """
        try:
            return self[key]
        except KeyError:
            return default

    def _resolve_key(self, key: int | str) -> int:
        """
        Resolve field alias to field ID.

        Args:
            key: Field ID (int) or alias (str).

        Returns:
            Field ID (int).

        Raises:
            KeyError: If alias not found in schema.

        Example:
            >>> custom._resolve_key(11)  # Already an ID
            11
            >>> custom._resolve_key("MY_FIELD")  # Alias lookup
            11
        """
        if isinstance(key, int):
            return key
        if key in self._schema:
            return self._schema[key]
        raise KeyError(f"Unknown custom field alias: {key}")

    def to_api_format(self) -> list[dict[str, Any]]:
        """
        Convert custom fields back to Upsales API format.

        Returns:
            List of custom field dicts suitable for API requests.

        Example:
            >>> custom[11] = "test"
            >>> custom.to_api_format()
            [{'fieldId': 11, 'value': 'test'}]
        """
        return [
            {"fieldId": field_id, "value": data.get("value")}
            for field_id, data in self._data.items()
            if "value" in data
        ]

    def __repr__(self) -> str:
        """
        Return string representation of custom fields.

        Returns:
            String showing field IDs and their values.
        """
        fields = ", ".join(f"{fid}: {data.get('value')}" for fid, data in self._data.items())
        return f"<CustomFields({fields})>"
