"""
Base exporter class.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("uniff")


class BaseExporter(ABC):
    """
    Base class for all exporters.

    This class defines the interface that all exporters must implement.
    """

    @property
    @abstractmethod
    def format_type(self) -> str:
        """
        Get the format type that this exporter handles.

        Returns:
            The format type (e.g., 'csv', 'json', 'lua', 'txt')
        """
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """
        Get the file extension for this format.

        Returns:
            The file extension (e.g., '.csv', '.json', '.lua', '.txt')
        """
        pass

    @abstractmethod
    def write(
        self,
        unicode_data: dict[str, dict[str, str]],
        aliases_data: dict[str, list[str]],
        output_filename: str,
    ) -> bool:
        """
        Write Unicode data to the specified format.

        Args:
            unicode_data: Dictionary mapping code points to character information
            aliases_data: Dictionary mapping code points to lists of aliases
            output_filename: Path to the output file

        Returns:
            True if the write was successful, False otherwise
        """
        logger.debug(
            f"Writing {len(unicode_data)} characters and {len(aliases_data)} aliases "
            f"to {output_filename} using {self.format_type} exporter"
        )
        pass

    @abstractmethod
    def verify(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Verify that a file is valid for this format.

        Args:
            file_path: Path to the file to verify

        Returns:
            A tuple of (is_valid, error_message)
        """
        logger.debug(f"Verifying {self.format_type} file: {file_path}")
        pass
