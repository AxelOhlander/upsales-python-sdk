# Advanced Usage Patterns

Advanced examples using Pydantic v2 features and bulk operations.

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
# Bulk update with parallelism
await upsales.products.bulk_update(
    ids=[1, 2, 3, 4, 5],
    data={"active": 1},
    max_concurrent=10
)

# Bulk deactivate
await upsales.products.bulk_deactivate([10, 11, 12])
```

## Free-Threaded Mode (Python 3.13)

```bash
# Enable for true parallelism without GIL
python -X gil=0 your_script.py
```

See [Pydantic v2 Features](../patterns/pydantic-v2-features.md) for more advanced patterns.
