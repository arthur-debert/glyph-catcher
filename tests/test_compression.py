import os
import tempfile
import pytest
import gzip
from pathlib import Path

from glyph_catcher.exporter import compress_file, decompress_file
from glyph_catcher.types import ExportOptions
from glyph_catcher.exporter import export_data


def test_compress_decompress_file():
    """Test compressing and decompressing a file."""
    # Create a temporary file with some content - make it larger to ensure compression works
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Create a larger file to ensure compression is effective
        temp_file.write(b"This is a test file for compression. " * 100)
        temp_path = temp_file.name

    # Initialize variables to avoid UnboundLocalError in finally block
    compressed_path = temp_path + ".gz"
    decompressed_path = temp_path + ".decompressed"
    
    try:
        # Compress the file
        compress_file(temp_path, temp_path)
        
        # Check that the compressed file exists and is smaller than the original
        assert os.path.exists(compressed_path)
        assert os.path.getsize(compressed_path) < os.path.getsize(temp_path)
        
        # Decompress the file
        decompress_file(compressed_path, decompressed_path)
        
        # Check that the decompressed file has the same content as the original
        with open(temp_path, "rb") as f1, open(decompressed_path, "rb") as f2:
            assert f1.read() == f2.read()
    
    finally:
        # Clean up temporary files
        for path in [temp_path, compressed_path, decompressed_path]:
            if os.path.exists(path):
                os.remove(path)


def test_export_with_compression():
    """Test exporting data with compression enabled."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal test data
        unicode_data = {
            "0041": {
                "char_obj": "A",
                "name": "LATIN CAPITAL LETTER A",
                "category": "Lu",
                "block": "Basic Latin"
            }
        }
        aliases_data = {
            "0041": ["A", "Capital A"]
        }
        
        # Export with compression
        options = ExportOptions(
            format_type="lua",
            output_dir=temp_dir,
            compress=True
        )
        
        output_files = export_data(unicode_data, aliases_data, options)
        
        # Check that the compressed file exists
        assert len(output_files) == 1
        assert output_files[0].endswith(".gz")
        assert os.path.exists(output_files[0])
        
        # Check that the compressed file is a valid gzip file
        with open(output_files[0], "rb") as f:
            # gzip magic number is 0x1F8B
            assert f.read(2) == b'\x1f\x8b'


def test_export_without_compression():
    """Test exporting data without compression."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal test data
        unicode_data = {
            "0041": {
                "char_obj": "A",
                "name": "LATIN CAPITAL LETTER A",
                "category": "Lu",
                "block": "Basic Latin"
            }
        }
        aliases_data = {
            "0041": ["A", "Capital A"]
        }
        
        # Export without compression
        options = ExportOptions(
            format_type="lua",
            output_dir=temp_dir,
            compress=False
        )
        
        output_files = export_data(unicode_data, aliases_data, options)
        
        # Check that the uncompressed file exists
        assert len(output_files) == 1
        assert not output_files[0].endswith(".gz")
        assert os.path.exists(output_files[0])
        
        # Check that the file contains Lua code
        with open(output_files[0], "r") as f:
            content = f.read()
            assert "return {" in content
            assert "LATIN CAPITAL LETTER A" in content