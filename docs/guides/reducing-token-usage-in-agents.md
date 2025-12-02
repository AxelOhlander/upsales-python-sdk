# Reducing Token Usage in Validation Workflow Agents

This guide provides strategies to reduce token consumption when using Claude Code agents for endpoint validation and documentation workflows.

## Table of Contents

1. [Token Usage Analysis](#token-usage-analysis)
2. [Hook-Based Automation Strategy](#hook-based-automation-strategy)
3. [Specific Hook Implementations](#specific-hook-implementations)
4. [Workflow Optimization](#workflow-optimization)
5. [Best Practices](#best-practices)

---

## Token Usage Analysis

### Current Workflow (High Token Usage)

**Typical endpoint validation flow**:
```
User: "Validate the orders endpoint"
  ↓
Claude: Reads CLAUDE.md, api_endpoints_with_fields.json, multiple test scripts
  ↓
Claude: Runs test_required_create_fields.py
  ↓
Claude: Reads output (622 lines of script + output)
  ↓
Claude: Analyzes results, updates models
  ↓
Claude: Runs test_field_editability_bulk.py
  ↓
Claude: Reads output (330 lines)
  ↓
Claude: Updates documentation
```

**Estimated token usage**: 50,000-100,000 tokens per endpoint

### Why Token Usage Is High

1. **Large context files**: CLAUDE.md (1400+ lines), api_endpoints_with_fields.json (3535 lines)
2. **Verbose scripts**: test_required_create_fields.py (622 lines), validate_and_update_models.py (641 lines)
3. **Multiple reads**: Claude re-reads files multiple times
4. **Output parsing**: Claude reads and analyzes script output
5. **Documentation updates**: Reads and updates multiple docs

---

## Hook-Based Automation Strategy

**Key Insight**: Use hooks to run validation scripts **automatically** without agent involvement.

### Strategy 1: Automatic Validation on Model Generation

**Instead of**:
```
User: "Generate model for orders and validate it"
Claude: (reads context, runs scripts, analyzes, updates) = 80K tokens
```

**Use hook**:
```json
{
  "name": "auto-validate-new-models",
  "event": "PostToolUse",
  "matchers": ["Bash"],
  "command": "bash scripts/hooks/auto_validate_model.sh"
}
```

**Hook script** (`scripts/hooks/auto_validate_model.sh`):
```bash
#!/bin/bash
# Automatically run validation after generate-model

command=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.command')

# Check if this was a generate-model command
if [[ "$command" =~ upsales\ generate-model\ ([a-zA-Z_]+) ]]; then
    endpoint="${BASH_REMATCH[1]}"

    echo "" >&2
    echo "🔍 Auto-running validation suite for: $endpoint" >&2
    echo "" >&2

    # Run full CRUD lifecycle validation automatically
    python scripts/test_full_crud_lifecycle.py "$endpoint" 2>&1 | \
        grep -E "(✅|❌|REQUIRED|EDITABLE|READ-ONLY|SUMMARY)" >&2

    echo "" >&2
    echo "💡 Validation complete - results above" >&2
fi

exit 0
```

**Result**: Validation runs automatically, Claude doesn't need to orchestrate it. **Savings: ~40K tokens**

---

### Strategy 2: Pre-Commit Hook for Documentation Updates

**Instead of**:
```
Claude: "Let me update endpoint-map.md with verification status"
Claude: (reads file 800 lines, finds section, updates) = 15K tokens
```

**Use hook**:
```bash
#!/bin/bash
# scripts/hooks/auto_update_endpoint_map.sh

# Detect if we just ran a successful validation
if [[ "$CLAUDECODE_TOOL_OUTPUT" =~ "ALL VALIDATIONS PASSED" ]]; then
    endpoint=$(echo "$CLAUDECODE_TOOL_INPUT" | grep -oP 'test_full_crud_lifecycle.py \K\w+')

    if [ -n "$endpoint" ]; then
        # Auto-update endpoint-map.md
        python scripts/update_endpoint_status.py "$endpoint" "verified"
        echo "✅ Auto-updated docs/endpoint-map.md with verified status" >&2
    fi
fi

exit 0
```

**Result**: Documentation updated automatically. **Savings: ~15K tokens**

---

### Strategy 3: Output Summarization Hook

**Instead of**: Claude reads 500+ lines of validation output

**Use hook** to filter only essential info:
```bash
#!/bin/bash
# scripts/hooks/summarize_validation.sh

command=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.command')

if [[ "$command" =~ test_required_create_fields.py ]]; then
    # Capture output and filter to essentials
    output=$(eval "$command" 2>&1)

    # Only show: required fields, summary, next steps
    echo "$output" | grep -A 100 "REQUIRED FIELDS:\|SUMMARY\|Next Steps:" >&2

    # Don't send full output to Claude
    exit 0
fi

# For other commands, pass through normally
exit 0
```

**Result**: Claude only sees essential info. **Savings: ~20K tokens**

---

## Specific Hook Implementations

### Hook 1: Auto-Run Validation (PostToolUse on Bash)

**Trigger**: After `uv run upsales generate-model <endpoint>`
**Action**: Automatically run `test_full_crud_lifecycle.py`
**Savings**: 40K tokens (Claude doesn't orchestrate)

```json
{
  "name": "auto-validate-endpoint",
  "event": "PostToolUse",
  "matchers": ["Bash"],
  "command": "bash scripts/hooks/auto_validate_endpoint.sh"
}
```

### Hook 2: Smart Context Injection (SessionStart)

**Trigger**: Session start
**Action**: Inject minimal, focused context based on recent work
**Savings**: 30K tokens (smaller context than full CLAUDE.md)

```bash
#!/bin/bash
# Only inject relevant sections of CLAUDE.md, not all 1400 lines

cat <<EOF
Upsales SDK Quick Context:
- Files: snake_case (order_stages.py)
- Classes: PascalCase (OrderStage)
- CLI: uv run upsales generate-model <endpoint>
- Validation: python scripts/test_full_crud_lifecycle.py <endpoint>
- API Reference: api_endpoints_with_fields.json

Last work: $(git log -1 --oneline)
EOF
```

### Hook 3: Template-Based Model Updates (PostToolUse)

**Trigger**: After validation scripts complete
**Action**: Auto-update model files with results
**Savings**: 25K tokens (Claude doesn't read/edit files)

```python
#!/usr/bin/env python
# scripts/hooks/auto_update_model_from_validation.py

import json
import os
import re

# Parse validation output
output = os.environ.get("CLAUDECODE_TOOL_OUTPUT", "")

# Extract required fields
required = re.findall(r"✅ REQUIRED: (\w+)", output)
read_only = re.findall(r"❌ READ-ONLY: (\w+)", output)

# Auto-generate TypedDict and frozen fields
# Apply to model file directly
# ...
```

---

## Workflow Optimization

### Before: Manual Agent-Driven (80K+ tokens)

```
1. User asks to validate endpoint
2. Claude reads CLAUDE.md (1400 lines) = 5K tokens
3. Claude reads api_endpoints_with_fields.json (3535 lines) = 12K tokens
4. Claude reads validation scripts (622 + 330 + 329 lines) = 8K tokens
5. Claude runs scripts = 2K tokens
6. Claude reads output (500+ lines) = 5K tokens
7. Claude analyzes and plans = 10K tokens
8. Claude updates model files = 15K tokens
9. Claude updates documentation = 10K tokens
10. Claude creates summary = 3K tokens

TOTAL: ~70K tokens
```

### After: Hook-Driven Automation (10K tokens)

```
1. User runs: uv run upsales generate-model orders
   → Hook automatically runs validation ✅
   → Hook automatically updates docs ✅
   → Hook summarizes results ✅

2. User asks: "What were the validation results?"
3. Claude reads hook output summary (50 lines) = 2K tokens
4. Claude provides answer = 3K tokens

TOTAL: ~5K tokens (93% reduction!)
```

---

## Hook Configuration for Maximum Token Savings

**File**: `.claude/settings.json`

```json
{
  "hooks": [
    {
      "name": "auto-validate-and-document",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/endpoint_workflow_automation.sh"
    },
    {
      "name": "inject-minimal-context",
      "event": "SessionStart",
      "command": "bash scripts/hooks/inject_minimal_context.sh"
    },
    {
      "name": "summarize-script-output",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/summarize_output.sh"
    }
  ]
}
```

---

## Complete Automation Script

**File**: `scripts/hooks/endpoint_workflow_automation.sh`

```bash
#!/bin/bash
# Complete endpoint validation workflow automation

command=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.command')

# Detect generate-model command
if [[ "$command" =~ upsales\ generate-model\ ([a-zA-Z_]+) ]]; then
    endpoint="${BASH_REMATCH[1]}"

    echo "" >&2
    echo "════════════════════════════════════════════════════════════" >&2
    echo "🤖 AUTO-WORKFLOW: Endpoint Validation & Documentation" >&2
    echo "════════════════════════════════════════════════════════════" >&2
    echo "" >&2
    echo "Endpoint: $endpoint" >&2
    echo "" >&2

    # Step 1: Run validation suite
    echo "Step 1/3: Running validation suite..." >&2
    validation_output=$(python scripts/test_full_crud_lifecycle.py "$endpoint" 2>&1)

    # Check if validation passed
    if echo "$validation_output" | grep -q "ALL VALIDATIONS PASSED"; then
        echo "   ✅ All validations passed" >&2

        # Step 2: Auto-update endpoint-map.md
        echo "Step 2/3: Updating documentation..." >&2
        python scripts/update_endpoint_map.py "$endpoint" --status verified >/dev/null 2>&1
        echo "   ✅ Updated docs/endpoint-map.md" >&2

        # Step 3: Generate summary
        echo "Step 3/3: Generating summary..." >&2

        # Extract key info only
        required=$(echo "$validation_output" | grep -A 20 "REQUIRED FIELDS:" | grep "^   -" | wc -l)
        editable=$(echo "$validation_output" | grep -A 50 "EDITABLE Fields" | grep "^   -" | wc -l)
        readonly=$(echo "$validation_output" | grep -A 50 "READ-ONLY Fields" | grep "^   -" | wc -l)

        # Create compact summary
        summary_file="ai_temp_files/${endpoint}_validation_summary.txt"
        cat > "$summary_file" <<EOF
ENDPOINT: $endpoint
STATUS: ✅ Fully Validated
DATE: $(date +%Y-%m-%d)

REQUIRED FIELDS: $required
EDITABLE FIELDS: $editable
READ-ONLY FIELDS: $readonly

DETAILS:
$(echo "$validation_output" | grep -A 20 "REQUIRED FIELDS:")

$(echo "$validation_output" | grep -A 20 "📋 RECOMMENDATIONS")

NEXT STEPS:
$(echo "$validation_output" | grep -A 10 "Next Steps:")
EOF

        echo "   ✅ Summary saved to $summary_file" >&2
        echo "" >&2
        echo "════════════════════════════════════════════════════════════" >&2
        echo "✅ AUTO-WORKFLOW COMPLETE" >&2
        echo "════════════════════════════════════════════════════════════" >&2
        echo "" >&2
        echo "Summary saved to: $summary_file" >&2
        echo "View with: cat $summary_file" >&2
        echo "" >&2

    else
        echo "   ❌ Validation failed - see output above" >&2
        # Show only error lines
        echo "$validation_output" | grep -E "(❌|ERROR|FAILED)" >&2
    fi
fi

exit 0
```

**Token Savings**:
- Claude doesn't orchestrate workflow: **-40K tokens**
- Claude doesn't read full output: **-20K tokens**
- Claude reads summary file instead: **+2K tokens**
- **Net savings: 58K tokens (82% reduction)**

---

## Additional Token-Saving Strategies

### 1. **Use `.claudeignore` for Large Files**

Create `.claudeignore` to exclude files from context:

```
# Exclude large data files
api_endpoints_with_fields.json
ai_temp_files/*.txt
ai_temp_files/*.md

# Exclude VCR cassettes
tests/cassettes/**/*.yaml

# Exclude generated files
.venv/
__pycache__/
htmlcov/
```

**Savings**: Prevents Claude from reading 3500+ line JSON file unnecessarily. **~15K tokens**

### 2. **Create Compact Reference Files**

Instead of reading full `api_endpoints_with_fields.json`, create endpoint-specific summaries:

**Script**: `scripts/create_endpoint_summary.sh`
```bash
#!/bin/bash
endpoint=$1

# Extract just this endpoint's info
cat api_endpoints_with_fields.json | \
    jq ".endpoints.$endpoint" > "ai_temp_files/${endpoint}_api_spec.json"

echo "Created compact reference: ai_temp_files/${endpoint}_api_spec.json"
```

**Hook**:
```json
{
  "name": "create-compact-reference",
  "event": "PostToolUse",
  "matchers": ["Bash"],
  "command": "bash scripts/hooks/create_endpoint_summary.sh"
}
```

**Savings**: Read 50 lines instead of 3500. **~12K tokens**

### 3. **Pre-Cache Validation Results**

Store validation results in structured format that's easy to read:

```json
{
  "endpoint": "orders",
  "validated": "2025-11-13",
  "required_fields": ["client", "user", "stage", "date", "orderRow"],
  "editable_fields": ["description", "probability", "value"],
  "read_only_fields": ["id", "regDate", "modDate"],
  "status": "verified"
}
```

**Savings**: Claude reads 20 lines of JSON instead of 500 lines of output. **~18K tokens**

### 4. **Use Slash Commands Instead of Agents**

Create custom slash commands for common workflows:

**File**: `.claude/commands/validate-endpoint.md`
```markdown
---
description: Validate endpoint CRUD operations
---

Run the validation workflow for an endpoint:

1. Run: python scripts/test_full_crud_lifecycle.py {{ENDPOINT_NAME}}
2. Read the summary from: ai_temp_files/{{ENDPOINT_NAME}}_validation_summary.txt
3. Report the results to the user

Do NOT read the full scripts or CLAUDE.md - just run and report.
```

**Usage**: `/validate-endpoint orders`

**Savings**: Focused prompt, no context loading. **~40K tokens**

### 5. **Minimize Context with Focused Prompts**

Instead of:
```
User: "Help me validate and document the orders endpoint"
```

Use:
```
User: "Run: python scripts/test_full_crud_lifecycle.py orders
Then read: ai_temp_files/orders_validation_summary.txt
Report the results"
```

**Savings**: Claude knows exactly what to do, doesn't load unnecessary context. **~30K tokens**

---

## Complete Hook-Based Workflow

### Phase 1: Model Generation (Automated)

**User runs**:
```bash
uv run upsales generate-model orders --partial
```

**Hook automatically**:
1. ✅ Converts to snake_case → `order_stages.py`
2. ✅ Creates compact API reference → `ai_temp_files/orders_api_spec.json`
3. ✅ Runs validation suite → `test_full_crud_lifecycle.py orders`
4. ✅ Saves summary → `ai_temp_files/orders_validation_summary.txt`
5. ✅ Updates endpoint-map.md → marks as verified
6. ✅ Shows next steps

**Claude's role**: None! (0 tokens)

### Phase 2: User Review (Minimal Tokens)

**User asks**:
```
"What were the validation results for orders?"
```

**Claude reads**:
- `ai_temp_files/orders_validation_summary.txt` (50 lines) = 2K tokens
- Responds with summary = 2K tokens

**Total**: 4K tokens (was 70K)

### Phase 3: Model Updates (Focused)

**User asks**:
```
"Update the Order model with the validation results"
```

**Claude**:
- Reads validation summary (50 lines) = 2K tokens
- Reads model file (200 lines) = 3K tokens
- Updates model = 5K tokens
- Responds = 2K tokens

**Total**: 12K tokens (was 40K)

---

## Recommended Hook Configuration

**File**: `.claude/settings.json`

```json
{
  "hooks": [
    {
      "name": "auto-workflow",
      "description": "Automated validation and documentation",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/endpoint_workflow_automation.sh"
    },
    {
      "name": "minimal-context",
      "description": "Inject focused context only",
      "event": "SessionStart",
      "command": "bash scripts/hooks/inject_minimal_context.sh"
    },
    {
      "name": "summarize-output",
      "description": "Filter script output to essentials",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/summarize_output.sh"
    },
    {
      "name": "create-compact-refs",
      "description": "Generate endpoint-specific references",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/create_compact_reference.sh"
    }
  ]
}
```

---

## Token Savings Breakdown

| Optimization | Before | After | Savings |
|--------------|--------|-------|---------|
| **Auto-validation** | 40K | 0K | 40K (100%) |
| **Compact API refs** | 12K | 1K | 11K (92%) |
| **Output filtering** | 20K | 2K | 18K (90%) |
| **Focused context** | 30K | 5K | 25K (83%) |
| **Cached results** | 10K | 1K | 9K (90%) |
| **TOTAL** | **112K** | **9K** | **103K (92%)** |

---

## Best Practices

### DO:

✅ **Use hooks for deterministic tasks** - Validation, formatting, documentation updates
✅ **Cache results in compact formats** - JSON summaries, not verbose output
✅ **Filter output to essentials** - Only show what Claude needs
✅ **Create focused slash commands** - Specific instructions, minimal context
✅ **Use .claudeignore** - Exclude large files from context

### DON'T:

❌ **Don't use hooks for complex decisions** - Let Claude handle nuanced choices
❌ **Don't over-automate** - Some tasks benefit from Claude's intelligence
❌ **Don't ignore hook output** - Important feedback might be in stderr
❌ **Don't skip testing** - Verify hooks work before relying on them

---

## Implementation Priority

| Priority | Hook | Savings | Effort | ROI |
|----------|------|---------|--------|-----|
| 🔥 **1** | Auto-validation workflow | 40K | Low | ⭐⭐⭐⭐⭐ |
| 🔥 **2** | Output summarization | 18K | Low | ⭐⭐⭐⭐⭐ |
| ⭐ **3** | Minimal context injection | 25K | Low | ⭐⭐⭐⭐ |
| ⭐ **4** | Compact API references | 11K | Medium | ⭐⭐⭐ |
| 📊 **5** | Auto-update models | 25K | High | ⭐⭐ |
| 📊 **6** | .claudeignore setup | 15K | Low | ⭐⭐⭐⭐ |

**Recommended order**: 1 → 2 → 6 → 3 → 4 → 5

---

## Quick Start: Implement Top 3 Hooks (30 minutes)

### Step 1: Create hooks directory
```bash
mkdir -p scripts/hooks
```

### Step 2: Create auto-validation hook
```bash
cat > scripts/hooks/endpoint_workflow_automation.sh << 'EOF'
#!/bin/bash
command=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.command')

if [[ "$command" =~ upsales\ generate-model\ ([a-zA-Z_]+) ]]; then
    endpoint="${BASH_REMATCH[1]}"
    echo "🤖 Auto-validating $endpoint..." >&2
    python scripts/test_full_crud_lifecycle.py "$endpoint" 2>&1 | \
        grep -E "(✅|❌|SUMMARY)" >&2
fi
exit 0
EOF
chmod +x scripts/hooks/endpoint_workflow_automation.sh
```

### Step 3: Create .claudeignore
```bash
cat > .claudeignore << 'EOF'
api_endpoints_with_fields.json
ai_temp_files/*.txt
tests/cassettes/**/*.yaml
.venv/
__pycache__/
EOF
```

### Step 4: Configure hooks
```bash
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "hooks": [
    {
      "name": "auto-validate",
      "event": "PostToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/endpoint_workflow_automation.sh"
    }
  ]
}
EOF
```

### Step 5: Test it
```bash
uv run upsales generate-model contacts --partial
# Hook should automatically run validation!
```

**Expected savings**: 40K+ tokens per endpoint validation

---

## Advanced: Prompt-Based Hook for Code Review

**Use Case**: Intelligent validation of model files after creation

```json
{
  "name": "review-new-models",
  "event": "Stop",
  "prompt": "Check if the response created or modified any model files (upsales/models/*.py). If yes, verify: 1) File uses snake_case name 2) Classes use PascalCase 3) Has TypedDict for UpdateFields 4) Has frozen fields marked. Block if critical issues found, warn otherwise."
}
```

**Savings**: Catches issues before user notices. **Prevents 50K+ token rework**

---

## Monitoring Token Usage

Track hook effectiveness:

```bash
# Add to hooks
echo "$(date),${CLAUDECODE_EVENT},${CLAUDECODE_TOOL_NAME}" >> .claude/hook_usage.log
```

Analyze:
```bash
# See most-used hooks
cat .claude/hook_usage.log | cut -d, -f2 | sort | uniq -c | sort -rn
```

---

## Summary: Maximum Token Reduction Strategy

**Implement these 4 changes for 90%+ token reduction**:

1. ✅ **Auto-validation hook** (40K savings)
   - Runs `test_full_crud_lifecycle.py` automatically after `generate-model`

2. ✅ **Output summarization hook** (18K savings)
   - Filters validation output to essentials only

3. ✅ **.claudeignore** (15K savings)
   - Excludes large files from context

4. ✅ **Minimal context injection** (25K savings)
   - SessionStart hook provides focused context, not full CLAUDE.md

**Total savings**: **98K tokens per endpoint** (92% reduction)
**Time to implement**: **1-2 hours**
**Maintenance**: **Minimal** (hooks are stable once working)

---

## Next Steps

1. **Review this guide** and choose which hooks to implement
2. **Start with Quick Start** (30 minutes, 40K+ savings immediately)
3. **Test with one endpoint** to verify hook behavior
4. **Expand gradually** with additional hooks
5. **Monitor savings** with usage logs

---

**Questions?** Ask Claude to help implement specific hooks from this guide!
