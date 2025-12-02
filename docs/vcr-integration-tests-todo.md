# VCR Integration Tests - Action List

This document tracks which endpoints need VCR integration tests recorded to validate models against real API responses.

## Why This Matters

- VCR cassettes capture real API responses and replay them in tests
- Ensures Pydantic models correctly parse actual API data
- Catches field requirement mismatches (like we found with `Ticket.regBy` and `PartialUser.email`)
- Enables offline testing without hitting the real API

## Priority Levels

- **P0 - Critical**: Core CRM entities, heavily used
- **P1 - High**: Common operations, likely to have complex nested objects
- **P2 - Medium**: Less common but still important
- **P3 - Low**: Rarely used, admin features, or simple endpoints

---

## Completed

- [x] `apikeys` - API key management
- [x] `companies` - Core CRM entity
- [x] `contacts` - Core CRM entity
- [x] `currencies` - Currency configuration
- [x] `files` - File management
- [x] `forms` - Form definitions
- [x] `journey_steps` - Marketing journeys
- [x] `metadata` - System metadata
- [x] `opportunity_ai` - AI features
- [x] `order_stages` - Order pipeline stages
- [x] `pricelists` - Pricing
- [x] `products` - Product catalog
- [x] `project_plan_stages` - Project stages
- [x] `project_plan_priority` - Project priorities
- [x] `project_plan_status` - Project statuses
- [x] `projects` - Project management
- [x] `quota` - Sales quotas
- [x] `roles` - User roles
- [x] `sales_coaches` - Sales coaching
- [x] `segments` - Customer segments
- [x] `standard_integrations` - Integration configs
- [x] `tickets` - Support tickets
- [x] `todo_views` - Todo list views
- [x] `trigger_attributes` - Automation triggers
- [x] `triggers` - Automation triggers
- [x] `users` - User management

---

## P0 - Critical (Core CRM)

- [ ] `activities` - Activity tracking (calls, emails, meetings)
- [ ] `appointments` - Calendar appointments
- [ ] `opportunities` - Sales opportunities/deals
- [ ] `orders` - Sales orders
- [ ] `leads` - Lead management

## P1 - High Priority

- [ ] `events` - Event tracking
- [ ] `flows` - Automation flows
- [ ] `mail` - Email sending
- [ ] `mail_campaigns` - Email campaigns
- [ ] `phone_calls` - Phone call logs
- [ ] `agreements` - Customer agreements
- [ ] `activity_types` - Activity type definitions
- [ ] `ticket_statuses` - Ticket status definitions
- [ ] `ticket_types` - Ticket type definitions
- [ ] `product_categories` - Product categorization
- [ ] `project_plan_types` - Project type definitions

## P2 - Medium Priority

- [ ] `activity_list` - Activity list view (read-only)
- [ ] `activity_quota` - Activity quotas
- [ ] `client_categories` (clientcategories) - Company categories
- [ ] `client_category_types` - Category type definitions
- [ ] `client_relations` - Company relationships
- [ ] `contact_relations` - Contact relationships
- [ ] `contract_accepted` - Contract acceptance tracking
- [ ] `custom_fields` - Custom field definitions
- [ ] `esigns` - E-signature documents
- [ ] `form_submits` - Form submission data
- [ ] `group_mail_categories` - Email grouping
- [ ] `list_views` - Saved list views
- [ ] `mail_templates` - Email templates
- [ ] `mail_domains` - Email domain config
- [ ] `market_rejectlist` - Marketing opt-outs
- [ ] `notifications` - User notifications
- [ ] `notification_settings` - Notification preferences
- [ ] `pages` - Landing pages
- [ ] `periodization` - Revenue periodization
- [ ] `self` - Current user/session info
- [ ] `static_values` - System static values
- [ ] `suggestions` - Prospecting suggestions
- [ ] `visits` - Website visits

## P3 - Low Priority (Admin/Rare)

- [ ] `ad_accounts` - Advertising accounts
- [ ] `ad_campaigns` - Ad campaigns
- [ ] `ad_creatives` - Ad creatives
- [ ] `banner_groups` - Banner management
- [ ] `bulk` - Bulk operations (POST-only)
- [ ] `client_ip_info` - IP lookup (POST-only)
- [ ] `client_ips` - IP whitelist
- [ ] `data_source` - Data source functions
- [ ] `engage_credit_transaction` - Engage credits
- [ ] `esign_function` - E-sign functions
- [ ] `file_upload` - File upload endpoint
- [ ] `functions` - Utility functions
- [ ] `image_compose` - Image composition (POST-only)
- [ ] `import_mail_campaign_mail` - Mail import
- [ ] `import_mail_event` - Event import
- [ ] `mail_editor` - Email editor
- [ ] `mail_multi` - Batch email (POST-only)
- [ ] `mail_test` - Test email sending
- [ ] `onboarding_imports` - Onboarding data
- [ ] `provisioning` - Account provisioning
- [ ] `report_view` - Report views
- [ ] `reset_score` - Score reset
- [ ] `resources_upload_external` - External uploads
- [ ] `resources_upload_internal` - Internal uploads
- [ ] `salesboard_cards` - Salesboard UI
- [ ] `send_beam` - Beam notifications
- [ ] `soliditet_clients` - Soliditet integration
- [ ] `standard_creative` - Standard creatives
- [ ] `standard_integration_data` - Integration data
- [ ] `standard_integration_settings` - Integration settings
- [ ] `standard_integration_user_settings` - User integration settings
- [ ] `system_mail` - System email (POST-only)
- [ ] `unsub` - Unsubscribe management
- [ ] `user_defined_object_1` - Custom object 1
- [ ] `user_defined_object_2` - Custom object 2
- [ ] `user_defined_object_3` - Custom object 3
- [ ] `user_defined_object_4` - Custom object 4
- [ ] `user_defined_object_categories` - Custom object categories
- [ ] `user_defined_object_definition` - Custom object definitions
- [ ] `user_invites` - User invitation management
- [ ] `validate_page` - Page validation
- [ ] `voice` - Voice/phone integration

---

## How to Add a Test

1. Copy pattern from `tests/integration/test_tickets_integration.py`
2. Create `tests/integration/test_{endpoint}_integration.py`
3. Run: `uv run pytest tests/integration/test_{endpoint}_integration.py -v`
4. Review cassettes in `tests/cassettes/integration/test_{endpoint}_integration/`
5. Check for sensitive data (should be REDACTED)
6. If model validation fails, fix the model (usually making fields optional)
7. Mark as completed in this list

## Notes

- Some endpoints are POST-only or function-based - may need different test patterns
- Some endpoints require specific data to exist (e.g., activities need an account)
- Read-only endpoints (like `static_values`) are simpler to test
- Endpoints with nested objects are most likely to reveal model issues
