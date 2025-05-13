"""
Tests for the exporter module.
"""

import unittest
from unittest.mock import MagicMock, patch

from glyph_catcher.exporter import (
    export_data,
    save_source_files,
)
from glyph_catcher.exporters import BaseExporter
from glyph_catcher.types import ExportOptions


class TestExporter(unittest.TestCase):
    """Test the exporter module."""

    def setUp(self):
        """Set up test data."""
        # Create test Unicode data as dictionaries (not UnicodeCharInfo objects)
        self.unicode_data = {
            "0041": {
                "name": "LATIN CAPITAL LETTER A",
                "category": "Lu",
                "char_obj": "A",
                "block": "Basic Latin",
            },
            "0042": {
                "name": "LATIN CAPITAL LETTER B",
                "category": "Lu",
                "char_obj": "B",
                "block": "Basic Latin",
            },
        }

        # Create test aliases data
        self.aliases_data = {
            "0041": ["LATIN LETTER A", "first letter"],
            "0042": ["LATIN LETTER B", "second letter"],
        }

    # The individual exporter tests have been moved to test_exporters.py

    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_csv(self, mock_get_exporter):
        """Test exporting data to CSV format."""
        # Create a mock exporter
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = True
        mock_exporter.verify.return_value = (True, None)

        # Set up the mock to return our mock exporter
        mock_get_exporter.return_value = mock_exporter

        # Call the function
        options = ExportOptions(format_type="csv", output_dir="/tmp", dataset="every-day")
        result = export_data(self.unicode_data, self.aliases_data, options)

        # Check the result
        self.assertEqual(result, ["/tmp/unicode.every-day.csv"])

        # Check that the exporter was used correctly
        mock_get_exporter.assert_called_once_with("csv")
        mock_exporter.write.assert_called_once_with(
            self.unicode_data, self.aliases_data, "/tmp/unicode.every-day.csv"
        )
        mock_exporter.verify.assert_called_once_with("/tmp/unicode.every-day.csv")

    @patch("glyph_catcher.exporters.registry.get_supported_formats")
    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_all(self, mock_get_exporter, mock_get_supported_formats):
        """Test exporting data to all formats."""
        # Set up the mock to return a list of supported formats
        mock_get_supported_formats.return_value = ["csv", "json", "lua", "txt"]

        # Create a mock exporter
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = True
        mock_exporter.verify.return_value = (True, None)

        # Set up the mock to return our mock exporter for any format
        mock_get_exporter.return_value = mock_exporter

        # Call the function
        options = ExportOptions(format_type="all", output_dir="/tmp", dataset="every-day")
        result = export_data(self.unicode_data, self.aliases_data, options)

        # Check the result
        self.assertEqual(
            set(result),
            {
                "/tmp/unicode.every-day.csv",
                "/tmp/unicode.every-day.json",
                "/tmp/unicode.every-day.lua",
                "/tmp/unicode.every-day.txt",
            },
        )

        # Check that the exporter was used correctly for each format
        self.assertEqual(mock_get_exporter.call_count, 4)
        self.assertEqual(mock_exporter.write.call_count, 4)
        self.assertEqual(mock_exporter.verify.call_count, 4)

    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_write_failure(self, mock_get_exporter):
        """Test exporting data when writing fails."""
        # Create a mock exporter that fails to write
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = False

        # Set up the mock to return our mock exporter
        mock_get_exporter.return_value = mock_exporter

        # Call the function
        options = ExportOptions(format_type="csv", output_dir="/tmp", dataset="every-day")
        result = export_data(self.unicode_data, self.aliases_data, options)

        # The function should not add the file to the output list if writing fails
        self.assertEqual(result, [])

        # Check that the exporter was used correctly
        mock_get_exporter.assert_called_once_with("csv")
        mock_exporter.write.assert_called_once_with(
            self.unicode_data, self.aliases_data, "/tmp/unicode.every-day.csv"
        )
        mock_exporter.verify.assert_not_called()

    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_with_validation(self, mock_get_exporter):
        """Test exporting data with validation."""
        # Create a mock exporter
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = True
        mock_exporter.verify.return_value = (True, None)

        # Set up the mock to return our mock exporter
        mock_get_exporter.return_value = mock_exporter

        # Call the function
        options = ExportOptions(format_type="csv", output_dir="/tmp", dataset="every-day")
        result = export_data(self.unicode_data, self.aliases_data, options)

        # Check the result
        self.assertEqual(result, ["/tmp/unicode.every-day.csv"])

        # Check that validation was called
        mock_exporter.verify.assert_called_once_with("/tmp/unicode.every-day.csv")

    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_with_validation_failure(self, mock_get_exporter):
        """Test exporting data with validation failure."""
        # Create a mock exporter
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = True
        mock_exporter.verify.return_value = (False, "Validation error")

        # Set up the mock to return our mock exporter
        mock_get_exporter.return_value = mock_exporter

        # Call the function
        options = ExportOptions(format_type="csv", output_dir="/tmp", dataset="every-day")
        result = export_data(self.unicode_data, self.aliases_data, options)

        # Check the result - file should still be in the output list even if
        # validation fails
        self.assertEqual(result, ["/tmp/unicode.every-day.csv"])

        # Check that validation was called
        mock_exporter.verify.assert_called_once_with("/tmp/unicode.every-day.csv")

    @patch("glyph_catcher.exporters.registry.get_exporter")
    def test_export_data_with_compression_skips_validation(self, mock_get_exporter):
        """Test that compressed files skip validation."""
        # Create a mock exporter
        mock_exporter = MagicMock(spec=BaseExporter)
        mock_exporter.write.return_value = True

        # Set up the mock to return our mock exporter
        mock_get_exporter.return_value = mock_exporter

        # Call the function with compression enabled
        options = ExportOptions(
            format_type="csv", output_dir="/tmp", dataset="every-day", compress=True
        )

        # Mock the compress_file function to avoid actual file operations
        with (
            patch("glyph_catcher.exporter.compress_file"),
            patch("os.remove"),  # Mock os.remove to avoid removing temp files
        ):
            result = export_data(self.unicode_data, self.aliases_data, options)

        # Check the result
        self.assertEqual(result, ["/tmp/unicode.every-day.csv.gz"])

        # Validation should not be called for compressed files
        mock_exporter.verify.assert_not_called()

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("shutil.copy2")
    def test_save_source_files(self, mock_copy, mock_exists, mock_makedirs):
        """Test saving source files."""
        # Set up the mock to return True for all file paths
        mock_exists.return_value = True

        # Create test file paths
        file_paths = {
            "unicode_data": "/tmp/UnicodeData.txt",
            "name_aliases": "/tmp/NameAliases.txt",
            "names_list": "/tmp/NamesList.txt",
        }

        # Call the function
        save_source_files(file_paths, "/output")

        # Check that the output directory was created
        mock_makedirs.assert_any_call("/output", exist_ok=True)

        # We don't test the XDG directory creation since that's implementation-specific
        # and might vary across systems

        # We don't test the exact copy destinations since they depend on the XDG path
        # which varies by system. Instead, just verify copy2 was called the right
        # number of times
        self.assertEqual(mock_copy.call_count, 3)


if __name__ == "__main__":
    unittest.main()
