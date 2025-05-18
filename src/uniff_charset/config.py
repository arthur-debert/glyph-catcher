"""
Configuration for the uniff-charset package.
"""

import os

# Dataset types
DATASET_EVERYDAY = "every-day"
DATASET_COMPLETE = "complete"
DATASET_TEST = "test"
DATASET_TYPES = [DATASET_EVERYDAY, DATASET_COMPLETE]

# Alias source types
ALIAS_SOURCE_FORMAL = "formal"
ALIAS_SOURCE_INFORMATIVE = "informative"
ALIAS_SOURCE_CLDR = "cldr"

# Cache directories
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/uniff-gen")
TMP_CACHE_DIR = "/tmp/uniff-gen"

# Data directories and files
DEFAULT_DATA_DIR = os.path.expanduser("~/.local/share/uniff-gen")
MASTER_DATA_FILE = "unicode_master_data.json"

# URLs for Unicode data files
UNICODE_DATA_FILE_URL = "https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt"
NAME_ALIASES_FILE_URL = "https://www.unicode.org/Public/UCD/latest/ucd/NameAliases.txt"
NAMES_LIST_FILE_URL = "https://www.unicode.org/Public/UCD/latest/ucd/NamesList.txt"
CLDR_ANNOTATIONS_URL = (
    "https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/en.xml"
)

# User agent for HTTP requests
USER_AGENT = "uniff-gen/1.0"

# Unicode block definitions
import os

import yaml

# Load block definitions from YAML
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, encoding="utf-8") as f:
    _config = yaml.safe_load(f)

# Convert YAML block ranges to Python ranges
_UNICODE_BLOCKS = {
    range(start, end): name for name, (start, end) in _config["unicode-blocks"].items()
}

# Dataset block definitions from YAML
_DATASET_BLOCKS = {
    DATASET_EVERYDAY: _config["datasets"]["every-day"],
    DATASET_COMPLETE: [],  # Empty list means include all blocks
    DATASET_TEST: ["Basic Latin"],  # Only Basic Latin for testing
}

# Alias source configuration
_ALIAS_SOURCES = {
    DATASET_EVERYDAY: {ALIAS_SOURCE_FORMAL, ALIAS_SOURCE_INFORMATIVE, ALIAS_SOURCE_CLDR},
    DATASET_COMPLETE: {ALIAS_SOURCE_FORMAL, ALIAS_SOURCE_INFORMATIVE, ALIAS_SOURCE_CLDR},
    DATASET_TEST: {ALIAS_SOURCE_FORMAL},  # Only formal aliases for testing
}


def get_unicode_blocks() -> dict[range, str]:
    """Get the Unicode block definitions."""
    return _UNICODE_BLOCKS


def get_dataset_blocks(dataset: str) -> list[str]:
    """Get the list of blocks for a dataset."""
    return _DATASET_BLOCKS.get(dataset, [])


def get_alias_sources(dataset: str = DATASET_EVERYDAY) -> set[str]:
    """Get the configured alias sources for a dataset."""
    return _ALIAS_SOURCES.get(dataset, set())


def get_output_filename(fmt: str, dataset: str = DATASET_EVERYDAY) -> str:
    """Get the output filename for a given format and dataset."""
    # Always use consistent naming pattern
    if fmt == "csv":
        return "unicode_data.csv"
    return f"unicode.{dataset}.{fmt}"
