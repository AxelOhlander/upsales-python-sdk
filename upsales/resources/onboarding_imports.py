"""Onboarding import resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.onboarding_imports import OnboardingImport, PartialOnboardingImport
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class OnboardingImportsResource(BaseResource[OnboardingImport, PartialOnboardingImport]):
    """Resource manager for onboarding imports.

    Handles CRUD operations for onboarding imports (standard integration import processes).

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create onboarding import
            import_job = await upsales.onboarding_imports.create(
                integrationId=1
            )

            # Get onboarding import
            import_job = await upsales.onboarding_imports.get(1)

            # List onboarding imports
            imports = await upsales.onboarding_imports.list(limit=10)

            # Update onboarding import
            updated = await upsales.onboarding_imports.update(
                1,
                progress=50,
                clientCount=100
            )

            # Delete onboarding import
            await upsales.onboarding_imports.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize onboarding imports resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/onboardingImports",
            model_class=OnboardingImport,
            partial_class=PartialOnboardingImport,
        )
