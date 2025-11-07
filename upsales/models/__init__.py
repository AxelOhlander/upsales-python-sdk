"""
Data models for Upsales API objects.

All models use Python 3.13 native type hints and Pydantic v2 advanced features:
- Reusable validators for consistent validation
- Computed fields for derived properties
- Optimized serialization (5-50x faster)
- Field descriptions for documentation
- TypedDict for IDE autocomplete

Example:
    >>> from upsales.models import User, Company, Product
    >>>
    >>> # Models validate on creation and assignment
    >>> user = User(id=1, name="John", email="john@example.com", active=1)
    >>> user.name = "Jane"  # Validated assignment
    >>>
    >>> # Computed fields provide convenience
    >>> user.is_admin  # Boolean helper
    >>> user.custom_fields[11]  # Dict-like custom fields access
"""

from upsales.models.activities import Activity, ActivityUpdateFields, PartialActivity
from upsales.models.activity_list_item import ActivityListItem
from upsales.models.ad_campaign import AdCampaign, PartialAdCampaign
from upsales.models.address import Address, PartialAddress
from upsales.models.address_list import AddressList
from upsales.models.apiKeys import Apikey, ApikeyUpdateFields, PartialApikey
from upsales.models.appointments import Appointment, AppointmentUpdateFields, PartialAppointment
from upsales.models.assignment import Assignment, PartialAssignment
from upsales.models.base import BaseModel, PartialModel
from upsales.models.bundled_product import (
    BundledProduct,
    BundledProductUpdateFields,
    PartialBundledProduct,
)
from upsales.models.campaign import PartialCampaign
from upsales.models.category import PartialCategory
from upsales.models.clientcategories import (
    ClientCategory,
    ClientCategoryUpdateFields,
    PartialClientCategory,
)
from upsales.models.company import Company, PartialCompany
from upsales.models.contacts import Contact, ContactUpdateFields, PartialContact
from upsales.models.currency import Currency, CurrencyUpdateFields, PartialCurrency
from upsales.models.currency_configuration import (
    CurrencyConfiguration,
    PartialCurrencyConfiguration,
)
from upsales.models.custom_field import (
    CustomField,
    CustomFieldType,
    PartialCustomField,
)
from upsales.models.custom_fields import CustomFields
from upsales.models.files import File, FileUpdateFields, PartialFile
from upsales.models.form_action import FormAction, FormActionProperty, PartialFormAction
from upsales.models.form_element import (
    FormElement,
    FormElementUpdateFields,
    PartialFormElement,
)
from upsales.models.form_field import FormField, PartialFormField
from upsales.models.forms import Form, FormUpdateFields, PartialForm
from upsales.models.journey_step import JourneyStep, JourneyStepUpdateFields, PartialJourneyStep
from upsales.models.mail import Mail, MailUpdateFields, PartialMail
from upsales.models.mail_templates import (
    MailTemplate,
    MailTemplateUpdateFields,
    PartialMailTemplate,
)
from upsales.models.metadata import Currency as MetadataCurrency
from upsales.models.metadata import FieldDefinition, Metadata, MetadataUser, SystemParams
from upsales.models.notifications import (
    Notification,
    PartialNotification,
)
from upsales.models.opportunity_ai import OpportunityAI, PartialOpportunityAI
from upsales.models.orders import Order, OrderCreateFields, OrderUpdateFields, PartialOrder
from upsales.models.orderStages import OrderStage, OrderStageUpdateFields, PartialOrderStage
from upsales.models.price_tier import PartialPriceTier, PriceTier
from upsales.models.pricelist import PartialPricelist, Pricelist, PricelistUpdateFields
from upsales.models.processed_by import PartialProcessedBy, ProcessedBy
from upsales.models.product import PartialProduct, Product
from upsales.models.project_plan_types import (
    PartialProjectPlanType,
    ProjectPlanType,
    ProjectPlanTypeUpdateFields,
)
from upsales.models.projectplanpriority import (
    PartialProjectPlanPriority,
    ProjectPlanPriority,
    ProjectPlanPriorityUpdateFields,
)
from upsales.models.projects import PartialProject, Project, ProjectUpdateFields
from upsales.models.roles import PartialRole, Role, RoleUpdateFields
from upsales.models.salesCoaches import PartialSalesCoach, SalesCoach, SalesCoachUpdateFields
from upsales.models.segments import PartialSegment, Segment, SegmentUpdateFields
from upsales.models.self import AccountManager, ClientDetail, Self, SelfClient, VersionData
from upsales.models.standard_integration import (
    PartialStandardIntegration,
    StandardIntegration,
    StandardIntegrationUpdateFields,
)
from upsales.models.static_values import CreditRating, IndustryCode, StaticValue, StaticValues
from upsales.models.todoViews import TodoView
from upsales.models.trigger_attributes import TriggerAttribute, TriggerAttributes
from upsales.models.triggers import PartialTrigger, Trigger, TriggerUpdateFields
from upsales.models.user import PartialUser, User

# Rebuild models with forward references after all models are imported
# This resolves Pydantic v2 forward reference issues
Company.model_rebuild()

__all__ = [
    "BaseModel",
    "PartialModel",
    "BundledProduct",
    "BundledProductUpdateFields",
    "PartialBundledProduct",
    "CustomFields",
    "CustomField",
    "CustomFieldType",
    "PartialCustomField",
    "Activity",
    "ActivityUpdateFields",
    "PartialActivity",
    "ActivityListItem",
    "AdCampaign",
    "PartialAdCampaign",
    "Address",
    "AddressList",
    "PartialAddress",
    "Apikey",
    "ApikeyUpdateFields",
    "PartialApikey",
    "Appointment",
    "AppointmentUpdateFields",
    "PartialAppointment",
    "Assignment",
    "PartialAssignment",
    "ClientCategory",
    "ClientCategoryUpdateFields",
    "PartialClientCategory",
    "Company",
    "PartialCompany",
    "Contact",
    "ContactUpdateFields",
    "PartialContact",
    "Currency",
    "CurrencyUpdateFields",
    "PartialCurrency",
    "CurrencyConfiguration",
    "PartialCurrencyConfiguration",
    "File",
    "FileUpdateFields",
    "PartialFile",
    "Form",
    "FormUpdateFields",
    "PartialForm",
    "FormAction",
    "FormActionProperty",
    "PartialFormAction",
    "FormElement",
    "FormElementUpdateFields",
    "PartialFormElement",
    "FormField",
    "PartialFormField",
    "JourneyStep",
    "JourneyStepUpdateFields",
    "PartialJourneyStep",
    "Mail",
    "MailUpdateFields",
    "PartialMail",
    "MailTemplate",
    "MailTemplateUpdateFields",
    "PartialMailTemplate",
    "Metadata",
    "Notification",
    "MetadataCurrency",
    "MetadataUser",
    "SystemParams",
    "FieldDefinition",
    "PartialNotification",
    "OpportunityAI",
    "PartialOpportunityAI",
    "Order",
    "OrderCreateFields",
    "OrderUpdateFields",
    "PartialOrder",
    "OrderStage",
    "OrderStageUpdateFields",
    "PartialOrderStage",
    "PriceTier",
    "PartialPriceTier",
    "Pricelist",
    "PricelistUpdateFields",
    "PartialPricelist",
    "ProcessedBy",
    "PartialProcessedBy",
    "Product",
    "PartialProduct",
    "ProjectPlanPriority",
    "ProjectPlanPriorityUpdateFields",
    "PartialProjectPlanPriority",
    "ProjectPlanType",
    "ProjectPlanTypeUpdateFields",
    "PartialProjectPlanType",
    "Project",
    "ProjectUpdateFields",
    "PartialProject",
    "Role",
    "RoleUpdateFields",
    "PartialRole",
    "SalesCoach",
    "SalesCoachUpdateFields",
    "PartialSalesCoach",
    "Segment",
    "SegmentUpdateFields",
    "PartialSegment",
    "StandardIntegration",
    "StandardIntegrationUpdateFields",
    "PartialStandardIntegration",
    "Self",
    "SelfClient",
    "ClientDetail",
    "VersionData",
    "AccountManager",
    "StaticValue",
    "CreditRating",
    "IndustryCode",
    "StaticValues",
    "TodoView",
    "TriggerAttribute",
    "TriggerAttributes",
    "Trigger",
    "TriggerUpdateFields",
    "PartialTrigger",
    "User",
    "PartialUser",
    "PartialCategory",
    "PartialCampaign",
]
