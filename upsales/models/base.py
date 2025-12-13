"""
Base model classes for Upsales objects.

Uses Python 3.13 features:
- Native type hints (no typing imports needed)
- TYPE_CHECKING for forward references
- Mutable models with assignment validation
- TypedDict + Unpack for type-safe updates with IDE autocomplete

Example:
    >>> from typing import Unpack, TypedDict
    >>> from pydantic import Field
    >>>
    >>> class UserUpdateFields(TypedDict, total=False):
    ...     '''Fields available for updating a User.'''
    ...     name: str
    ...     email: str
    ...     administrator: int
    >>>
    >>> class User(BaseModel):
    ...     id: int = Field(frozen=True)
    ...     name: str
    ...     email: str
    ...     administrator: int
    ...
    ...     async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
    ...         '''Edit with full IDE autocomplete!'''
    ...         if not self._client:
    ...             raise RuntimeError("No client available")
    ...         return await self._client.users.update(
    ...             self.id,
    ...             **self.to_update_dict(**kwargs)
    ...         )
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from upsales.client import Upsales


class BaseModel(PydanticBase):
    """
    Base class for full Upsales API objects.

    All fields are guaranteed to be present when you receive a full object
    from the API. Subclasses represent complete API responses with all data.

    All models are mutable and validate assignments using Pydantic v2.
    Models can optionally hold a reference to the client for edit operations.

    Attributes:
        id: Unique identifier for the object.

    Example:
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        ...     administrator: int
        ...
        >>> user = User(id=1, name="John", email="john@example.com", administrator=0)
        >>> user.name = "Jane"  # Validated assignment
        >>> print(f"{user.id = }, {user.name = }")  # Python 3.12+ f-string debugging
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    id: int
    _client: "Upsales | None" = PrivateAttr(default=None)

    def __init__(self, **data: Any) -> None:
        """
        Initialize model with optional client reference.

        Args:
            **data: Model field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        self._client = client

    def to_update_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize model for update requests.

        Excludes read-only fields (marked with frozen=True) and private fields.
        Use this when you need to send the model state to an update endpoint.

        Args:
            **overrides: Additional fields to override in the output.

        Returns:
            Dict suitable for API update requests, with read-only fields removed.

        Example:
            >>> user = await client.users.get(1)
            >>> user.name = "Jane"
            >>> update_dict = user.to_update_dict()
            >>> # Returns: {'name': 'Jane', 'email': '...', ...}
            >>> # Excludes: id, created_at, updated_at (if frozen=True)
            >>>
            >>> # With overrides
            >>> update_dict = user.to_update_dict(active=0)

        Note:
            Mark read-only fields with Field(frozen=True) in your model:
            ```python
            from pydantic import Field

            class User(BaseModel):
                id: int = Field(frozen=True)  # Won't be in update dict
                name: str  # Will be in update dict
            ```
        """
        # Get all fields except private ones
        data = self.model_dump(exclude={"_client"})

        # Build set of frozen field names
        # Access model_fields from class, not instance (Pydantic v2.11+)
        frozen_fields = {
            field_name
            for field_name, field_info in self.__class__.model_fields.items()
            if field_info.frozen
        }

        # Remove frozen fields from data
        for field_name in frozen_fields:
            data.pop(field_name, None)

        # Apply overrides, but exclude frozen fields from overrides too
        for key, value in overrides.items():
            if key not in frozen_fields:
                data[key] = value

        return data

    def to_api_dict(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize model for API requests using Pydantic v2 optimized serialization.

        This method leverages Pydantic v2's Rust-based serialization for better
        performance. Automatically excludes frozen fields and uses field aliases.

        Args:
            **overrides: Additional fields to override in the output.

        Returns:
            Dict suitable for API requests with proper field names and values.

        Example:
            >>> user = await client.users.get(1)
            >>> user.name = "Jane"
            >>> api_data = user.to_api_dict()
            >>> # Returns: {'name': 'Jane', 'email': '...', ...}
            >>> # Excludes: id, created_at, updated_at (frozen fields)
            >>>
            >>> # With overrides
            >>> api_data = user.to_api_dict(active=0)

        Note:
            This method uses Pydantic v2's optimized serialization which is
            5-50x faster than v1 due to its Rust core.

            For backward compatibility, to_update_dict() remains available.
        """
        # Build set of frozen field names and exclude fields
        # Access model_fields from class, not instance (Pydantic v2.11+)
        frozen_fields = {
            field_name
            for field_name, field_info in self.__class__.model_fields.items()
            if field_info.frozen
        }

        # Also exclude computed fields from serialization
        computed_fields = set(self.__class__.model_computed_fields.keys())

        exclude_fields = frozen_fields | computed_fields | {"_client"}

        # Use Pydantic's optimized serialization
        # Note: exclude_unset=False to include all fields with defaults
        # Note: exclude_none=False to include None values (API may need them)
        data = self.model_dump(
            mode="python",  # Use 'python' mode to avoid computed field serialization issues
            exclude=exclude_fields,
            by_alias=True,  # Use field aliases for API compatibility
            exclude_unset=False,
            exclude_none=False,
        )

        # Apply overrides, but exclude frozen fields from overrides too
        for key, value in overrides.items():
            if key not in frozen_fields:
                data[key] = value

        return data

    def to_update_dict_minimal(self, **overrides: Any) -> dict[str, Any]:
        """
        Serialize only changed fields + required fields for updates.

        This minimizes the payload and reduces risk of edit conflicts when
        multiple users/integrations are updating the same object concurrently.

        Only includes:
        1. Fields explicitly passed in overrides (what you want to change)
        2. Fields in _required_update_fields (API requirements)

        Args:
            **overrides: Fields to update with new values.

        Returns:
            Minimal dict with only changed and required fields.

        Example:
            >>> stage = await client.order_stages.get(1)
            >>> # Only sends name + probability (required)
            >>> update_dict = stage.to_update_dict_minimal(name="New Name")
            >>> # Returns: {"name": "New Name", "probability": 50}
            >>> # Excludes: exclude, roles (not changed, not required)
            >>>
            >>> # Reduces edit conflicts!
            >>> # Won't overwrite exclude if someone else changed it

        Note:
            Use this in edit() methods to minimize payloads and conflicts.
            Falls back to to_api_dict() if no required fields defined.
        """
        # Get frozen and computed fields to exclude
        frozen_fields = {
            field_name
            for field_name, field_info in self.__class__.model_fields.items()
            if field_info.frozen
        }
        computed_fields = set(self.__class__.model_computed_fields.keys())
        exclude_fields = frozen_fields | computed_fields | {"_client"}

        # Start with required fields (must include in every update)
        data: dict[str, Any] = {}
        required_fields: set[str] = getattr(self, "_required_update_fields", set())
        if required_fields:
            for field in required_fields:
                if field not in exclude_fields:
                    value = getattr(self, field, None)
                    data[field] = value

        # Add explicitly changed fields (from overrides)
        for key, value in overrides.items():
            if key not in exclude_fields:
                data[key] = value

        return data

    async def edit(self, **kwargs: Any) -> "BaseModel":
        """
        Edit this object via the API.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated object with fresh data from API.

        Raises:
            NotImplementedError: Subclass must implement this method.

        Example:
            >>> user = await client.users.get(1)
            >>> updated = await user.edit(name="New Name")
        """
        raise NotImplementedError("Subclass must implement edit()")

    def __repr__(self) -> str:
        """
        Return string representation of the model.

        Returns:
            String like "<User id=1>".
        """
        return f"<{self.__class__.__name__} id={self.id}>"


class PartialModel(PydanticBase):
    """
    Base class for partial Upsales API objects.

    Only minimal fields are guaranteed to be present. Represents nested
    objects in API responses where not all data is included.

    Use fetch_full() to retrieve the complete object from the API.

    Attributes:
        id: Unique identifier for the object.

    Example:
        >>> class PartialUser(PartialModel):
        ...     id: int
        ...     name: str
        ...     email: str | None = None  # May not be present
        ...
        ...     async def fetch_full(self) -> User:
        ...         if not self._client:
        ...             raise RuntimeError("No client available")
        ...         return await self._client.users.get(self.id)
        ...
        >>> partial = PartialUser(id=1, name="John")
        >>> full = await partial.fetch_full()
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow Upsales type
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    id: int
    _client: "Upsales | None" = PrivateAttr(default=None)

    def __init__(self, **data: Any) -> None:
        """
        Initialize partial model with optional client reference.

        Args:
            **data: Model field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        self._client = client

    async def fetch_full(self) -> BaseModel:
        """
        Fetch the full object from the API.

        Returns:
            Full object with all fields populated.

        Raises:
            NotImplementedError: Subclass must implement this method.

        Example:
            >>> partial = PartialUser(id=1, name="John")
            >>> full = await partial.fetch_full()
            >>> print(full.email)  # Now available
        """
        raise NotImplementedError("Subclass must implement fetch_full()")

    async def edit(self, **kwargs: Any) -> BaseModel:
        """
        Edit this object via the API.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full object with fresh data from API.

        Raises:
            NotImplementedError: Subclass must implement this method.

        Example:
            >>> partial = PartialUser(id=1, name="John")
            >>> updated = await partial.edit(name="Jane")
        """
        raise NotImplementedError("Subclass must implement edit()")

    def __repr__(self) -> str:
        """
        Return string representation of the partial model.

        Returns:
            String like "<PartialUser id=1>".
        """
        return f"<{self.__class__.__name__} id={self.id}>"
