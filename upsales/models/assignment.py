"""
Assignment models for company user assignments.

These models represent the assignment of users to companies in the Upsales API.
Assignments appear as nested objects in company responses and do not have
their own dedicated endpoint.

API Structure:
    {
        "user": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "role": {...}
        },
        "regDate": "2025-01-01T00:00:00.000Z"
    }

Note:
    Assignments are always nested within company objects and cannot be
    fetched or edited directly. No edit() or fetch_full() methods are provided.

Example:
    >>> company = await upsales.companies.get(1)
    >>> if isinstance(company.assigned, dict):
    ...     assignment = Assignment(**company.assigned)
    ...     print(f"Assigned to: {assignment.user.name}")
    ...     print(f"Assigned on: {assignment.regDate}")
"""

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser


class Assignment(BaseModel):
    """
    Company user assignment from nested company responses.

    Represents a user assigned to a company with the assignment date.
    This object appears nested in company data and has no dedicated endpoint.

    Attributes:
        user: The assigned user (partial data).
        regDate: ISO 8601 timestamp when assignment was created.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> if isinstance(company.assigned, dict):
        ...     assignment = Assignment(**company.assigned, _client=upsales)
        ...     print(f"User: {assignment.user.name}")
        ...     print(f"Email: {assignment.user.email}")
        ...     print(f"Assigned: {assignment.regDate}")
        ...
        ...     # Fetch full user data if needed
        ...     full_user = await assignment.user.fetch_full()
        ...     print(f"Admin: {full_user.is_admin}")
    """

    # Assignments don't have their own IDs - use dummy value for base class
    id: int = Field(default=0, frozen=True, strict=True, description="Not used (nested only)")

    # Required fields
    user: PartialUser = Field(description="Assigned user with partial data")
    regDate: str = Field(frozen=True, description="Assignment date (ISO 8601 timestamp)")

    async def edit(self, **kwargs: Any) -> "Assignment":
        """
        Edit operation not supported for assignments.

        Assignments are nested within companies and cannot be edited directly.
        To change a company's assignment, update the company object.

        Raises:
            NotImplementedError: Assignments cannot be edited directly.

        Example:
            >>> # ❌ Wrong - assignments cannot be edited directly
            >>> await assignment.edit(user=other_user)
            NotImplementedError: Assignments are nested and cannot be edited directly

            >>> # ✅ Correct - update the company's assignment
            >>> await company.edit(assigned={"user": {"id": 2}})
        """
        raise NotImplementedError(
            "Assignments are nested within companies and cannot be edited directly. "
            "Update the parent company object instead."
        )

    def __repr__(self) -> str:
        """
        Return string representation of the assignment.

        Returns:
            String like "<Assignment user='John Doe' regDate='2025-01-01'>".

        Example:
            >>> assignment = Assignment(
            ...     user=PartialUser(id=1, name="John Doe", email="john@example.com"),
            ...     regDate="2025-01-01T00:00:00.000Z"
            ... )
            >>> repr(assignment)
            "<Assignment user='John Doe' regDate='2025-01-01T00:00:00.000Z'>"
        """
        return f"<Assignment user='{self.user.name}' regDate='{self.regDate}'>"


class PartialAssignment(PartialModel):
    """
    Partial Assignment for deeply nested responses.

    Contains minimal assignment data when nested deeply in API responses.
    Since assignments themselves are already nested, this partial version
    is rarely used but provided for completeness.

    Attributes:
        user: The assigned user (partial data).
        regDate: ISO 8601 timestamp when assignment was created.

    Example:
        >>> partial = PartialAssignment(
        ...     user=PartialUser(id=1, name="John Doe", email="john@example.com"),
        ...     regDate="2025-01-01T00:00:00.000Z"
        ... )
        >>> print(f"Assigned to: {partial.user.name}")
    """

    # Assignments don't have their own IDs - use dummy value for base class
    id: int = Field(default=0, frozen=True, strict=True, description="Not used (nested only)")

    # Required fields
    user: PartialUser = Field(description="Assigned user with partial data")
    regDate: str = Field(frozen=True, description="Assignment date (ISO 8601 timestamp)")

    async def fetch_full(self) -> Assignment:
        """
        Fetch full operation not supported for assignments.

        Assignments are nested within companies and have no dedicated endpoint.
        This partial already contains all available assignment data.

        Raises:
            NotImplementedError: Assignments have no dedicated endpoint.

        Example:
            >>> # ❌ Wrong - assignments have no endpoint
            >>> await partial.fetch_full()
            NotImplementedError: Assignments are nested and have no dedicated endpoint

            >>> # ✅ Correct - convert to full Assignment directly
            >>> full = Assignment(**partial.model_dump())
        """
        raise NotImplementedError(
            "Assignments are nested within companies and have no dedicated endpoint. "
            "Convert to Assignment directly if needed."
        )

    async def edit(self, **kwargs: Any) -> Assignment:
        """
        Edit operation not supported for assignments.

        Assignments are nested within companies and cannot be edited directly.
        To change a company's assignment, update the company object.

        Raises:
            NotImplementedError: Assignments cannot be edited directly.

        Example:
            >>> # ❌ Wrong - assignments cannot be edited directly
            >>> await partial.edit(user=other_user)
            NotImplementedError: Assignments are nested and cannot be edited directly

            >>> # ✅ Correct - update the parent company object
            >>> await company.edit(assigned={"user": {"id": 2}})
        """
        raise NotImplementedError(
            "Assignments are nested within companies and cannot be edited directly. "
            "Update the parent company object instead."
        )

    def __repr__(self) -> str:
        """
        Return string representation of the partial assignment.

        Returns:
            String like "<PartialAssignment user='John Doe' regDate='2025-01-01'>".

        Example:
            >>> partial = PartialAssignment(
            ...     user=PartialUser(id=1, name="John Doe", email="john@example.com"),
            ...     regDate="2025-01-01T00:00:00.000Z"
            ... )
            >>> repr(partial)
            "<PartialAssignment user='John Doe' regDate='2025-01-01T00:00:00.000Z'>"
        """
        return f"<PartialAssignment user='{self.user.name}' regDate='{self.regDate}'>"
