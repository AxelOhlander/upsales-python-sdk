"""
Form action models for Upsales API.

Form actions are always nested within Form objects (Form.actions) and don't
have their own endpoint. These are data models for type-safe access to form
action configurations like sending emails, creating tasks, etc.

Note:
    Form actions don't have edit() or fetch_full() methods since they're not
    standalone resources. They must be updated through their parent Form object.

Example:
    >>> form = await upsales.forms.get(1)
    >>> if form.actions:
    ...     action = form.actions[0]
    ...     print(f"Action: {action.action}")  # e.g., "SendEmail"
    ...     for prop in action.properties:
    ...         print(f"{prop.name}: {prop.value}")
    ...     # EmailTo: admin@company.com
    ...     # Subject: New form submission
"""

from typing import Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

from upsales.validators import NonEmptyStr


class FormActionProperty(PydanticBase):
    """
    Form action property model.

    Represents a single property within a form action, such as email recipient,
    subject line, or other action-specific configuration values.

    Example:
        >>> prop = FormActionProperty(name="EmailTo", value="admin@company.com")
        >>> prop.name
        'EmailTo'
        >>> prop.value
        'admin@company.com'
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    name: NonEmptyStr = Field(description="Property name (e.g., 'EmailTo', 'Subject')")
    value: str | None = Field(None, description="Property value")

    @computed_field
    @property
    def has_value(self) -> bool:
        """
        Check if property has a non-empty value.

        Returns:
            True if value is present and non-empty, False otherwise.

        Example:
            >>> prop.has_value
            True
        """
        return self.value is not None and self.value.strip() != ""

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize property to dict for API requests.

        Returns:
            Dict suitable for API requests, excluding computed fields.

        Example:
            >>> prop_dict = prop.to_dict()
            >>> # Returns: {'name': 'EmailTo', 'value': 'admin@company.com'}
        """
        return self.model_dump(
            mode="python",
            exclude={"has_value"},
            exclude_none=False,  # Include None values
        )

    def __repr__(self) -> str:
        """
        Return string representation of the property.

        Returns:
            String like "<FormActionProperty name=EmailTo>".
        """
        return f"<{self.__class__.__name__} name={self.name}>"


class FormAction(PydanticBase):
    """
    Form action model.

    Represents an action triggered when a form is submitted, such as sending
    an email notification or creating a task. Contains action type and
    configuration properties.

    Note:
        Form actions don't have their own API endpoint. They must be managed
        through parent Form objects.

    Example:
        >>> action = FormAction(
        ...     id=1,
        ...     action="SendEmail",
        ...     properties=[
        ...         {"name": "EmailTo", "value": "admin@company.com"},
        ...         {"name": "Subject", "value": "New form submission"}
        ...     ]
        ... )
        >>> action.action
        'SendEmail'
        >>> action.property_count
        2
        >>> action.get_property("EmailTo")
        'admin@company.com'
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    id: int = Field(description="Unique action ID")
    action: NonEmptyStr = Field(description="Action type (e.g., 'SendEmail', 'CreateTask')")
    properties: list[FormActionProperty] = Field(
        default=[], description="Action configuration properties"
    )

    @computed_field
    @property
    def property_count(self) -> int:
        """
        Get number of properties in this action.

        Returns:
            Number of properties.

        Example:
            >>> action.property_count
            2
        """
        return len(self.properties)

    @computed_field
    @property
    def has_properties(self) -> bool:
        """
        Check if action has any properties.

        Returns:
            True if properties list is not empty, False otherwise.

        Example:
            >>> action.has_properties
            True
        """
        return len(self.properties) > 0

    def get_property(self, name: str) -> str | None:
        """
        Get property value by name.

        Args:
            name: Property name to search for (case-sensitive).

        Returns:
            Property value if found, None otherwise.

        Example:
            >>> action.get_property("EmailTo")
            'admin@company.com'
            >>> action.get_property("NonExistent")
            None
        """
        for prop in self.properties:
            if prop.name == name:
                return prop.value
        return None

    def get_property_names(self) -> list[str]:
        """
        Get list of all property names.

        Returns:
            List of property names in order.

        Example:
            >>> action.get_property_names()
            ['EmailTo', 'Subject']
        """
        return [prop.name for prop in self.properties]

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize action to dict for API requests.

        Returns:
            Dict suitable for API requests, excluding computed fields.

        Example:
            >>> action_dict = action.to_dict()
            >>> # Returns: {'id': 1, 'action': 'SendEmail', 'properties': [...]}
        """
        return self.model_dump(
            mode="python",
            exclude={"property_count", "has_properties"},
            exclude_none=False,  # Include None values
        )

    def __repr__(self) -> str:
        """
        Return string representation of the action.

        Returns:
            String like "<FormAction id=1 action=SendEmail>".
        """
        return f"<{self.__class__.__name__} id={self.id} action={self.action}>"


class PartialFormAction(PydanticBase):
    """
    Partial form action model.

    Minimal form action information for nested responses where not all fields
    are guaranteed to be present. Use FormAction for complete action data.

    Note:
        PartialFormAction doesn't have fetch_full() or edit() methods since
        form actions are not standalone resources with their own endpoint.

    Example:
        >>> form = await upsales.forms.get(1)
        >>> for action in form.actions:
        ...     print(f"{action.id}: {action.action}")
        1: SendEmail
        2: CreateTask
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    id: int = Field(description="Unique action ID")
    action: str = Field(description="Action type (e.g., 'SendEmail', 'CreateTask')")
    properties: list[dict[str, Any]] = Field(
        default=[], description="Action configuration properties (raw dicts)"
    )

    @computed_field
    @property
    def property_count(self) -> int:
        """
        Get number of properties in this action.

        Returns:
            Number of properties.

        Example:
            >>> action.property_count
            2
        """
        return len(self.properties)

    def to_full(self) -> FormAction:
        """
        Convert partial action to full FormAction model.

        Returns:
            Full FormAction model with all available fields.

        Example:
            >>> partial = PartialFormAction(id=1, action="SendEmail", properties=[...])
            >>> full = partial.to_full()
            >>> full.property_count
            2
        """
        return FormAction(**self.model_dump())

    def __repr__(self) -> str:
        """
        Return string representation of the partial action.

        Returns:
            String like "<PartialFormAction id=1 action=SendEmail>".
        """
        return f"<{self.__class__.__name__} id={self.id} action={self.action}>"
