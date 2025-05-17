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
            dataset="complete",
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
            assert rows[0] == [
                "unicode_codepoint",
                "unicode_name",
                "unicode_utf8",
                "sequence",
                "category",
                "description",
            ]

            # Check that there are some rows
            assert len(rows) > 1

            # Check a specific row (e.g., the arrow ligature)
            arrow_row = None
            for row in rows:
                if len(row) > 3 and "->" in row[3]:
                    arrow_row = row
                    break

            assert arrow_row is not None
            assert arrow_row[2] == "→"  # unicode_utf8
            assert "ARROW" in arrow_row[1]  # unicode_name
            assert arrow_row[4] == "arrows"  # category
            assert "Arrow" in arrow_row[5]  # description


def test_process_ligature_data_everyday():
    """Test the process_ligature_data function with the everyday dataset."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up options
        options = ExportOptions(
            format_type="csv",
            output_dir=temp_dir,
            compress=False,
            dataset="everyday",
        )

        # Process ligature data
        success, output_files = process_ligature_data(options, verbose=False)

        # Check that the function was successful
        assert success
        assert len(output_files) == 1

        # Check that the output file exists
        output_file = output_files[0]
        assert os.path.exists(output_file)


def test_process_ligature_data_json():
    """Test the process_ligature_data function with JSON output."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up options
        options = ExportOptions(
            format_type="json",
            output_dir=temp_dir,
            compress=False,
            dataset="complete",
        )

        # Process ligature data
        success, output_files = process_ligature_data(options, verbose=False)

        # Check that the function was successful
        assert success
        assert len(output_files) == 1

        # Check that the output file exists
        output_file = output_files[0]
        assert os.path.exists(output_file)
        assert output_file.endswith(".json")


def test_process_ligature_data_all_formats():
    """Test the process_ligature_data function with all output formats."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up options
        options = ExportOptions(
            format_type="all",
            output_dir=temp_dir,
            compress=False,
            dataset="complete",
        )

        # Process ligature data
        success, output_files = process_ligature_data(options, verbose=False)

        # Check that the function was successful
        assert success

        # We should have at least CSV and JSON outputs
        assert len(output_files) >= 2

        # Check that the output files exist
        csv_file = None
        json_file = None

        for file in output_files:
            if file.endswith(".csv"):
                csv_file = file
            elif file.endswith(".json"):
                json_file = file

        assert csv_file is not None
        assert os.path.exists(csv_file)

        assert json_file is not None
        assert os.path.exists(json_file)
