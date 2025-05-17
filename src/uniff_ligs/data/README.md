# Ligature Datasets

This directory contains CSV files with ligature mappings from ASCII sequences to
Unicode glyphs.

## Datasets

There are two datasets provided:

1. **Everyday Ligatures** (`ligatures_everyday.csv`): A curated set of
   approximately 70 commonly used ligatures. This dataset is designed to be
   lightweight and include only the most frequently used ligatures across
   programming and text editing.

2. **Complete Ligatures** (`ligatures_complete.csv`): A comprehensive set of
   approximately 260 ligatures, including specialized symbols for mathematics,
   logic, programming, and various other domains.

## File Format

Each CSV file contains the following columns:

- `sequence`: The ASCII sequence that triggers the ligature
- `glyph`: The Unicode character/glyph to display
- `category`: The category the ligature belongs to (e.g., arrows, math, logic)
- `description`: A human-readable description of the glyph

## Categories

The ligatures are organized into the following categories:

- `arrows`: Directional arrows of various styles
- `comparison`: Comparison operators (equal, not equal, etc.)
- `math`: Mathematical symbols and operators
- `logic`: Logical operators and symbols
- `sets`: Set theory symbols
- `punctuation`: Special punctuation marks
- `currency`: Currency symbols
- `common_symbols`: Commonly used symbols (copyright, trademark, etc.)
- `greek`: Greek letters (only in complete dataset)
- `programming`: Programming-specific symbols (only in complete dataset)
- `technical`: Technical symbols for keyboards, devices, etc. (only in complete
  dataset)

## Example Usage

```python
import csv

# Load the everyday ligatures
with open("ligatures_everyday.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    ligatures = list(reader)

# Print all arrow ligatures
for lig in ligatures:
    if lig["category"] == "arrows":
        print(f"{lig['sequence']} -> {lig['glyph']} ({lig['description']})")
```

## Character Count

The everyday dataset contains approximately 77 characters in total (sum of all
glyphs), well under the 1000 character limit.
