"""
Type definitions and dataclasses for the uniff packages.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("uniff")


@dataclass
class FetchOptions:
    """Options for fetching data files."""

    use_cache: bool = False
    cache_dir: Optional[str] = None
    use_temp_cache: bool = False  # If True, use temporary cache location
    data_dir: Optional[str] = None  # Directory to store the master data file
    force: bool = False  # If True, force regeneration of data files

    def __post_init__(self):
        """Log fetch options after initialization."""
        logger.debug(
            f"FetchOptions created: cache={self.use_cache}, "
            f"cache_dir={self.cache_dir}, temp_cache={self.use_temp_cache}, "
            f"data_dir={self.data_dir}"
        )


@dataclass
class ExportOptions:
    """Options for exporting data."""

    format_type: str = "csv"
    output_dir: str = "."
    use_master_file: bool = True  # Whether to use the master data file for exporting
    master_file_path: Optional[str] = None  # Path to the master data file
    dataset: str = "complete"  # Dataset to use ("everyday" or "complete")
    compress: bool = False  # Whether to compress the output files
    debug: bool = False  # Whether to enable debug logging

    def __post_init__(self):
        """Log export options after initialization."""
        logger.debug(
            f"ExportOptions created: format={self.format_type}, "
            f"output_dir={self.output_dir}, use_master={self.use_master_file}, "
            f"master_path={self.master_file_path}, dataset={self.dataset}, "
            f"compress={self.compress}, debug={self.debug}"
        )
