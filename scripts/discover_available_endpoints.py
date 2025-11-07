"""
Discover available endpoints by testing API responses.

Tests all known Upsales API endpoints to determine which are accessible
and creates a master task list for sub-agents to implement.

Usage:
    python scripts/discover_available_endpoints.py

Output:
    - Console: Status of each endpoint
    - ai_temp_files/ENDPOINT_TASK_LIST.md - Master task list for sub-agents
    - ai_temp_files/endpoint_discovery.json - Raw results
"""

import asyncio
import json
import os
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://power.upsales.com/api/v2"
TOKEN = os.getenv("UPSALES_TOKEN")

# All known endpoints from user's list
ENDPOINTS = [
    "/projectPlan",
    "/clients",              # Likely same as /accounts
    "/currencies",
    "/contacts",
    "/users",
    "/appointments",
    "/activites",            # Typo? Should be activities?
    "/agreements",
    "/projects",
    "/products",
    "/pricelists",
    "/orderStages",
    "/roles",
    "/forms",
    "/form_submits",
    "/visits",
    "/notifications",
    "/projectPlanTemplates",
    "/projectPlanPriority",
    "/ProjectPlanStatus",    # Capital P - might be case sensitive
    "/projectPlanTypes",
    "/todos",
    "/todoViews",
    "/leads2",
    "/segments",
    "/flows",
    "/mailCampaigns",
    "/mail/templates",
    "/socialEvents",
    "/activitytypes",
    "/metadata",
    "/triggers",
    "/journeySteps",
    "/staticValues/all",
    "/roleSettings",
    "/self",
    "/alliwant",
    "/files",
    "/resources/download",
    "/mail",
    "/tickets",
    "/userDefinedObjects/1",
    "/userDefinedObjects/2",
    "/userDefinedObjects/3",
    "/userDefinedObjects/4",
    # "/customfields/{entity}",  # Skip - entity-specific, already done
    "/apiKeys",
    "/uiScript",
    "/detectedduplicates",
    "/function/whatismyip",
    "/clientIps",
    "/esign",
    "/standardIntegration",
    "/search/activitylist",
    "/engage/account",
    "/opportunityAI",
    "/salesCoaches",
    "/salesboardCards",
    "/triggerAttributes",
    "/orders",
    "/activities",           # Correct spelling
    "/clientcategories",
]


async def test_endpoints():
    """Test all endpoints and generate task list."""

    print("\n" + "="*70)
    print("DISCOVERING AVAILABLE ENDPOINTS")
    print("="*70 + "\n")

    results = {
        "tested_at": datetime.now().isoformat(),
        "total_tested": len(ENDPOINTS),
        "accessible": [],
        "inaccessible": [],
        "errors": [],
    }

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Cookie": f"token={TOKEN}"},
        timeout=10.0
    ) as client:

        for endpoint in sorted(ENDPOINTS):
            try:
                print(f"Testing {endpoint}...", end=" ")

                response = await client.get(endpoint, params={"limit": 1})

                if response.status_code == 200:
                    data = response.json()
                    # Check if it has data structure
                    if "data" in data:
                        count = len(data["data"]) if isinstance(data["data"], list) else 1
                        results["accessible"].append({
                            "endpoint": endpoint,
                            "status": "accessible",
                            "sample_count": count,
                        })
                        print(f"✅ OK ({count} items)")
                    else:
                        results["accessible"].append({
                            "endpoint": endpoint,
                            "status": "accessible",
                            "note": "Non-standard response format"
                        })
                        print("✅ OK (non-standard format)")

                elif response.status_code == 404:
                    results["inaccessible"].append({
                        "endpoint": endpoint,
                        "status": 404,
                        "reason": "Not found"
                    })
                    print("❌ 404 Not Found")

                elif response.status_code == 405:
                    results["inaccessible"].append({
                        "endpoint": endpoint,
                        "status": 405,
                        "reason": "Method not allowed (might need POST)"
                    })
                    print("⚠️ 405 Method Not Allowed")

                elif response.status_code == 403:
                    results["inaccessible"].append({
                        "endpoint": endpoint,
                        "status": 403,
                        "reason": "Forbidden (permission required)"
                    })
                    print("⚠️ 403 Forbidden")

                else:
                    results["inaccessible"].append({
                        "endpoint": endpoint,
                        "status": response.status_code,
                        "reason": f"HTTP {response.status_code}"
                    })
                    print(f"⚠️ {response.status_code}")

            except asyncio.TimeoutError:
                results["errors"].append({
                    "endpoint": endpoint,
                    "error": "Timeout"
                })
                print("❌ Timeout")

            except Exception as e:
                results["errors"].append({
                    "endpoint": endpoint,
                    "error": str(e)[:100]
                })
                print(f"❌ Error: {str(e)[:30]}")

    # Save raw results
    with open("ai_temp_files/endpoint_discovery.json", "w") as f:
        json.dump(results, f, indent=2)

    # Generate task list
    generate_task_list(results)

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")

    print(f"Total tested: {len(ENDPOINTS)}")
    print(f"✅ Accessible: {len(results['accessible'])}")
    print(f"❌ Inaccessible: {len(results['inaccessible'])}")
    print(f"❌ Errors: {len(results['errors'])}")

    print(f"\n✅ Task list created: ai_temp_files/ENDPOINT_TASK_LIST.md")
    print(f"✅ Raw data saved: ai_temp_files/endpoint_discovery.json")


def generate_task_list(results):
    """Generate markdown task list for sub-agents."""

    task_list = f"""# Master Endpoint Task List for Sub-Agents

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Accessible Endpoints**: {len(results['accessible'])}
**Status**: Ready for implementation

---

## 🎯 Implementation Priority

### High Priority (Core CRM)
These are the most commonly used endpoints in CRM systems.

### Medium Priority (Supporting Features)
Supporting features and less frequently used endpoints.

### Low Priority (Advanced/Specialized)
Advanced features, integrations, and specialized endpoints.

---

## ✅ Completed Endpoints

**Already implemented with full test coverage**:
- [x] **users** - User management (100% coverage, validated)
- [x] **companies** (/accounts) - Company/account management (100% coverage)
- [x] **products** - Product catalog (100% coverage)
- [x] **orderStages** - Order pipeline stages (100% coverage, sub-agent validated)
- [x] **customFields** - Custom field definitions (complete infrastructure)

---

## 📋 Accessible Endpoints to Implement

"""

    # Categorize endpoints by priority
    high_priority = [
        "/contacts", "/orders", "/activities", "/appointments",
        "/projects", "/agreements", "/todos"
    ]

    medium_priority = [
        "/leads2", "/tickets", "/roles", "/pricelists",
        "/currencies", "/journeySteps", "/segments"
    ]

    # Add high priority
    task_list += "### 🔥 High Priority - Core CRM Features\n\n"
    for item in results['accessible']:
        endpoint = item['endpoint']
        if endpoint in high_priority:
            task_list += f"- [ ] **{endpoint.lstrip('/')}** - {item.get('sample_count', 0)} sample items\n"

    # Add medium priority
    task_list += "\n### 🟡 Medium Priority - Supporting Features\n\n"
    for item in results['accessible']:
        endpoint = item['endpoint']
        if endpoint in medium_priority:
            task_list += f"- [ ] **{endpoint.lstrip('/')}** - {item.get('sample_count', 0)} sample items\n"

    # Add remaining (low priority)
    task_list += "\n### 🟢 Low Priority - Specialized/Advanced\n\n"
    for item in results['accessible']:
        endpoint = item['endpoint']
        if endpoint not in high_priority and endpoint not in medium_priority:
            task_list += f"- [ ] **{endpoint.lstrip('/')}** - {item.get('sample_count', 0)} sample items\n"

    # Add inaccessible for reference
    if results['inaccessible']:
        task_list += "\n---\n\n## ⚠️ Inaccessible Endpoints (Reference Only)\n\n"
        task_list += "These endpoints returned errors and should be investigated separately:\n\n"

        for item in results['inaccessible']:
            endpoint = item['endpoint']
            reason = item.get('reason', 'Unknown')
            task_list += f"- ~~{endpoint.lstrip('/')}~~ - {reason}\n"

    # Add instructions
    task_list += """

---

## 📖 Implementation Instructions

### For Each Endpoint

**Follow**: `docs/guides/adding-endpoints.md` (3,078-line autonomous guide)

**Workflow** (~60 minutes per endpoint):
1. Generate model: `uv run upsales generate-model {endpoint} --partial`
2. Test required fields: `python scripts/test_required_update_fields.py {endpoint}`
3. Enhance model (apply all 12 patterns)
4. Create resource: `uv run upsales init-resource {endpoint}`
5. Copy test template
6. Create integration tests
7. Record VCR cassettes
8. Verify 100% resource coverage
9. Pass all quality checks
10. Mark as complete ✅

### Quality Requirements (Non-Negotiable)

**Every endpoint MUST have**:
- ✅ 100% resource test coverage
- ✅ 100% docstrings (interrogate)
- ✅ All 12 patterns applied
- ✅ VCR cassettes (3+ tests)
- ✅ Type safety (mypy strict)
- ✅ Clean code (ruff pass)

### Validation Tools

**Use these scripts**:
```bash
# Discover required update fields
python scripts/test_required_update_fields.py {endpoint}

# Test field capabilities (sorting, search)
# See: docs/guides/testing-field-capabilities.md

# Validate with real API
uv run pytest tests/integration/test_{endpoint}_integration.py -v
```

### Completion Checklist

When marking an endpoint complete, verify:
- [ ] Model has all 12 patterns
- [ ] Resource has 100% coverage
- [ ] Integration tests recorded
- [ ] All quality checks pass
- [ ] Registered in client
- [ ] Exports updated
- [ ] Committed to git

---

## 📊 Progress Tracking

**Total endpoints**: {len(results['accessible'])}
**Completed**: 5
**Remaining**: {len(results['accessible'])}

**Expected time**: {len(results['accessible'])} endpoints × 60 min = ~{len(results['accessible'])} hours

With sub-agents working in parallel, can be completed much faster!

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Ready for sub-agent implementation
**Guide**: docs/guides/adding-endpoints.md (validated with orderStages)
"""

    with open("ai_temp_files/ENDPOINT_TASK_LIST.md", "w", encoding="utf-8") as f:
        f.write(task_list)


if __name__ == "__main__":
    asyncio.run(test_endpoints())
