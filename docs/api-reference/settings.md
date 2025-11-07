# Settings API Reference

Auto-generated API documentation for pydantic-settings configuration.

## UpsalesSettings

Type-safe configuration management using Pydantic v2 and pydantic-settings.

::: upsales.settings.UpsalesSettings
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      heading_level: 3

## Helper Functions

::: upsales.settings.load_settings
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Usage Example

```python
from upsales import UpsalesSettings, Upsales

# Load configuration with validation
settings = UpsalesSettings()

# Automatic validation
# - UPSALES_TOKEN required
# - UPSALES_EMAIL validated (EmailStr)
# - UPSALES_MAX_CONCURRENT validated (1-200)
# - UPSALES_BASE_URL validated (HttpUrl)

# Use with client
async with Upsales(
    token=settings.upsales_token,
    max_concurrent=settings.upsales_max_concurrent
) as upsales:
    user = await upsales.users.get(1)
```

## Environment Variables

| Variable | Type | Required | Default | Validation |
|----------|------|----------|---------|------------|
| `UPSALES_TOKEN` | str | Yes | - | Non-empty |
| `UPSALES_EMAIL` | EmailStr | No | None | Valid email format |
| `UPSALES_PASSWORD` | str | No | None | - |
| `UPSALES_ENABLE_FALLBACK_AUTH` | bool | No | false | - |
| `UPSALES_BASE_URL` | HttpUrl | No | https://power.upsales.com/api/v2 | Valid URL |
| `UPSALES_MAX_CONCURRENT` | int | No | 50 | Range: 1-200 |

## Benefits

- ✅ Type-safe configuration with validation
- ✅ Reuses EmailStr validator from models
- ✅ Clear errors for missing/invalid settings
- ✅ IDE autocomplete for all settings
- ✅ Supports multiple .env files
- ✅ Range validation (max_concurrent: 1-200)
- ✅ URL validation (base_url)

## See Also

- [Pydantic Settings Pattern](../patterns/pydantic-v2-features.md#pydantic-settings-configuration)
- [Getting Started](../getting-started.md)
- [Authentication](../authentication.md)
