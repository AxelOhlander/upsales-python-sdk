# VCR-First Workflow Update

**Date**: 2025-11-06
**Change**: Move VCR recording to Step 2 (right after model generation)

## Why This Change?

**Benefits**:
1. ✅ Capture real API structure immediately
2. ✅ Develop offline after recording (no API calls)
3. ✅ Avoid rate limits during development
4. ✅ Validate model against real API response
5. ✅ Faster iteration (VCR replay vs API)
6. ✅ Work anywhere (no internet needed)

## New Workflow Order

### Phase 1: Capture Real API Data
**STEP 1**: Generate Model (5 min)
- `uv run upsales generate-model {endpoint} --partial`

**STEP 2**: Record VCR Cassette (5 min) ⭐ **MOVED HERE**
- Create minimal integration test
- Record real API responses
- Save cassettes for offline use
- **All subsequent work uses VCR, not live API!**

### Phase 2: Model Enhancement (Using VCR)
**STEP 3**: Analyze Cassette for Real Structure (5 min) ⭐ **NEW**
- Read cassette YAML
- Identify actual field types
- Find nested objects
- Validate against generated model

**STEP 4**: Review Generated Code (5 min)
- Address TODOs
- Use cassette as source of truth

**STEP 5-12**: Enhance Model
- Mark frozen fields
- Add validators
- Add computed fields
- etc.

### Phase 3: Resource & Testing (Using VCR)
**STEP 13**: Create Resource
**STEP 14**: Add Custom Methods
**STEP 15**: Register in Client
**STEP 16**: Update Exports
**STEP 17**: Copy Test Template
**STEP 18**: Run Unit Tests (mocked, fast)
**STEP 19**: Run Integration Tests (uses existing VCR)
**STEP 20**: Quality Checks

## Key Changes

### Old Way (API-Last)
```
Generate → Enhance → Build → Test → Record VCR
         ↓         ↓      ↓      ↓
      Live API  Guess  Live API  Finally save
```

### New Way (VCR-First)
```
Generate → Record VCR → Enhance → Build → Test
         ↓           ↓         ↓      ↓      ↓
      Live API    Offline  Offline Offline VCR Replay
```

## Implementation Notes

### Step 2 (New): Record VCR Cassette

Create minimal test to record API structure:

```python
# tests/integration/test_contacts_integration.py
import pytest
import vcr
from upsales import Upsales

my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
)

@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_record_structure.yaml")
async def test_record_api_structure():
    """Record real API structure for offline development."""
    async with Upsales.from_env() as upsales:
        # Record GET single
        contact = await upsales.contacts.get(1)
        assert contact

        # Record LIST
        contacts = await upsales.contacts.list(limit=5)
        assert len(contacts) > 0
```

Run once to record:
```bash
uv run pytest tests/integration/test_contacts_integration.py::test_record_api_structure -v
```

### Step 3 (New): Analyze Cassette

Script to extract API structure:

```python
import yaml
import json

with open("tests/cassettes/.../test_record_structure.yaml") as f:
    cassette = yaml.safe_load(f)

for interaction in cassette["interactions"]:
    response = json.loads(interaction["response"]["body"]["string"])
    data = response["data"]

    if isinstance(data, list):
        item = data[0]
    else:
        item = data

    print("API Fields:")
    for field, value in item.items():
        print(f"  {field}: {type(value).__name__} = {value}")
```

Compare against generated model:
```python
from upsales.models.contact import Contact

api_fields = set(item.keys())
model_fields = set(Contact.model_fields.keys())

missing = api_fields - model_fields
extra = model_fields - api_fields

print(f"Missing in model: {missing}")
print(f"Extra in model: {extra}")
```

## Benefits Demonstrated

### Before (API-Last)
- 10+ API calls during development
- Rate limit concerns
- Slow iteration (network latency)
- Need internet connection
- Risk of sandbox resets

### After (VCR-First)
- 1-2 API calls (initial recording)
- No rate limit concerns
- Fast iteration (instant replay)
- Work offline
- Repeatable (cassettes don't change)

## Files to Update

1. `docs/guides/adding-endpoints.md` - Main guide
2. `docs/guides/adding-endpoints-ai.md` - AI condensed version
3. Both need Step 2 moved to VCR recording
4. Add Step 3 for cassette analysis
5. Update all references to "real API" to "VCR cassette"

## Validation

After update, verify:
- [ ] Step 2 is VCR recording
- [ ] Step 3 is cassette analysis
- [ ] All subsequent steps reference VCR
- [ ] No mention of "hit live API" after Step 2
- [ ] Integration tests note they use existing VCR
- [ ] Quality checks note VCR replay speed
