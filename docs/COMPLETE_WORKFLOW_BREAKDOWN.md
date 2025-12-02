# Complete Endpoint Implementation Workflow - Token Usage Breakdown

This document provides a comprehensive breakdown of the entire process from API documentation to validated, tested endpoints.

**Last Updated**: 2025-11-14
**Project Status**: 36/167 endpoints implemented (21.6%)
**Remaining**: 131 endpoints

---

## Table of Contents

1. [Project Scope Overview](#project-scope-overview)
2. [Complete Workflow (22 Steps)](#complete-workflow-22-steps)
3. [Token Usage Analysis](#token-usage-analysis)
4. [Optimization Strategies](#optimization-strategies)
5. [Time & Cost Projections](#time--cost-projections)

---

## Project Scope Overview

### What Needs to Be Done

**Total API endpoints**: 167 (documented in `api_endpoints_with_fields.json`)
**Already implemented**: 36 endpoints (21.6%)
**Remaining to implement**: 131 endpoints (78.4%)

### Endpoint Breakdown by Complexity

| Complexity | Count | Criteria | Examples |
|------------|-------|----------|----------|
| **Simple** | 52 (40%) | 0-2 required fields, basic CRUD | currencies, roles, segments |
| **Medium** | 59 (45%) | 3-5 required fields, nested objects | contacts, products, tickets |
| **Complex** | 20 (15%) | 6+ required fields, complex validation | orders, agreements, forms |

### Success Criteria Per Endpoint

For an endpoint to be considered "complete":

1. ✅ **Model file** exists (`upsales/models/{endpoint}.py`)
   - All 12 Pydantic v2 patterns implemented
   - 100% docstring coverage
   - TypedDict for IDE autocomplete
   - Frozen fields marked
   - Validators applied

2. ✅ **Resource file** exists (`upsales/resources/{endpoint}.py`)
   - Inherits from BaseResource
   - Registered in client.py
   - Exported in __init__.py

3. ✅ **Validation completed**
   - CREATE operation tested (required fields identified)
   - UPDATE operation tested (editable vs read-only)
   - DELETE operation tested
   - Search/sort/pagination tested (if applicable)

4. ✅ **Tests passing**
   - Unit tests (100% resource coverage)
   - Integration tests (VCR cassettes recorded)
   - All quality checks passing (ruff, mypy, interrogate)

5. ✅ **Documentation updated**
   - endpoint-map.md marked as verified
   - ENDPOINT_TASK_LIST.md updated
   - Any discrepancies documented

---

## Complete Workflow (22 Steps)

### Phase 1: Setup & Generation (Steps 0-4)

---

#### **STEP 0: Consult API Reference File**

**What happens**:
- Read `api_endpoints_with_fields.json` to understand endpoint
- Extract expected required/optional fields
- Identify CRUD operations supported
- Note any special structures or validation

**Commands**:
```bash
# Option A: Manual extraction
cat api_endpoints_with_fields.json | jq '.endpoints.{endpoint}' > ai_temp_files/{endpoint}_api_spec.json

# Option B: Use extraction script
python scripts/extract_endpoint_info.py {endpoint}
```

**Outputs**:
- `ai_temp_files/{endpoint}_api_spec.json` (50-100 lines)

**Token usage**:
- Reading full API file: **12,000 tokens** (3535 lines)
- Reading extracted spec: **200 tokens** (50 lines)
- **Optimization savings**: 11,800 tokens (98%)

**Time**: 2 minutes (manual) or 30 seconds (scripted)

---

#### **STEP 0a: Verify Environment Setup**

**What happens**:
- Check UPSALES_TOKEN in .env
- Verify uv is installed
- Confirm Python 3.13+

**Commands**:
```bash
# Check token exists
if test -f .env; then grep -E "^UPSALES_TOKEN=" .env; else echo "No .env file"; fi

# Check uv
uv --version

# Check Python
python --version
```

**Token usage**: 500 tokens (reading commands/output)

**Time**: 1 minute

---

#### **STEP 1: Generate Model from API**

**What happens**:
- CLI tool fetches sample data from API
- Generates Pydantic models with Python 3.13 syntax
- Creates TypedDict for IDE autocomplete
- Marks TODOs for review

**Commands**:
```bash
uv run upsales generate-model {endpoint} --partial
```

**Outputs**:
- `upsales/models/{endpoint}.py` (200-400 lines)
  - Main model class
  - Partial model class
  - UpdateFields TypedDict

**Token usage**:
- CLI reading: 1,000 tokens
- Generating code: 3,000 tokens
- Writing file: 2,000 tokens
- **Total**: 6,000 tokens

**Time**: 3-5 minutes

---

#### **STEP 2: Create Resource Manager**

**What happens**:
- CLI generates resource boilerplate
- Inherits from BaseResource[T, P]
- Includes standard CRUD methods

**Commands**:
```bash
uv run upsales init-resource {endpoint}
```

**Outputs**:
- `upsales/resources/{endpoint}.py` (80-120 lines)

**Token usage**:
- CLI execution: 500 tokens
- Template generation: 1,500 tokens
- **Total**: 2,000 tokens

**Time**: 2 minutes

---

#### **STEP 3: Register in Client**

**What happens**:
- Add import to `upsales/client.py`
- Add resource attribute initialization

**Changes**:
```python
# Add import
from upsales.resources.{endpoint} import {Model}sResource

# Add in __init__
self.{endpoint} = {Model}sResource(self.http)
```

**Token usage**:
- Reading client.py: 2,000 tokens (200 lines)
- Making edits: 1,000 tokens
- **Total**: 3,000 tokens

**Time**: 3 minutes

---

#### **STEP 4: Update Exports**

**What happens**:
- Update `upsales/models/__init__.py` with model exports
- Update `upsales/resources/__init__.py` with resource exports

**Changes**:
```python
# upsales/models/__init__.py
from upsales.models.{endpoint} import {Model}, Partial{Model}, {Model}UpdateFields

__all__ = [
    ...
    "{Model}",
    "Partial{Model}",
    "{Model}UpdateFields",
]
```

**Token usage**:
- Reading __init__ files: 1,500 tokens (2 files)
- Making edits: 1,000 tokens
- **Total**: 2,500 tokens

**Time**: 3 minutes

**Phase 1 Total**: 14,000 tokens, ~15 minutes

---

### Phase 2: Validation & Analysis (Steps 5-9)

---

#### **STEP 5: Record VCR Cassette**

**What happens**:
- Create integration test that calls real API
- VCR.py records HTTP interactions
- First run uses real API, subsequent runs replay

**Commands**:
```bash
# Create integration test file
# tests/integration/test_{endpoint}_integration.py

# Run to record cassette
uv run pytest tests/integration/test_{endpoint}_integration.py -v
```

**Outputs**:
- `tests/integration/test_{endpoint}_integration.py` (100-150 lines)
- `tests/cassettes/integration/test_{endpoint}_integration/*.yaml` (VCR cassettes)

**Token usage**:
- Reading test template: 1,500 tokens
- Creating test: 2,000 tokens
- Running test: 500 tokens
- Reading cassette: 1,000 tokens
- **Total**: 5,000 tokens

**Time**: 5 minutes

---

#### **STEP 6: Full CRUD Validation**

**What happens**:
- Test CREATE operation (discover required fields)
- Test UPDATE operation (discover editable vs read-only)
- Test DELETE operation (verify deletion)
- Optional: Test search, sort, pagination

**Commands**:
```bash
# Full validation suite
python scripts/test_full_crud_lifecycle.py {endpoint} --full

# Or individual tests
python scripts/test_required_create_fields.py {endpoint}
python scripts/test_field_editability_bulk.py {endpoint}
python scripts/test_delete_operation.py {endpoint}
```

**Outputs**:
- Console output (500-800 lines)
- Required fields list
- Editable fields list
- Read-only fields list
- Validation status

**Token usage** (traditional):
- Reading validation scripts: 3,000 tokens (952 lines)
- Running scripts: 2,000 tokens
- Reading output: 5,000 tokens (500+ lines)
- **Total**: 10,000 tokens

**Token usage** (optimized with JSON output):
- Running scripts: 1,000 tokens
- Reading JSON output: 500 tokens (20 lines)
- **Total**: 1,500 tokens
- **Savings**: 8,500 tokens (85%)

**Time**: 10-15 minutes (API calls)

---

#### **STEP 7: Analyze VCR Cassette**

**What happens**:
- Compare API file predictions vs actual API response
- Identify discrepancies
- Find fields not in API file
- Verify field types and structures

**Commands**:
```bash
# Manual analysis or use helper script
python ai_temp_files/find_unmapped_fields.py {endpoint}
```

**Outputs**:
- List of discrepancies
- Missing fields report
- Type mismatches

**Token usage**:
- Reading cassette: 2,000 tokens (YAML file)
- Reading API spec: 200 tokens
- Comparing and analyzing: 2,000 tokens
- **Total**: 4,200 tokens

**Time**: 5 minutes

---

#### **STEP 8: Apply Validation Results to Model**

**What happens**:
- Mark frozen=True on read-only fields (id, regDate, modDate, etc.)
- Create {Model}CreateFields TypedDict with required fields
- Update {Model}UpdateFields to exclude frozen fields
- Add field descriptions based on validation

**Changes** (example):
```python
# Before
id: int

# After
id: int = Field(frozen=True, strict=True, description="Unique identifier")

# Add CreateFields
class OrderCreateFields(TypedDict, total=False):
    """Required and optional fields for creating an Order."""
    client: dict[str, Any]  # Required: {"id": number}
    user: dict[str, Any]    # Required: {"id": number}
    stage: dict[str, Any]   # Required: {"id": number}
    date: str               # Required: YYYY-MM-DD
    orderRow: list[dict]    # Required: [{"product": {"id": number}}]
```

**Token usage**:
- Reading validation results: 500 tokens (JSON) or 5,000 tokens (verbose)
- Reading model file: 2,500 tokens (250 lines)
- Updating model: 3,000 tokens (multiple edits)
- **Total**: 6,000 tokens (JSON) or 10,500 tokens (verbose)

**Time**: 10 minutes

---

#### **STEP 9: Document Always-Returned Fields**

**What happens**:
- Identify tracking fields always returned (id, regDate, modDate)
- Document in model docstring
- Note any special fields

**Token usage**: 1,000 tokens

**Time**: 2 minutes

**Phase 2 Total**: 26,200 tokens (traditional) or 17,700 tokens (optimized), ~35 minutes

---

### Phase 3: Model Enhancement (Steps 10-16)

---

#### **STEP 10: Add Reusable Validators**

**What happens**:
- Map field types to validators (BinaryFlag, EmailStr, etc.)
- Replace generic types with semantic validators
- Import from upsales.validators

**Changes**:
```python
# Before
active: int

# After
from upsales.validators import BinaryFlag
active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

# Before
email: str

# After
from upsales.validators import EmailStr
email: EmailStr = Field(description="Email address")
```

**Token usage**:
- Reading validators.py: 1,000 tokens
- Reading model: 2,500 tokens
- Updating fields: 2,000 tokens
- **Total**: 5,500 tokens

**Time**: 8 minutes

---

#### **STEP 11: Add Computed Fields**

**What happens**:
- Add @computed_field + @property for derived values
- Standard: custom_fields property (for custom field access)
- Standard: is_active, is_admin (boolean helpers)
- Custom: Business logic properties

**Changes**:
```python
@computed_field
@property
def custom_fields(self) -> CustomFields:
    """Access custom fields with dict-like interface."""
    return CustomFields(self.custom)

@computed_field
@property
def is_active(self) -> bool:
    """Check if entity is active."""
    return self.active == 1
```

**Token usage**:
- Reading patterns: 1,500 tokens
- Reading model: 2,500 tokens
- Adding properties: 2,500 tokens
- **Total**: 6,500 tokens

**Time**: 10 minutes

---

#### **STEP 12: Add Field Serializer**

**What happens**:
- Add @field_serializer for custom fields
- Clean custom fields before API requests
- Remove empty values

**Changes**:
```python
@field_serializer('custom', when_used='json')
def serialize_custom_fields(self, custom: list[dict]) -> list[dict]:
    """Clean custom fields for API requests."""
    return [
        {"fieldId": item["fieldId"], "value": item.get("value")}
        for item in custom
        if "value" in item and item.get("value") is not None
    ]
```

**Token usage**:
- Reading pattern: 500 tokens
- Reading model: 2,500 tokens
- Adding serializer: 1,500 tokens
- **Total**: 4,500 tokens

**Time**: 5 minutes

---

#### **STEP 13: Verify TypedDict Completeness**

**What happens**:
- Check UpdateFields has all editable fields
- Check CreateFields has all required fields
- Verify type annotations are correct

**Token usage**:
- Reading validation results: 500 tokens
- Reading model: 2,500 tokens
- Verification: 1,000 tokens
- **Total**: 4,000 tokens

**Time**: 5 minutes

---

#### **STEP 14: Implement edit() Method**

**What happens**:
- Add instance method for updating object
- Use Unpack[UpdateFields] for IDE autocomplete
- Use to_api_dict() for serialization

**Changes**:
```python
async def edit(self, **kwargs: Unpack[{Model}UpdateFields]) -> "{Model}":
    """
    Edit this {model} with type-safe field updates.

    Args:
        **kwargs: Fields to update (IDE autocomplete available)

    Returns:
        Updated {model} object
    """
    if not self._client:
        raise RuntimeError("No client available")
    return await self._client.{endpoint}.update(
        self.id,
        **self.to_api_dict(**kwargs)
    )
```

**Token usage**:
- Reading pattern: 800 tokens
- Reading model: 2,500 tokens
- Adding method: 1,500 tokens
- **Total**: 4,800 tokens

**Time**: 5 minutes

---

#### **STEP 15: Enhance Partial Model**

**What happens**:
- Implement fetch_full() method
- Implement edit() method
- Add docstring with usage example

**Changes**:
```python
class Partial{Model}(PartialModel):
    id: int
    name: str

    async def fetch_full(self) -> {Model}:
        """Fetch complete object from API."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{endpoint}.get(self.id)

    async def edit(self, **kwargs) -> {Model}:
        """Edit and return full object."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{endpoint}.update(self.id, **kwargs)
```

**Token usage**: 3,000 tokens

**Time**: 5 minutes

---

#### **STEP 16: Add Custom Resource Methods**

**What happens**:
- Add endpoint-specific convenience methods
- Examples: get_active(), get_by_email(), get_administrators()
- Based on common use cases

**Changes**:
```python
class {Model}sResource(BaseResource[{Model}, Partial{Model}]):
    # ... inherited methods ...

    async def get_active(self) -> list[{Model}]:
        """Get all active {models}."""
        return await self.list_all(active=1)

    async def get_by_name(self, name: str) -> {Model} | None:
        """Find {model} by name."""
        results = await self.search(name=name)
        return results[0] if results else None
```

**Token usage**:
- Reading resource patterns: 1,500 tokens
- Reading resource file: 1,500 tokens
- Adding methods: 2,500 tokens
- **Total**: 5,500 tokens

**Time**: 10 minutes

**Phase 3 Total**: 34,300 tokens, ~50 minutes

---

### Phase 4: Testing (Steps 17-21)

---

#### **STEP 17: Create Unit Tests from Template**

**What happens**:
- Copy `tests/templates/resource_template.py`
- Customize for endpoint
- Test all CRUD operations
- Test search, bulk operations

**Commands**:
```bash
# Copy and customize template
cp tests/templates/resource_template.py tests/unit/test_{endpoint}_resource.py

# Edit to customize
# Replace placeholders with actual endpoint name
```

**Outputs**:
- `tests/unit/test_{endpoint}_resource.py` (200-300 lines)

**Token usage**:
- Reading template: 2,500 tokens
- Customizing: 2,000 tokens
- Writing file: 2,500 tokens
- **Total**: 7,000 tokens

**Time**: 10 minutes

---

#### **STEP 18: Run Unit Tests**

**What happens**:
- Execute pytest on new tests
- Verify all tests pass
- Check coverage

**Commands**:
```bash
uv run pytest tests/unit/test_{endpoint}_resource.py -v --cov=upsales.resources.{endpoint}
```

**Outputs**:
- Test results
- Coverage report

**Token usage**:
- Running tests: 500 tokens
- Reading output: 1,500 tokens
- **Total**: 2,000 tokens

**Time**: 3 minutes

---

#### **STEP 19: Expand Integration Tests**

**What happens**:
- Add more integration test scenarios
- Test edge cases
- Ensure VCR cassettes cover all operations

**Commands**:
```bash
# Edit integration test file
# Add more test functions

# Re-record cassettes
rm tests/cassettes/integration/test_{endpoint}_integration/*.yaml
uv run pytest tests/integration/test_{endpoint}_integration.py -v
```

**Token usage**:
- Reading existing tests: 2,000 tokens
- Adding scenarios: 2,500 tokens
- Running tests: 500 tokens
- **Total**: 5,000 tokens

**Time**: 10 minutes

---

#### **STEP 20: Verify VCR Tests Work Offline**

**What happens**:
- Run integration tests WITHOUT API access
- Ensure cassettes replay correctly
- Verify no live API calls made

**Commands**:
```bash
# Temporarily remove token
export UPSALES_TOKEN=""

# Run tests (should work from cassettes)
uv run pytest tests/integration/test_{endpoint}_integration.py -v

# Restore token
export UPSALES_TOKEN="<token>"
```

**Token usage**: 1,000 tokens

**Time**: 2 minutes

---

#### **STEP 21: Run All Quality Checks**

**What happens**:
- Run ruff (formatting & linting)
- Run mypy (type checking)
- Run interrogate (docstring coverage)
- All must pass 100%

**Commands**:
```bash
# Format
uv run ruff format upsales/models/{endpoint}.py upsales/resources/{endpoint}.py

# Lint
uv run ruff check upsales/models/{endpoint}.py upsales/resources/{endpoint}.py

# Type check
uv run mypy upsales/models/{endpoint}.py upsales/resources/{endpoint}.py

# Docstring coverage
uv run interrogate upsales/models/{endpoint}.py upsales/resources/{endpoint}.py
```

**Token usage**:
- Running tools: 1,000 tokens
- Reading output: 1,500 tokens
- **Total**: 2,500 tokens

**Time**: 5 minutes

**Phase 4 Total**: 17,500 tokens, ~30 minutes

---

### Phase 5: Documentation (Step 22)

---

#### **STEP 22: Update Documentation**

**What happens**:
- Update `docs/endpoint-map.md` with verification status
- Update `ENDPOINT_TASK_LIST.md` to move from "unimplemented" to "verified"
- Document any discrepancies found
- Add to statistics

**Changes**:
```markdown
# docs/endpoint-map.md

### {Endpoint}
**Status**: ✅ Verified
**API**: `/{endpoint}`
**Models**: `{Model}`, `Partial{Model}`
**Client**: `upsales.{endpoint}`

**CREATE**: {required_fields_count} required fields
**UPDATE**: {editable_fields_count} editable, {readonly_count} read-only
**DELETE**: Supported

**Discrepancies**:
- Field X: API file says optional, actually required
- Field Y: Returns as string, documented as number
```

**Token usage**:
- Reading endpoint-map.md: 4,000 tokens (800 lines)
- Finding section: 1,000 tokens
- Updating: 2,000 tokens
- Reading task list: 3,000 tokens (600 lines)
- Updating: 1,500 tokens
- **Total**: 11,500 tokens

**Token usage** (optimized - targeted edits):
- Reading only relevant section: 500 tokens
- Making edits: 1,000 tokens
- **Total**: 1,500 tokens
- **Savings**: 10,000 tokens (87%)

**Time**: 5 minutes

**Phase 5 Total**: 11,500 tokens (traditional) or 1,500 tokens (optimized), ~5 minutes

---

## Complete Workflow Summary

### Token Usage by Phase (Traditional Approach)

| Phase | Steps | Tokens | Time | % of Total |
|-------|-------|--------|------|------------|
| **Phase 1: Setup** | 0-4 | 14,000 | 15 min | 14% |
| **Phase 2: Validation** | 5-9 | 26,200 | 35 min | 26% |
| **Phase 3: Enhancement** | 10-16 | 34,300 | 50 min | 34% |
| **Phase 4: Testing** | 17-21 | 17,500 | 30 min | 17% |
| **Phase 5: Documentation** | 22 | 11,500 | 5 min | 11% |
| **TOTAL** | 22 | **103,500** | **135 min** | 100% |

### Token Usage by Phase (Optimized with Sub-Agents)

| Phase | Steps | Tokens | Time | % of Total |
|-------|-------|--------|------|------------|
| **Phase 1: Setup** | 0-4 | 14,000 | 15 min | 32% |
| **Phase 2: Validation** | 5-9 | 17,700 | 35 min | 41% |
| **Phase 3: Enhancement** | 10-16 | 34,300 | 50 min | 79% |
| **Phase 4: Testing** | 17-21 | 17,500 | 30 min | 40% |
| **Phase 5: Documentation** | 22 | 1,500 | 5 min | 3% |
| **Sub-agent isolation** | - | -60,000 | - | -138% |
| **TOTAL (Parent context)** | 22 | **25,000** | **135 min** | 100% |
| **TOTAL (Sub-agent work)** | 22 | **43,500** | **50 min** | - |

**Explanation of sub-agent optimization**:
- Parent spawns sub-agent with 2K context
- Sub-agent does 43.5K of work internally
- Sub-agent returns 1K report
- Parent's context only grows by 1K (not 43.5K!)

---

## Token Usage Analysis

### Per-Endpoint Breakdown

#### Traditional (Single-Threaded Agent)

**Context loaded once**:
- CLAUDE.md: 6,000 tokens
- API file (full): 12,000 tokens
- Validation scripts: 3,000 tokens
- Documentation files: 7,000 tokens
- **Subtotal**: 28,000 tokens

**Work performed**:
- Generate & setup: 14,000 tokens
- Validate & analyze: 26,200 tokens
- Enhance model: 34,300 tokens
- Create tests: 17,500 tokens
- Update docs: 11,500 tokens
- **Subtotal**: 103,500 tokens

**Total per endpoint**: 28,000 + 103,500 = **131,500 tokens**

---

#### Optimized (Sub-Agent Spawning)

**Parent context** (grows minimally):
- Initial: 10,000 tokens (orchestrator setup)
- Spawn sub-agent: +500 tokens (prompt)
- Receive report: +1,000 tokens (completion report)
- **Parent total**: 11,500 tokens

**Sub-agent context** (isolated, not added to parent):
- Inherited conversation: 10,000 tokens (read-only)
- Endpoint context files: 1,500 tokens (API spec + checklist)
- Work performed: 43,500 tokens (all 22 steps)
- **Sub-agent total**: 55,000 tokens (NOT added to parent!)

**Effective cost to parent**: 11,500 tokens (just orchestration)
**Actual work done**: 55,000 tokens (in isolated sub-agent)

**Key insight**: Parent pays for 11.5K, gets 55K of work done!

---

#### Further Optimized (Pre-Computed Context)

**Parent context**:
- Orchestrator setup: 5,000 tokens (minimal)
- Spawn sub-agent: +500 tokens
- Receive report: +500 tokens (JSON format)
- **Parent total**: 6,000 tokens

**Sub-agent context**:
- Endpoint-specific only: 1,500 tokens
- Work performed: 25,000 tokens (using pre-computed refs)
- **Sub-agent total**: 26,500 tokens

**Best case**: Parent 6K, Sub-agent 26.5K

---

### For 131 Endpoints

| Approach | Tokens/Endpoint | Total Tokens | Parent Context Growth |
|----------|----------------|--------------|----------------------|
| **Traditional (Single-threaded)** | 131,500 | 17.2M | 17.2M (all in one session) |
| **Sub-agents (Basic)** | 11,500 parent + 55K sub | 1.5M + 7.2M | 1.5M (131 × 11.5K) |
| **Sub-agents (Optimized)** | 6,000 parent + 26.5K sub | 786K + 3.5M | 786K (131 × 6K) |
| **Batched Sub-agents** | 20K batch + 26.5K per sub | 260K + 3.5M | 260K (13 batches × 20K) |

**Best approach**: Batched sub-agents
- **Your context**: 260K tokens total (spread across 13 sessions)
- **Sub-agents**: 3.5M tokens (but isolated, not added to yours)
- **Per batch session**: ~20K tokens (stays under 200K threshold!)

---

## Optimization Strategies

### Strategy 1: Pre-Compute All Context Files

**Before starting batch**:
```bash
# Extract all API specs (5 minutes, one-time)
python scripts/extract_endpoint_info.py --all

# Generates 167 × 1KB files = 167KB total
# vs reading 138KB file 167 times = 23MB
```

**Savings**: 11,000 tokens per endpoint × 131 = 1.44M tokens

---

### Strategy 2: JSON Output Mode for Scripts

**Add to validation scripts**:
```python
parser.add_argument("--format", choices=["human", "json"], default="human")

if args.format == "json":
    output = {"required": [...], "editable": [...], "readonly": [...]}
    print(json.dumps(output))
```

**Savings**: 4,500 tokens per endpoint × 131 = 589K tokens

---

### Strategy 3: Batch Processing (10 endpoints)

**Session 1**: Orchestrate batch 1
- Context: 20K tokens
- Spawns 10 sub-agents
- Receives 10 reports

**Session 2**: Orchestrate batch 2
- Fresh session: 20K tokens
- Spawns 10 sub-agents
- Receives 10 reports

**Benefit**: Each session stays under 200K tokens (standard pricing!)

**Savings**: Avoids premium pricing (50% cost reduction on your context)

---

### Strategy 4: Parallel Sub-Agent Execution

**Sequential** (10 endpoints):
- Time: 10 × 50 min = 500 minutes (8.3 hours)

**Parallel** (10 endpoints):
- Time: max(50, 50, 50, ...) = 50 minutes (10× faster!)

**Same token cost, 10× faster!**

---

## Time & Cost Projections

### Time Investment Breakdown

#### Per Endpoint (Average)

| Approach | AI Time | Human Time | Total | Parallelizable |
|----------|---------|------------|-------|----------------|
| **Manual (no AI)** | 0 min | 90 min | 90 min | No |
| **Traditional agent** | 80 min | 10 min | 90 min | No |
| **Sub-agent** | 50 min | 5 min | 55 min | Yes! |
| **Sub-agent optimized** | 35 min | 3 min | 38 min | Yes! |

#### For 131 Endpoints

| Approach | AI Time | Human Time | Total Time | Calendar Time |
|----------|---------|------------|------------|---------------|
| **Manual** | 0 | 196 hours | 196 hours | 5 weeks |
| **Traditional** | 175 hours | 22 hours | 197 hours | 5 weeks |
| **Sub-agents (sequential)** | 109 hours | 11 hours | 120 hours | 3 weeks |
| **Sub-agents (10 parallel)** | 109 hours | 11 hours | 120 hours | **13 batches × 50 min = 11 hours!** |

**Calendar time with parallel sub-agents**: 11 hours of AI work + 7 hours human review = **18 hours total**

---

### Cost Projections

#### Token Costs (Claude Sonnet 4.5)

**Pricing**:
- Under 200K tokens: $3/M input, $15/M output
- Over 200K tokens: $6/M input, $22.50/M output

---

#### Traditional Approach (Single Session, All Endpoints)

```
Session starts: 10K tokens
Process 131 endpoints: +17.2M tokens
Final context: 17.21M tokens (MASSIVE, hits premium tier immediately)

Cost:
- Input: 17.2M × $6/M = $103.20
- Output: ~2M × $22.50/M = $45.00
Total: $148.20
```

**❌ VERY EXPENSIVE** and likely hits context limits

---

#### Sub-Agent Approach (Batched, 13 Sessions)

```
Batch 1:
  Parent session: 20K tokens (standard rate)
  10 sub-agents: 10 × 26.5K = 265K tokens (10 separate sessions, standard rate each)

  Parent cost: 20K × $3/M = $0.06
  Sub-agents: 10 × (26.5K × $3/M) = $0.795
  Batch total: $0.855

13 batches: 13 × $0.855 = $11.12
```

**✅ Much cheaper!**

---

#### Optimized Sub-Agent Approach (Pre-computed Context)

```
Batch 1:
  Parent session: 20K tokens
  10 sub-agents: 10 × 15K = 150K tokens

  Parent cost: 20K × $3/M = $0.06
  Sub-agents: 10 × (15K × $3/M) = $0.45
  Batch total: $0.51

13 batches: 13 × $0.51 = $6.63
```

**✅ BEST - Only $6.63 for all 131 endpoints!**

---

### Cost Comparison Summary

| Approach | Total Tokens | Total Cost | Cost/Endpoint |
|----------|--------------|------------|---------------|
| **Traditional (single session)** | 17.21M | $148.20 | $1.13 |
| **Sub-agents (batched)** | 3.76M | $11.12 | $0.085 |
| **Sub-agents (optimized)** | 2.22M | $6.63 | $0.051 |

**Savings**: $141.57 (95% cost reduction) with optimized approach!

---

## Full Scope: What Gets Built

### Files Created Per Endpoint (14 files)

1. **Model file**: `upsales/models/{endpoint}.py` (300-400 lines)
2. **Resource file**: `upsales/resources/{endpoint}.py` (100-150 lines)
3. **Unit test**: `tests/unit/test_{endpoint}_resource.py` (250-350 lines)
4. **Integration test**: `tests/integration/test_{endpoint}_integration.py` (100-200 lines)
5. **VCR cassettes**: `tests/cassettes/integration/test_{endpoint}_integration/*.yaml` (3-5 files)
6. **API spec**: `ai_temp_files/{endpoint}_api_spec.json` (50-100 lines)
7. **Context files**: `ai_temp_files/{endpoint}_context/*` (4 files)
8. **Validation output**: `ai_temp_files/{endpoint}_validation_summary.txt`
9. **Completion report**: `ai_temp_files/{endpoint}_completion_report.json`

### Files Modified Per Endpoint (4 files)

10. **Client**: `upsales/client.py` (+3 lines)
11. **Models exports**: `upsales/models/__init__.py` (+4 lines)
12. **Resources exports**: `upsales/resources/__init__.py` (+2 lines)
13. **Endpoint map**: `docs/endpoint-map.md` (+15 lines)
14. **Task list**: `ENDPOINT_TASK_LIST.md` (+5 lines)

### Total for 131 Endpoints

**New files**: 131 × 9 files = **1,179 files**
**Modified files**: 5 files (many times)
**Lines of code**: 131 × ~1,000 lines = **~131,000 lines**
**Test coverage**: 131 × 15 tests = **~1,965 tests**

---

## Workflow Comparison Matrix

| Metric | Manual | Traditional Agent | Sub-Agent (Sequential) | Sub-Agent (Parallel) |
|--------|--------|-------------------|----------------------|---------------------|
| **Total time** | 196 hours | 197 hours | 120 hours | 18 hours |
| **Your time** | 196 hours | 22 hours | 11 hours | 7 hours |
| **AI time** | 0 | 175 hours | 109 hours | 11 hours (parallel!) |
| **Token usage** | 0 | 17.2M | 8.7M | 3.76M |
| **Cost** | $0 | $148 | $75 | $11.12 |
| **Context growth** | N/A | 17.2M | 1.5M | 260K (batched) |
| **Quality** | ✅ High | ✅ High | ✅ High | ✅ High |
| **Tedium** | ❌ Very high | ⚠️ Medium | ⚠️ Low | ✅ Minimal |

**Winner**: Sub-Agent Parallel (Batched)
- 18 hours calendar time (vs 5 weeks manual)
- 7 hours of your actual work
- $11.12 total cost
- Maintains quality
- Minimal tedium

---

## Recommended Execution Plan

### Week 1: Pilot (20 Endpoints, Batches 1-2)

**Monday**:
```bash
# Prepare batch 1
python ai_temp_files/orchestrate_endpoints.py --batch 1 --execute

# Give Claude the printed prompt
# Claude spawns 10 sub-agents in parallel
# Wait ~50 minutes
```

**Monday afternoon**: Review batch 1 results (30 min)

**Tuesday**: Same for batch 2

**Wednesday**: Fix any issues from batches 1-2

**Results**: 20 endpoints done, validate approach works

---

### Weeks 2-3: Production (91 Endpoints, Batches 3-11)

**Daily routine**:
- Morning: Prepare batch, launch Claude (15 min)
- Wait: 50 minutes (Claude works)
- Review: 30 minutes
- Repeat: 1 batch per day

**Cadence**: 10 endpoints/day × 5 days/week = 50 endpoints/week

**Results**: 91 endpoints in 2 weeks

---

### Week 4: Cleanup (20 Endpoints + Fixes, Batches 12-13)

**Tasks**:
- Remaining simple endpoints (batches 12-13)
- Fix partial successes from previous batches
- Manual implementation of complex endpoints
- Final quality checks
- Documentation review

**Results**: All 131 endpoints complete

---

## Expected Outcomes

### Success Rate Projections

Based on complexity analysis:

**Full Success** (70% = 92 endpoints):
- All 22 steps completed
- Tests passing 100%
- Quality checks passing 100%
- Documentation complete

**Partial Success** (20% = 26 endpoints):
- Basic structure complete (steps 1-9)
- Validation done
- Manual enhancement needed for:
  - Complex computed fields
  - Custom business logic methods
  - Edge case handling

**Needs Manual Work** (10% = 13 endpoints):
- Too complex for automation
- Special patterns required
- Examples: Complex nested structures, circular references

---

### Quality Metrics Targets

**Code Quality**:
- ✅ ruff format: 100% (automated)
- ✅ ruff check: 100% (automated)
- ✅ mypy strict: 100% (target)
- ✅ interrogate: 100% (required)

**Test Coverage**:
- ✅ Resource methods: 100% (inherited from BaseResource)
- ✅ Unit tests: 100% (generated from template)
- ✅ Integration tests: 95%+ (VCR cassettes)
- ✅ Overall coverage: 85%+ (target)

**Documentation**:
- ✅ All endpoints in endpoint-map.md
- ✅ All marked with verification status
- ✅ Discrepancies documented
- ✅ Statistics updated

---

## Token Usage Summary

### Best Case (Optimized Sub-Agents, Batched)

**For 131 endpoints in 13 batches**:

**Your sessions** (13 batch sessions):
- 13 batches × 20K tokens = 260K tokens
- Cost: 260K × $3/M = $0.78 (all under 200K threshold!)

**Sub-agent work** (131 endpoint workers):
- 131 agents × 26.5K tokens = 3.47M tokens
- Cost: 3.47M × $3/M = $10.41 (each under 200K threshold!)

**Total**:
- Tokens: 3.73M
- Cost: $11.19
- Time: 18 hours (11 hours AI + 7 hours human)

---

### Worst Case (Traditional Single Session)

**One massive session**:
- Tokens: 17.2M (exceeds 1M context limit!)
- Cost: ~$150+ (premium pricing)
- Time: 197 hours
- **Not feasible** - would hit context window limits

---

## Conclusion: The Optimal Workflow

### The Winning Approach

**Batched Sub-Agent Execution**:

1. ✅ **Pre-compute all context** (1 hour, one-time)
   ```bash
   python scripts/extract_endpoint_info.py --all
   ```

2. ✅ **Process in batches of 10** (13 batches total)
   ```bash
   # For each batch
   python ai_temp_files/orchestrate_endpoints.py --batch N --execute
   # Give Claude the printed prompt
   # Claude spawns 10 parallel sub-agents
   # Wait 50 minutes
   # Review results (30 minutes)
   ```

3. ✅ **Human checkpoints** (after each batch)
   - Review completion reports
   - Fix critical issues
   - Approve next batch

4. ✅ **Final cleanup** (week 4)
   - Fix partial successes
   - Manual work on complex endpoints
   - Full regression testing

### Results

**Time**: 18 hours total (11 AI + 7 human)
**Cost**: $11.19
**Quality**: Same as manual (automated validation)
**Coverage**: 131 endpoints implemented
**Your effort**: 7 hours of actual work vs 196 hours manual

---

## Next Steps

1. **Review this breakdown** - Understand the full scope
2. **Run pilot batch** - Test with batch 1 (10 endpoints)
3. **Refine orchestration** - Based on pilot results
4. **Execute production batches** - 11 more batches
5. **Final quality review** - Ensure everything works

**You're ready to implement 131 endpoints in ~18 hours!** 🚀
