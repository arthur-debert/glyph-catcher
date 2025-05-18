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
_UNICODE_BLOCKS = {
    range(0x0000, 0x007F + 1): "Basic Latin",
    range(0x0080, 0x00FF + 1): "Latin-1 Supplement",
    range(0x0100, 0x017F + 1): "Latin Extended-A",
    range(0x0180, 0x024F + 1): "Latin Extended-B",
    range(0x0250, 0x02AF + 1): "IPA Extensions",
    range(0x02B0, 0x02FF + 1): "Spacing Modifier Letters",
    range(0x0300, 0x036F + 1): "Combining Diacritical Marks",
    range(0x0370, 0x03FF + 1): "Greek and Coptic",
    range(0x0400, 0x04FF + 1): "Cyrillic",
    range(0x0500, 0x052F + 1): "Cyrillic Supplement",
    range(0x0530, 0x058F + 1): "Armenian",
    range(0x0590, 0x05FF + 1): "Hebrew",
    range(0x0600, 0x06FF + 1): "Arabic",
    range(0x0900, 0x097F + 1): "Devanagari",
    range(0x0980, 0x09FF + 1): "Bengali",
    range(0x0A00, 0x0A7F + 1): "Gurmukhi",
    range(0x0A80, 0x0AFF + 1): "Gujarati",
    range(0x0B80, 0x0BFF + 1): "Tamil",
    range(0x0C00, 0x0C7F + 1): "Telugu",
    range(0x0C80, 0x0CFF + 1): "Kannada",
    range(0x0D00, 0x0D7F + 1): "Malayalam",
    range(0x0E00, 0x0E7F + 1): "Thai",
    range(0x0E80, 0x0EFF + 1): "Lao",
    range(0x0F00, 0x0FFF + 1): "Tibetan",
    range(0x10A0, 0x10FF + 1): "Georgian",
    range(0x1100, 0x11FF + 1): "Hangul Jamo",
    range(0x1E00, 0x1EFF + 1): "Latin Extended Additional",
    range(0x1F00, 0x1FFF + 1): "Greek Extended",
    range(0x2000, 0x206F + 1): "General Punctuation",
    range(0x2070, 0x209F + 1): "Superscripts and Subscripts",
    range(0x20A0, 0x20CF + 1): "Currency Symbols",
    range(0x20D0, 0x20FF + 1): "Combining Diacritical Marks for Symbols",
    range(0x2100, 0x214F + 1): "Letterlike Symbols",
    range(0x2150, 0x218F + 1): "Number Forms",
    range(0x2190, 0x21FF + 1): "Arrows",
    range(0x2200, 0x22FF + 1): "Mathematical Operators",
    range(0x2300, 0x23FF + 1): "Miscellaneous Technical",
    range(0x2400, 0x243F + 1): "Control Pictures",
    range(0x2440, 0x245F + 1): "Optical Character Recognition",
    range(0x2460, 0x24FF + 1): "Enclosed Alphanumerics",
    range(0x2500, 0x257F + 1): "Box Drawing",
    range(0x2580, 0x259F + 1): "Block Elements",
    range(0x25A0, 0x25FF + 1): "Geometric Shapes",
    range(0x2600, 0x26FF + 1): "Miscellaneous Symbols",
    range(0x2700, 0x27BF + 1): "Dingbats",
    range(0x27C0, 0x27EF + 1): "Miscellaneous Mathematical Symbols-A",
    range(0x27F0, 0x27FF + 1): "Supplemental Arrows-A",
    range(0x2800, 0x28FF + 1): "Braille Patterns",
    range(0x2900, 0x297F + 1): "Supplemental Arrows-B",
    range(0x2980, 0x29FF + 1): "Miscellaneous Mathematical Symbols-B",
    range(0x2A00, 0x2AFF + 1): "Supplemental Mathematical Operators",
    range(0x2B00, 0x2BFF + 1): "Miscellaneous Symbols and Arrows",
    range(0x1F300, 0x1F5FF + 1): "Miscellaneous Symbols and Pictographs",
    range(0x1F600, 0x1F64F + 1): "Emoticons",
}

# Dataset block definitions
_DATASET_BLOCKS = {
    DATASET_EVERYDAY: [
        "Basic Latin",
        "Latin-1 Supplement",
        "Latin Extended-A",
        "General Punctuation",
        "Mathematical Operators",
        "Geometric Shapes",
        "Arrows",
        "Box Drawing",
        "Block Elements",
        "Miscellaneous Symbols",
        "Dingbats",
        "Emoticons",
    ],
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
    if dataset == DATASET_EVERYDAY:
        return f"unicode.{dataset}.{fmt}"
    else:
        return f"unicode_data.{fmt}"
