"""
Registry for exporters.
"""


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
        self._exporters[exporter.format_type] = exporter

    def get_exporter(self, format_type: str):
        """
        Get the exporter for the specified format.

        Args:
            format_type: The format type to get the exporter for

        Returns:
            The exporter for the specified format, or None if no exporter is registered
            for that format
        """
        return self._exporters.get(format_type)

    def get_all_exporters(self) -> dict[str, object]:
        """
        Get all registered exporters.

        Returns:
            A dictionary mapping format types to exporters
        """
        return self._exporters.copy()

    def get_supported_formats(self) -> list[str]:
        """
        Get a list of all supported format types.

        Returns:
            A list of all format types that have registered exporters
        """
        return list(self._exporters.keys())
