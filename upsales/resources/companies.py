"""
Companies resource manager for Upsales API.

Provides methods to interact with the /accounts endpoint using Company models.

Note:
    API endpoint is /accounts, but we use "Company" terminology to match
    what users see in the Upsales UI. See docs/terminology.md for rationale.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single company
    ...     company = await upsales.companies.get(1)
    ...     print(company.name)
    ...
    ...     # List companies
    ...     companies = await upsales.companies.list(limit=10)
    ...
    ...     # Update company
    ...     updated = await upsales.companies.update(1, name="New Name")
"""

from upsales.http import HTTPClient
from upsales.models.company import Company, PartialCompany
from upsales.resources.base import BaseResource


class CompaniesResource(BaseResource[Company, PartialCompany]):
    """
    Resource manager for Company (accounts) endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single company
    - list(limit, offset, **params) - List companies with pagination
    - list_all(**params) - Auto-paginated list of all companies
    - update(id, **data) - Update company
    - delete(id) - Delete company
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> companies = CompaniesResource(http_client)
        >>> company = await companies.get(1)
        >>> companies_list = await companies.list(limit=100)
        >>> all_active = await companies.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize companies resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/accounts",  # API endpoint (not /companies!)
            model_class=Company,
            partial_class=PartialCompany,
        )

    # Add company-specific methods here as needed
    # Example:
    # async def get_by_name(self, name: str) -> list[Company]:
    #     """Get companies by name."""
    #     response = await self._http.get(self._endpoint, params={"name": name})
    #     return [
    #         self._model_class(**item, _client=self._http._client)
    #         for item in response["data"]
    #     ]
