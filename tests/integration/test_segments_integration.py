"""
Integration tests for Segment model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_segments_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_segments_integration/*.yaml
    uv run pytest tests/integration/test_segments_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.segments import Segment

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_segments_integration/test_get_segment_real_response.yaml")
async def test_get_segment_real_response():
    """
    Test getting a segment with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Segment
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_segments_integration/test_get_segment_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real segment (or replay from cassette)
        segments = await upsales.segments.list(limit=1)

        assert len(segments) > 0, "Should have at least one segment"
        segment = segments[0]

        # Validate Segment model with Pydantic v2 features
        assert isinstance(segment, Segment)
        assert isinstance(segment.id, int)
        assert isinstance(segment.name, str)
        assert segment.name  # Name should not be empty (NonEmptyStr validator)

        # Validate BinaryFlag fields (0 or 1)
        assert segment.active in (0, 1)
        assert segment.usedForProspectingMonitor in (0, 1)

        # Validate read-only fields
        assert isinstance(segment.nrOfContacts, int)
        assert segment.nrOfContacts >= 0
        assert isinstance(segment.regBy, int)
        assert isinstance(segment.modBy, int)

        # Validate computed fields
        assert isinstance(segment.is_active, bool)
        assert isinstance(segment.has_contacts, bool)
        assert isinstance(segment.is_used_for_prospecting, bool)

        # Validate filter structure
        assert isinstance(segment.filter, list)

        print(
            f"[OK] Segment parsed successfully: {segment.name} (ID: {segment.id}, Contacts: {segment.nrOfContacts})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_segments_integration/test_list_segments_real_response.yaml")
async def test_list_segments_real_response():
    """
    Test listing segments with real API response.

    Validates that list responses correctly parse and return multiple Segment objects.

    Cassette: tests/cassettes/integration/test_segments_integration/test_list_segments_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List segments (or replay from cassette)
        segments = await upsales.segments.list(limit=10)

        assert isinstance(segments, list)
        assert all(isinstance(seg, Segment) for seg in segments)

        if len(segments) > 0:
            # Validate first segment
            segment = segments[0]
            assert segment.id > 0
            assert segment.name
            assert segment.active in (0, 1)

            print(f"[OK] Listed {len(segments)} segments successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_segments_integration/test_segment_computed_fields.yaml")
async def test_segment_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_active, has_contacts, etc.)
    return correct values based on actual API data.

    Cassette: tests/cassettes/integration/test_segments_integration/test_segment_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        segments = await upsales.segments.list(limit=5)

        for segment in segments:
            # Test computed field: is_active
            if segment.active == 1:
                assert segment.is_active is True
            else:
                assert segment.is_active is False

            # Test computed field: has_contacts
            if segment.nrOfContacts > 0:
                assert segment.has_contacts is True
            else:
                assert segment.has_contacts is False

            # Test computed field: is_used_for_prospecting
            if segment.usedForProspectingMonitor == 1:
                assert segment.is_used_for_prospecting is True
            else:
                assert segment.is_used_for_prospecting is False

        print(f"[OK] Computed fields validated for {len(segments)} segments")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_segments_integration/test_segment_custom_methods.yaml")
async def test_segment_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_active(), get_populated(), and get_by_name() methods
    work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_segments_integration/test_segment_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active_segments = await upsales.segments.get_active()
        assert isinstance(active_segments, list)
        assert all(seg.is_active for seg in active_segments)

        # Test get_populated()
        populated_segments = await upsales.segments.get_populated()
        assert isinstance(populated_segments, list)
        assert all(seg.has_contacts for seg in populated_segments)
        assert all(seg.nrOfContacts > 0 for seg in populated_segments)

        # Test get_by_name() with first segment
        if len(active_segments) > 0:
            first_segment = active_segments[0]
            found_segment = await upsales.segments.get_by_name(first_segment.name)
            assert found_segment is not None
            assert found_segment.id == first_segment.id
            assert found_segment.name == first_segment.name

        print(
            f"[OK] Custom methods validated: {len(active_segments)} active, {len(populated_segments)} populated"
        )
