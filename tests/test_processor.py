"""
Tests for the processor module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from collections import defaultdict

from glyph_catcher.types import UnicodeCharInfo
from glyph_catcher.processor import (
    parse_unicode_data,
    parse_name_aliases,
    parse_names_list,
    parse_cldr_annotations,
    process_data_files,
)


class TestProcessor(unittest.TestCase):
    """Test the processor module."""

    def test_parse_unicode_data(self):
        """Test parsing UnicodeData.txt."""
        # Create a temporary file with test data
        test_data = (
            "0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;\n"
            "0042;LATIN CAPITAL LETTER B;Lu;0;L;;;;;N;;;;0062;\n"
            "0043;LATIN CAPITAL LETTER C;Lu;0;L;;;;;N;;;;0063;\n"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        try:
            # Parse the test data
            result = parse_unicode_data(temp_file_path)
            
            # Check the result
            self.assertEqual(len(result), 3)
            
            # Check the first character
            self.assertIn('0041', result)
            self.assertEqual(result['0041']['name'], 'LATIN CAPITAL LETTER A')
            self.assertEqual(result['0041']['category'], 'Lu')
            self.assertEqual(result['0041']['char_obj'], 'A')
            
            # Check the second character
            self.assertIn('0042', result)
            self.assertEqual(result['0042']['name'], 'LATIN CAPITAL LETTER B')
            self.assertEqual(result['0042']['category'], 'Lu')
            self.assertEqual(result['0042']['char_obj'], 'B')
            
            # Check the third character
            self.assertIn('0043', result)
            self.assertEqual(result['0043']['name'], 'LATIN CAPITAL LETTER C')
            self.assertEqual(result['0043']['category'], 'Lu')
            self.assertEqual(result['0043']['char_obj'], 'C')
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except FileNotFoundError:
                pass

    def test_parse_unicode_data_with_range(self):
        """Test parsing UnicodeData.txt with character ranges."""
        # Create a temporary file with test data including ranges
        test_data = (
            "0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;\n"
            "4E00;<CJK Ideograph, First>;Lo;0;L;;;;;N;;;;;\n"
            "9FFF;<CJK Ideograph, Last>;Lo;0;L;;;;;N;;;;;\n"
            "0042;LATIN CAPITAL LETTER B;Lu;0;L;;;;;N;;;;0062;\n"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Parse the test data
            result = parse_unicode_data(temp_file_path)
            
            # Check the result
            self.assertEqual(len(result), 2)
            
            # Check that the range markers are skipped
            self.assertIn('0041', result)
            self.assertIn('0042', result)
            self.assertNotIn('4E00', result)
            self.assertNotIn('9FFF', result)
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_parse_unicode_data_file_not_found(self):
        """Test parsing UnicodeData.txt when the file is not found."""
        # Call the function with a non-existent file
        result = parse_unicode_data('/non/existent/file.txt')
        
        # Check that the function returned an empty dictionary
        self.assertEqual(result, {})

    def test_parse_name_aliases(self):
        """Test parsing NameAliases.txt."""
        # Create a temporary file with test data
        test_data = (
            "0000;NULL;control;\n"
            "0000;NUL;abbreviation;\n"
            "0041;LATIN LETTER A;correction;\n"
            "0041;LA;abbreviation;\n"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Parse the test data
            result = parse_name_aliases(temp_file_path)
            
            # Check the result
            self.assertEqual(len(result), 2)
            
            # Check the aliases for the first character
            self.assertIn('0000', result)
            self.assertEqual(len(result['0000']), 2)
            self.assertIn('NULL', result['0000'])
            self.assertIn('NUL', result['0000'])
            
            # Check the aliases for the second character
            self.assertIn('0041', result)
            self.assertEqual(len(result['0041']), 2)
            self.assertIn('LATIN LETTER A', result['0041'])
            self.assertIn('LA', result['0041'])
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_parse_name_aliases_file_not_found(self):
        """Test parsing NameAliases.txt when the file is not found."""
        # Call the function with a non-existent file
        result = parse_name_aliases('/non/existent/file.txt')
        
        # Check that the function returned an empty dictionary
        self.assertEqual(result, {})

    def test_parse_names_list(self):
        """Test parsing NamesList.txt."""
        # Create a temporary file with test data
        test_data = (
            "0041\tLATIN CAPITAL LETTER A\n"
            "\t= first letter of the Latin alphabet\n"
            "\t* used for ...\n"
            "0042\tLATIN CAPITAL LETTER B\n"
            "\t= second letter of the Latin alphabet\n"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Parse the test data
            result = parse_names_list(temp_file_path)
            
            # Check the result
            self.assertEqual(len(result), 2)
            
            # Check the aliases for the first character
            self.assertIn('0041', result)
            self.assertEqual(len(result['0041']), 2)
            self.assertIn('first letter of the Latin alphabet', result['0041'])
            self.assertIn('used for ...', result['0041'])
            
            # Check the aliases for the second character
            self.assertIn('0042', result)
            self.assertEqual(len(result['0042']), 1)
            self.assertIn('second letter of the Latin alphabet', result['0042'])
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_parse_names_list_file_not_found(self):
        """Test parsing NamesList.txt when the file is not found."""
        # Call the function with a non-existent file
        result = parse_names_list('/non/existent/file.txt')
        
        # Check that the function returned an empty dictionary
        self.assertEqual(result, {})

    @patch('xml.etree.ElementTree.parse')
    def test_parse_cldr_annotations(self, mock_parse):
        """Test parsing CLDR annotations XML file."""
        # Create a mock XML tree
        mock_root = MagicMock()
        mock_parse.return_value.getroot.return_value = mock_root
        
        # Create mock annotations
        mock_annotation1 = MagicMock()
        mock_annotation1.attrib = {'cp': 'A'}
        mock_annotation1.text = 'letter a | first letter'
        
        mock_annotation2 = MagicMock()
        mock_annotation2.attrib = {'cp': 'B'}
        mock_annotation2.text = 'letter b | second letter'
        
        mock_annotation3 = MagicMock()
        mock_annotation3.attrib = {'cp': 'A', 'type': 'tts'}
        mock_annotation3.text = 'capital a'
        
        # Set up the mock to return the annotations
        mock_root.findall.return_value = [mock_annotation1, mock_annotation2, mock_annotation3]
        
        # Parse the mock data
        result = parse_cldr_annotations('dummy.xml')
        
        # Check the result
        self.assertEqual(len(result), 2)
        
        # Check the annotations for the first character
        self.assertIn('41', result)  # 'A' -> '41' in hex
        self.assertEqual(len(result['41']), 2)
        self.assertIn('letter a', result['41'])
        self.assertIn('first letter', result['41'])
        
        # Check the annotations for the second character
        self.assertIn('42', result)  # 'B' -> '42' in hex
        self.assertEqual(len(result['42']), 2)
        self.assertIn('letter b', result['42'])
        self.assertIn('second letter', result['42'])

    @patch('xml.etree.ElementTree.parse')
    def test_parse_cldr_annotations_file_not_found(self, mock_parse):
        """Test parsing CLDR annotations XML file when the file is not found."""
        # Set up the mock to raise a FileNotFoundError
        mock_parse.side_effect = FileNotFoundError()
        
        # Call the function
        result = parse_cldr_annotations('/non/existent/file.xml')
        
        # Check that the function returned an empty dictionary
        self.assertEqual(result, {})

    @patch('glyph_catcher.processor.get_alias_sources')
    def test_process_data_files_merges_aliases(self, mock_get_alias_sources):
        """Test that process_data_files correctly merges aliases from different sources."""
        # Mock the get_alias_sources function to return all sources
        mock_get_alias_sources.return_value = [
            'formal_aliases', 'informative_aliases', 'cldr_annotations'
        ]
        
        # Create test data files
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as unicode_data_file:
            unicode_data_file.write("0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;\n")
            unicode_data_file.write("0042;LATIN CAPITAL LETTER B;Lu;0;L;;;;;N;;;;0062;\n")
            unicode_data_file.write("0043;LATIN CAPITAL LETTER C;Lu;0;L;;;;;N;;;;0063;\n")
            unicode_data_path = unicode_data_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as name_aliases_file:
            name_aliases_file.write("0041;LATIN LETTER A;correction;\n")
            name_aliases_file.write("0041;LA;abbreviation;\n")
            name_aliases_file.write("0042;LATIN LETTER B;correction;\n")
            name_aliases_path = name_aliases_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as names_list_file:
            names_list_file.write("0041\tLATIN CAPITAL LETTER A\n")
            names_list_file.write("\t= first letter of the Latin alphabet\n")
            names_list_file.write("0043\tLATIN CAPITAL LETTER C\n")
            names_list_file.write("\t= third letter of the Latin alphabet\n")
            names_list_path = names_list_file.name
            
        try:
            # Call process_data_files with our test files
            file_paths = {
                'unicode_data': unicode_data_path,
                'name_aliases': name_aliases_path,
                'names_list': names_list_path,
            }
            unicode_data, aliases_data = process_data_files(file_paths)
            
            # Check that the aliases were merged correctly
            self.assertEqual(len(aliases_data), 3)
            
            # Check the merged aliases for the first character
            self.assertIn('0041', aliases_data)
            self.assertEqual(len(aliases_data['0041']), 3)
            
            # Check that aliases are normalized (lowercase)
            expected_aliases_a = ['first letter of the latin alphabet', 'la', 'latin letter a']
            for alias in expected_aliases_a:
                self.assertIn(alias, aliases_data['0041'])
            
            # Check the merged aliases for the second character
            self.assertIn('0042', aliases_data)
            self.assertEqual(len(aliases_data['0042']), 1)
            self.assertIn('latin letter b', aliases_data['0042'])
            
            # Check the merged aliases for the third character
            self.assertIn('0043', aliases_data)
            self.assertEqual(len(aliases_data['0043']), 1)
            self.assertIn('third letter of the latin alphabet', aliases_data['0043'])
        finally:
            # Clean up
            os.unlink(unicode_data_path)
            os.unlink(name_aliases_path)
            os.unlink(names_list_path)

    @patch('glyph_catcher.processor.parse_unicode_data')
    @patch('glyph_catcher.processor.parse_name_aliases')
    @patch('glyph_catcher.processor.parse_names_list')
    @patch('glyph_catcher.processor.parse_cldr_annotations')
    @patch('glyph_catcher.processor.get_alias_sources')
    def test_process_data_files_success(
        self, mock_get_alias_sources, mock_parse_cldr, mock_parse_names, mock_parse_aliases, mock_parse_unicode
    ):
        """Test processing all data files successfully."""
        # Mock the get_alias_sources function to return all sources
        mock_get_alias_sources.return_value = [
            'formal_aliases', 'informative_aliases', 'cldr_annotations'
        ]
        
        # Set up the mock returns
        unicode_data = {
            '0041': {'name': 'LATIN CAPITAL LETTER A', 'category': 'Lu', 'char_obj': 'A', 'block': 'Basic Latin'},
            '0042': {'name': 'LATIN CAPITAL LETTER B', 'category': 'Lu', 'char_obj': 'B', 'block': 'Basic Latin'},
        }
        mock_parse_unicode.return_value = unicode_data
        
        formal_aliases = {'0041': ['LATIN LETTER A']}
        mock_parse_aliases.return_value = formal_aliases
        
        informative_aliases = {'0042': ['second letter']}
        mock_parse_names.return_value = informative_aliases
        
        cldr_annotations = {'0041': ['letter a']}
        mock_parse_cldr.return_value = cldr_annotations
        
        # Call the function
        file_paths = {
            'unicode_data': '/path/to/UnicodeData.txt',
            'name_aliases': '/path/to/NameAliases.txt',
            'names_list': '/path/to/NamesList.txt',
            'cldr_annotations': '/path/to/en.xml',
        }
        result_unicode_data, result_aliases = process_data_files(file_paths)
        
        # Check the result
        self.assertEqual(result_unicode_data, unicode_data)
        
        # Create expected aliases data with normalization and deduplication
        expected_aliases = {
            '0041': ['latin letter a', 'letter a'],  # Normalized and sorted
            '0042': ['second letter']  # Normalized
        }
        
        # Check that the result matches our expected normalized and deduplicated aliases
        self.assertEqual(len(result_aliases), len(expected_aliases))
        for code_point, aliases in expected_aliases.items():
            self.assertIn(code_point, result_aliases)
            for alias in aliases:
                self.assertIn(alias, result_aliases[code_point])
        
        # Check that the parsing functions were called with the correct arguments
        mock_parse_unicode.assert_called_once_with('/path/to/UnicodeData.txt')
        mock_parse_aliases.assert_called_once_with('/path/to/NameAliases.txt')
        mock_parse_names.assert_called_once_with('/path/to/NamesList.txt')
        mock_parse_cldr.assert_called_once_with('/path/to/en.xml')

    @patch('glyph_catcher.processor.parse_unicode_data')
    def test_process_data_files_unicode_data_missing(self, mock_parse_unicode):
        """Test processing data files when UnicodeData.txt parsing fails."""
        # Set up the mock to return None
        mock_parse_unicode.return_value = None
        
        # Call the function
        file_paths = {
            'unicode_data': '/path/to/UnicodeData.txt',
            'name_aliases': '/path/to/NameAliases.txt',
            'names_list': '/path/to/NamesList.txt',
        }
        result_unicode_data, result_aliases = process_data_files(file_paths)
        
        # Check that the function returned None for unicode_data and an empty defaultdict for aliases_data
        self.assertIsNone(result_unicode_data)
        self.assertEqual(result_aliases, defaultdict(list))
        
    def test_normalize_alias(self):
        """Test the normalize_alias function."""
        from glyph_catcher.processor import normalize_alias
        
        # Test basic normalization
        self.assertEqual(normalize_alias("TEST"), "test")
        self.assertEqual(normalize_alias("Test String"), "test string")
        
        # Test whitespace handling
        self.assertEqual(normalize_alias("  leading spaces"), "leading spaces")
        self.assertEqual(normalize_alias("trailing spaces  "), "trailing spaces")
        self.assertEqual(normalize_alias("  both sides  "), "both sides")
        
        # Test mixed case
        self.assertEqual(normalize_alias("MiXeD CaSe"), "mixed case")
        
        # Test with special characters
        self.assertEqual(normalize_alias("Special-Characters!"), "special-characters!")
        
        # Test with duplicate aliases that would normalize to the same value
        self.assertEqual(normalize_alias("Test"), normalize_alias("TEST"))
        self.assertEqual(normalize_alias("test"), normalize_alias("  Test  "))
        
    def test_alias_deduplication(self):
        """Test that duplicate aliases are properly deduplicated."""
        from glyph_catcher.processor import process_data_files
        from collections import defaultdict
        
        # Create mock data with duplicate aliases
        mock_unicode_data = {
            '0041': {'name': 'LATIN CAPITAL LETTER A', 'category': 'Lu', 'char_obj': 'A', 'block': 'Basic Latin'},
        }
        
        # Mock the parsing functions
        with patch('glyph_catcher.processor.parse_unicode_data') as mock_parse_unicode, \
             patch('glyph_catcher.processor.parse_name_aliases') as mock_parse_aliases, \
             patch('glyph_catcher.processor.parse_names_list') as mock_parse_names, \
             patch('glyph_catcher.processor.parse_cldr_annotations') as mock_parse_cldr:
            
            # Set up the mock returns with duplicate aliases
            mock_parse_unicode.return_value = mock_unicode_data
            mock_parse_aliases.return_value = {'0041': ['First Letter', 'FIRST letter']}
            mock_parse_names.return_value = {'0041': ['first LETTER', 'Letter A']}
            mock_parse_cldr.return_value = {'0041': ['First Letter', 'letter a']}
            
            # Call the function
            file_paths = {
                'unicode_data': '/path/to/UnicodeData.txt',
                'name_aliases': '/path/to/NameAliases.txt',
                'names_list': '/path/to/NamesList.txt',
                'cldr_annotations': '/path/to/en.xml',
            }
            _, result_aliases = process_data_files(file_paths)
            
            # Check that duplicates were removed (case-insensitive)
            self.assertIn('0041', result_aliases)
            
            # There should be exactly 2 unique aliases after normalization and deduplication
            expected_aliases = ['first letter', 'letter a']
            self.assertEqual(len(result_aliases['0041']), 2)
            
            # Check that all expected aliases are present
            for alias in ['first letter', 'letter a']:
                self.assertIn(alias, result_aliases['0041'])
    
    def test_calculate_alias_statistics(self):
        """Test calculating alias statistics."""
        from glyph_catcher.processor import calculate_alias_statistics
        
        # Test with empty data
        empty_stats = calculate_alias_statistics({})
        self.assertEqual(empty_stats["total_characters"], 0)
        self.assertEqual(empty_stats["total_aliases"], 0)
        self.assertEqual(empty_stats["avg_aliases_per_char"], 0)
        self.assertEqual(empty_stats["median_aliases_per_char"], 0)
        self.assertEqual(empty_stats["max_aliases"], 0)
        self.assertEqual(empty_stats["min_aliases"], 0)
        self.assertEqual(empty_stats["chars_with_no_aliases"], 0)
        
        # Test with sample data
        sample_data = {
            "0041": ["a", "letter a", "first letter"],  # 3 aliases
            "0042": ["b", "letter b"],                  # 2 aliases
            "0043": ["c"],                              # 1 alias
            "0044": [],                                 # 0 aliases
            "0045": ["e", "letter e", "vowel", "fifth letter"]  # 4 aliases
        }
        
        stats = calculate_alias_statistics(sample_data)
        self.assertEqual(stats["total_characters"], 5)
        self.assertEqual(stats["total_aliases"], 10)
        self.assertEqual(stats["avg_aliases_per_char"], 2.0)
        self.assertEqual(stats["median_aliases_per_char"], 2.0)
        self.assertEqual(stats["max_aliases"], 4)
        self.assertEqual(stats["min_aliases"], 0)
        self.assertEqual(stats["chars_with_no_aliases"], 1)
        
        # Test with odd number of characters for median calculation
        odd_sample = {
            "0041": ["a", "letter a", "first letter"],  # 3 aliases
            "0042": ["b", "letter b"],                  # 2 aliases
            "0043": ["c"]                               # 1 alias
        }
        
        odd_stats = calculate_alias_statistics(odd_sample)
        self.assertEqual(odd_stats["median_aliases_per_char"], 2.0)


if __name__ == '__main__':
    unittest.main()