"""
Simple test script to test the export functionality.
"""

from uniff_gen.exporter import export_data
from uniff_gen.types import ExportOptions

# Sample Unicode data
unicode_data = {
    "0041": {
        "name": "LATIN CAPITAL LETTER A",
        "category": "Lu",
        "char_obj": "A",
        "block": "Basic Latin",
    },
    "0042": {
        "name": "LATIN CAPITAL LETTER B",
        "category": "Lu",
        "char_obj": "B",
        "block": "Basic Latin",
    },
}

# Sample aliases data
aliases_data = {
    "0041": ["LATIN LETTER A", "first letter"],
    "0042": ["LATIN LETTER B", "second letter"],
}

# Export options
options = ExportOptions(
    format_type="all",
    output_dir="./tmp_output",
    dataset="every-day",
)

# Export the data
print("Exporting data...")
output_files = export_data(unicode_data, aliases_data, options)

# Print the output files
print(f"Generated {len(output_files)} files:")
for file_path in output_files:
    print(f"  - {file_path}")
