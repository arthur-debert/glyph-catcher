"""
JSON exporter implementation.
"""

import json
import logging
from typing import Optional

from ..validator import validate_json_file
from .base import BaseExporter

logger = logging.getLogger("uniff")


class JSONExporter(BaseExporter):
    """
    Exporter for JSON format.
    """

    @property
    def format_type(self) -> str:
        """
        Get the format type that this exporter handles.

        Returns:
            The format type ('json')
        """
        return "json"

    @property
    def extension(self) -> str:
        """
        Get the file extension for this format.

        Returns:
            The file extension ('.json')
        """
        return ".json"

    def write(
        self,
        unicode_data: dict[str, dict[str, str]],
        aliases_data: dict[str, list[str]],
        output_filename: str,
    ) -> bool:
        """
        Write Unicode data to JSON format.

        Args:
            unicode_data: Dictionary mapping code points to character information
            aliases_data: Dictionary mapping code points to lists of aliases
            output_filename: Path to the output file

        Returns:
            True if the write was successful, False otherwise
        """
        if not unicode_data:
            logger.debug("No Unicode data to write. Aborting JSON creation.")
            return False

        logger.debug(f"Creating JSON structure for {len(unicode_data)} characters")

        json_data = []
        for code_point_hex, data in unicode_data.items():
            entry = {
                "code_point": f"U+{code_point_hex}",
                "character": data["char_obj"],
                "name": data["name"],
                "category": data["category"],
                "block": data.get("block", "Unknown Block"),
                "aliases": aliases_data.get(code_point_hex, []),
            }
            json_data.append(entry)

        try:
            logger.debug(f"Writing JSON data to {output_filename}")
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully wrote {len(json_data)} entries to JSON file")
            return True
        except Exception as e:
            logger.debug(f"Error writing JSON file: {e}")
            return False

    def verify(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Verify that a file is valid for this format.

        Args:
            file_path: Path to the file to verify

        Returns:
            A tuple of (is_valid, error_message)
        """
        is_valid, error = validate_json_file(file_path)
        if not is_valid:
            logger.debug(f"JSON validation failed: {error}")
        else:
            logger.debug("JSON validation successful")
        return is_valid, error
