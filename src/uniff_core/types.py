"""
Type definitions and dataclasses for the uniff packages.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FetchOptions:
    """Options for fetching data files."""

    use_cache: bool = False
    cache_dir: Optional[str] = None
    use_temp_cache: bool = False  # If True, use temporary cache location
    data_dir: Optional[str] = None  # Directory to store the master data file


@dataclass
class ExportOptions:
    """Options for exporting data."""

    format_type: str = "csv"
    output_dir: str = "."
    use_master_file: bool = True  # Whether to use the master data file for exporting
    master_file_path: Optional[str] = None  # Path to the master data file
    dataset: str = "complete"  # Dataset to use ("everyday" or "complete")
    compress: bool = False  # Whether to compress the output files
