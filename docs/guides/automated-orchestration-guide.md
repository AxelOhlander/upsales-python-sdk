# Automated Endpoint Implementation - User Guide

This guide explains how to use the orchestration system to implement 131+ endpoints with minimal manual effort.

## Overview

The orchestration system allows Claude to autonomously implement multiple endpoints by:
1. Creating focused context files per endpoint (saves 11K tokens each)
2. Generating workflow instructions
3. Spawning task-specific agents
4. Tracking progress across batches
5. Providing checkpoints for human review

**Time savings**: 64% (51 hours vs 142 hours manual)
**Token savings**: 78% (1.97M vs 9.17M tokens)

---

## Quick Start

### Step 1: Generate Implementation Plan

```bash
python ai_temp_files/orchestrate_endpoints.py --plan
```

**Output**:
- Prioritized list of 167 endpoints
- Organized into batches of 10
- Time estimates per batch
- Saves plan to `ai_temp_files/implementation_plan.json`

---

### Step 2: Prepare First Batch

```bash
python ai_temp_files/orchestrate_endpoints.py --batch 1 --dry-run
```

**What this does**:
1. Extracts API specs for 10 endpoints (lightweight, 50 lines each)
2. Creates context directories with workflow checklists
3. Generates patterns reference (no need to read full CLAUDE.md)
4. Finds similar endpoints for reference
5. Creates batch instructions file

**Output**:
- `ai_temp_files/{endpoint}_api_spec.json` for each endpoint
- `ai_temp_files/{endpoint}_context/` directory for each
- `ai_temp_files/batch_1/batch_instructions.md`

---

### Step 3: Execute Batch with Claude

**Prompt Claude**:
```
Read ai_temp_files/batch_1/batch_instructions.md

For each of the 10 endpoints in this batch:
1. Read the endpoint-specific context files in ai_temp_files/{endpoint}_context/
2. Follow the workflow checklist autonomously
3. Create completion report: ai_temp_files/{endpoint}_completion_report.json

Work through all 10 endpoints systematically. Report progress after each endpoint.
```

**What Claude will do**:
- Implement each endpoint following the 22-step workflow
- Run validation scripts automatically
- Apply results to models
- Create and run tests
- Update documentation
- Generate completion reports

**Your role**: Monitor progress, intervene only if critical failures occur

---

### Step 4: Review Batch Results

After Claude completes the batch:

```bash
# Check completion reports
ls ai_temp_files/*_completion_report.json

# Read batch summary (Claude should create this)
cat ai_temp_files/batch_1_summary.md
```

**Review**:
- How many succeeded (target: 70-80%)
- How many need manual work (target: 15-25%)
- Any systematic failures (target: <5%)

---

### Step 5: Fix Issues & Proceed

**If 80%+ success rate**:
```bash
# Proceed to next batch
python ai_temp_files/orchestrate_endpoints.py --batch 2 --execute
```

**If <70% success rate**:
- Review failures
- Adjust orchestration strategy
- Retry failed endpoints manually
- Then proceed to next batch

---

## Workflow Details

### Context Files Created Per Endpoint

Each endpoint gets a focused context bundle (~300 lines total vs 5000+):

```
ai_temp_files/{endpoint}_context/
├── workflow_checklist.md (80 lines) - Step-by-step instructions
├── patterns.md (150 lines) - Essential patterns only
├── similar_endpoints.md (20 lines) - Examples to follow
└── (reads) ../{endpoint}_api_spec.json (50 lines) - API data

Total: ~300 lines (vs 5235 if reading CLAUDE.md + API file)
Token savings: 18K per endpoint
```

### Agent Prompt Template

The orchestrator generates prompts like this for each endpoint:

```markdown
# AUTONOMOUS TASK: Implement {endpoint} Endpoint

## Context Files (Read These Only)
1. ai_temp_files/{endpoint}_context/workflow_checklist.md
2. ai_temp_files/{endpoint}_context/patterns.md
3. ai_temp_files/{endpoint}_api_spec.json

DO NOT read CLAUDE.md or full api_endpoints_with_fields.json

## Mission
Follow the workflow checklist step-by-step autonomously

## Reporting
Create: ai_temp_files/{endpoint}_completion_report.json
```

This gives Claude:
- ✅ Exactly what it needs
- ✅ Clear, focused task
- ✅ Minimal context (saves tokens)
- ✅ Structured output for tracking

---

## Batch Processing Strategy

### Batch Size: 10 Endpoints

**Why 10?**
- Manageable checkpoint (~8 hours work)
- Failure isolation (1 bad endpoint doesn't cascade)
- Human review cadence (2-3 times per week)
- Token budget (~150K per batch)

### Batch Priorities

The orchestrator prioritizes endpoints by:
1. **Simple first** (0-2 required fields)
2. **CRUD-capable** (has CREATE, UPDATE, DELETE)
3. **Well-documented** (in API file)

Complex endpoints (10+ required fields) come later after patterns established.

---

## Human Intervention Points

### Checkpoint A: After Each Batch (Every 10 Endpoints)

**Review**:
- Completion reports (success/partial/failed counts)
- Quality metrics (test coverage, type checking)
- Systematic issues (same failure pattern)

**Decision**:
- ✅ Proceed to next batch (if 70%+ success)
- ⚠️ Fix issues first (if 50-70% success)
- ❌ Stop and reassess (if <50% success)

**Time**: 30 minutes per checkpoint

---

### Checkpoint B: Complex Endpoints (~20%)

Some endpoints may need manual attention:
- 10+ required fields
- Complex nested structures
- Circular references
- Special business logic

**Orchestrator marks these**: "Status: needs_human_review"

**Your action**: Implement manually or guide Claude specifically

---

### Checkpoint C: Final Quality Gate

After all batches:
```bash
# Run full test suite
uv run pytest

# Run quality checks
uv run ruff check .
uv run mypy upsales
uv run interrogate upsales

# Review statistics
python ai_temp_files/generate_final_report.py
```

**Verify**:
- All tests passing
- No quality check failures
- Documentation complete
- Coverage at 100%

---

## Expected Outcomes

### Success Rates (Based on Analysis)

**Tier 1: Full Success** (Target: 70%)
- All 22 steps completed
- Tests passing
- Quality checks passing
- Documentation updated
- ~92 endpoints

**Tier 2: Partial Success** (Target: 20%)
- Basic structure complete
- Validation done
- Manual enhancement needed
- ~26 endpoints

**Tier 3: Needs Manual Work** (Target: 10%)
- Too complex for automation
- Special logic required
- ~13 endpoints

---

## Time Breakdown

### Per Endpoint

**Automated**: 45-50 minutes (Claude working)
**Human review**: 2-3 minutes (checking completion report)

### Per Batch (10 Endpoints)

**Automated**: 7-8 hours (Claude working)
**Human review**: 30 minutes (checkpoint review)

### Full Implementation (131 Endpoints)

**Preparation**: 8 hours (one-time, building orchestrator)
**Automated work**: ~40 hours (Claude implementing)
**Human checkpoints**: ~7 hours (13 batches × 30 min)
**Issue resolution**: ~10 hours (contingency)

**Total**: ~65 hours (vs 142 manual) - **54% time savings**

---

## Token Usage

### Per Endpoint

**Traditional approach**:
- Reads CLAUDE.md (1418 lines) = 6K tokens
- Reads api_endpoints_with_fields.json (3535 lines) = 12K tokens
- Processes workflow = 20K tokens
- **Total: ~38K tokens**

**Orchestrated approach**:
- Reads context bundle (300 lines) = 1.4K tokens
- Reads API spec (50 lines) = 0.2K tokens
- Processes workflow = 13K tokens
- **Total: ~15K tokens**

**Savings**: 23K tokens per endpoint (61% reduction)

### For 131 Endpoints

**Traditional**: 131 × 38K = 4.98M tokens
**Orchestrated**: 131 × 15K = 1.97M tokens
**Savings**: 3.01M tokens (60% reduction)

---

## Example: Running Batch 1

```bash
# Step 1: Prepare batch
python ai_temp_files/orchestrate_endpoints.py --batch 1 --execute

# Output:
📦 Preparing Batch 1...
  - Extracting API spec: accounts
  - Extracting API spec: contacts
  [... 8 more ...]
✅ Batch 1 prepared
   Instructions: ai_temp_files/batch_1/batch_instructions.md
   Endpoints: 10

🚀 Ready for execution

Prompt: 'Read ai_temp_files/batch_1/batch_instructions.md and implement
        all 10 endpoints following the workflow checklist for each one.'
```

```
# Step 2: Tell Claude
"Read ai_temp_files/batch_1/batch_instructions.md and implement all 10 endpoints
 following the workflow checklist for each one. Report progress after each endpoint."
```

```
# Step 3: Claude works autonomously (7-8 hours)
Claude: "Starting accounts endpoint..."
Claude: "✅ accounts completed in 45 min - tests passing"
Claude: "Starting contacts endpoint..."
Claude: "✅ contacts completed in 52 min - tests passing"
[... continues for all 10 ...]
Claude: "Batch 1 complete: 8/10 success, 2 partial"
```

```
# Step 4: Review results (30 min)
cat ai_temp_files/batch_1_summary.md

# See what needs attention
grep -l "partial\|failed" ai_temp_files/*_completion_report.json
```

```
# Step 5: Proceed to next batch
python ai_temp_files/orchestrate_endpoints.py --batch 2 --execute
```

---

## Handling Failures

### Graceful Degradation Levels

**Level 1: Full Success** - Everything works
- Model generated ✅
- Validation passed ✅
- Tests passing ✅
- Quality checks passing ✅
- Documentation updated ✅

**Level 2: Partial Success** - Basic structure works
- Model generated ✅
- Validation attempted ✅ (may have issues)
- Tests mostly passing ⚠️
- Needs manual enhancement

**Level 3: Minimal Success** - Structure only
- Model generated ✅
- Resource created ✅
- Registered in client ✅
- Everything else needs manual work

**Level 4: Failure** - Skip for now
- Generation failed ❌
- Complex structure ❌
- Marked for manual implementation

### Claude's Failure Handling

Claude will:
1. Attempt all steps in workflow
2. If step fails critically, mark it in report
3. Continue to next achievable step (don't get stuck)
4. Generate completion report with status and issues
5. Move to next endpoint in batch

**You will**:
- Review failures after batch
- Decide if worth manual fix now or later
- Approve next batch or address issues

---

## Best Practices

### DO:

✅ **Review each batch checkpoint**
- Don't skip the 30-min review
- Catch systematic errors early
- Adjust strategy based on patterns

✅ **Start with simple batches first**
- Build confidence in orchestration
- Refine workflow based on results
- Save complex endpoints for later

✅ **Keep quality standards high**
- Don't accept partial success as "good enough"
- Mark partial endpoints for enhancement
- Maintain 100% test coverage requirement

✅ **Track metrics**
- Success rates by batch
- Time per endpoint
- Common failure modes
- Token usage

### DON'T:

❌ **Don't run all 17 batches at once**
- Process in manageable chunks
- Review and learn between batches

❌ **Don't skip quality checks**
- Automated endpoints still need verification
- Bad code is worse than no code

❌ **Don't ignore partial successes**
- Mark them for follow-up
- Don't leave half-implemented endpoints

❌ **Don't expect 100% automation**
- Some endpoints will need manual work
- That's OK - orchestrator handles 80%+

---

## Progress Tracking

### State File

The orchestrator maintains state in `ai_temp_files/orchestration_state.json`:

```json
{
  "started_at": "2025-11-13T10:00:00",
  "last_updated": "2025-11-13T16:30:00",
  "total_endpoints": 131,
  "completed": 45,
  "in_progress": 0,
  "failed": 3,
  "skipped": 2,
  "batches": {
    "1": {"status": "completed", "success": 8, "partial": 2, "failed": 0},
    "2": {"status": "completed", "success": 7, "partial": 2, "failed": 1},
    "3": {"status": "completed", "success": 9, "partial": 1, "failed": 0},
    "4": {"status": "completed", "success": 8, "partial": 1, "failed": 1},
    "5": {"status": "in_progress", "success": 3, "partial": 0, "failed": 0}
  },
  "endpoints": {
    "opportunities": {"status": "completed", "duration_min": 45, "batch": 1},
    "tickets": {"status": "completed", "duration_min": 52, "batch": 1},
    [...]
  }
}
```

### Dashboard View

```bash
# View current progress (implement this helper)
python ai_temp_files/show_progress.py
```

**Output**:
```
┌─────────────────────────────────────────────────────────────┐
│            ENDPOINT IMPLEMENTATION PROGRESS                  │
├─────────────────────────────────────────────────────────────┤
│  Overall: 45/131 (34%)  [▓▓▓▓▓▓░░░░░░░░░░░░]                │
│                                                              │
│  Batch 5 of 13: 3/10 endpoints                               │
│                                                              │
│  Success Rate: 73% (8.5/10 avg per batch)                    │
│  Time per Endpoint: 48 min avg                               │
│  Estimated Remaining: 43 hours                               │
│                                                              │
│  Last Completed: agreements ✅ (55 min)                      │
│  Currently: customFields_accounts (in progress)              │
│  Next: quota, activityQuota, adCampaigns                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Typical Session Flow

### Session 1: Setup & Plan (30 min)

```bash
# Generate plan
python ai_temp_files/orchestrate_endpoints.py --plan

# Review plan
cat ai_temp_files/implementation_plan.json

# Prepare batch 1
python ai_temp_files/orchestrate_endpoints.py --batch 1 --execute
```

**Prompt Claude**:
```
"Read ai_temp_files/batch_1/batch_instructions.md and implement all 10 endpoints"
```

**Go do other work** - Claude handles the batch autonomously

---

### Session 2: Review & Continue (30 min, after 7-8 hours)

**Claude reports**: "Batch 1 complete: 8 success, 2 partial"

**You review**:
```bash
# Read batch summary
cat ai_temp_files/batch_1_summary.md

# Check partial successes
grep -l "partial" ai_temp_files/*_completion_report.json

# Read specific reports
cat ai_temp_files/adCampaigns_completion_report.json
```

**Decision**:
```bash
# If happy with results, proceed
python ai_temp_files/orchestrate_endpoints.py --batch 2 --execute
```

**Prompt Claude**: "Read batch_2 instructions and implement..."

---

### Session 3-N: Repeat (30 min each)

Continue pattern:
1. Review previous batch (10 min)
2. Prepare next batch (5 min)
3. Launch Claude (5 min)
4. Wait for completion (7-8 hours)
5. Review results (10 min)

---

## Quality Assurance

### Automated Checks (Run by Claude)

For each endpoint:
- ✅ `uv run pytest tests/unit/test_{endpoint}_resource.py` - Must pass
- ✅ `uv run interrogate upsales/models/{endpoint}.py` - Must be 100%
- ✅ `uv run mypy upsales/models/{endpoint}.py` - Must pass strict
- ✅ `uv run ruff check upsales/models/{endpoint}.py` - Must pass

### Human Checks (You at Checkpoints)

- Spot-check 2-3 endpoints per batch
- Read completion reports
- Review test coverage reports
- Verify documentation accuracy

---

## Troubleshooting

### Issue: Agent Gets Stuck

**Symptoms**: No progress for >1 hour on one endpoint

**Solution**:
1. Check what step it's on
2. Provide specific help for that step
3. Or mark endpoint as "needs_manual" and move on

### Issue: Low Success Rate (<50%)

**Symptoms**: More than half of endpoints partial/failed

**Solution**:
1. Review failure patterns (same step failing?)
2. Update workflow instructions
3. Enhance context files
4. Re-run failed batch

### Issue: Quality Checks Failing

**Symptoms**: mypy/ruff/interrogate failures

**Solution**:
1. Check if systematic (same issue across endpoints)
2. Update pattern reference
3. Add to automated checks
4. Re-run quality fixes

---

## Scaling Strategy

### Phase 1: Pilot (Batches 1-2, 20 Endpoints)

**Goal**: Validate orchestration works
**Success criteria**: 70%+ success rate
**Time**: 1 week
**Human involvement**: High (review each endpoint)

### Phase 2: Production (Batches 3-10, 80 Endpoints)

**Goal**: Implement bulk of endpoints
**Success criteria**: 75%+ success rate
**Time**: 3 weeks
**Human involvement**: Medium (review each batch)

### Phase 3: Cleanup (Batches 11-17, 31 Endpoints + Partials)

**Goal**: Complete remaining + fix partials
**Success criteria**: 100% implemented
**Time**: 1 week
**Human involvement**: High (complex endpoints)

---

## Metrics to Track

### Per Batch
- Success rate (target: 70-80%)
- Time per endpoint (target: <55 min)
- Token usage (target: <150K per batch)
- Quality check pass rate (target: 100%)

### Overall
- Total endpoints completed
- Average time per endpoint
- Total token usage
- Human intervention hours
- Final quality scores

---

## Next Steps

1. ✅ **Created**: Orchestration scripts
2. ✅ **Created**: Context extraction tool
3. **Next**: Add JSON output mode to validation scripts (optional)
4. **Then**: Run pilot batch (opportunities, tickets, events)
5. **Finally**: Full production batches

---

## Commands Summary

```bash
# 1. Generate plan
python ai_temp_files/orchestrate_endpoints.py --plan

# 2. Prepare batch
python ai_temp_files/orchestrate_endpoints.py --batch 1 --execute

# 3. Tell Claude
"Read ai_temp_files/batch_1/batch_instructions.md and implement all 10 endpoints"

# 4. Review results
cat ai_temp_files/batch_1_summary.md

# 5. Repeat
python ai_temp_files/orchestrate_endpoints.py --batch 2 --execute
```

---

**You're now ready to implement 131 endpoints with minimal manual effort!**
