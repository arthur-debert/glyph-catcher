"""
Exporters module for glyph-catcher.

This module contains the exporter registry and base exporter class.
"""

from .base import BaseExporter
from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .lua_exporter import LuaExporter
from .registry import ExporterRegistry
from .txt_exporter import TxtExporter

# Initialize the registry
registry = ExporterRegistry()

# Register the exporters
registry.register(CSVExporter())
registry.register(JSONExporter())
registry.register(LuaExporter())
registry.register(TxtExporter())

__all__ = [
    "registry",
    "BaseExporter",
    "CSVExporter",
    "JSONExporter",
    "LuaExporter",
    "TxtExporter",
]
