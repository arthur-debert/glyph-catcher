"""
Type definitions and dataclasses for the uniff-charset package.
"""

from dataclasses import dataclass
from typing import Optional

from uniff_core.types import ExportOptions


@dataclass
class UnicodeCharInfo:
    """Information about a Unicode character."""

    name: str
    category: str
    char_obj: str


@dataclass
class CharsetExportOptions(ExportOptions):
    """Options for exporting Unicode character data."""

    unicode_blocks: Optional[list[str]] = None  # List of Unicode block names to include
    dataset: str = "every-day"  # Dataset to use ('every-day' or 'complete')
