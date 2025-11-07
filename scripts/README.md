# Testing Scripts

This directory contains testing utilities for the Upsales SDK.

## Available Scripts

### test_field_editability.py
**Test which fields can be updated via the API**

```bash
python scripts/test_field_editability.py users
python scripts/test_field_editability.py companies 123
```

**Purpose**: Validate frozen fields and TypedDict accuracy
**Warning**: Makes real API updates! Use test/sandbox environment only!

**Output**:
- ✅ Editable fields
- ❌ Read-only fields  
- ⚠️ Warnings for model mismatches

**Use when**:
- Adding new endpoint
- Validating existing models
- Updating frozen field definitions

## Best Practices

1. **Use test environment** - Don't run against production data
2. **Backup data** - Have a way to restore if needed
3. **Review results** - Don't blindly trust, verify makes sense
4. **Update models** - Keep frozen fields accurate
5. **Re-test** - After model changes, re-run to verify

## See Also

- `docs/guides/testing-field-capabilities.md` - Complete testing guide
- `docs/guides/adding-endpoints.md` - Endpoint addition workflow
