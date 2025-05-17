"""
Base module for exporting processed data to various formats.
"""

import gzip
import os
from abc import ABC, abstractmethod


class Exporter(ABC):
    """Base class for data exporters."""

    @abstractmethod
    def write(self, data: dict, metadata: dict, output_filename: str) -> bool:
        """
        Write data to the specified output file.

        Args:
            data: The main data to export
            metadata: Additional metadata for the export
            output_filename: Path to the output file

        Returns:
            True if the export was successful, False otherwise
        """
        pass

    def verify(self, output_filename: str) -> bool:
        """
        Verify the exported file.

        Args:
            output_filename: Path to the exported file

        Returns:
            True if the file is valid, False otherwise
        """
        return os.path.exists(output_filename) and os.path.getsize(output_filename) > 0


class ExporterRegistry:
    """Registry for exporters."""

    def __init__(self):
        """Initialize the registry."""
        self.exporters = {}

    def register(self, format_type: str, exporter: Exporter) -> None:
        """
        Register an exporter for a format.

        Args:
            format_type: Format type identifier
            exporter: Exporter instance
        """
        self.exporters[format_type] = exporter

    def get_exporter(self, format_type: str) -> Exporter:
        """
        Get an exporter for a format.

        Args:
            format_type: Format type identifier

        Returns:
            Exporter instance or None if not found
        """
        return self.exporters.get(format_type)

    def get_supported_formats(self) -> list[str]:
        """
        Get a list of supported export formats.

        Returns:
            List of format type identifiers
        """
        return list(self.exporters.keys())


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
