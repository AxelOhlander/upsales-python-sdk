# Advanced Usage Patterns

Advanced examples using Pydantic v2 features, bulk operations, and binary downloads.

## Using Computed Fields

```python
from upsales import Upsales

async with Upsales.from_env() as upsales:
    user = await upsales.users.get(1)

    # Use computed properties
    if user.is_admin and user.is_active:
        print(f"Active admin: {user.display_name}")

    # Access custom fields
    department = user.custom_fields.get(11, "Unknown")
```

## Bulk Operations

```python
# Bulk update with concurrency control
await upsales.products.bulk_update(
    ids=[1, 2, 3, 4, 5],
    data={"active": 1},
    max_concurrent=10
)

# Bulk deactivate
await upsales.products.bulk_deactivate([10, 11, 12])
```

## Downloading Binary Files

The SDK supports downloading binary files like PDFs, audio recordings, and other non-JSON responses.

### E-signature PDF Downloads

```python
# Download a signed PDF document
pdf_bytes = await upsales.esign_function.download(document_id=456)

# Save to file
with open("signed_contract.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### Voice Recordings

```python
# Download a voice call recording
recording = await upsales.voice.get_recording(
    integration_id="123",
    recording_id="456"
)

# Save audio file
if recording.content:
    with open("call_recording.wav", "wb") as f:
        f.write(recording.content)
```

### Using HTTPClient Directly

```python
# For custom endpoints that return binary data
pdf_bytes = await upsales.http.get_bytes("/custom/endpoint/file.pdf")

# Or with full control over response type
response = await upsales.http.request(
    "GET",
    "/custom/endpoint",
    response_type="bytes"  # Options: "json", "bytes", "text", "response"
)
```

## Free-Threaded Mode (Python 3.13, Optional)

Python 3.13 supports running without the GIL:

```bash
python -X gil=0 your_script.py
```

**When it helps**: CPU-bound callbacks, thread pools, or hybrid workloads. For pure async I/O operations like HTTP requests, asyncio already provides efficient concurrency, and free-threaded mode offers minimal benefit.

See [Pydantic v2 Features](../patterns/pydantic-v2-features.md) for more advanced patterns.
