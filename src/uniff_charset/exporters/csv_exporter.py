"""
CSV exporter implementation.
"""

import csv
import logging
from typing import Optional

from ..validator import validate_csv_file
from .base import BaseExporter

logger = logging.getLogger("uniff")


class CSVExporter(BaseExporter):
    """
    Exporter for CSV format.
    """

    @property
    def format_type(self) -> str:
        """
        Get the format type that this exporter handles.

        Returns:
            The format type ('csv')
        """
        return "csv"

    @property
    def extension(self) -> str:
        """
        Get the file extension for this format.

        Returns:
            The file extension ('.csv')
        """
        return ".csv"

    def write(
        self,
        unicode_data: dict[str, dict[str, str]],
        aliases_data: dict[str, list[str]],
        output_filename: str,
    ) -> bool:
        """
        Write Unicode data to CSV format.

        Args:
            unicode_data: Dictionary mapping code points to character information
            aliases_data: Dictionary mapping code points to lists of aliases
            output_filename: Path to the output file

        Returns:
            True if the write was successful, False otherwise
        """
        if not unicode_data:
            logger.debug("No Unicode data to write. Aborting CSV creation.")
            return False

        # Determine the maximum number of aliases for any character
        max_aliases = 0
        if aliases_data:
            for cp in unicode_data:
                if cp in aliases_data:
                    max_aliases = max(max_aliases, len(aliases_data[cp]))
        logger.debug(f"Maximum aliases per character: {max_aliases}")

        # Create CSV headers
        headers = ["code_point", "character", "name", "category", "block"]
        for i in range(1, max_aliases + 1):
            headers.append(f"alias_{i}")

        try:
            logger.debug(f"Writing CSV file with headers: {', '.join(headers)}")
            with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)

                for code_point_hex, data in unicode_data.items():
                    current_aliases = aliases_data.get(code_point_hex, [])
                    row = [
                        f"U+{code_point_hex}",
                        data["char_obj"],
                        data["name"],
                        data["category"],
                        data.get("block", "Unknown Block"),
                    ]
                    for i in range(max_aliases):
                        row.append(current_aliases[i] if i < len(current_aliases) else "")
                    writer.writerow(row)

            return True
        except Exception as e:
            logger.debug(f"Error writing CSV file: {e}")
            return False

    def verify(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Verify that a file is valid for this format.

        Args:
            file_path: Path to the file to verify

        Returns:
            A tuple of (is_valid, error_message)
        """
        is_valid, error = validate_csv_file(file_path)
        if not is_valid:
            logger.debug(f"CSV validation failed: {error}")
        else:
            logger.debug("CSV validation successful")
        return is_valid, error
