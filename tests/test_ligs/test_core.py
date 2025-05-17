"""Tests for the uniff_ligs.core module."""

import csv
import os
import tempfile

from uniff_core.types import ExportOptions
from uniff_ligs.core import process_ligature_data


def test_process_ligature_data():
    """Test the process_ligature_data function."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up options
        options = ExportOptions(
            format_type="csv",
            output_dir=temp_dir,
            compress=False,
        )

        # Process ligature data
        success, output_files = process_ligature_data(options, verbose=False)

        # Check that the function was successful
        assert success
        assert len(output_files) == 1

        # Check that the output file exists
        output_file = output_files[0]
        assert os.path.exists(output_file)

        # Check the content of the file
        with open(output_file, newline="") as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

            # Check header
            assert rows[0] == ["sequence", "glyph", "description"]

            # Check that there are some rows
            assert len(rows) > 1

            # Check a specific row (e.g., the arrow ligature)
            arrow_row = None
            for row in rows:
                if row[0] == "->":
                    arrow_row = row
                    break

            assert arrow_row is not None
            assert arrow_row[1] == "→"
            assert "Arrow" in arrow_row[2]
