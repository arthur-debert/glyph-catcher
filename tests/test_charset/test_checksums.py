"""
Tests for the checksum functionality.
"""

import os
import tempfile
import unittest

from uniff_charset.processor import (
    calculate_file_checksum,
    calculate_source_files_checksum,
    find_master_file_by_checksum,
    get_master_file_path,
)
from uniff_core.types import FetchOptions


class TestChecksums(unittest.TestCase):
    """Test the checksum functionality."""

    def setUp(self):
        """Set up test data."""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create test files with known content
        self.file1_path = os.path.join(self.temp_dir.name, "file1.txt")
        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write("test content 1")

        self.file2_path = os.path.join(self.temp_dir.name, "file2.txt")
        with open(self.file2_path, "w", encoding="utf-8") as f:
            f.write("test content 2")

        # Create a dictionary of file paths for testing
        self.file_paths = {
            "file1": self.file1_path,
            "file2": self.file2_path,
        }

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_calculate_file_checksum(self):
        """Test calculating a checksum for a single file."""
        # Calculate checksum for file1
        checksum1 = calculate_file_checksum(self.file1_path)

        # Verify that the checksum is a non-empty string
        self.assertIsInstance(checksum1, str)
        self.assertTrue(len(checksum1) > 0)

        # Calculate checksum for file2
        checksum2 = calculate_file_checksum(self.file2_path)

        # Verify that the checksums are different for different files
        self.assertNotEqual(checksum1, checksum2)

        # Modify file1 and recalculate the checksum
        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write("modified content")

        modified_checksum = calculate_file_checksum(self.file1_path)

        # Verify that the checksum changed after modifying the file
        self.assertNotEqual(checksum1, modified_checksum)

    def test_calculate_source_files_checksum(self):
        """Test calculating a combined checksum for multiple files."""
        # Calculate combined checksum
        combined_checksum = calculate_source_files_checksum(self.file_paths)

        # Verify that the checksum is a non-empty string
        self.assertIsInstance(combined_checksum, str)
        self.assertTrue(len(combined_checksum) > 0)

        # Modify file1 and recalculate the combined checksum
        with open(self.file1_path, "w", encoding="utf-8") as f:
            f.write("modified content")

        modified_combined_checksum = calculate_source_files_checksum(self.file_paths)

        # Verify that the combined checksum changed after modifying one of the files
        self.assertNotEqual(combined_checksum, modified_combined_checksum)

    def test_get_master_file_path_with_checksum(self):
        """Test getting a master file path with a checksum."""
        # Create fetch options
        fetch_options = FetchOptions(data_dir=self.temp_dir.name)

        # Get master file path without checksum
        base_path = get_master_file_path(fetch_options)

        # Verify that the path does not include a specific checksum
        filename = os.path.basename(base_path)
        self.assertEqual(filename, "unicode_master_data.json")

        # Get master file path with file_paths
        path_with_file_paths = get_master_file_path(
            fetch_options, file_paths=self.file_paths
        )

        # Verify that the path includes a checksum
        filename = os.path.basename(path_with_file_paths)
        self.assertIn("_", filename)

        # Get master file path with explicit checksum
        test_checksum = "test_checksum_123"
        path_with_explicit_checksum = get_master_file_path(
            fetch_options, checksum=test_checksum
        )

        # Verify that the path includes the explicit checksum
        self.assertIn(test_checksum, os.path.basename(path_with_explicit_checksum))

    def test_find_master_file_by_checksum(self):
        """Test finding a master file by checksum."""
        # Create a master file with a checksum
        test_checksum = "test_checksum_456"
        master_filename = f"unicode_master_data_{test_checksum}.json"
        master_path = os.path.join(self.temp_dir.name, master_filename)

        # Create the file
        with open(master_path, "w", encoding="utf-8") as f:
            f.write("{}")

        # Find the file by checksum
        found_path = find_master_file_by_checksum(self.temp_dir.name, test_checksum)

        # Verify that the file was found
        self.assertEqual(found_path, master_path)

        # Try to find a file with a non-existent checksum
        non_existent_path = find_master_file_by_checksum(
            self.temp_dir.name, "non_existent_checksum"
        )

        # Verify that no file was found
        self.assertIsNone(non_existent_path)


if __name__ == "__main__":
    unittest.main()
