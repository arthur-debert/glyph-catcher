from unittest.mock import MagicMock, patch

from uniff_charset.core import process_unicode_data
from uniff_charset.types import ExportOptions
from uniff_core.progress import ProgressStatus
from uniff_core.types import FetchOptions


def test_export_fails_on_empty_output():
    """Test that export fails when no output files are generated."""
    fetch_options = FetchOptions(
        use_cache=True,
        cache_dir="/tmp/test-cache",
        data_dir="/tmp/test-data",
    )
    export_options = ExportOptions(
        format_type="csv",
        output_dir="/tmp/test-output",
        dataset="complete",
        compress=True,
    )

    # Mock the progress display
    mock_progress = MagicMock()

    with (
        patch("uniff_charset.core.ProgressDisplay", return_value=mock_progress),
        patch(
            "uniff_charset.core.fetch_all_data_files",
            return_value={"unicode_data": "test.txt"},
        ),
        patch("uniff_charset.core.process_data_files", return_value=({}, {})),
    ):
        success, output_files = process_unicode_data(fetch_options, export_options)

        assert not success
        assert not output_files
        mock_progress.update_item.assert_any_call(
            ["Exporting"], ProgressStatus.FAILURE, "No output files generated"
        )


def test_export_fails_on_compression_error():
    """Test that export fails when compression fails."""
    fetch_options = FetchOptions(
        use_cache=True,
        cache_dir="/tmp/test-cache",
        data_dir="/tmp/test-data",
    )
    export_options = ExportOptions(
        format_type="csv",
        output_dir="/tmp/test-output",
        dataset="complete",
        compress=True,
    )

    # Create a mock unicode_data and aliases_data
    unicode_data = {
        "0041": {
            "name": "LATIN A",
            "char_obj": "A",
            "category": "Lu",
            "block": "Basic Latin",
        }
    }
    aliases_data = {"0041": ["Capital A"]}

    # Mock the progress display
    mock_progress = MagicMock()

    with (
        patch("uniff_charset.core.ProgressDisplay", return_value=mock_progress),
        patch(
            "uniff_charset.core.fetch_all_data_files",
            return_value={"unicode_data": "test.txt"},
        ),
        patch(
            "uniff_charset.core.process_data_files",
            return_value=(unicode_data, aliases_data),
        ),
        patch(
            "uniff_charset.exporter.compress_file",
            side_effect=Exception("Compression failed"),
        ),
    ):
        success, output_files = process_unicode_data(fetch_options, export_options)

        assert not success
        assert not output_files
        mock_progress.update_item.assert_any_call(
            ["Exporting"], ProgressStatus.FAILURE, "Error: Compression failed"
        )


def test_export_fails_on_write_error():
    """Test that export fails when file write fails."""
    fetch_options = FetchOptions(
        use_cache=True,
        cache_dir="/tmp/test-cache",
        data_dir="/tmp/test-data",
    )
    export_options = ExportOptions(
        format_type="csv",
        output_dir="/dev/null/invalid",  # Invalid directory to force write error
        dataset="complete",
        compress=True,
    )

    # Create a mock unicode_data and aliases_data
    unicode_data = {
        "0041": {
            "name": "LATIN A",
            "char_obj": "A",
            "category": "Lu",
            "block": "Basic Latin",
        }
    }
    aliases_data = {"0041": ["Capital A"]}

    # Mock the progress display
    mock_progress = MagicMock()

    with (
        patch("uniff_charset.core.ProgressDisplay", return_value=mock_progress),
        patch(
            "uniff_charset.core.fetch_all_data_files",
            return_value={"unicode_data": "test.txt"},
        ),
        patch(
            "uniff_charset.core.process_data_files",
            return_value=(unicode_data, aliases_data),
        ),
    ):
        success, output_files = process_unicode_data(fetch_options, export_options)

        assert not success
        assert not output_files
        mock_progress.update_item.assert_any_call(["Exporting"], ProgressStatus.FAILURE)


def test_export_fails_when_master_file_load_fails():
    """Test that export fails when loading from master file fails."""
    fetch_options = FetchOptions(
        use_cache=True,
        cache_dir="/tmp/test-cache",
        data_dir="/tmp/test-data",
    )
    export_options = ExportOptions(
        format_type="csv",
        output_dir="/tmp/test-output",
        dataset="complete",
        compress=True,
        use_master_file=True,
        master_file_path="/tmp/master.json",
    )

    # Mock the progress display
    mock_progress = MagicMock()

    with (
        patch("uniff_charset.core.ProgressDisplay", return_value=mock_progress),
        patch(
            "uniff_charset.core.fetch_all_data_files",
            return_value={"unicode_data": "test.txt"},
        ),
        patch("uniff_charset.exporter.load_master_data_file", return_value=(None, None)),
    ):
        success, output_files = process_unicode_data(fetch_options, export_options)

        assert not success
        assert not output_files
        mock_progress.update_item.assert_any_call(
            ["Exporting"], ProgressStatus.FAILURE, "Failed to load data from master file"
        )


def test_export_fails_when_no_exporters_available():
    """Test export failure when no exporters are available.

    Verifies that the export process fails appropriately when there are
    no exporters available for the requested formats.
    """
    fetch_options = FetchOptions(
        use_cache=True,
        cache_dir="/tmp/test-cache",
        data_dir="/tmp/test-data",
    )
    export_options = ExportOptions(
        format_type="all",
        output_dir="/tmp/test-output",
        dataset="complete",
        compress=True,
    )

    # Create a mock unicode_data and aliases_data
    unicode_data = {
        "0041": {
            "name": "LATIN A",
            "char_obj": "A",
            "category": "Lu",
            "block": "Basic Latin",
        }
    }
    aliases_data = {"0041": ["Capital A"]}

    # Mock the progress display
    mock_progress = MagicMock()

    with (
        patch("uniff_charset.core.ProgressDisplay", return_value=mock_progress),
        patch(
            "uniff_charset.core.fetch_all_data_files",
            return_value={"unicode_data": "test.txt"},
        ),
        patch(
            "uniff_charset.core.process_data_files",
            return_value=(unicode_data, aliases_data),
        ),
        patch("uniff_charset.exporters.registry.get_supported_formats", return_value=[]),
    ):
        success, output_files = process_unicode_data(fetch_options, export_options)

        assert not success
        assert not output_files
        mock_progress.update_item.assert_any_call(
            ["Exporting"], ProgressStatus.FAILURE, "No formats available for export"
        )
