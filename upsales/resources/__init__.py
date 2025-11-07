"""
Resource managers for Upsales API endpoints.

Each resource manager handles CRUD operations for a specific API endpoint.
All use Python 3.13 type parameter syntax for clean generics.

All resource managers inherit standard CRUD from BaseResource:
- get(id) - Get single object
- list(limit, offset, **params) - Paginated list
- list_all(**params) - Auto-paginated list of all objects
- update(id, **data) - Update object
- delete(id) - Delete object
- bulk_update(ids, data, max_concurrent) - Parallel updates
- bulk_delete(ids, max_concurrent) - Parallel deletes

Example:
    >>> from upsales.resources import CompaniesResource, ProductsResource, UsersResource
    >>> from upsales.http import HTTPClient
    >>>
    >>> http = HTTPClient(token="...")
    >>> companies = CompaniesResource(http)
    >>> company = await companies.get(1)
"""

from upsales.resources.activities import ActivitiesResource
from upsales.resources.activity_list import ActivityListResource
from upsales.resources.apikeys import ApikeysResource
from upsales.resources.appointments import AppointmentsResource
from upsales.resources.base import BaseResource
from upsales.resources.clientcategories import ClientCategoriesResource
from upsales.resources.companies import CompaniesResource
from upsales.resources.contacts import ContactsResource
from upsales.resources.currencies import CurrenciesResource
from upsales.resources.files import FilesResource
from upsales.resources.forms import FormsResource
from upsales.resources.functions import FunctionsResource
from upsales.resources.journey_steps import JourneyStepsResource
from upsales.resources.mail import MailResource
from upsales.resources.mail_templates import MailTemplatesResource
from upsales.resources.metadata import MetadataResource
from upsales.resources.notifications import NotificationsResource
from upsales.resources.opportunity_ai import OpportunityAIResource
from upsales.resources.orders import OrdersResource
from upsales.resources.orderStages import OrderStagesResource
from upsales.resources.pricelists import PricelistsResource
from upsales.resources.products import ProductsResource
from upsales.resources.project_plan_types import ProjectPlanTypesResource
from upsales.resources.projectplanpriority import ProjectPlanPrioritiesResource
from upsales.resources.projects import ProjectsResource
from upsales.resources.roles import RolesResource
from upsales.resources.sales_coaches import SalesCoachesResource
from upsales.resources.segments import SegmentsResource
from upsales.resources.self import SelfResource
from upsales.resources.standard_integrations import StandardIntegrationsResource
from upsales.resources.static_values import StaticValuesResource
from upsales.resources.todoViews import TodoViewsResource
from upsales.resources.trigger_attributes import TriggerAttributesResource
from upsales.resources.triggers import TriggersResource
from upsales.resources.users import UsersResource

__all__ = [
    "BaseResource",
    "ActivitiesResource",
    "ActivityListResource",
    "ApikeysResource",
    "AppointmentsResource",
    "ClientCategoriesResource",
    "CompaniesResource",
    "ContactsResource",
    "CurrenciesResource",
    "FilesResource",
    "FormsResource",
    "FunctionsResource",
    "JourneyStepsResource",
    "MailResource",
    "MailTemplatesResource",
    "NotificationsResource",
    "MetadataResource",
    "OpportunityAIResource",
    "OrdersResource",
    "OrderStagesResource",
    "PricelistsResource",
    "ProductsResource",
    "ProjectPlanPrioritiesResource",
    "ProjectPlanTypesResource",
    "ProjectsResource",
    "RolesResource",
    "SalesCoachesResource",
    "SegmentsResource",
    "StandardIntegrationsResource",
    "SelfResource",
    "StaticValuesResource",
    "TodoViewsResource",
    "TriggerAttributesResource",
    "TriggersResource",
    "UsersResource",
]
