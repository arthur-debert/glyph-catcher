"""
Base module for exporting processed data to various formats.
"""

import gzip
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger("uniff")


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
        valid = os.path.exists(output_filename) and os.path.getsize(output_filename) > 0
        if valid:
            logger.debug(
                f"Verified export file: {output_filename} (size: {os.path.getsize(output_filename)} bytes)"
            )
        else:
            logger.debug(f"Export file verification failed: {output_filename}")
        return valid


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
        logger.debug(f"Registering exporter for format: {format_type}")
        self.exporters[format_type] = exporter

    def get_exporter(self, format_type: str) -> Exporter:
        """
        Get an exporter for a format.

        Args:
            format_type: Format type identifier

        Returns:
            Exporter instance or None if not found
        """
        exporter = self.exporters.get(format_type)
        if exporter is None:
            logger.debug(f"No exporter found for format: {format_type}")
        return exporter

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
            data = f_in.read()
            f_out.write(data)
            logger.debug(
                f"Compressed file {input_filename} to {output_filename}.gz (original: {len(data)} bytes)"
            )
    except Exception as e:
        logger.debug(f"Failed to compress file {input_filename}: {str(e)}")


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
            data = f_in.read()
            f_out.write(data)
            logger.debug(
                f"Decompressed file {input_filename} to {output_filename} (size: {len(data)} bytes)"
            )
    except Exception as e:
        logger.debug(f"Failed to decompress file {input_filename}: {str(e)}")
