"""
Module for exporting processed Unicode data to various formats.
"""

import gzip
import os
import shutil

from .config import get_output_filename
from .exporters import registry
from .processor import (
    filter_by_dataset,
    filter_by_unicode_blocks,
    load_master_data_file,
)
from .types import ExportOptions


def export_data(
    unicode_data: dict[str, dict[str, str]],
    aliases_data: dict[str, list[str]],
    options: ExportOptions,
) -> list[str]:
    """
    Export Unicode data to the specified format(s).

    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        options: Export options

    Returns:
        List of paths to the generated output files
    """
    # If use_master_file is True and master_file_path is provided, load data from the
    # master file
    if options.use_master_file and options.master_file_path:
        try:
            loaded_unicode_data, loaded_aliases_data = load_master_data_file(
                options.master_file_path
            )

            if loaded_unicode_data and loaded_aliases_data:
                unicode_data = loaded_unicode_data
                aliases_data = loaded_aliases_data
        except Exception:
            pass

    # Filter data by dataset or Unicode blocks if specified
    if options.dataset:
        unicode_data, aliases_data = filter_by_dataset(
            unicode_data, aliases_data, options.dataset
        )
    elif options.unicode_blocks:
        unicode_data, aliases_data = filter_by_unicode_blocks(
            unicode_data, aliases_data, options.unicode_blocks
        )

    # Create output directory if it doesn't exist
    os.makedirs(options.output_dir, exist_ok=True)

    output_files = []

    # Determine which formats to export
    formats = (
        registry.get_supported_formats()
        if options.format_type == "all"
        else [options.format_type]
    )

    # Export to each format
    for fmt in formats:
        # Get the exporter for this format
        exporter = registry.get_exporter(fmt)
        if not exporter:
            continue

        # Get the output filename based on format and dataset
        filename = get_output_filename(fmt, options.dataset)
        output_filename = os.path.join(options.output_dir, filename)

        # Create a temporary file for uncompressed output
        temp_filename = output_filename
        if options.compress:
            temp_filename = output_filename + ".temp"

        # Write the data using the exporter
        success = exporter.write(unicode_data, aliases_data, temp_filename)

        if not success:
            continue

        # Compress the file if requested
        if options.compress:
            compress_file(temp_filename, output_filename)
            os.remove(temp_filename)  # Remove the temporary uncompressed file
            output_filename = output_filename + ".gz"
        else:
            # Validate the exported file
            exporter.verify(output_filename)

        output_files.append(output_filename)

    return output_files


def save_source_files(file_paths: dict[str, str], output_dir: str) -> None:
    """
    Save the source files to the output directory.

    Args:
        file_paths: Dictionary mapping file types to file paths
        output_dir: Directory to save the files to
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get XDG data directory for source files
        xdg_data_dir = os.environ.get(
            "XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")
        )
        source_files_dir = os.path.join(xdg_data_dir, "glyph-catcher", "source-files")

        # Create XDG directory if it doesn't exist
        os.makedirs(source_files_dir, exist_ok=True)

        # Copy each source file to the XDG data directory
        for file_type, file_path in file_paths.items():
            if os.path.exists(file_path):
                # Map file types to more descriptive filenames
                if file_type == "unicode_data":
                    filename = "UnicodeData.txt"
                elif file_type == "name_aliases":
                    filename = "NameAliases.txt"
                elif file_type == "names_list":
                    filename = "NamesList.txt"
                elif file_type == "cldr_annotations":
                    filename = "en.xml"
                else:
                    filename = os.path.basename(file_path)

                dest_path = os.path.join(source_files_dir, filename)
                shutil.copy2(file_path, dest_path)
    except Exception:
        pass


def compress_file(input_filename: str, output_filename: str) -> None:
    """
    Compress a file using gzip with maximum compression level.

    Args:
        input_filename: Path to the input file
        output_filename: Path to the output compressed file (without extension)
    """
    try:
        # Use the highest compression level (9) for maximum compression
        with (
            open(input_filename, "rb") as f_in,
            gzip.open(output_filename + ".gz", "wb", compresslevel=9) as f_out,
        ):
            f_out.write(f_in.read())
    except Exception:
        pass


def decompress_file(input_filename: str, output_filename: str) -> None:
    """
    Decompress a gzip compressed file.

    Args:
        input_filename: Path to the compressed input file
        output_filename: Path to the output decompressed file
    """
    try:
        with (
            gzip.open(input_filename, "rb") as f_in,
            open(output_filename, "wb") as f_out,
        ):
            f_out.write(f_in.read())
    except Exception:
        pass
