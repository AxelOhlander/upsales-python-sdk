"""
Sync api_endpoints_with_fields.json with current SDK implementation.

Compares the 167 endpoints documented in the API file with the 35 currently
implemented resources to identify gaps and prioritize remaining work.

Usage:
    python ai_temp_files/sync_api_file_with_implementation.py
"""

import json
from pathlib import Path

# Load API endpoints file
with open("api_endpoints_with_fields.json") as f:
    api_data = json.load(f)

# Currently implemented resources (from client.py)
IMPLEMENTED = {
    "activities",
    "activity_list",  # Special: activityList in API
    "apikeys",
    "appointments",
    "clientcategories",
    "companies",  # API: accounts
    "contacts",
    "currencies",
    "custom_fields",  # Special: customfields_* in API
    "files",
    "forms",
    "functions",
    "journey_steps",  # API: journeySteps
    "mail",
    "mail_templates",  # API: mailTemplates
    "metadata",
    "notifications",
    "opportunity_ai",  # Special
    "order_stages",  # API: orderStages
    "orders",
    "pricelists",
    "products",
    "project_plan_priorities",  # API: projectPlanPriority
    "project_plan_types",  # API: projectPlanTypes
    "projects",
    "roles",
    "sales_coaches",  # API: salesCoaches
    "segments",
    "self",
    "standard_integrations",  # API: standardIntegration
    "static_values",  # API: staticValues
    "todo_views",  # API: todoViews
    "trigger_attributes",  # API: triggerAttributes
    "triggers",
    "users",
}

# Mapping from API endpoint names to SDK resource names
API_TO_SDK_MAPPING = {
    "accounts": "companies",
    "activityList": "activity_list",
    "journeySteps": "journey_steps",
    "mailTemplates": "mail_templates",
    "orderStages": "order_stages",
    "projectPlanPriority": "project_plan_priorities",
    "projectPlanTypes": "project_plan_types",
    "salesCoaches": "sales_coaches",
    "standardIntegration": "standard_integrations",
    "staticValues": "static_values",
    "todoViews": "todo_views",
    "triggerAttributes": "trigger_attributes",
}

# SDK to API reverse mapping
SDK_TO_API_MAPPING = {v: k for k, v in API_TO_SDK_MAPPING.items()}

# Categorize endpoints
print("🔍 ENDPOINT COVERAGE ANALYSIS")
print("=" * 80)
print()

# Get all API endpoints
api_endpoints = set(api_data["endpoints"].keys())

# Map SDK resources to API endpoint names
implemented_api_names = set()
for sdk_name in IMPLEMENTED:
    api_name = SDK_TO_API_MAPPING.get(sdk_name, sdk_name)
    implemented_api_names.add(api_name)

# Find gaps
not_implemented = api_endpoints - implemented_api_names
implemented_verified = implemented_api_names & api_endpoints

print(f"📊 STATISTICS")
print(f"   Total API Endpoints: {len(api_endpoints)}")
print(f"   Currently Implemented: {len(implemented_verified)}")
print(f"   Not Yet Implemented: {len(not_implemented)}")
print(f"   Coverage: {len(implemented_verified) / len(api_endpoints) * 100:.1f}%")
print()

# Categorize not-implemented by priority
print("=" * 80)
print("🎯 NOT IMPLEMENTED ENDPOINTS (Priority Categorization)")
print("=" * 80)
print()

# Define priority categories based on common usage
HIGH_PRIORITY = {
    "opportunities",  # Same as orders
    "agreements",
    "quotes",
    "tickets",
    "events",
    "tasks",
}

MEDIUM_PRIORITY = {
    "customfields_orders",
    "customfields_accounts",
    "customfields_contacts",
    "customfields_activities",
    "customfields_appointments",
    "customfields_products",
    "customfields_orderrows",
    "adCampaigns",
    "adAccounts",
    "quota",
    "report",
}

# Categorize
high_priority_missing = not_implemented & HIGH_PRIORITY
medium_priority_missing = not_implemented & MEDIUM_PRIORITY
low_priority_missing = not_implemented - HIGH_PRIORITY - MEDIUM_PRIORITY

# Print high priority
print("🔴 HIGH PRIORITY (Core Business Operations)")
print(f"   Count: {len(high_priority_missing)}")
for endpoint in sorted(high_priority_missing):
    info = api_data["endpoints"][endpoint]
    desc = info.get("description", "")
    has_post = "POST" in info.get("methods", {})
    has_put = "PUT" in info.get("methods", {})
    operations = []
    if has_post:
        operations.append("CREATE")
    if has_put:
        operations.append("UPDATE")
    print(f"   - {endpoint:<30} {desc:<40} [{', '.join(operations)}]")
print()

# Print medium priority
print("🟡 MEDIUM PRIORITY (Configuration & Features)")
print(f"   Count: {len(medium_priority_missing)}")
for endpoint in sorted(medium_priority_missing):
    info = api_data["endpoints"][endpoint]
    desc = info.get("description", "")
    print(f"   - {endpoint:<30} {desc}")
print()

# Print low priority (just count and examples)
print("🟢 LOW PRIORITY (Specialized/Admin Features)")
print(f"   Count: {len(low_priority_missing)}")
print(f"   Examples: {', '.join(sorted(list(low_priority_missing))[:10])}")
print()

# Analyze CREATE capability
print("=" * 80)
print("📝 CREATE OPERATION ANALYSIS")
print("=" * 80)
print()

create_capable = []
create_verified = []
create_inherited = []

for endpoint in sorted(api_endpoints):
    info = api_data["endpoints"][endpoint]
    methods = info.get("methods", {})

    if "POST" in methods:
        sdk_name = API_TO_SDK_MAPPING.get(endpoint, endpoint)

        if sdk_name == "orders":
            create_verified.append(endpoint)
        elif endpoint in implemented_api_names:
            create_inherited.append(endpoint)
        else:
            create_capable.append(endpoint)

print(f"✅ CREATE Verified: {len(create_verified)}")
for ep in create_verified:
    print(f"   - {ep} (nested required fields pattern documented)")
print()

print(f"🔶 CREATE Inherited (Not Verified): {len(create_inherited)}")
for ep in sorted(create_inherited)[:10]:
    sdk_name = API_TO_SDK_MAPPING.get(ep, ep)
    print(f"   - {ep:<30} SDK: {sdk_name}")
if len(create_inherited) > 10:
    print(f"   ... and {len(create_inherited) - 10} more")
print()

print(f"❌ CREATE Capable But Not Implemented: {len(create_capable)}")
for ep in sorted(create_capable)[:10]:
    info = api_data["endpoints"][ep]
    required_count = len(info["methods"]["POST"].get("required", []))
    print(f"   - {ep:<30} Required fields: {required_count}")
if len(create_capable) > 10:
    print(f"   ... and {len(create_capable) - 10} more")
print()

# Summary recommendation
print("=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)
print()
print("1. IMMEDIATE: Verify CREATE operations for implemented endpoints")
print(f"   - {len(create_inherited)} endpoints have CREATE but field requirements not verified")
print()
print("2. HIGH PRIORITY: Implement core business endpoints")
print(f"   - {len(high_priority_missing)} critical endpoints missing")
print()
print("3. MEDIUM PRIORITY: Configuration endpoints")
print(f"   - {len(medium_priority_missing)} feature endpoints missing")
print()
print("4. LOW PRIORITY: Specialized/admin endpoints")
print(f"   - {len(low_priority_missing)} specialized endpoints")
print()
print(f"📈 TOTAL WORK REMAINING: {len(not_implemented)} endpoints to implement")
print()
