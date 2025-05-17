"""
Integration tests for master data caching functionality.
"""

import os
import tempfile
import unittest

from uniff_charset.core import process_unicode_data
from uniff_charset.types import CharsetExportOptions
from uniff_core.types import FetchOptions


@unittest.skip("Skipping test for master data caching")
class TestMasterDataCaching(unittest.TestCase):
    """Test the master data caching functionality."""

    def setUp(self):
        """Set up test data."""
        # Create temporary directories
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = os.path.join(self.temp_dir.name, "cache")
        self.data_dir = os.path.join(self.temp_dir.name, "data")
        self.output_dir = os.path.join(self.temp_dir.name, "output")

        # Create the directories
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_master_data_caching(self):
        """Test that master data is cached and reused."""
        # Create options for first run (with cache enabled)
        fetch_options = FetchOptions(
            use_cache=True,
            cache_dir=self.cache_dir,
            data_dir=self.data_dir,
            force=False,
        )

        export_options = CharsetExportOptions(
            format_type="csv",
            output_dir=self.output_dir,
            dataset="every-day",
        )

        # Process Unicode data for the first time
        success1, output_files1 = process_unicode_data(
            fetch_options, export_options, verbose=False
        )

        # Verify that processing was successful
        self.assertTrue(success1)
        self.assertTrue(len(output_files1) > 0)

        # Get the list of master data files in the data directory
        master_files = [
            f
            for f in os.listdir(self.data_dir)
            if f.startswith("unicode_master_data_") and f.endswith(".json")
        ]

        # Verify that a master data file was created with a checksum
        self.assertTrue(len(master_files) > 0)

        # Get the first master file (there should be only one)
        first_master_file = master_files[0]

        # Extract the checksum from the filename
        first_master_file.replace("unicode_master_data_", "").replace(".json", "")

        # Run again with cache enabled (should use cached master data)
        # First, let's get the modification time of the master data file
        master_file_path = os.path.join(self.data_dir, first_master_file)
        first_mtime = os.path.getmtime(master_file_path)

        # Create a new output directory for the second run
        output_dir2 = os.path.join(self.temp_dir.name, "output2")
        os.makedirs(output_dir2, exist_ok=True)

        export_options2 = CharsetExportOptions(
            format_type="csv",
            output_dir=output_dir2,
            dataset="every-day",
        )

        # Process Unicode data again
        success2, output_files2 = process_unicode_data(
            fetch_options, export_options2, verbose=False
        )

        # Verify that processing was successful
        self.assertTrue(success2)
        self.assertTrue(len(output_files2) > 0)

        # Verify that the master data file was not modified (it was reused)
        second_mtime = os.path.getmtime(master_file_path)
        self.assertEqual(first_mtime, second_mtime)

        # Now run with force=True (should regenerate master data)
        force_options = FetchOptions(
            use_cache=True,
            cache_dir=self.cache_dir,
            data_dir=self.data_dir,
            force=True,
        )

        # Create a new output directory for the forced run
        output_dir3 = os.path.join(self.temp_dir.name, "output3")
        os.makedirs(output_dir3, exist_ok=True)

        export_options3 = CharsetExportOptions(
            format_type="csv",
            output_dir=output_dir3,
            dataset="every-day",
        )

        # Process Unicode data again with force=True
        success3, output_files3 = process_unicode_data(
            force_options, export_options3, verbose=False
        )

        # Verify that processing was successful
        self.assertTrue(success3)
        self.assertTrue(len(output_files3) > 0)

        # Get the updated list of master data files
        master_files_after_force = [
            f
            for f in os.listdir(self.data_dir)
            if f.startswith("unicode_master_data_") and f.endswith(".json")
        ]

        # We may have a new master file with the same checksum or a different one
        # Either way, we should still have at least one master file
        self.assertTrue(len(master_files_after_force) > 0)


if __name__ == "__main__":
    unittest.main()
