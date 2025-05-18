"""
Registry for exporters.
"""

import logging

logger = logging.getLogger("uniff")


class ExporterRegistry:
    """
    Registry for exporters.

    This class provides a central registry for all exporters. Exporters can register
    themselves with the registry, and the registry can be used to get the appropriate
    exporter for a given format.
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._exporters = {}

    def register(self, exporter) -> None:
        """
        Register an exporter with the registry.

        Args:
            exporter: The exporter to register
        """
        format_type = exporter.format_type
        logger.debug(f"Registering exporter for format: {format_type}")
        self._exporters[format_type] = exporter

    def get_exporter(self, format_type: str):
        """
        Get the exporter for the specified format.

        Args:
            format_type: The format type to get the exporter for

        Returns:
            The exporter for the specified format, or None if no exporter is registered
            for that format
        """
        exporter = self._exporters.get(format_type)
        if exporter is None:
            logger.debug(f"No exporter found for format: {format_type}")
        else:
            logger.debug(f"Found exporter for format: {format_type}")
        return exporter

    def get_all_exporters(self) -> dict[str, object]:
        """
        Get all registered exporters.

        Returns:
            A dictionary mapping format types to exporters
        """
        exporters = self._exporters.copy()
        logger.debug(f"Retrieved all exporters: {', '.join(exporters.keys())}")
        return exporters

    def get_supported_formats(self) -> list[str]:
        """
        Get a list of all supported format types.

        Returns:
            A list of all format types that have registered exporters
        """
        formats = list(self._exporters.keys())
        logger.debug(f"Supported formats: {', '.join(formats)}")
        return formats
