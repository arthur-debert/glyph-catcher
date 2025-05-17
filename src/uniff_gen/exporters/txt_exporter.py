"""
TXT exporter implementation.
"""

from typing import Optional

from ..validator import validate_txt_file
from .base import BaseExporter


class TxtExporter(BaseExporter):
    """
    Exporter for TXT format.
    """

    @property
    def format_type(self) -> str:
        """
        Get the format type that this exporter handles.

        Returns:
            The format type ('txt')
        """
        return "txt"

    @property
    def extension(self) -> str:
        """
        Get the file extension for this format.

        Returns:
            The file extension ('.txt')
        """
        return ".txt"

    def write(
        self,
        unicode_data: dict[str, dict[str, str]],
        aliases_data: dict[str, list[str]],
        output_filename: str,
    ) -> bool:
        """
        Write Unicode data in a grep-friendly text format.

        Args:
            unicode_data: Dictionary mapping code points to character information
            aliases_data: Dictionary mapping code points to lists of aliases
            output_filename: Path to the output file

        Returns:
            True if the write was successful, False otherwise
        """
        if not unicode_data:
            print("No Unicode data to write. Aborting text file creation.")
            return False

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                for code_point_hex, data in unicode_data.items():
                    # Format: character|name|code_point|category|block|alias1|alias2|...
                    # Optimized for grep with searchable fields first

                    # Create the base parts of the line
                    line_parts = [
                        data["char_obj"],
                        data["name"],
                        f"U+{code_point_hex}",
                        data["category"],
                        data.get("block", "Unknown Block"),
                    ]

                    # Add aliases if they exist
                    if code_point_hex in aliases_data:
                        line_parts.extend(aliases_data[code_point_hex])

                    # Join with pipe separator
                    f.write("|".join(line_parts) + "\n")
            return True
        except Exception as e:
            print(f"Error writing text file: {e}")
            return False

    def verify(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Verify that a file is valid for this format.

        Args:
            file_path: Path to the file to verify

        Returns:
            A tuple of (is_valid, error_message)
        """
        return validate_txt_file(file_path)
