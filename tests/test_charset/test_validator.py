"""
Tests for the validator module.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from uniff_gen.validator import (
    validate_csv_file,
    validate_exported_file,
    validate_json_file,
    validate_lua_file,
    validate_txt_file,
)


class TestValidator(unittest.TestCase):
    """Test the validator module."""

    def test_validate_csv_file_valid(self):
        """Test validating a valid CSV file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        ) as temp_file:
            temp_file.write("code_point,character,name,category,block,alias_1,alias_2\n")
            temp_file.write(
                "U+0041,A,LATIN CAPITAL LETTER A,Lu,Basic Latin,LATIN LETTER A,"
                "first letter\n"
            )
            temp_file.write(
                "U+0042,B,LATIN CAPITAL LETTER B,Lu,Basic Latin,"
                "LATIN LETTER B,second letter\n"
            )
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_csv_file(temp_file_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_csv_file_invalid(self):
        """Test validating an invalid CSV file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        ) as temp_file:
            # Missing required columns
            temp_file.write("character,name,category\n")
            temp_file.write("A,LATIN CAPITAL LETTER A,Lu\n")
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_csv_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("Missing required column", error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_csv_file_not_found(self):
        """Test validating a non-existent CSV file."""
        is_valid, error_message = validate_csv_file("nonexistent.csv")
        self.assertFalse(is_valid)
        self.assertIn("File not found", error_message)

    def test_validate_json_file_valid(self):
        """Test validating a valid JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            json_data = [
                {
                    "code_point": "U+0041",
                    "character": "A",
                    "name": "LATIN CAPITAL LETTER A",
                    "category": "Lu",
                    "block": "Basic Latin",
                    "aliases": ["LATIN LETTER A", "first letter"],
                },
                {
                    "code_point": "U+0042",
                    "character": "B",
                    "name": "LATIN CAPITAL LETTER B",
                    "category": "Lu",
                    "block": "Basic Latin",
                    "aliases": ["LATIN LETTER B", "second letter"],
                },
            ]
            json.dump(json_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_json_file(temp_file_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_json_file_invalid(self):
        """Test validating an invalid JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            # Invalid JSON syntax
            temp_file.write('{"invalid": "json",')
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_json_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("JSON validation error", error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_json_file_missing_fields(self):
        """Test validating a JSON file with missing required fields."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            json_data = [
                {
                    "code_point": "U+0041",
                    "character": "A",
                    "name": "LATIN CAPITAL LETTER A",
                    # Missing 'category', 'block', and 'aliases'
                }
            ]
            json.dump(json_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_json_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("missing required field", error_message)
        finally:
            os.unlink(temp_file_path)

    @patch("subprocess.run")
    def test_validate_lua_file_valid(self, mock_run):
        """Test validating a valid Lua file."""
        # Mock the subprocess.run call to luac
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".lua"
        ) as temp_file:
            temp_file.write("-- Auto-generated unicode data module\n")
            temp_file.write("-- Generated by uniff-gen\n")
            temp_file.write("return {\n")
            temp_file.write("  {\n")
            temp_file.write('    code_point = "U+0041",\n')
            temp_file.write('    character = "A",\n')
            temp_file.write('    name = "LATIN CAPITAL LETTER A",\n')
            temp_file.write('    category = "Lu",\n')
            temp_file.write('    block = "Basic Latin",\n')
            temp_file.write('    aliases = {"LATIN LETTER A", "first letter"},\n')
            temp_file.write("  },\n")
            temp_file.write("}\n")
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_lua_file(temp_file_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error_message)
            mock_run.assert_called_once_with(
                ["luac", "-p", temp_file_path],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            os.unlink(temp_file_path)

    @patch("subprocess.run")
    def test_validate_lua_file_invalid_syntax(self, mock_run):
        """Test validating a Lua file with syntax errors."""
        # Mock the subprocess.run call to luac
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "luac: test.lua:5: syntax error"
        mock_run.return_value = mock_process

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".lua"
        ) as temp_file:
            temp_file.write("-- Auto-generated unicode data module\n")
            temp_file.write("-- Generated by uniff-gen\n")
            temp_file.write("return {\n")
            temp_file.write("  {\n")
            temp_file.write('    code_point = "U+0041",\n')
            # Missing closing brace
            temp_file.write('    character = "A",\n')
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_lua_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("Lua syntax error", error_message)
        finally:
            os.unlink(temp_file_path)

    @patch("subprocess.run")
    def test_validate_lua_file_missing_header(self, mock_run):
        """Test validating a Lua file with missing header."""
        # Mock the subprocess.run call to luac
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".lua"
        ) as temp_file:
            # Missing comment header
            temp_file.write("return {\n")
            temp_file.write("  {\n")
            temp_file.write('    code_point = "U+0041",\n')
            temp_file.write('    character = "A",\n')
            temp_file.write("  },\n")
            temp_file.write("}\n")
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_lua_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("Missing expected Lua comment header", error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_txt_file_valid(self):
        """Test validating a valid text file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            temp_file.write(
                "A|LATIN CAPITAL LETTER A|U+0041|Lu|Basic Latin|LATIN LETTER A|"
                "first letter\n"
            )
            temp_file.write(
                "B|LATIN CAPITAL LETTER B|U+0042|Lu|Basic Latin|"
                "LATIN LETTER B|second letter\n"
            )
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_txt_file(temp_file_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_txt_file_invalid_format(self):
        """Test validating a text file with invalid format."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            # Not enough fields
            temp_file.write("A|LATIN CAPITAL LETTER A|U+0041\n")
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_txt_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("insufficient fields", error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_txt_file_invalid_code_point(self):
        """Test validating a text file with invalid code point format."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            # Invalid code point format
            temp_file.write("A|LATIN CAPITAL LETTER A|0041|Lu|Basic Latin\n")
            temp_file_path = temp_file.name

        try:
            is_valid, error_message = validate_txt_file(temp_file_path)
            self.assertFalse(is_valid)
            self.assertIsNotNone(error_message)
            self.assertIn("no valid code point format", error_message)
        finally:
            os.unlink(temp_file_path)

    def test_validate_exported_file(self):
        """Test the validate_exported_file function."""
        # Test with different file extensions
        with patch("os.path.exists", return_value=True):  # Mock file existence
            with patch("uniff_gen.validator.validate_csv_file") as mock_csv:
                mock_csv.return_value = (True, None)
                result = validate_exported_file("test.csv")
                self.assertTrue(result[0])
                mock_csv.assert_called_once()

            with patch("uniff_gen.validator.validate_json_file") as mock_json:
                mock_json.return_value = (True, None)
                result = validate_exported_file("test.json")
                self.assertTrue(result[0])
                mock_json.assert_called_once()

            with patch("uniff_gen.validator.validate_lua_file") as mock_lua:
                mock_lua.return_value = (True, None)
                result = validate_exported_file("test.lua")
                self.assertTrue(result[0])
                mock_lua.assert_called_once()

            with patch("uniff_gen.validator.validate_txt_file") as mock_txt:
                mock_txt.return_value = (True, None)
                result = validate_exported_file("test.txt")
                self.assertTrue(result[0])
                mock_txt.assert_called_once()

        # Test with unsupported file extension
        with patch("os.path.exists", return_value=True):  # Mock file existence
            result = validate_exported_file("test.unknown")
            self.assertFalse(result[0])
            self.assertIn("Unsupported file type", result[1])

        # Test with compressed file
        with patch("os.path.exists", return_value=True):  # Mock file existence
            result = validate_exported_file("test.csv.gz")
            self.assertFalse(result[0])
            self.assertIn("Cannot validate compressed files", result[1])

        # Test with non-existent file
        with patch("os.path.exists", return_value=False):
            result = validate_exported_file("nonexistent.csv")
            self.assertFalse(result[0])
            self.assertIn("File not found", result[1])


if __name__ == "__main__":
    unittest.main()
