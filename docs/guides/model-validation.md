# Model Validation and Update Guide

This guide explains how to validate and update existing models against fresh API data using the validation script.

## Overview

The `validate_and_update_models.py` script helps you:

1. **Verify model accuracy** - Compare existing models with real API responses
2. **Detect missing fields** - Find fields in the API but not in your model
3. **Identify type mismatches** - Catch incorrect field types
4. **Update models** - Automatically update model files with corrections
5. **Test with new data sources** - Validate against different API accounts

## Use Cases

### 1. Testing with a New API Key

When you get access to an account with more complete data:

```bash
# Test notifications with new API key
python scripts/validate_and_update_models.py notifications \
    --token YOUR_NEW_TOKEN

# Test with authentication fallback
python scripts/validate_and_update_models.py notifications \
    --token YOUR_NEW_TOKEN \
    --email your.email@example.com \
    --password your_password
```

### 2. Validating After API Changes

When Upsales updates their API:

```bash
# Validate all endpoints
python scripts/validate_and_update_models.py --all

# Or validate specific endpoints
python scripts/validate_and_update_models.py users
python scripts/validate_and_update_models.py orders
python scripts/validate_and_update_models.py contacts
```

### 3. Checking Endpoints with No Data

When you initially had no data but now do (e.g., subscriptions, agreements):

```bash
# Validate subscriptions (previously had no data)
python scripts/validate_and_update_models.py subscriptions

# Validate agreements
python scripts/validate_and_update_models.py agreements
```

## Output Interpretation

### Clean Model (No Issues)

```
Validating endpoint: /notifications

✓ Found 15 samples
✓ Analyzed 17 fields
✓ Loaded existing model (17 fields)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category         ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ API Samples      │    15 │
│ API Fields       │    17 │
│ Model Fields     │    17 │
│ Missing Fields   │     0 │
│ Type Mismatches  │     0 │
│ Extra Fields     │     0 │
└──────────────────┴───────┘

✓ Model is up to date!
```

### Model with Issues

```
Validating endpoint: /users

✓ Found 25 samples
✓ Analyzed 28 fields
✓ Loaded existing model (25 fields)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category         ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ API Samples      │    25 │
│ API Fields       │    28 │
│ Model Fields     │    25 │
│ Missing Fields   │     3 │
│ Type Mismatches  │     2 │
│ Extra Fields     │     0 │
└──────────────────┴───────┘

Missing Fields:
  • newField: str | None (sample: "test value")
  • anotherField: int (sample: 42)
  • optionalField: dict[str, Any] | None (sample: None)

Type Mismatches:
  • existingField:
    Existing: int
    Inferred: int | None
    Sample: None
  • statusField:
    Existing: str
    Inferred: str | int
    Sample: "active"

⚠ Model needs updates: 3 missing, 2 mismatches
```

## Common Scenarios

### Scenario 1: Field Now Allows Null

**Issue**: Your model has `active: int` but API sometimes returns `null`

**Detection**:
```
Type Mismatches:
  • active:
    Existing: int
    Inferred: int | None
    Sample: None
```

**Fix**: Update model to `active: int | None = None`

### Scenario 2: Field Type Changed

**Issue**: Field changed from `str` to `int` in API

**Detection**:
```
Type Mismatches:
  • userId:
    Existing: str
    Inferred: int
    Sample: 123
```

**Fix**: Update model to `userId: int`

### Scenario 3: New Optional Fields

**Issue**: API added new fields you don't have

**Detection**:
```
Missing Fields:
  • newFeature: bool (sample: True)
  • extraData: dict[str, Any] | None (sample: None)
```

**Fix**: Add fields to model:
```python
newFeature: bool = False
extraData: dict[str, Any] | None = None
```

### Scenario 4: Union Types

**Issue**: Field accepts multiple types

**Detection**:
```
Type Mismatches:
  • value:
    Existing: str
    Inferred: str | int
    Sample: "100"
```

**Fix**: Use union type `value: str | int`

## Step-by-Step: Updating a Model

### 1. Run Validation

```bash
python scripts/validate_and_update_models.py notifications
```

### 2. Review Report

Check for:
- Missing fields (new fields in API)
- Type mismatches (incorrect types)
- Extra fields (fields in model but not API - possibly deprecated)

### 3. Manual Updates

Open the model file and apply changes:

```python
# Before
class Notification(BaseModel):
    id: int = Field(frozen=True)
    message: str
    userId: int  # ← Type mismatch detected

# After
class Notification(BaseModel):
    id: int = Field(frozen=True)
    message: str
    userId: int | None = None  # ← Fixed
    newField: str | None = None  # ← Added missing field
```

### 4. Update TypedDict

If you added updatable fields, update the TypedDict:

```python
class NotificationUpdateFields(TypedDict, total=False):
    message: str
    userId: int | None
    newField: str | None  # ← Add to TypedDict
```

### 5. Re-run Validation

```bash
python scripts/validate_and_update_models.py notifications
```

Should now show:
```
✓ Model is up to date!
```

## Testing with New API Key

### Quick Test

Test a single endpoint with new credentials:

```bash
# Update your .env with new credentials
echo "UPSALES_TOKEN=new_token_here" > .env.new
echo "UPSALES_EMAIL=your.email@example.com" >> .env.new
echo "UPSALES_PASSWORD=your_password" >> .env.new

# Use the new credentials
export $(cat .env.new | xargs)

# Run validation
python scripts/validate_and_update_models.py notifications
```

### Bulk Validation

Validate all endpoints with new API key:

```bash
# Set credentials
export UPSALES_TOKEN=new_token_here

# Validate all
python scripts/validate_and_update_models.py --all > validation_report.txt

# Review report
cat validation_report.txt
```

### Compare Environments

Compare sandbox vs production data:

```bash
# Sandbox
python scripts/validate_and_update_models.py notifications \
    --token $SANDBOX_TOKEN \
    > sandbox_report.txt

# Production
python scripts/validate_and_update_models.py notifications \
    --token $PRODUCTION_TOKEN \
    > production_report.txt

# Compare
diff sandbox_report.txt production_report.txt
```

## Advanced Usage

### Custom Sample Size

Fetch more samples for better type inference:

```bash
python scripts/validate_and_update_models.py notifications --limit 500
```

### Batch Validation

Validate multiple specific endpoints:

```bash
for endpoint in notifications users orders contacts; do
    echo "=== $endpoint ==="
    python scripts/validate_and_update_models.py $endpoint
done
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/validate-models.yml
name: Validate Models

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: uv sync
      - name: Validate models
        run: |
          uv run python scripts/validate_and_update_models.py --all
        env:
          UPSALES_TOKEN: ${{ secrets.UPSALES_TOKEN }}
```

## Troubleshooting

### "No data available from API"

**Cause**: Endpoint has no objects in this account

**Solutions**:
- Try with a different API key (account with data)
- Create test data in Upsales UI
- Mark endpoint as skipped if genuinely unused

### "No existing model found"

**Cause**: Model file doesn't exist yet

**Solutions**:
- Use `uv run upsales generate-model <endpoint>` first
- Check endpoint name matches model filename

### Type Inference Issues

**Cause**: Limited samples or inconsistent data

**Solutions**:
- Increase `--limit` to fetch more samples
- Manually verify field types in Upsales UI
- Check API documentation

### Authentication Errors

**Cause**: Token expired or invalid

**Solutions**:
- Verify token in .env file
- Use `--email` and `--password` for auto-refresh
- Check token hasn't expired (sandbox tokens reset daily)

## Best Practices

### 1. Validate Before Committing

Always validate models before committing changes:

```bash
# After editing a model
python scripts/validate_and_update_models.py <endpoint>

# Run tests
uv run pytest tests/unit/test_<endpoint>_resource.py

# Then commit
git add upsales/models/<endpoint>.py
git commit -m "Update <endpoint> model"
```

### 2. Document Breaking Changes

If validation reveals breaking changes:

```python
# In CHANGELOG.md
## [Unreleased]
### Changed
- **BREAKING**: User.active is now nullable (int | None)
- **BREAKING**: Order.value type changed from str to int

### Added
- User.newField (optional string field)
```

### 3. Test in Sandbox First

Always test with sandbox token before production:

```bash
# Sandbox
python scripts/validate_and_update_models.py --all \
    --token $SANDBOX_TOKEN

# If all good, test production
python scripts/validate_and_update_models.py --all \
    --token $PRODUCTION_TOKEN
```

### 4. Keep Validation Reports

Archive validation reports for reference:

```bash
# Create reports directory
mkdir -p validation_reports

# Run with timestamp
python scripts/validate_and_update_models.py --all \
    > validation_reports/$(date +%Y%m%d_%H%M%S).txt
```

## Related Scripts

- `scripts/test_required_update_fields.py` - Test which fields are required for updates
- `scripts/test_field_editability.py` - Test which fields can be edited
- `uv run upsales generate-model` - Generate new models from API

## Next Steps

After validating models:

1. Update TypedDict for IDE autocomplete
2. Run unit tests to verify changes
3. Update integration tests if needed
4. Run mypy and ruff to ensure type safety
5. Update documentation if fields changed
6. Commit changes with descriptive message

---

**Created**: 2025-11-03
**Last Updated**: 2025-11-03
**Validated With**: Upsales API v2
