"""
Tests for the master data file functionality.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from glyph_catcher.types import FetchOptions, ExportOptions
from glyph_catcher.processor import (
    save_master_data_file,
    load_master_data_file,
    get_master_file_path
)
from glyph_catcher.config import MASTER_DATA_FILE


class TestMasterDataFile(unittest.TestCase):
    """Test the master data file functionality."""

    def setUp(self):
        """Set up test data."""
        # Create test Unicode data
        self.unicode_data = {
            '0041': {
                'name': 'LATIN CAPITAL LETTER A',
                'category': 'Lu',
                'char_obj': 'A',
                'block': 'Basic Latin'
            },
            '0042': {
                'name': 'LATIN CAPITAL LETTER B',
                'category': 'Lu',
                'char_obj': 'B',
                'block': 'Basic Latin'
            }
        }
        
        # Create test aliases data
        self.aliases_data = {
            '0041': ['LATIN LETTER A', 'first letter'],
            '0042': ['LATIN LETTER B', 'second letter']
        }

    def test_save_and_load_master_data_file(self):
        """Test saving and loading the master data file."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the master data file
            master_file_path = save_master_data_file(
                self.unicode_data,
                self.aliases_data,
                temp_dir
            )
            
            # Check that the file was saved
            self.assertIsNotNone(master_file_path)
            self.assertTrue(os.path.exists(master_file_path))
            
            # Check the file content
            with open(master_file_path, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # Check that the data was saved correctly
            self.assertIn('unicode_data', master_data)
            self.assertIn('aliases_data', master_data)
            self.assertEqual(len(master_data['unicode_data']), 2)
            self.assertEqual(len(master_data['aliases_data']), 2)
            
            # Load the master data file
            loaded_unicode_data, loaded_aliases_data = load_master_data_file(master_file_path)
            
            # Check that the data was loaded correctly
            self.assertIsNotNone(loaded_unicode_data)
            self.assertIsNotNone(loaded_aliases_data)
            self.assertEqual(len(loaded_unicode_data), 2)
            self.assertEqual(len(loaded_aliases_data), 2)
            
            # Check the unicode data
            self.assertIn('0041', loaded_unicode_data)
            self.assertEqual(loaded_unicode_data['0041']['name'], 'LATIN CAPITAL LETTER A')
            self.assertEqual(loaded_unicode_data['0041']['category'], 'Lu')
            self.assertEqual(loaded_unicode_data['0041']['char_obj'], 'A')
            self.assertEqual(loaded_unicode_data['0041']['block'], 'Basic Latin')
            
            # Check the aliases data
            self.assertIn('0041', loaded_aliases_data)
            self.assertEqual(len(loaded_aliases_data['0041']), 2)
            self.assertIn('LATIN LETTER A', loaded_aliases_data['0041'])
            self.assertIn('first letter', loaded_aliases_data['0041'])

    def test_load_master_data_file_not_found(self):
        """Test loading a non-existent master data file."""
        # Try to load a non-existent file
        unicode_data, aliases_data = load_master_data_file('/non/existent/file.json')
        
        # Check that the function returned None, None
        self.assertIsNone(unicode_data)
        self.assertIsNone(aliases_data)

    def test_load_master_data_file_invalid_json(self):
        """Test loading an invalid JSON file."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('invalid json')
            temp_file_path = temp_file.name
        
        try:
            # Try to load the invalid file
            unicode_data, aliases_data = load_master_data_file(temp_file_path)
            
            # Check that the function returned None, None
            self.assertIsNone(unicode_data)
            self.assertIsNone(aliases_data)
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_get_master_file_path(self):
        """Test getting the master file path."""
        # Create fetch options with a custom data directory
        fetch_options = FetchOptions(data_dir='/custom/data/dir')
        
        # Get the master file path
        master_file_path = get_master_file_path(fetch_options)
        
        # Check that the path is correct
        self.assertEqual(master_file_path, '/custom/data/dir/' + MASTER_DATA_FILE)
        
        # Create fetch options without a data directory
        fetch_options = FetchOptions()
        
        # Get the master file path
        master_file_path = get_master_file_path(fetch_options)
        
        # Check that the path uses the default data directory
        self.assertTrue(master_file_path.endswith(MASTER_DATA_FILE))


if __name__ == '__main__':
    unittest.main()