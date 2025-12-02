# Claude Code Hooks for Upsales SDK Development

This guide explains how to leverage Claude Code hooks to improve development workflow, enforce standards, and automate quality checks in the Upsales SDK project.

## Table of Contents

1. [What Are Claude Code Hooks?](#what-are-claude-code-hooks)
2. [Project-Specific Use Cases](#project-specific-use-cases)
3. [Recommended Hook Configurations](#recommended-hook-configurations)
4. [Implementation Examples](#implementation-examples)
5. [General Use Cases](#general-use-cases)

---

## What Are Claude Code Hooks?

Claude Code hooks are automated scripts that execute at specific points during development:

- **PreToolUse/PostToolUse**: Before/after tool execution
- **UserPromptSubmit**: When you submit prompts (validation, context injection)
- **Stop/SubagentStop**: When Claude finishes responding
- **SessionStart/SessionEnd**: Session lifecycle
- **PreCompact**: Before context compaction

**Two Types**:
1. **Command hooks**: Fast bash scripts for deterministic rules
2. **Prompt hooks**: LLM-powered for context-aware decisions (Stop/SubagentStop only)

---

## Project-Specific Use Cases

### 1. **Enforce Naming Conventions** ✅ High Priority

**Problem**: Prevent creation of files with camelCase names (e.g., `orderStages.py` should be `order_stages.py`)

**Solution**: `PreToolUse` hook on `Write` tool

```json
{
  "hooks": [
    {
      "name": "enforce-snake-case-files",
      "event": "PreToolUse",
      "matchers": ["Write"],
      "command": "bash scripts/hooks/enforce_snake_case.sh"
    }
  ]
}
```

**Script** (`scripts/hooks/enforce_snake_case.sh`):
```bash
#!/bin/bash
# Enforce snake_case for model and resource files

file_path=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.file_path')

# Check if it's a model or resource file
if [[ "$file_path" =~ upsales/(models|resources)/ ]]; then
    filename=$(basename "$file_path")

    # Check for camelCase (has uppercase letter not at start)
    if [[ "$filename" =~ [a-z][A-Z] ]] || [[ "$filename" =~ [A-Z]{2,} ]]; then
        echo "❌ ERROR: File name must use snake_case: $filename" >&2
        echo "Examples: order_stages.py, sales_coaches.py, api_keys.py" >&2
        exit 2  # Block the operation
    fi
fi

exit 0  # Allow operation
```

**Impact**: Prevents mistakes, enforces standards automatically

---

### 2. **Auto-Format Code After Edit** ✅ High Priority

**Problem**: Ensure all code is formatted consistently without manual intervention

**Solution**: `PostToolUse` hook on `Edit` and `Write` tools

```json
{
  "hooks": [
    {
      "name": "auto-format-python",
      "event": "PostToolUse",
      "matchers": ["Edit", "Write"],
      "command": "bash scripts/hooks/auto_format.sh"
    }
  ]
}
```

**Script** (`scripts/hooks/auto_format.sh`):
```bash
#!/bin/bash
# Auto-format Python files after edit

file_path=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.file_path')

# Only format Python files
if [[ "$file_path" == *.py ]]; then
    echo "Formatting $file_path..." >&2
    uv run ruff format "$file_path" 2>&1

    # Check for obvious issues
    uv run ruff check "$file_path" --fix 2>&1
fi

exit 0
```

**Impact**: Always consistent formatting, no manual `ruff format` needed

---

### 3. **Validate Model Classes** ✅ Medium Priority

**Problem**: Ensure models follow required patterns (frozen fields, TypedDict, etc.)

**Solution**: `PostToolUse` hook on model file writes

```json
{
  "hooks": [
    {
      "name": "validate-model-structure",
      "event": "PostToolUse",
      "matchers": ["Write", "Edit"],
      "command": "python scripts/hooks/validate_model.py"
    }
  ]
}
```

**Script** (`scripts/hooks/validate_model.py`):
```python
#!/usr/bin/env python
"""Validate model structure follows conventions."""
import json
import os
import sys
import re

# Get tool input
tool_input = json.loads(os.environ.get("CLAUDECODE_TOOL_INPUT", "{}"))
file_path = tool_input.get("file_path", "")

# Only check model files
if not file_path.startswith("upsales/models/") or not file_path.endswith(".py"):
    sys.exit(0)

# Skip base and __init__
if file_path.endswith("base.py") or file_path.endswith("__init__.py"):
    sys.exit(0)

# Read file content
try:
    with open(file_path, 'r') as f:
        content = f.read()
except:
    sys.exit(0)

errors = []

# Check for TypedDict (UpdateFields)
if "class.*BaseModel" in content and "UpdateFields" not in content:
    errors.append(f"Missing UpdateFields TypedDict for IDE autocomplete")

# Check for frozen fields on id
if "id:" in content and "Field(frozen=True" not in content:
    errors.append(f"'id' field should be marked with Field(frozen=True)")

# Check for custom_fields property if custom field exists
if 'custom:' in content and '@computed_field' not in content:
    errors.append(f"Models with 'custom' field should have @computed_field for custom_fields property")

if errors:
    print(f"⚠️  Model validation warnings for {file_path}:", file=sys.stderr)
    for error in errors:
        print(f"   - {error}", file=sys.stderr)
    print(f"   See: docs/patterns/creating-models.md", file=sys.stderr)
    # Don't block, just warn
    sys.exit(0)

sys.exit(0)
```

**Impact**: Catches pattern violations early, maintains code quality

---

### 4. **Protect Critical Files** ✅ High Priority

**Problem**: Prevent accidental modification of critical infrastructure files

**Solution**: `PreToolUse` hook on `Edit` and `Write`

```json
{
  "hooks": [
    {
      "name": "protect-critical-files",
      "event": "PreToolUse",
      "matchers": ["Edit", "Write"],
      "command": "bash scripts/hooks/protect_files.sh"
    }
  ]
}
```

**Script** (`scripts/hooks/protect_files.sh`):
```bash
#!/bin/bash
# Protect critical files from accidental modification

file_path=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.file_path')

# List of protected files
protected_files=(
    "upsales/models/base.py"
    "upsales/resources/base.py"
    "upsales/http.py"
    "upsales/exceptions.py"
    "api_endpoints_with_fields.json"
    ".env"
)

for protected in "${protected_files[@]}"; do
    if [[ "$file_path" == "$protected" ]]; then
        echo "❌ BLOCKED: $file_path is a critical file" >&2
        echo "These files should rarely be modified." >&2
        echo "If you need to modify this, please ask the user first." >&2
        exit 2  # Block operation
    fi
done

exit 0
```

**Impact**: Prevents catastrophic mistakes on core infrastructure

---

### 5. **Inject Project Context at Session Start** ✅ Medium Priority

**Problem**: Claude might not always load CLAUDE.md or remember project patterns

**Solution**: `SessionStart` hook

```json
{
  "hooks": [
    {
      "name": "inject-project-context",
      "event": "SessionStart",
      "command": "bash scripts/hooks/inject_context.sh"
    }
  ]
}
```

**Script** (`scripts/hooks/inject_context.sh`):
```bash
#!/bin/bash
# Inject project context at session start

cat <<EOF
📚 Upsales SDK Development Context:

Quick Reference:
- Naming: snake_case files, PascalCase classes (order_stages.py → OrderStage)
- Models: Always include TypedDict for UpdateFields
- Frozen fields: id, regDate, modDate, etc. use Field(frozen=True)
- Custom fields: Add @computed_field for custom_fields property
- CLI: 'uv run upsales generate-model <endpoint> --partial'
- Tests: 'uv run pytest tests/unit/' for fast checks
- Docs: CLAUDE.md has complete patterns and conventions

Current Status:
- 36/167 endpoints implemented (21%)
- 895 tests passing
- Python 3.13+ required

API Reference: api_endpoints_with_fields.json (167 endpoints documented)
EOF

exit 0
```

**Impact**: Ensures Claude always has project context, reduces mistakes

---

### 6. **Run Tests Before Commit** 🚀 Advanced

**Problem**: Catch test failures before committing

**Solution**: `PreToolUse` hook on `Bash` tool for git commit

```json
{
  "hooks": [
    {
      "name": "pre-commit-tests",
      "event": "PreToolUse",
      "matchers": ["Bash"],
      "command": "bash scripts/hooks/pre_commit.sh"
    }
  ]
}
```

**Script** (`scripts/hooks/pre_commit.sh`):
```bash
#!/bin/bash
# Run tests before git commit

command=$(echo "$CLAUDECODE_TOOL_INPUT" | jq -r '.command')

# Only check git commit commands
if [[ "$command" =~ ^git\ commit ]]; then
    echo "⚡ Running quick tests before commit..." >&2

    # Run fast unit tests only
    if ! uv run pytest tests/unit/ -q --tb=no 2>&1 | tail -5; then
        echo "" >&2
        echo "❌ BLOCKED: Tests are failing" >&2
        echo "Fix test failures before committing" >&2
        exit 2  # Block commit
    fi

    echo "✅ Tests passed, proceeding with commit" >&2
fi

exit 0
```

**Impact**: Never commit broken code, maintain high quality

---

### 7. **Validate API Endpoint Names** ✅ High Priority

**Problem**: Ensure generate-model uses real API endpoints

**Solution**: `PreToolUse` hook on `Bash` for CLI commands

```json
{
  "hooks": [
    {
      "name": "validate-endpoint-names",
      "event": "PreToolUse",
      "matchers": ["Bash"],
      "command": "python scripts/hooks/validate_endpoint.py"
    }
  ]
}
```

**Script** (`scripts/hooks/validate_endpoint.py`):
```python
#!/usr/bin/env python
"""Validate endpoint names against api_endpoints_with_fields.json"""
import json
import os
import sys
import re

tool_input = json.loads(os.environ.get("CLAUDECODE_TOOL_INPUT", "{}"))
command = tool_input.get("command", "")

# Check for generate-model commands
match = re.search(r'upsales generate-model ([a-zA-Z_]+)', command)
if not match:
    sys.exit(0)

endpoint = match.group(1)

# Load API file
try:
    with open("api_endpoints_with_fields.json", 'r') as f:
        api_data = json.load(f)
except:
    sys.exit(0)

# Check if endpoint exists
endpoints = list(api_data.get("endpoints", {}).keys())
if endpoint not in endpoints:
    print(f"❌ BLOCKED: Unknown endpoint '{endpoint}'", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(f"Available endpoints ({len(endpoints)} total):", file=sys.stderr)
    # Show first 20 matching suggestions
    matches = [e for e in endpoints if endpoint.lower() in e.lower()]
    if matches:
        print(f"Did you mean:", file=sys.stderr)
        for match in matches[:10]:
            print(f"  - {match}", file=sys.stderr)
    else:
        print(f"First 20 endpoints:", file=sys.stderr)
        for ep in sorted(endpoints)[:20]:
            print(f"  - {ep}", file=sys.stderr)
    exit(2)  # Block

sys.exit(0)
```

**Impact**: Prevents typos, ensures correctness

---

## General Use Cases (Beyond This Project)

### 1. **Security Scanning**

```bash
# Hook to scan for secrets before write
if grep -E "(password|secret|token|key).*=.*['\"]" "$file"; then
    echo "⚠️  Potential secret detected"
fi
```

### 2. **Documentation Generation**

```bash
# Auto-update API docs after model changes
if [[ "$file" =~ upsales/models/ ]]; then
    uv run mkdocs build --quiet
fi
```

### 3. **Cost Tracking**

```bash
# Log tool usage for cost analysis
echo "$(date),${CLAUDECODE_TOOL_NAME},${CLAUDECODE_EVENT}" >> .claude/usage.log
```

### 4. **Workspace Management**

```bash
# Clean up temp files on session end
if [ "$CLAUDECODE_EVENT" == "SessionEnd" ]; then
    find ai_temp_files/ -name "*.tmp" -delete
fi
```

### 5. **AI-Powered Code Review**

```json
{
  "name": "code-review",
  "event": "Stop",
  "prompt": "Review the code changes. Block if: 1) Missing docstrings 2) No type hints 3) Security issues"
}
```

---

## Recommended Configuration for This Project

**File**: `.claude/settings.json` (project-level)

```json
{
  "hooks": [
    {
      "name": "enforce-snake-case",
      "event": "PreToolUse",
      "matchers": ["Write"],
      "command": "bash scripts/hooks/enforce_snake_case.sh"
    },
    {
      "name": "auto-format",
      "event": "PostToolUse",
      "matchers": ["Edit", "Write"],
      "command": "bash scripts/hooks/auto_format.sh"
    },
    {
      "name": "protect-critical-files",
      "event": "PreToolUse",
      "matchers": ["Edit", "Write"],
      "command": "bash scripts/hooks/protect_files.sh"
    },
    {
      "name": "validate-endpoints",
      "event": "PreToolUse",
      "matchers": ["Bash"],
      "command": "python scripts/hooks/validate_endpoint.py"
    },
    {
      "name": "inject-context",
      "event": "SessionStart",
      "command": "bash scripts/hooks/inject_context.sh"
    }
  ]
}
```

---

## Hook Priority Ranking

| Priority | Hook | Impact | Effort |
|----------|------|--------|--------|
| 🔥 **Critical** | Enforce snake_case | Prevents naming mistakes | Low |
| 🔥 **Critical** | Protect critical files | Prevents catastrophic errors | Low |
| ⭐ **High** | Auto-format | Consistent code style | Low |
| ⭐ **High** | Validate endpoints | Prevents typos in CLI | Medium |
| 📊 **Medium** | Inject context | Improves Claude awareness | Low |
| 📊 **Medium** | Validate models | Enforces patterns | Medium |
| 🚀 **Advanced** | Pre-commit tests | Quality gate | High |

---

## Implementation Steps

### Phase 1: Essential Hooks (1 hour)

1. Create `scripts/hooks/` directory
2. Implement `enforce_snake_case.sh`
3. Implement `protect_files.sh`
4. Implement `auto_format.sh`
5. Create `.claude/settings.json` with these 3 hooks
6. Test with sample file operations

### Phase 2: Quality Hooks (2 hours)

1. Implement `validate_endpoint.py`
2. Implement `validate_model.py`
3. Implement `inject_context.sh`
4. Add to settings.json
5. Test with model generation

### Phase 3: Advanced (Optional)

1. Implement `pre_commit.sh`
2. Add prompt-based code review hook
3. Custom notification hooks

---

## Testing Hooks

```bash
# Test enforce-snake-case
export CLAUDECODE_TOOL_INPUT='{"file_path":"upsales/models/orderStages.py"}'
bash scripts/hooks/enforce_snake_case.sh
# Should exit with code 2 (blocked)

# Test protect-files
export CLAUDECODE_TOOL_INPUT='{"file_path":"upsales/models/base.py"}'
bash scripts/hooks/protect_files.sh
# Should exit with code 2 (blocked)

# Test auto-format
export CLAUDECODE_TOOL_INPUT='{"file_path":"upsales/models/user.py"}'
bash scripts/hooks/auto_format.sh
# Should format the file
```

---

## Security Considerations

**Best Practices**:

1. ✅ **Quote all variables**: `"$file_path"` not `$file_path`
2. ✅ **Validate inputs**: Check for path traversal (`../`)
3. ✅ **Use absolute paths**: `/usr/bin/python` not `python`
4. ✅ **Limit permissions**: Hooks run with your user permissions
5. ✅ **Review before enabling**: Understand what each hook does

**From docs**: "Claude Code hooks execute arbitrary shell commands on your system automatically."

---

## Benefits Summary

### For This Project

- ✅ **Enforces naming conventions automatically**
- ✅ **Prevents mistakes on critical files**
- ✅ **Auto-formats code (no manual ruff format)**
- ✅ **Validates model patterns**
- ✅ **Catches typos in endpoint names**
- ✅ **Always injects project context**
- ✅ **Optional: Tests before commits**

### General Benefits

- 🚀 **Automation**: Repetitive tasks happen automatically
- 🛡️ **Safety**: Prevent common mistakes before they happen
- 📊 **Quality**: Enforce standards without manual checking
- ⚡ **Speed**: Less back-and-forth, faster development
- 🧠 **Context**: Claude always knows project patterns

---

## Next Steps

1. **Review this guide** and decide which hooks to implement
2. **Start with Phase 1** (3 essential hooks)
3. **Create hooks directory**: `mkdir -p scripts/hooks`
4. **Implement scripts** from examples above
5. **Configure** `.claude/settings.json`
6. **Test** with sample operations
7. **Iterate** based on what works

---

## References

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [Project Naming Conventions](../../CLAUDE.md#naming-conventions)
- [Model Patterns](../patterns/creating-models.md)
- [Resource Patterns](../patterns/adding-resources.md)

---

**Questions?** Ask Claude to help implement specific hooks!
