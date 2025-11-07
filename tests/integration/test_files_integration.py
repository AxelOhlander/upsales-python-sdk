"""
Integration tests for File model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_files_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_files_integration/*.yaml
    uv run pytest tests/integration/test_files_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.files import File

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
@my_vcr.use_cassette("test_files_integration/test_get_file_real_response.yaml")
async def test_get_file_real_response():
    """
    Test getting a file with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our File
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_files_integration/test_get_file_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real file (or replay from cassette)
        files = await upsales.files.list(limit=1)

        assert len(files) > 0, "Should have at least one file"
        file = files[0]

        # Validate File model with Pydantic v2 features
        assert isinstance(file, File)
        assert isinstance(file.id, int)
        assert isinstance(file.filename, str)
        assert file.filename  # Filename should not be empty (NonEmptyStr validator)

        # Validate required fields
        assert isinstance(file.entity, str)
        assert file.entity  # NonEmptyStr
        assert isinstance(file.entityId, int)
        assert file.entityId >= 0  # PositiveInt
        assert isinstance(file.extension, str)
        assert isinstance(file.mimetype, str)
        assert isinstance(file.size, int)
        assert file.size >= 0  # PositiveInt
        assert isinstance(file.type, str)

        # Validate BinaryFlag fields (0 or 1)
        assert file.private in (0, 1)
        assert file.public in (0, 1)

        # Validate read-only fields
        assert isinstance(file.uploadDate, str)
        assert isinstance(file.encryptedCustomerId, str)

        # Validate computed fields
        assert isinstance(file.is_private, bool)
        assert isinstance(file.is_public, bool)
        assert isinstance(file.file_size_mb, float)
        assert isinstance(file.file_size_kb, float)
        assert isinstance(file.is_image, bool)
        assert isinstance(file.is_document, bool)
        assert isinstance(file.display_name, str)

        print(
            f"[OK] File parsed successfully: {file.filename} (ID: {file.id}, Size: {file.file_size_mb} MB)"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_files_integration/test_list_files_real_response.yaml")
async def test_list_files_real_response():
    """
    Test listing files with real API response.

    Validates that list responses correctly parse and return multiple File objects.

    Cassette: tests/cassettes/integration/test_files_integration/test_list_files_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List files (or replay from cassette)
        files = await upsales.files.list(limit=10)

        assert isinstance(files, list)
        assert all(isinstance(f, File) for f in files)

        if len(files) > 0:
            # Validate first file
            file = files[0]
            assert file.id > 0
            assert file.filename
            assert file.private in (0, 1)
            assert file.public in (0, 1)
            assert file.size >= 0

            print(f"[OK] Listed {len(files)} files successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_files_integration/test_file_computed_fields.yaml")
async def test_file_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_private, is_image, file_size_mb, etc.)
    return correct values based on actual API data.

    Cassette: tests/cassettes/integration/test_files_integration/test_file_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        files = await upsales.files.list(limit=5)

        for file in files:
            # Test computed field: is_private
            if file.private == 1:
                assert file.is_private is True
            else:
                assert file.is_private is False

            # Test computed field: is_public
            if file.public == 1:
                assert file.is_public is True
            else:
                assert file.is_public is False

            # Test computed field: file_size_mb (conversion)
            expected_mb = round(file.size / (1024 * 1024), 2)
            assert file.file_size_mb == expected_mb

            # Test computed field: file_size_kb (conversion)
            expected_kb = round(file.size / 1024, 2)
            assert file.file_size_kb == expected_kb

            # Test computed field: is_image
            if file.mimetype.startswith("image/"):
                assert file.is_image is True
            else:
                assert file.is_image is False

            # Test computed field: display_name
            assert file.filename in file.display_name
            assert str(file.file_size_mb) in file.display_name

        print(f"[OK] Computed fields validated for {len(files)} files")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_files_integration/test_file_custom_methods.yaml")
async def test_file_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_images(), get_documents(), get_private(), and other methods
    work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_files_integration/test_file_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all files first to filter locally
        all_files = await upsales.files.list(limit=50)

        # Test get_images()
        images = await upsales.files.get_images()
        assert isinstance(images, list)
        assert all(f.is_image for f in images)
        assert all(f.mimetype.startswith("image/") for f in images)

        # Test get_documents()
        documents = await upsales.files.get_documents()
        assert isinstance(documents, list)
        assert all(f.is_document for f in documents)

        # Test get_private()
        private_files = await upsales.files.get_private()
        assert isinstance(private_files, list)
        assert all(f.is_private for f in private_files)
        assert all(f.private == 1 for f in private_files)

        # Test get_public()
        public_files = await upsales.files.get_public()
        assert isinstance(public_files, list)
        assert all(f.is_public for f in public_files)
        assert all(f.public == 1 for f in public_files)

        # Test get_by_filename() if we have files
        if len(all_files) > 0:
            first_file = all_files[0]
            found_files = await upsales.files.get_by_filename(first_file.filename)
            assert isinstance(found_files, list)
            assert len(found_files) > 0
            assert any(f.id == first_file.id for f in found_files)

        # Test get_by_extension() if we have files
        if len(all_files) > 0:
            first_file = all_files[0]
            found_by_ext = await upsales.files.get_by_extension(first_file.extension)
            assert isinstance(found_by_ext, list)
            assert len(found_by_ext) > 0
            assert all(f.extension == first_file.extension for f in found_by_ext)

        print(
            f"[OK] Custom methods validated: {len(images)} images, {len(documents)} documents, "
            f"{len(private_files)} private, {len(public_files)} public"
        )
