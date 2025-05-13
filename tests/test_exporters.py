"""
Tests for the exporters module.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from glyph_catcher.exporters import (
    BaseExporter,
    CSVExporter,
    JSONExporter,
    LuaExporter,
    TxtExporter,
)
from glyph_catcher.exporters.registry import ExporterRegistry


class TestExporterRegistry(unittest.TestCase):
    """Test the exporter registry."""

    def setUp(self):
        """Set up test data."""
        self.registry = ExporterRegistry()

        # Create mock exporters
        self.csv_exporter = MagicMock(spec=BaseExporter)
        self.csv_exporter.format_type = "csv"

        self.json_exporter = MagicMock(spec=BaseExporter)
        self.json_exporter.format_type = "json"

    def test_register(self):
        """Test registering an exporter."""
        self.registry.register(self.csv_exporter)
        self.assertEqual(self.registry.get_exporter("csv"), self.csv_exporter)

    def test_get_exporter(self):
        """Test getting an exporter."""
        self.registry.register(self.csv_exporter)
        self.registry.register(self.json_exporter)

        self.assertEqual(self.registry.get_exporter("csv"), self.csv_exporter)
        self.assertEqual(self.registry.get_exporter("json"), self.json_exporter)
        self.assertIsNone(self.registry.get_exporter("unknown"))

    def test_get_all_exporters(self):
        """Test getting all exporters."""
        self.registry.register(self.csv_exporter)
        self.registry.register(self.json_exporter)

        exporters = self.registry.get_all_exporters()
        self.assertEqual(len(exporters), 2)
        self.assertEqual(exporters["csv"], self.csv_exporter)
        self.assertEqual(exporters["json"], self.json_exporter)

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        self.registry.register(self.csv_exporter)
        self.registry.register(self.json_exporter)

        formats = self.registry.get_supported_formats()
        self.assertEqual(set(formats), {"csv", "json"})


class TestCSVExporter(unittest.TestCase):
    """Test the CSV exporter."""

    def setUp(self):
        """Set up test data."""
        self.exporter = CSVExporter()

        # Create test Unicode data
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

    def test_format_type(self):
        """Test the format_type property."""
        self.assertEqual(self.exporter.format_type, "csv")

    def test_extension(self):
        """Test the extension property."""
        self.assertEqual(self.exporter.extension, ".csv")

    def test_write(self):
        """Test writing data to CSV format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Write the data to the file
            result = self.exporter.write(
                self.unicode_data, self.aliases_data, temp_file_path
            )

            # Check that the write was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file_path))

            # Read the file and check its contents
            with open(temp_file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Check the header
            self.assertEqual(
                lines[0].strip(),
                "code_point,character,name,category,block,alias_1,alias_2",
            )

            # Check the data rows
            self.assertIn(
                "U+0041,A,LATIN CAPITAL LETTER A,Lu,Basic Latin,LATIN LETTER A,"
                "first letter",
                lines[1].strip(),
            )
            self.assertIn(
                "U+0042,B,LATIN CAPITAL LETTER B,Lu,Basic Latin,LATIN LETTER B,"
                "second letter",
                lines[2].strip(),
            )
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_write_no_data(self):
        """Test writing to CSV format with no data."""
        result = self.exporter.write({}, self.aliases_data, "dummy.csv")
        self.assertFalse(result)

    @patch("glyph_catcher.exporters.csv_exporter.validate_csv_file")
    def test_verify(self, mock_validate):
        """Test verifying a CSV file."""
        mock_validate.return_value = (True, None)
        result, message = self.exporter.verify("test.csv")
        self.assertTrue(result)
        self.assertIsNone(message)
        mock_validate.assert_called_once_with("test.csv")


class TestJSONExporter(unittest.TestCase):
    """Test the JSON exporter."""

    def setUp(self):
        """Set up test data."""
        self.exporter = JSONExporter()

        # Create test Unicode data
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

    def test_format_type(self):
        """Test the format_type property."""
        self.assertEqual(self.exporter.format_type, "json")

    def test_extension(self):
        """Test the extension property."""
        self.assertEqual(self.exporter.extension, ".json")

    def test_write(self):
        """Test writing data to JSON format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Write the data to the file
            result = self.exporter.write(
                self.unicode_data, self.aliases_data, temp_file_path
            )

            # Check that the write was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file_path))

            # Read the file and check its contents
            import json

            with open(temp_file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Check the data
            self.assertEqual(len(data), 2)

            # Check the first character
            self.assertEqual(data[0]["code_point"], "U+0041")
            self.assertEqual(data[0]["character"], "A")
            self.assertEqual(data[0]["name"], "LATIN CAPITAL LETTER A")
            self.assertEqual(data[0]["category"], "Lu")
            self.assertEqual(data[0]["aliases"], ["LATIN LETTER A", "first letter"])

            # Check the second character
            self.assertEqual(data[1]["code_point"], "U+0042")
            self.assertEqual(data[1]["character"], "B")
            self.assertEqual(data[1]["name"], "LATIN CAPITAL LETTER B")
            self.assertEqual(data[1]["category"], "Lu")
            self.assertEqual(data[1]["aliases"], ["LATIN LETTER B", "second letter"])
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_write_no_data(self):
        """Test writing to JSON format with no data."""
        result = self.exporter.write({}, self.aliases_data, "dummy.json")
        self.assertFalse(result)

    @patch("glyph_catcher.exporters.json_exporter.validate_json_file")
    def test_verify(self, mock_validate):
        """Test verifying a JSON file."""
        mock_validate.return_value = (True, None)
        result, message = self.exporter.verify("test.json")
        self.assertTrue(result)
        self.assertIsNone(message)
        mock_validate.assert_called_once_with("test.json")


class TestLuaExporter(unittest.TestCase):
    """Test the Lua exporter."""

    def setUp(self):
        """Set up test data."""
        self.exporter = LuaExporter()

        # Create test Unicode data
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

    def test_format_type(self):
        """Test the format_type property."""
        self.assertEqual(self.exporter.format_type, "lua")

    def test_extension(self):
        """Test the extension property."""
        self.assertEqual(self.exporter.extension, ".lua")

    def test_write(self):
        """Test writing data to Lua format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Write the data to the file
            result = self.exporter.write(
                self.unicode_data, self.aliases_data, temp_file_path
            )

            # Check that the write was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file_path))

            # Read the file and check its contents
            with open(temp_file_path, encoding="utf-8") as f:
                content = f.read()

            # Check that the file starts with the correct header
            self.assertTrue(content.startswith("-- Auto-generated unicode data module"))

            # Check that the file contains the data
            self.assertIn('code_point = "U+0041"', content)
            self.assertIn('character = "A"', content)
            self.assertIn('name = "LATIN CAPITAL LETTER A"', content)
            self.assertIn('category = "Lu"', content)
            self.assertIn('"LATIN LETTER A"', content)
            self.assertIn('"first letter"', content)

            self.assertIn('code_point = "U+0042"', content)
            self.assertIn('character = "B"', content)
            self.assertIn('name = "LATIN CAPITAL LETTER B"', content)
            self.assertIn('category = "Lu"', content)
            self.assertIn('"LATIN LETTER B"', content)
            self.assertIn('"second letter"', content)
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_write_no_data(self):
        """Test writing to Lua format with no data."""
        result = self.exporter.write({}, self.aliases_data, "dummy.lua")
        self.assertFalse(result)

    @patch("glyph_catcher.exporters.lua_exporter.validate_lua_file")
    def test_verify(self, mock_validate):
        """Test verifying a Lua file."""
        mock_validate.return_value = (True, None)
        result, message = self.exporter.verify("test.lua")
        self.assertTrue(result)
        self.assertIsNone(message)
        mock_validate.assert_called_once_with("test.lua")


class TestTxtExporter(unittest.TestCase):
    """Test the TXT exporter."""

    def setUp(self):
        """Set up test data."""
        self.exporter = TxtExporter()

        # Create test Unicode data
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

    def test_format_type(self):
        """Test the format_type property."""
        self.assertEqual(self.exporter.format_type, "txt")

    def test_extension(self):
        """Test the extension property."""
        self.assertEqual(self.exporter.extension, ".txt")

    def test_write(self):
        """Test writing data to TXT format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Write the data to the file
            result = self.exporter.write(
                self.unicode_data, self.aliases_data, temp_file_path
            )

            # Check that the write was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_file_path))

            # Read the file and check its contents
            with open(temp_file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Check the data lines
            self.assertEqual(
                lines[0].strip(),
                "A|LATIN CAPITAL LETTER A|U+0041|Lu|Basic Latin|LATIN LETTER A|"
                "first letter",
            )
            self.assertEqual(
                lines[1].strip(),
                "B|LATIN CAPITAL LETTER B|U+0042|Lu|Basic Latin|LATIN LETTER B|"
                "second letter",
            )
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_write_no_data(self):
        """Test writing to TXT format with no data."""
        result = self.exporter.write({}, self.aliases_data, "dummy.txt")
        self.assertFalse(result)

    @patch("glyph_catcher.exporters.txt_exporter.validate_txt_file")
    def test_verify(self, mock_validate):
        """Test verifying a TXT file."""
        mock_validate.return_value = (True, None)
        result, message = self.exporter.verify("test.txt")
        self.assertTrue(result)
        self.assertIsNone(message)
        mock_validate.assert_called_once_with("test.txt")


if __name__ == "__main__":
    unittest.main()
