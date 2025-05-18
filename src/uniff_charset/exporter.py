"""
Module for exporting processed Unicode data to various formats.
"""

import contextlib
import csv
import gzip
import logging
import os
import shutil
from typing import TextIO

from .config import get_output_filename

logger = logging.getLogger("uniff")
from .exporters import registry
from .processor import (
    filter_by_dataset,
    filter_by_unicode_blocks,
    load_master_data_file,
)
from .types import ExportOptions


@contextlib.contextmanager
def managed_file_handlers():
    """Context manager for handling multiple file handlers."""
    handlers: dict[str, TextIO] = {}
    try:
        yield handlers
    finally:
        # Ensure all files are properly closed
        for handler in handlers.values():
            try:
                if not handler.closed:
                    handler.close()
            except Exception as e:
                logger.error(f"Error closing file handler: {e}")


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
    # Check for empty input data
    if not unicode_data or not aliases_data:
        error_msg = "No data to export"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Load data from master file if specified in options
    if options.use_master_file and options.master_file_path:
        loaded_unicode_data, loaded_aliases_data = load_master_data_file(
            options.master_file_path
        )

        if not loaded_unicode_data or not loaded_aliases_data:
            error_msg = "Failed to load data from master file"
            logger.error(error_msg)
            raise ValueError(error_msg)

        unicode_data = loaded_unicode_data
        aliases_data = loaded_aliases_data

    # Filter data by dataset or Unicode blocks if specified
    if options.dataset:
        unicode_data, aliases_data = filter_by_dataset(
            unicode_data, aliases_data, options.dataset
        )
    elif options.unicode_blocks:
        unicode_data, aliases_data = filter_by_unicode_blocks(
            unicode_data, aliases_data, options.unicode_blocks
        )

    # Check if we have any data to export
    if not unicode_data:
        error_msg = "No output files generated"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Create output directory if it doesn't exist and ensure proper permissions
    os.makedirs(options.output_dir, exist_ok=True)
    os.chmod(options.output_dir, 0o755)  # rwxr-xr-x

    # Determine which formats to export
    if options.format_type == "all":
        formats = registry.get_supported_formats()
        if not formats:
            logger.error("No supported formats available")
            return []
        logger.debug(f"Using all supported formats: {formats}")
    else:
        exporter = registry.get_exporter(options.format_type)
        if not exporter:
            logger.error(f"No exporter found for format: {options.format_type}")
            return []
        formats = [options.format_type]
        logger.debug(f"Using single format: {options.format_type}")

    logger.debug(f"Exporting formats: {formats}")
    logger.debug(f"Format type: {options.format_type}")
    logger.debug(f"Supported formats: {registry.get_supported_formats()}")
    logger.debug(f"Output directory: {options.output_dir}")

    # Optimized export: process all formats at once to avoid multiple reads of master data
    output_files = optimized_export(unicode_data, aliases_data, formats, options)

    logger.debug(f"Generated output files: {output_files}")
    return output_files


def optimized_export(
    unicode_data: dict[str, dict[str, str]],
    aliases_data: dict[str, list[str]],
    formats: list[str],
    options: ExportOptions,
) -> list[str]:
    """
    Export Unicode data to multiple formats at once in an optimized way.

    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        formats: List of formats to export to
        options: Export options

    Returns:
        List of paths to the generated output files
    """
    if unicode_data is None or not unicode_data:
        raise ValueError("No Unicode data provided for export")

    output_files = []
    file_handlers: dict[str, TextIO] = {}
    exporters: dict[str, object] = {}
    temp_filenames: dict[str, tuple] = {}
    csv_writers: dict[str, object] = {}
    max_aliases_by_fmt: dict[str, int] = {}

    # Create output directory if it doesn't exist and ensure proper permissions
    os.makedirs(options.output_dir, exist_ok=True)
    os.chmod(options.output_dir, 0o755)  # rwxr-xr-x
    if not os.access(options.output_dir, os.W_OK):
        raise OSError(f"Output directory {options.output_dir} is not writable")

    # Check if we have any exporters available
    available_exporters = {fmt: registry.get_exporter(fmt) for fmt in formats}
    active_formats = [fmt for fmt, exp in available_exporters.items() if exp]

    if not active_formats:
        raise ValueError("No exporters available for the requested formats")

    try:
        # Use ExitStack to manage all file handlers
        with contextlib.ExitStack():
            # 1. Initialize exporters and open files for all formats
            for fmt in active_formats:
                exporter = available_exporters[fmt]
                exporters[fmt] = exporter

                # Get the output filename based on format and dataset
                filename = get_output_filename(fmt, options.dataset)
                # Add extension if not already present
                if not filename.endswith(exporter.extension):
                    filename = filename + exporter.extension
                output_filename = os.path.join(options.output_dir, filename)

                # Create a temporary file for uncompressed output
                temp_filename = output_filename
                if options.compress:
                    temp_filename = output_filename + ".temp"

                # Initialize format-specific handlers
                if fmt == "json":
                    temp_filenames[fmt] = (
                        temp_filename,
                        output_filename,
                        False,  # False = no items written yet
                    )
                else:
                    temp_filenames[fmt] = (temp_filename, output_filename)

                # Open file handler with context manager
                with open(
                    temp_filename, "w", encoding="utf-8", newline=""
                ) as file_handler:
                    file_handlers[fmt] = file_handler

                # Write format-specific headers
                if fmt == "json":
                    file_handler.write("[\n")
                elif fmt == "lua":
                    file_handler.write("-- Auto-generated unicode data module\n")
                    file_handler.write("-- Generated by uniff-gen\n")
                    file_handler.write("return {\n")
                elif fmt == "csv":
                    csv_writers[fmt] = csv.writer(file_handler)

            # Write format-specific headers
            if fmt == "json":
                file_handlers[fmt].write("[\n")
            elif fmt == "lua":
                file_handlers[fmt].write("-- Auto-generated unicode data module\n")
                file_handlers[fmt].write("-- Generated by uniff-gen\n")
                file_handlers[fmt].write("return {\n")
            elif fmt == "csv":
                # Calculate max aliases
                max_aliases = 0
                if aliases_data:
                    for aliases in aliases_data.values():
                        max_aliases = max(max_aliases, len(aliases))
                max_aliases_by_fmt[fmt] = max_aliases

                # Create CSV writer and write header
                csv_writers[fmt] = csv.writer(file_handlers[fmt])
                headers = ["code_point", "character", "name", "category", "block"]
                for i in range(1, max_aliases + 1):
                    headers.append(f"alias_{i}")
                csv_writers[fmt].writerow(headers)

        # 2. Process each record once and write to all formats
        for code_point_hex, data in unicode_data.items():
            current_aliases = aliases_data.get(code_point_hex, [])

            # Write this record to all active formats
            for fmt in active_formats:
                file_handler = file_handlers[fmt]

                if fmt == "csv":
                    # Write CSV row
                    row = [
                        f"U+{code_point_hex}",
                        data["char_obj"],
                        data["name"],
                        data["category"],
                        data.get("block", "Unknown Block"),
                    ]

                    max_aliases = max_aliases_by_fmt[fmt]
                    for i in range(max_aliases):
                        row.append(current_aliases[i] if i < len(current_aliases) else "")

                    csv_writers[fmt].writerow(row)

                elif fmt == "json":
                    # Add JSON entry
                    import json

                    entry = {
                        "code_point": f"U+{code_point_hex}",
                        "character": data["char_obj"],
                        "name": data["name"],
                        "category": data["category"],
                        "block": data.get("block", "Unknown Block"),
                        "aliases": current_aliases,
                    }
                    json_str = json.dumps(entry, ensure_ascii=False, indent=2)

                    # Add comma if not the first item
                    if fmt in temp_filenames:
                        temp_filename, output_filename, has_items = temp_filenames[fmt]
                        if has_items:
                            file_handler.write(",\n")
                        else:
                            # Mark that we've written the first item
                            temp_filenames[fmt] = (temp_filename, output_filename, True)

                    file_handler.write(json_str)

                elif fmt == "lua":
                    # Handle special characters for Lua
                    char = data["char_obj"]
                    if char == "\n":
                        char = "\\n"
                    elif char == "\r":
                        char = "\\r"
                    elif char == "\t":
                        char = "\\t"
                    elif char == '"':
                        char = '\\"'
                    elif char == "\\":
                        char = "\\\\"
                    elif ord(char) < 32:  # Other control characters
                        char = f"\\{ord(char):03d}"

                    # Helper function to properly escape Lua strings
                    def escape_lua_string(s):
                        # First escape backslashes
                        s = s.replace("\\", "\\\\")
                        # Then escape other special characters
                        s = s.replace('"', '\\"')
                        s = s.replace("\n", "\\n")
                        s = s.replace("\r", "\\r")
                        s = s.replace("\t", "\\t")
                        # Replace any other control characters
                        result = ""
                        for c in s:
                            if ord(c) < 32 and c not in "\n\r\t":
                                result += f"\\{ord(c):03d}"
                            else:
                                result += c
                        return result

                    # Escape special characters in all string fields
                    name = escape_lua_string(data["name"])
                    category = escape_lua_string(data["category"])
                    block = escape_lua_string(data.get("block", "Unknown Block"))

                    file_handler.write("  {\n")
                    file_handler.write(f'    code_point = "U+{code_point_hex}",\n')
                    file_handler.write(f'    character = "{char}",\n')
                    file_handler.write(f'    name = "{name}",\n')
                    file_handler.write(f'    category = "{category}",\n')
                    file_handler.write(f'    block = "{block}",\n')

                    # Write aliases as a Lua table
                    if current_aliases:
                        file_handler.write("    aliases = {\n")
                        for alias in current_aliases:
                            # Use the same escaping function for aliases
                            escaped_alias = escape_lua_string(alias)
                            file_handler.write(f'      "{escaped_alias}",\n')
                        file_handler.write("    },\n")
                    else:
                        file_handler.write("    aliases = {},\n")

                    file_handler.write("  },\n")

                elif fmt == "txt":
                    # Format: character|name|code_point|category|block|alias1|alias2|...
                    # Optimized for grep with searchable fields first
                    line_parts = [
                        data["char_obj"],
                        data["name"],
                        f"U+{code_point_hex}",
                        data["category"],
                        data.get("block", "Unknown Block"),
                    ]

                    # Add aliases if they exist
                    if current_aliases:
                        line_parts.extend(current_aliases)

                    # Join with pipe separator
                    file_handler.write("|".join(line_parts) + "\n")
        # 3. Write footers and process files
        for fmt in formats:
            if fmt not in file_handlers:
                continue

            file_handler = file_handlers[fmt]

            try:
                # Write format-specific footers
                if fmt == "json":
                    file_handler.write("\n]")
                elif fmt == "lua":
                    file_handler.write("}\n")

                # Flush and close the file
                file_handler.flush()
                os.fsync(file_handler.fileno())
                file_handler.close()

                # Get filenames
                if fmt == "json":
                    temp_filename, output_filename, _ = temp_filenames[fmt]
                else:
                    temp_filename, output_filename = temp_filenames[fmt]

                # Verify the uncompressed file exists and is not empty
                if (
                    not os.path.exists(temp_filename)
                    or os.path.getsize(temp_filename) == 0
                ):
                    raise OSError(f"Failed to create output file: {temp_filename}")

                # Compress if requested
                if options.compress:
                    compressed_filename = output_filename + ".gz"
                    try:
                        compress_file(temp_filename, compressed_filename)
                        if not os.path.exists(compressed_filename) or (
                            os.path.getsize(compressed_filename) == 0
                        ):
                            raise OSError("Compressed file is missing or empty")
                        os.remove(
                            temp_filename
                        )  # Remove temp file only after successful compression
                        output_filename = compressed_filename
                    except Exception as e:
                        logger.error(f"Compression failed: {e}")
                        raise  # Let the original exception propagate
                else:
                    # Validate the exported file
                    exporters[fmt].verify(temp_filename)
                    output_filename = temp_filename

                # Add to output files list
                output_files.append(output_filename)

            except Exception:
                # Close file before re-raising
                with contextlib.suppress(Exception):
                    file_handler.close()
                raise  # Let the original exception propagate

        if not output_files:
            raise ValueError("No output files were generated")

        return output_files

    except Exception as e:
        logger.error("Export failed: %s", e)
        raise

    finally:
        # Clean up temporary files
        for fmt in formats:
            if fmt in temp_filenames:
                temp_file = temp_filenames[fmt][0]
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as cleanup_error:
                        msg = "Failed to clean temp file"
                        logger.error("%s: %s", msg, cleanup_error)


def compress_file(input_file: str, output_file: str) -> None:
    """
    Compress a file using gzip.

    Args:
        input_file: Path to the file to compress
        output_file: Path to the output file

    Raises:
        OSError: If there is an error reading, writing, or compressing the file
    """
    if not os.path.exists(input_file):
        raise OSError(f"Input file does not exist: {input_file}")

    if os.path.exists(output_file):
        os.remove(output_file)  # Remove existing output file to avoid partial writes

    try:
        with (
            open(input_file, "rb") as f_in,
            gzip.open(output_file, "wb", compresslevel=9) as f_out,
        ):
            shutil.copyfileobj(f_in, f_out)
            f_out.flush()
            os.fsync(f_out.fileno())  # Ensure data is written to disk
    except Exception as e:
        # Clean up partial output file if compression failed
        if os.path.exists(output_file):
            os.remove(output_file)
        raise OSError(f"Failed to compress file {input_file}: {str(e)}") from e


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
        source_files_dir = os.path.join(xdg_data_dir, "uniff-gen", "source-files")

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
