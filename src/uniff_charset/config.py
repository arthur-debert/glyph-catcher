"""
Configuration constants and settings for the uniff-gen package.
"""

import os
import tempfile
from typing import Optional

# Try to import yaml, but provide fallback if not available
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Dataset constants
DATASET_EVERYDAY = "every-day"
DATASET_COMPLETE = "complete"
DATASET_TEST = "test"
DATASETS = [DATASET_EVERYDAY, DATASET_COMPLETE, DATASET_TEST]
CONFIG_YAML_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

# Alias source constants
ALIAS_SOURCE_FORMAL = "formal_aliases"
ALIAS_SOURCE_INFORMATIVE = "informative_aliases"
ALIAS_SOURCE_CLDR = "cldr_annotations"
ALIAS_SOURCES = [ALIAS_SOURCE_FORMAL, ALIAS_SOURCE_INFORMATIVE, ALIAS_SOURCE_CLDR]

# URLs for data sources
UCD_LATEST_URL = "https://www.unicode.org/Public/UCD/latest/ucd/"
UNICODE_DATA_FILE_URL = UCD_LATEST_URL + "UnicodeData.txt"
NAME_ALIASES_FILE_URL = UCD_LATEST_URL + "NameAliases.txt"
NAMES_LIST_FILE_URL = UCD_LATEST_URL + "NamesList.txt"
CLDR_ANNOTATIONS_URL = (
    "https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations/en.xml"
)

# Output file names for different formats
OUTPUT_FILES = {
    "csv": "unicode.{dataset}.csv",
    "json": "unicode.{dataset}.json",
    "lua": "unicode.{dataset}.lua",
    "txt": "unicode.{dataset}.txt",
}

# Master data file name (contains the complete processed dataset)
MASTER_DATA_FILE = "unicode_master_data.json"

# Default cache directory

# Use XDG_CACHE_HOME if available, otherwise use a temporary directory
DEFAULT_CACHE_DIR = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.join(os.path.expanduser("~"), ".cache")),
    "uniff-gen",
)

# Default data directory for storing the master data file
DEFAULT_DATA_DIR = os.path.join(
    os.environ.get(
        "XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")
    ),
    "uniff-gen",
)

# Alternative cache location in /tmp for non-persistent storage
TMP_CACHE_DIR = os.path.join(tempfile.gettempdir(), "uniff-gen-cache")

# User agent for HTTP requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


def load_config() -> dict:
    """
    Load configuration from config.yaml.

    Returns:
        Dictionary containing the configuration
    """
    # Default configuration if YAML is not available or loading fails
    default_config = {
        "datasets": {DATASET_EVERYDAY: [], DATASET_COMPLETE: ["all"]},
        "alias-sources": [ALIAS_SOURCE_CLDR],
    }

    if not YAML_AVAILABLE:
        print("Warning: PyYAML not installed. Using default configuration.")
        return default_config

    try:
        with open(CONFIG_YAML_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if config else default_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return default_config


def load_dataset_config() -> dict[str, list[str]]:
    """
    Load dataset configuration from config.yaml.

    Returns:
        Dictionary mapping dataset names to lists of Unicode block names
    """
    config = load_config()
    return config.get("datasets", {DATASET_EVERYDAY: [], DATASET_COMPLETE: ["all"]})


def get_dataset_blocks(dataset_name: str) -> Optional[list[str]]:
    """
    Get the list of Unicode blocks for a given dataset.

    Args:
        dataset_name: Name of the dataset (e.g., 'every-day', 'complete')

    Returns:
        List of Unicode block names, or None if the dataset doesn't exist
    """
    datasets = load_dataset_config()
    return datasets.get(dataset_name)


def get_output_filename(format_type: str, dataset: str) -> str:
    """
    Get the output filename for a given format and dataset.

    Args:
        format_type: Format type (e.g., 'csv', 'json', 'lua', 'txt')
        dataset: Dataset name (e.g., 'every-day', 'complete')

    Returns:
        Output filename
    """
    if format_type in OUTPUT_FILES:
        return OUTPUT_FILES[format_type].format(dataset=dataset)
    return f"unicode.{dataset}.{format_type}"


def get_alias_sources() -> list[str]:
    """
    Get the list of alias sources to use when processing Unicode data.

    Returns:
        List of alias source names (e.g., 'formal_aliases', 'informative_aliases',
        'cldr_annotations')
    """
    # Default to only using CLDR annotations if config loading fails
    default_sources = [ALIAS_SOURCE_CLDR]

    config = load_config()
    sources = config.get("alias-sources", default_sources)

    # Validate sources
    valid_sources = []
    for source in sources:
        if source in ALIAS_SOURCES:
            valid_sources.append(source)
        else:
            print(
                f"Warning: Unknown alias source '{source}'. Valid sources are: "
                f"{', '.join(ALIAS_SOURCES)}"
            )

    # If no valid sources were found, use the default
    if not valid_sources:
        print(
            f"Warning: No valid alias sources found in config. "
            f"Using default: {default_sources}"
        )
        return default_sources

    return valid_sources


def get_unicode_blocks() -> dict[range, str]:
    """
    Get the Unicode blocks from config.yaml.

    Returns:
        Dictionary mapping code point ranges to block names
    """
    config = load_config()
    blocks_config = config.get("unicode-blocks", {})

    # Convert the list ranges to Python range objects
    unicode_blocks = {}
    for block_name, range_values in blocks_config.items():
        if len(range_values) == 2:
            start, end = range_values
            unicode_blocks[range(start, end)] = block_name

    return unicode_blocks
