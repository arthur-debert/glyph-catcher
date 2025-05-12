"""
Tests for the fetcher module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from glyph_catcher.types import FetchOptions
from glyph_catcher.fetcher import download_file, fetch_all_data_files
from glyph_catcher.config import (
    UNICODE_DATA_FILE_URL,
    NAME_ALIASES_FILE_URL,
    NAMES_LIST_FILE_URL,
    CLDR_ANNOTATIONS_URL,
)


class TestFetcher(unittest.TestCase):
    """Test the fetcher module."""

    @patch('requests.get')
    def test_download_file_success(self, mock_get):
        """Test downloading a file successfully."""
        # Set up the mock response
        mock_response = mock_get.return_value
        mock_response.iter_content.return_value = [b'test data']
        mock_response.raise_for_status.return_value = None
        
        # Call the function
        options = FetchOptions(use_cache=False)
        result = download_file(UNICODE_DATA_FILE_URL, options)
        
        # Check that the file was downloaded
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        
        # Check the file content
        with open(result, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b'test data')
        
        # Clean up
        os.remove(result)

    @patch('requests.get')
    def test_download_file_with_cache(self, mock_get):
        """Test downloading a file with cache enabled."""
        # Create a temporary directory for the cache
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the mock response
            mock_response = mock_get.return_value
            mock_response.iter_content.return_value = [b'test data']
            mock_response.raise_for_status.return_value = None
            
            # Call the function
            options = FetchOptions(use_cache=True, cache_dir=temp_dir)
            result = download_file(UNICODE_DATA_FILE_URL, options)
            
            # Check that the file was downloaded
            self.assertIsNotNone(result)
            
            # Check that the file exists in the cache
            cache_file = os.path.join(temp_dir, os.path.basename(UNICODE_DATA_FILE_URL))
            self.assertTrue(os.path.exists(cache_file))
            
            # Reset the mock
            mock_get.reset_mock()
            
            # Call the function again to use the cached file
            result2 = download_file(UNICODE_DATA_FILE_URL, options)
            
            # Check that the same file was returned
            self.assertEqual(result, result2)
            
            # Check that the request was not made again
            mock_get.assert_not_called()

    @patch('requests.get')
    def test_download_file_request_error(self, mock_get):
        """Test downloading a file with a request error."""
        # Set up the mock response
        mock_get.side_effect = Exception("Connection error")
        
        # Call the function
        options = FetchOptions(use_cache=False)
        result = download_file(UNICODE_DATA_FILE_URL, options)
        
        # Check that the function returned None
        self.assertIsNone(result)

    @patch('glyph_catcher.fetcher.download_file')
    def test_fetch_all_data_files_success(self, mock_download):
        """Test fetching all data files successfully."""
        # Set up the mock response
        mock_download.side_effect = [
            '/tmp/UnicodeData.txt',
            '/tmp/NameAliases.txt',
            '/tmp/NamesList.txt',
            '/tmp/en.xml',
        ]
        
        # Call the function
        options = FetchOptions(use_cache=False)
        result = fetch_all_data_files(options)
        
        # Check that all files were downloaded
        self.assertEqual(len(result), 4)
        self.assertEqual(result['unicode_data'], '/tmp/UnicodeData.txt')
        self.assertEqual(result['name_aliases'], '/tmp/NameAliases.txt')
        self.assertEqual(result['names_list'], '/tmp/NamesList.txt')
        self.assertEqual(result['cldr_annotations'], '/tmp/en.xml')
        
        # Check that download_file was called with the correct arguments
        self.assertEqual(mock_download.call_count, 4)
        mock_download.assert_any_call(UNICODE_DATA_FILE_URL, options)
        mock_download.assert_any_call(NAME_ALIASES_FILE_URL, options)
        mock_download.assert_any_call(NAMES_LIST_FILE_URL, options)
        mock_download.assert_any_call(CLDR_ANNOTATIONS_URL, options)

    @patch('glyph_catcher.fetcher.download_file')
    def test_fetch_all_data_files_required_file_missing(self, mock_download):
        """Test fetching all data files with a required file missing."""
        # Set up the mock response to simulate a missing file
        mock_download.side_effect = [
            '/tmp/UnicodeData.txt',
            None,  # NameAliases.txt is missing
            '/tmp/NamesList.txt',
            '/tmp/en.xml',
        ]
        
        # Call the function
        options = FetchOptions(use_cache=False)
        result = fetch_all_data_files(options)
        
        # Check that the function returned an empty dictionary
        self.assertEqual(result, {})

    @patch('glyph_catcher.fetcher.download_file')
    def test_fetch_all_data_files_optional_file_missing(self, mock_download):
        """Test fetching all data files with an optional file missing."""
        # Set up the mock response to simulate a missing optional file
        mock_download.side_effect = [
            '/tmp/UnicodeData.txt',
            '/tmp/NameAliases.txt',
            '/tmp/NamesList.txt',
            None,  # CLDR annotations is missing
        ]
        
        # Call the function
        options = FetchOptions(use_cache=False)
        result = fetch_all_data_files(options)
        
        # Check that the function returned the required files
        self.assertEqual(len(result), 3)
        self.assertEqual(result['unicode_data'], '/tmp/UnicodeData.txt')
        self.assertEqual(result['name_aliases'], '/tmp/NameAliases.txt')
        self.assertEqual(result['names_list'], '/tmp/NamesList.txt')
        self.assertNotIn('cldr_annotations', result)


if __name__ == '__main__':
    unittest.main()