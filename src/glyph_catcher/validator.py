"""
Module for validating exported Unicode data files.
"""

import csv
import json
import os
import re
import subprocess
import tempfile
from typing import Optional


def validate_csv_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a CSV file by attempting to read all rows.

    Args:
        file_path: Path to the CSV file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    try:
        # First, check for NUL characters which can cause issues with CSV parsing
        with open(file_path, "rb") as f:
            content = f.read()
            if b"\x00" in content:
                # Replace NUL characters for validation purposes
                content = content.replace(b"\x00", b"?")
                # Write to a temporary file for validation
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".csv"
                ) as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(content)

                file_to_validate = temp_file_path
            else:
                file_to_validate = file_path

        with open(file_to_validate, encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)
            # Read header
            header = next(reader)

            # Check if header contains expected columns
            required_columns = ["code_point", "character", "name", "category", "block"]
            for col in required_columns:
                if col not in header:
                    return False, f"Missing required column: {col}"

            # Read all rows to check for CSV format errors
            row_count = 1  # Already read header
            for row in reader:
                row_count += 1

                # Check if row has at least the required number of columns
                if len(row) < len(required_columns):
                    return (
                        False,
                        f"Row {row_count} has insufficient columns: {len(row)} (expected at least {len(required_columns)})",
                    )

        # Clean up temporary file if created
        if "temp_file_path" in locals():
            os.unlink(temp_file_path)

        return True, None
    except Exception as e:
        return False, f"CSV validation error: {str(e)}"


def validate_json_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a JSON file by attempting to parse it.

    Args:
        file_path: Path to the JSON file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

            # Check if data is a list
            if not isinstance(data, list):
                return False, "JSON data is not a list"

            # Check if list is empty
            if not data:
                return False, "JSON data is empty"

            # Check if each item has the required fields
            required_fields = [
                "code_point",
                "character",
                "name",
                "category",
                "block",
                "aliases",
            ]
            for i, item in enumerate(data):
                for field in required_fields:
                    if field not in item:
                        return False, f"Item {i} is missing required field: {field}"

        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON validation error: {str(e)}"
    except Exception as e:
        return False, f"Error validating JSON file: {str(e)}"


def validate_lua_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a Lua file by checking its syntax using luac.

    Args:
        file_path: Path to the Lua file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    try:
        # Use luac to check syntax without loading the file
        result = subprocess.run(
            ["luac", "-p", file_path], capture_output=True, text=True, check=False
        )

        # Check if luac command was successful
        if result.returncode != 0:
            return False, f"Lua syntax error: {result.stderr.strip()}"

        # Additional validation: check if the file starts with the expected header
        with open(file_path, encoding="utf-8") as f:
            first_line = f.readline().strip()
            if not first_line.startswith("--"):
                return False, "Missing expected Lua comment header"

            # Check if the file contains 'return {'
            f.seek(0)
            content = f.read()
            if "return {" not in content:
                return False, "Missing 'return {' in Lua file"

        return True, None
    except FileNotFoundError:
        return (
            False,
            "luac command not found. Please install Lua to validate Lua files.",
        )
    except Exception as e:
        return False, f"Error validating Lua file: {str(e)}"


def validate_txt_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate a text file by checking if each line follows the expected format.

    Args:
        file_path: Path to the text file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    try:
        with open(file_path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                line_number += 1
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Check if line has at least 5 pipe-separated fields
                # Format: character|name|code_point|category|block|alias1|alias2|...
                parts = line.split("|")
                if len(parts) < 5:
                    return (
                        False,
                        f"Line {line_number} has insufficient fields: {len(parts)} (expected at least 5)",
                    )

                # Find the code point field by looking for a pattern matching U+XXXX
                # This handles special cases like the vertical line character
                code_point_found = False
                for part in parts:
                    if re.match(r"^U\+[0-9A-F]{4,6}$", part):
                        code_point_found = True
                        break

                if not code_point_found:
                    return (
                        False,
                        f"Line {line_number} has no valid code point format (expected U+XXXX)",
                    )

        return True, None
    except Exception as e:
        return False, f"Error validating text file: {str(e)}"


def validate_exported_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate an exported file based on its extension.

    Args:
        file_path: Path to the file to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    # Check if file is gzipped
    if file_path.endswith(".gz"):
        return False, "Cannot validate compressed files. Please decompress first."

    # Determine file type based on extension
    if file_path.endswith(".csv"):
        return validate_csv_file(file_path)
    elif file_path.endswith(".json"):
        return validate_json_file(file_path)
    elif file_path.endswith(".lua"):
        return validate_lua_file(file_path)
    elif file_path.endswith(".txt"):
        return validate_txt_file(file_path)
    else:
        return False, f"Unsupported file type: {os.path.splitext(file_path)[1]}"
