"""
Module for processing Unicode data files.
"""

import hashlib
import json
import logging
import os
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from typing import Any, Optional

from .config import (
    ALIAS_SOURCE_CLDR,
    ALIAS_SOURCE_FORMAL,
    ALIAS_SOURCE_INFORMATIVE,
    DATASET_COMPLETE,
    DATASET_TEST,
    get_alias_sources,
    get_dataset_blocks,
    get_unicode_blocks,
)

logger = logging.getLogger("uniff")


def get_unicode_block(code_point: int) -> str:
    """
    Get the Unicode block name for a given code point.

    Args:
        code_point: Unicode code point as an integer

    Returns:
        Name of the Unicode block, or "Unknown Block" if not found
    """
    unicode_blocks = get_unicode_blocks()
    for block_range, block_name in unicode_blocks.items():
        if code_point in block_range:
            logger.debug(f"Code point {hex(code_point)} belongs to block '{block_name}'")
            return block_name
    logger.debug(f"No block found for code point {hex(code_point)}")
    return "Unknown Block"


def parse_unicode_data(filename: str) -> dict[str, dict[str, str]]:
    """
    Parse UnicodeData.txt.

    Args:
        filename: Path to UnicodeData.txt

    Returns:
        Dictionary mapping code points to character information:
        {code_point_hex: {'name': name, 'category': category, 'char_obj': char}}
    """
    data = {}
    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                fields = line.strip().split(";")
                if len(fields) >= 3:
                    try:
                        code_point_int = int(fields[0], 16)
                        name = fields[1]
                        category = fields[2]

                        if name.startswith("<") and name.endswith(", First>"):
                            continue
                        if name.startswith("<") and name.endswith(", Last>"):
                            continue

                        code_point_hex = format(code_point_int, "04X")
                        char_obj = chr(code_point_int)
                        block = get_unicode_block(code_point_int)
                        data[code_point_hex] = {
                            "name": name,
                            "category": category,
                            "char_obj": char_obj,
                            "block": block,
                        }
                        logger.debug(
                            f"Parsed character {code_point_hex}: {name}"
                            f"({category}) in block {block}"
                        )
                    except ValueError as e:
                        logger.debug(
                            f"Skipping invalid code point: {fields[0]} - {name}: {str(e)}"
                        )
                        continue
        return data
    except FileNotFoundError:
        logger.error(f"Error: {filename} not found.")
        return {}
    except Exception as e:
        logger.error(f"An error occurred while parsing {filename}: {e}")
        return {}


def parse_name_aliases(filename: str) -> dict[str, list[str]]:
    """
    Parse NameAliases.txt.

    Args:
        filename: Path to NameAliases.txt

    Returns:
        Dictionary mapping code points to lists of aliases:
        {code_point_hex: [alias1, alias2, ...]}
    """
    aliases_data = defaultdict(list)
    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                fields = line.split(";")
                if len(fields) >= 2:
                    code_point_int = int(fields[0], 16)
                    code_point_hex = format(code_point_int, "04X")
                    alias = fields[1]
                    aliases_data[code_point_hex].append(alias)
        return aliases_data
    except FileNotFoundError:
        logger.error(f"Error: {filename} not found.")
        return {}
    except Exception as e:
        logger.error(f"An error occurred while parsing {filename}: {e}")
        return {}


def parse_names_list(filename: str) -> dict[str, list[str]]:
    """
    Parse NamesList.txt to extract informative aliases.

    Args:
        filename: Path to NamesList.txt

    Returns:
        Dictionary mapping code points to lists of informative aliases:
        {code_point_hex: [alias1, alias2, ...]}
    """
    informative_aliases = defaultdict(list)
    current_code_point = None

    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                original_line = line
                line = line.strip()

                # Skip comments, headers, and empty lines
                if not line or line.startswith("@") or line.startswith(";"):
                    continue

                # Check if this is a new character definition
                if not original_line.startswith("\t"):
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        try:
                            # Store the code point as a hex string
                            current_code_point = parts[0].strip()
                        except ValueError:
                            current_code_point = None
                    else:
                        current_code_point = None
                # Check if this is an informative alias (starts with "= ")
                elif current_code_point and "=" in line and line.lstrip().startswith("="):
                    # Extract the alias (remove the "= " prefix)
                    alias = line.lstrip()[1:].strip()
                    # Convert code point to uppercase hex format to match
                    # unicode_char_info keys
                    code_point_hex = current_code_point.upper()
                    informative_aliases[code_point_hex].append(alias)
                # Also include cross-references as aliases (lines starting with "* ")
                elif current_code_point and "*" in line and line.lstrip().startswith("*"):
                    # Extract the descriptive note (remove the "* " prefix)
                    note = line.lstrip()[1:].strip()
                    # Only include if it's not too long and doesn't contain references
                    # to other characters
                    if len(note) < 50 and "(" not in note and ")" not in note:
                        code_point_hex = current_code_point.upper()
                        informative_aliases[code_point_hex].append(note)

        return informative_aliases
    except FileNotFoundError:
        logger.error(f"Error: {filename} not found.")
        return {}
    except Exception as e:
        logger.error(f"An error occurred while parsing {filename}: {e}")
        return {}


def parse_cldr_annotations(filename: str) -> dict[str, list[str]]:
    """
    Parse CLDR annotations XML file to extract common names and descriptions.

    Args:
        filename: Path to CLDR annotations XML file

    Returns:
        Dictionary mapping code points to lists of annotations:
        {code_point_hex: [annotation1, annotation2, ...]}
    """
    cldr_annotations = defaultdict(list)

    try:
        tree = ElementTree.parse(filename)
        root = tree.getroot()

        # Find all annotation elements
        for annotation in root.findall(".//annotation"):
            # Skip text-to-speech annotations (type="tts")
            if "type" in annotation.attrib:
                continue

            # Get the character code point
            if "cp" in annotation.attrib:
                char = annotation.attrib["cp"]
                # Convert character sequence to code points and ensure 4-digit format
                code_points = []
                for c in char:
                    cp = ord(c)
                    cp_hex = format(cp, "04X")
                    code_points.append(cp_hex)
                code_point_hex = code_points[0]  # Use first code point as key

                # Store full sequence info if multi-char
                if len(code_points) > 1:
                    logger.debug(f"Multi-char sequence: {char} -> {code_points}")

                # Get the annotations (pipe-separated list)
                if annotation.text:
                    # Split by pipe and strip whitespace
                    aliases = [alias.strip() for alias in annotation.text.split("|")]
                    cldr_annotations[code_point_hex].extend(aliases)

        return cldr_annotations
    except FileNotFoundError:
        logger.error(f"Error: {filename} not found.")
        return {}
    except Exception as e:
        logger.error(f"An error occurred while parsing {filename}: {e}")
        return {}


def normalize_alias(alias: str) -> str:
    """
    Normalize an alias by converting to lowercase and stripping whitespace.

    Args:
        alias: The alias to normalize

    Returns:
        Normalized alias string
    """
    return alias.lower().strip()


def process_data_files(
    file_paths: dict[str, str], progress_item=None
) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    """
    Process Unicode data files.

    Args:
        file_paths: Dictionary mapping file types to file paths

    Returns:
        Tuple of (unicode_data, aliases_data) where:
        - unicode_data is a dictionary mapping code points to character information
        - aliases_data is a dictionary mapping code points to lists of aliases
    """
    # Parse the Unicode data files
    logger.debug("Starting Unicode data file processing")
    unicode_data = parse_unicode_data(file_paths["unicode_data"])
    if not unicode_data:
        logger.debug("Failed to parse Unicode data file")
        return {}, {}

    # Get the configured alias sources
    alias_sources = get_alias_sources()

    # Parse the alias sources based on configuration
    formal_aliases = {}
    if ALIAS_SOURCE_FORMAL in alias_sources:
        formal_aliases = parse_name_aliases(file_paths["name_aliases"])

    informative_aliases = {}
    if ALIAS_SOURCE_INFORMATIVE in alias_sources:
        informative_aliases = parse_names_list(file_paths["names_list"])

    cldr_annotations = {}
    if ALIAS_SOURCE_CLDR in alias_sources and "cldr_annotations" in file_paths:
        cldr_annotations = parse_cldr_annotations(file_paths["cldr_annotations"])

    # Merge aliases with deduplication
    aliases_data = defaultdict(list)
    alias_sets = defaultdict(set)  # Use sets for deduplication

    # Calculate total work to be done - count total unique code points
    total_code_points = len(
        set().union(
            formal_aliases.keys() if ALIAS_SOURCE_FORMAL in alias_sources else set(),
            informative_aliases.keys()
            if ALIAS_SOURCE_INFORMATIVE in alias_sources
            else set(),
            cldr_annotations.keys() if ALIAS_SOURCE_CLDR in alias_sources else set(),
        )
    )

    # Initialize progress counter
    processed_code_points = 0

    # Process and add formal aliases if configured
    if ALIAS_SOURCE_FORMAL in alias_sources:
        for code_point, aliases in formal_aliases.items():
            code_point_hex = code_point.upper()
            for alias in aliases:
                normalized_alias = normalize_alias(alias)
                if normalized_alias not in alias_sets[code_point_hex]:
                    alias_sets[code_point_hex].add(normalized_alias)
            processed_code_points += 1
            if progress_item:
                progress_item.update_progress(
                    processed_code_points,
                    total_code_points,
                    (
                        f"Processing formal aliases "
                        f"({processed_code_points}/{total_code_points})"
                    ),
                )

    # Process and add informative aliases if configured
    if ALIAS_SOURCE_INFORMATIVE in alias_sources:
        for code_point, aliases in informative_aliases.items():
            code_point_hex = code_point.upper()
            for alias in aliases:
                normalized_alias = normalize_alias(alias)
                if normalized_alias not in alias_sets[code_point_hex]:
                    alias_sets[code_point_hex].add(normalized_alias)
            processed_code_points += 1
            if progress_item:
                progress_item.update_progress(
                    processed_code_points,
                    total_code_points,
                    (
                        f"Processing informative aliases "
                        f"({processed_code_points}/{total_code_points})"
                    ),
                )

    # Process and add CLDR annotations if configured
    if ALIAS_SOURCE_CLDR in alias_sources:
        for code_point, annotations in cldr_annotations.items():
            code_point_hex = code_point.upper()
            for annotation in annotations:
                normalized_alias = normalize_alias(annotation)
                if normalized_alias not in alias_sets[code_point_hex]:
                    alias_sets[code_point_hex].add(normalized_alias)
            processed_code_points += 1
            if progress_item:
                progress_item.update_progress(
                    processed_code_points,
                    total_code_points,
                    (
                        f"Processing CLDR annotations "
                        f"({processed_code_points}/{total_code_points})"
                    ),
                )

    # Convert sets back to lists for compatibility with the rest of the codebase
    for code_point, alias_set in alias_sets.items():
        aliases_data[code_point] = sorted(alias_set)

    return unicode_data, aliases_data


def filter_by_dataset(
    unicode_data: dict[str, dict[str, str]],
    aliases_data: dict[str, list[str]],
    dataset: str,
) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    """
    Filter Unicode data by dataset name.

    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        dataset: Dataset name (e.g., 'every-day', 'complete', 'test')

    Returns:
        Tuple of filtered (unicode_data, aliases_data)
    """
    # Special case for the test dataset - just take a small subset
    if dataset == DATASET_TEST:
        # Create a smaller dataset for testing - first 50 characters from Basic Latin
        test_unicode_data = {}
        test_aliases_data = {}

        # Sort code points for deterministic results
        code_points = sorted(unicode_data.keys())
        count = 0

        for code_point in code_points:
            char_info = unicode_data[code_point]
            if "block" in char_info and char_info["block"] == "Basic Latin":
                test_unicode_data[code_point] = char_info
                if code_point in aliases_data:
                    test_aliases_data[code_point] = aliases_data[code_point]
                count += 1
                if count >= 50:  # Only take the first 50 characters
                    break

        return test_unicode_data, test_aliases_data

    # Get the list of blocks for the dataset
    blocks = get_dataset_blocks(dataset)

    # If no blocks are defined or dataset is 'complete', return all data
    if not blocks or dataset == DATASET_COMPLETE:
        return unicode_data, aliases_data

    # Filter by blocks
    return filter_by_unicode_blocks(unicode_data, aliases_data, blocks)


def filter_by_unicode_blocks(
    unicode_data: dict[str, dict[str, str]],
    aliases_data: dict[str, list[str]],
    blocks: Optional[list[str]],
) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    """
    Filter Unicode data by block names.

    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        blocks: List of Unicode block names to include, or None to include all blocks

    Returns:
        Tuple of filtered (unicode_data, aliases_data)
    """
    if not blocks:
        return unicode_data, aliases_data

    # Special case: if blocks contains 'all', include all blocks
    if "all" in blocks:
        return unicode_data, aliases_data

    filtered_unicode_data = {}
    filtered_aliases_data = {}

    for code_point, char_info in unicode_data.items():
        if "block" in char_info and char_info["block"] in blocks:
            filtered_unicode_data[code_point] = char_info
            if code_point in aliases_data:
                filtered_aliases_data[code_point] = aliases_data[code_point]

    return filtered_unicode_data, filtered_aliases_data


def save_master_data_file(
    unicode_data: dict[str, dict[str, str]],
    aliases_data: dict[str, list[str]],
    data_dir: str,
    file_paths: Optional[dict[str, str]] = None,
    checksum: Optional[str] = None,
) -> Optional[str]:
    """
    Save the processed Unicode data to a master JSON file.

    If file_paths or checksum is provided, the filename will include a checksum
    to enable caching and reuse of processed data.

    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        data_dir: Directory to save the master data file
        file_paths: Dictionary mapping file types to file paths (optional)
        checksum: Pre-calculated checksum string (optional)

    Returns:
        Path to the saved master data file, or None if saving failed
    """
    if not unicode_data or not aliases_data:
        return None

    try:
        # Create the data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        logger.debug(f"Saving master data file to {data_dir}")

        # Prepare the data for serialization
        master_data = {"unicode_data": {}, "aliases_data": aliases_data}

        # Convert UnicodeCharInfo objects to dictionaries
        for code_point, char_info in unicode_data.items():
            master_data["unicode_data"][code_point] = {
                "name": char_info["name"],
                "category": char_info["category"],
                "char_obj": char_info["char_obj"],
                "block": char_info.get("block", "Unknown Block"),
            }

        # Determine the master file path based on checksum if available
        if checksum or file_paths:
            # Get a file path that includes the checksum
            master_file_path = get_master_file_path(
                fetch_options=type("FetchOptions", (), {"data_dir": data_dir})(),
                file_paths=file_paths,
                checksum=checksum,
            )
        else:
            # Use the default master file path
            from .config import MASTER_DATA_FILE

            master_file_path = os.path.join(data_dir, MASTER_DATA_FILE)

        # Save the data to the master file
        with open(master_file_path, "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

        logger.debug(f"Successfully saved master data file: {master_file_path}")
        logger.debug(
            f"Saved {len(unicode_data)} characters and {len(aliases_data)} alias entries"
        )
        return master_file_path

    except Exception as e:
        logger.error(f"Error saving master data file: {e}")
        return None


def load_master_data_file(
    master_file_path: str,
) -> tuple[Optional[dict[str, dict[str, str]]], Optional[dict[str, list[str]]]]:
    """
    Load the processed Unicode data from a master JSON file.

    Args:
        master_file_path: Path to the master data file

    Returns:
        Tuple of (unicode_data, aliases_data), or (None, None) if loading failed
    """
    try:
        # Check if the master file exists
        if not os.path.exists(master_file_path):
            logger.debug(f"Master data file not found: {master_file_path}")
            return None, None

        # Load the data from the master file
        with open(master_file_path, encoding="utf-8") as f:
            master_data = json.load(f)

        # Validate the master data structure
        if not isinstance(master_data, dict):
            logger.error("Invalid master data format: root must be a dictionary")
            return None, None

        # Extract and validate unicode_data
        unicode_data = master_data.get("unicode_data")
        if not isinstance(unicode_data, dict):
            logger.error("Invalid master data format: unicode_data must be a dictionary")
            return None, None

        # Validate unicode_data entries
        for code_point, char_info in unicode_data.items():
            if not isinstance(char_info, dict):
                logger.error(f"Invalid character info for code point {code_point}")
                return None, None
            required_fields = {"name", "category", "char_obj"}
            missing_fields = [
                field for field in required_fields if field not in char_info
            ]
            if missing_fields:
                logger.error(
                    f"Missing required fields in character info for {code_point}"
                )
                return None, None

        # Extract and validate aliases_data
        aliases_data = master_data.get("aliases_data")
        if not isinstance(aliases_data, dict):
            logger.error("Invalid master data format: aliases_data must be a dictionary")
            return None, None

        # Validate aliases_data entries
        for code_point, aliases in aliases_data.items():
            if not isinstance(aliases, list):
                logger.error(f"Invalid aliases format for code point {code_point}")
                return None, None

        total_aliases = sum(len(aliases) for aliases in aliases_data.values())
        logger.debug(f"Loaded master data file: {master_file_path}")
        logger.debug(f"Loaded {len(unicode_data)} characters and {total_aliases} aliases")

        return unicode_data, aliases_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from master file: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error loading master data file: {e}")
        return None, None


def get_master_file_path(
    fetch_options,
    file_paths: Optional[dict[str, str]] = None,
    checksum: Optional[str] = None,
) -> str:
    """
    Get the path to the master data file based on the fetch options.

    If file_paths is provided, a checksum will be calculated and included in
    the filename.
    If checksum is provided directly, it will be used instead of calculating it
    from file_paths.
    If neither file_paths nor checksum is provided, the base master file path
    is returned.

    Args:
        fetch_options: Options for fetching Unicode data files
        file_paths: Dictionary mapping file types to file paths (optional)
        checksum: Pre-calculated checksum string (optional)

    Returns:
        Path to the master data file
    """
    from .config import MASTER_DATA_FILE

    # Get the base master file path
    data_dir = getattr(fetch_options, "data_dir", None)
    if not data_dir:
        logger.error("No data directory specified in fetch options")
        return MASTER_DATA_FILE

    base_path = os.path.join(data_dir, MASTER_DATA_FILE)

    # If no checksum info provided, return the base path
    if not file_paths and not checksum:
        return base_path

    # Calculate or use the provided checksum
    if not checksum and file_paths:
        checksum = calculate_source_files_checksum(file_paths)

    # Insert the checksum before the file extension
    base_name, ext = os.path.splitext(MASTER_DATA_FILE)
    return os.path.join(data_dir, f"{base_name}-{checksum}{ext}")


def calculate_alias_statistics(aliases_data: dict[str, list[str]]) -> dict[str, Any]:
    """
    Calculate statistics about the aliases data.

    Args:
        aliases_data: Dictionary mapping code points to lists of aliases

    Returns:
        Dictionary containing statistics about the aliases data
    """
    total_chars = len(aliases_data)
    total_aliases = sum(len(aliases) for aliases in aliases_data.values())
    avg_aliases = total_aliases / total_chars if total_chars > 0 else 0
    max_aliases = max((len(aliases) for aliases in aliases_data.values()), default=0)
    min_aliases = min((len(aliases) for aliases in aliases_data.values()), default=0)

    return {
        "total_characters": total_chars,
        "total_aliases": total_aliases,
        "average_aliases_per_char": avg_aliases,
        "max_aliases_for_char": max_aliases,
        "min_aliases_for_char": min_aliases,
    }


def calculate_file_checksum(file_path: str) -> str:
    """
    Calculate a SHA-256 checksum of a file.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal string of the SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def calculate_source_files_checksum(file_paths: dict[str, str]) -> str:
    """
    Calculate a combined checksum for multiple source files.

    Args:
        file_paths: Dictionary mapping file types to file paths

    Returns:
        Combined checksum string
    """
    # Sort the file paths to ensure consistent ordering
    sorted_paths = sorted(file_paths.items())

    # Calculate checksums for each file
    checksums = []
    for file_type, file_path in sorted_paths:
        if os.path.exists(file_path):
            file_checksum = calculate_file_checksum(file_path)
            checksums.append(f"{file_type}:{file_checksum}")

    # Combine the checksums
    combined = "|".join(checksums)
    final_checksum = hashlib.sha256(combined.encode()).hexdigest()
    return final_checksum[:8]  # Use first 8 characters for brevity


def find_master_file_by_checksum(data_dir: str, checksum: str) -> Optional[str]:
    """
    Find a master data file with a specific checksum.

    Args:
        data_dir: Directory to search in
        checksum: Checksum to look for

    Returns:
        Path to the master data file if found, None otherwise
    """
    from .config import MASTER_DATA_FILE

    base_name, ext = os.path.splitext(MASTER_DATA_FILE)
    expected_name = f"{base_name}_{checksum}{ext}"  # Changed from - to _
    expected_path = os.path.join(data_dir, expected_name)

    if os.path.exists(expected_path):
        return expected_path

    return None
