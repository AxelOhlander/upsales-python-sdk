"""Type definitions for Upsales API.

This module contains TypedDict definitions for type-safe updates and IDE autocomplete.
"""

from typing import TypedDict


class UserUpdateFields(TypedDict, total=False):
    """Available fields for updating a User."""

    name: str
    email: str
    administrator: int
    active: int
    custom: list[dict]


class CompanyUpdateFields(TypedDict, total=False):
    """Available fields for updating a Company (Account)."""

    name: str
    active: int
    custom: list[dict]


class ProductUpdateFields(TypedDict, total=False):
    """Available fields for updating a Product."""

    name: str
    active: int
    price: float
    custom: list[dict]


class ContactUpdateFields(TypedDict, total=False):
    """Available fields for updating a Contact."""

    name: str
    email: str
    phone: str
    active: int
    custom: list[dict]


class ActivityUpdateFields(TypedDict, total=False):
    """Available fields for updating an Activity."""

    description: str
    notes: str
    date: str
    custom: list[dict]


class AppointmentUpdateFields(TypedDict, total=False):
    """Available fields for updating an Appointment."""

    description: str
    notes: str
    date: str
    custom: list[dict]


class OrderUpdateFields(TypedDict, total=False):
    """Available fields for updating an Order."""

    description: str
    notes: str
    date: str
    custom: list[dict]


class OpportunityUpdateFields(TypedDict, total=False):
    """Available fields for updating an Opportunity."""

    description: str
    notes: str
    date: str
    probability: int
    custom: list[dict]


class CampaignUpdateFields(TypedDict, total=False):
    """Available fields for updating a Campaign."""

    name: str
    active: int
    custom: list[dict]


class NotificationUpdateFields(TypedDict, total=False):
    """Available fields for updating a Notification."""

    message: str
    read: int


class ActivityTypeUpdateFields(TypedDict, total=False):
    """Available fields for updating an ActivityType."""

    name: str
    active: int
    sortOrder: int


class ClientCategoryTypeUpdateFields(TypedDict, total=False):
    """Available fields for updating a ClientCategoryType."""

    name: str
    active: int
    sortOrder: int


class ClientCategoryUpdateFields(TypedDict, total=False):
    """Available fields for updating a ClientCategory."""

    name: str
    active: int
    sortOrder: int
    custom: list[dict]


class ClientRelationUpdateFields(TypedDict, total=False):
    """Available fields for updating a ClientRelation."""

    active: int


class ContactRelationUpdateFields(TypedDict, total=False):
    """Available fields for updating a ContactRelation."""

    active: int


class FlowUpdateFields(TypedDict, total=False):
    """Available fields for updating a Flow."""

    name: str
    active: int
    description: str


class LeadUpdateFields(TypedDict, total=False):
    """Available fields for updating a Lead."""

    name: str
    email: str
    phone: str
    notes: str
    custom: list[dict]


class ProductCategoryUpdateFields(TypedDict, total=False):
    """Available fields for updating a ProductCategory."""

    name: str
    active: int
    sortOrder: int


class TicketStatusUpdateFields(TypedDict, total=False):
    """Available fields for updating a TicketStatus."""

    name: str
    active: int
    sortOrder: int


class TicketTypeUpdateFields(TypedDict, total=False):
    """Available fields for updating a TicketType."""

    name: str
    active: int
    sortOrder: int


class ApiKeyUpdateFields(TypedDict, total=False):
    """Available fields for updating an ApiKey."""

    name: str
    active: int
    description: str


class OrderStageUpdateFields(TypedDict, total=False):
    """Available fields for updating an OrderStage."""

    name: str
    active: int
    sortOrder: int
    probability: int


class BannerGroupUpdateFields(TypedDict, total=False):
    """Available fields for updating a BannerGroup."""

    title: str
    draft: bool
    body: str
    landingPage: str
    pages: str
    formats: str
    availableFormats: str
    custom: list[dict]


class ReportViewUpdateFields(TypedDict, total=False):
    """Available fields for updating a ReportView."""

    description: str
    type: str
    title: str
    default: bool
    editable: bool
    private: bool
    sorting: list[dict]
    grouping: str
    tableGrouping: str
    filters: list[dict]
    roleId: int
    custom: list[dict]


class NotificationSettingUpdateFields(TypedDict, total=False):
    """Available fields for updating a NotificationSetting."""

    entity: str
    enabled: bool
    mobile: bool
    reminderTime: int
    reminderUnit: str


class EsignUpdateFields(TypedDict, total=False):
    """Available fields for updating an Esign."""

    clientId: int
    userId: int
    opportunityId: int
    title: str
    state: str
    fileId: int
    signDate: str
    involved: list[dict]


class SalesboardCardUpdateFields(TypedDict, total=False):
    """Available fields for updating a SalesboardCard."""

    config: dict


class OnboardingImportUpdateFields(TypedDict, total=False):
    """Available fields for updating an OnboardingImport."""

    startDate: str
    endDate: str
    progress: int
    clientCount: int
    contactCount: int
    orderCount: int


class VisitUpdateFields(TypedDict, total=False):
    """Available fields for updating a Visit."""

    referer: str
    isFirst: bool
    client: dict
    contact: dict
    score: int
    pages: list[dict]


class UserDefinedObject1UpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObject1."""

    notes: str
    notes1: str
    notes2: str
    notes3: str
    notes4: str
    clientId: int
    contactId: int
    projectId: int
    userId: int
    roleId: int
    custom: list[dict]
    categories: list[dict]


class UserDefinedObject2UpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObject2."""

    notes: str
    notes1: str
    notes2: str
    notes3: str
    notes4: str
    clientId: int
    contactId: int
    projectId: int
    userId: int
    roleId: int
    custom: list[dict]
    categories: list[dict]


class UserDefinedObject3UpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObject3."""

    notes: str
    notes1: str
    notes2: str
    notes3: str
    notes4: str
    clientId: int
    contactId: int
    projectId: int
    userId: int
    roleId: int
    custom: list[dict]
    categories: list[dict]


class UserDefinedObject4UpdateFields(TypedDict, total=False):
    """Available fields for updating a UserDefinedObject4."""

    notes: str
    notes1: str
    notes2: str
    notes3: str
    notes4: str
    clientId: int
    contactId: int
    projectId: int
    userId: int
    roleId: int
    custom: list[dict]
    categories: list[dict]
