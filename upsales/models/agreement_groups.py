"""
Agreement Group models for Upsales API.

Agreement groups manage timelines of agreements for a single client,
allowing current and future agreements in the same group with
non-overlapping date ranges.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.agreements import Agreement, PartialAgreement
from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany


class AgreementGroupUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an AgreementGroup.

    All fields are optional. Only include fields you want to update.

    Important:
        When updating a group, include the full list of agreements you want to keep.
        Agreements not included may be deleted unless you set
        `opts.leaveMyAgreementsAlone=True`.

    Args:
        client: Client/company the group belongs to.
        agreements: List of agreements in the group. Include full list to avoid deletion.
        opts: Options for update behavior.
            - leaveMyAgreementsAlone: If True, don't delete agreements not in the list.
    """

    client: dict[str, Any]
    agreements: list[dict[str, Any]]
    opts: dict[str, Any]


class AgreementGroup(BaseModel):
    """
    Agreement Group model representing a timeline of agreements for a client.

    Agreement groups allow managing current and future agreements together,
    with automatic determination of the current agreement based on dates.

    Key behaviors:
        - Agreements in a group must not overlap in time
        - Each agreement must have a start date
        - The system computes currentAgreement based on dates
        - Deleting a group also deletes all agreements in it

    Examples:
        Get a group and its agreements:
            >>> group = await upsales.agreement_groups.get(1)
            >>> print(f"Current: {group.currentAgreement.description}")
            >>> print(f"Total agreements: {len(group.agreements)}")

        Update a group:
            >>> await group.edit(
            ...     agreements=[
            ...         {"id": 123, "description": "Updated"},
            ...         new_agreement_data,
            ...     ]
            ... )
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique agreement group ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")
    regBy: int = Field(frozen=True, description="User ID who created this group")
    modBy: int = Field(frozen=True, description="User ID who last modified this group")

    # Updatable fields
    client: PartialCompany = Field(description="Client/company the group belongs to")
    agreements: list[Agreement | PartialAgreement | dict[str, Any]] = Field(
        default=[], description="Agreements in this group"
    )
    currentAgreement: Agreement | PartialAgreement | dict[str, Any] | None = Field(
        None, description="Current active agreement (computed from dates)"
    )

    async def edit(self, **kwargs: Unpack[AgreementGroupUpdateFields]) -> "AgreementGroup":
        """
        Edit this agreement group.

        Args:
            **kwargs: Fields to update. See AgreementGroupUpdateFields.

        Returns:
            Updated agreement group instance.

        Raises:
            RuntimeError: If no client available.

        Warning:
            When updating, include the full list of agreements you want to keep.
            Agreements not included will be deleted unless you set
            `opts={"leaveMyAgreementsAlone": True}`.

        Examples:
            >>> # Update keeping all existing agreements
            >>> await group.edit(
            ...     agreements=[{"id": a.id} for a in group.agreements],
            ...     opts={"leaveMyAgreementsAlone": True}
            ... )
            >>>
            >>> # Add a future agreement to the group
            >>> await group.edit(
            ...     agreements=[
            ...         *[{"id": a.id} for a in group.agreements],
            ...         {
            ...             "description": "2026 subscription",
            ...             "client": {"id": group.client.id},
            ...             "user": {"id": 1},
            ...             "stage": {"id": 3},
            ...             "currency": "SEK",
            ...             "orderRow": [...],
            ...             "metadata": {"agreementStartdate": "2026-01-01", ...}
            ...         }
            ...     ]
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreement_groups.update(self.id, **self.to_api_dict(**kwargs))


class PartialAgreementGroup(PartialModel):
    """
    Partial Agreement Group model for nested responses.

    Used when agreement groups appear in other API responses.

    Examples:
        Fetch full agreement group:
            >>> full_group = await partial.fetch_full()
    """

    id: int = Field(description="Unique agreement group ID")

    async def fetch_full(self) -> AgreementGroup:
        """
        Fetch full agreement group data from API.

        Returns:
            Complete AgreementGroup instance.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreement_groups.get(self.id)

    async def edit(self, **kwargs: Unpack[AgreementGroupUpdateFields]) -> AgreementGroup:
        """
        Edit this agreement group.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated agreement group instance.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreement_groups.update(self.id, **kwargs)
