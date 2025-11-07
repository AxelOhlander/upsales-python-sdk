"""
Integration tests using VCR.py for real API response testing.

These tests record real API responses on first run, then replay them
from cassettes on subsequent runs. This ensures our models work with
actual API data structure without making API calls every test run.

To record new cassettes:
    1. Set up .env with UPSALES_TOKEN, UPSALES_EMAIL, UPSALES_PASSWORD
    2. Run: uv run pytest tests/integration/ -v
    3. Cassettes saved to tests/cassettes/

To update cassettes:
    1. Delete old cassette file in tests/cassettes/
    2. Run test again to re-record

See: docs/patterns/vcr-testing.md for complete guide
"""
