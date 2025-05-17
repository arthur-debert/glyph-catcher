uniff-gen
-------------------------

This project downloads and processes Unicode data from multiple sources
to create comprehensive datasets for text editors and plugins. It supports
two main types of data:

1. Charsets - Unicode character data (code points, names, categories, aliases)
2. Ligatures - Mappings of character sequences to single glyphs (e.g., -> to →)

TLDR
---------
Most likely the only thing relevant for you are the actual datasets.
They get built on new git tags and can be accessed with:

   https://github.com/arthur-debert/uniff-gen/releases/latest/download/unicode.complete.lua.gz
   https://github.com/arthur-debert/uniff-gen/releases/latest/download/unicode.every-day.lua.gz
   https://github.com/arthur-debert/uniff-gen/releases/latest/download/ligatures.csv.gz

OVERVIEW
---------------

This project consists of two main commands:

1. `uniff-charset`: Processes Unicode character data
   - Downloads Unicode data files from official sources
   - Processes the data to create a normalized character dataset
   - Exports the data to various formats for use in applications

2. `uniff-ligs`: Processes ligature mappings
   - Generates mappings from character sequences to ligature glyphs
   - Creates dataset files for use in text editors and plugins

The package is designed to be used both as a command-line tool and as a library
in other Python applications.

DATA SOURCES
-----------------------

The charset processor fetches and processes data from the following sources:

1. UnicodeData.txt
   - Source: Unicode Character Database (UCD)
   - Content: Primary character information including code points, official names,
     and general categories
   - URL: https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt

2. NameAliases.txt
   - Source: Unicode Character Database (UCD)
   - Content: Formal aliases for characters, including corrections, control codes,
     and alternative names
   - URL: https://www.unicode.org/Public/UCD/latest/ucd/NameAliases.txt

3. NamesList.txt
   - Source: Unicode Character Database (UCD)
   - Content: Informative aliases, cross-references, and notes about characters
   - URL: https://www.unicode.org/Public/UCD/latest/ucd/NamesList.txt
   - Format: Contains entries like "= z notation total function" which are
     extracted as aliases

4. CLDR Annotations
   - Source: Unicode Common Locale Data Repository (CLDR)
   - Content: Common names and descriptions for characters in various languages
   - URL: https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations/en.xml
   - Format: XML file with entries like <annotation cp="→">arrow | right | right-pointing</annotation>

The ligature processor works with sequence-to-glyph mappings.

DATA PROCESSING PIPELINE
-----------------------

The character data processing pipeline consists of three main stages:

1. Fetching
   - Downloads the raw Unicode data files from their sources
   - Caches the files locally to avoid repeated downloads
   - Handles network errors and retries

2. Processing
   - Parses the raw data files to extract relevant information
   - Normalizes the data (e.g., joining aliases, handling control characters)
   - Creates a master JSON file containing the complete dataset

3. Exporting
   - Reads from the master JSON file
   - Filters the data if specific Unicode blocks are requested
   - Exports to various formats (CSV, JSON, Lua, TXT)

The ligature processing pipeline focuses on mapping character sequences to their corresponding glyphs.

MASTER DATA FILE
---------------

The master data file is a JSON file that contains the complete processed dataset.
It serves as an intermediate representation between the raw Unicode data files
and the exported formats. The master file:

- Contains all Unicode characters and their aliases
- Is not filtered by Unicode blocks
- Is stored in a persistent location (by default in ~/.local/share/uniff-gen)
- Is used as the source for exporting to different formats

This approach provides several benefits:
- Faster exports since the data is already processed
- Consistent data across different export formats
- Ability to filter the data without reprocessing the raw files

USAGE
-----

Basic charset usage:
  poetry run uniff-charset generate --format all

Basic ligature usage:
  poetry run uniff-ligs generate --format csv

Charset options:
  --format FORMAT        Output format: csv, json, lua, txt, or all (default: csv)
  --output-dir DIR       Output directory (default: current directory)
  --use-cache            Use cached files if available
  --cache-dir DIR        Directory to store cached files (default: ~/.cache/uniff-gen)
  --use-temp-cache       Use temporary cache directory (/tmp/uniff-gen-cache)
  --unicode-blocks BLOCK Unicode block(s) to include (can be specified multiple times)
  --exit-on-error        Exit with code 1 on error
  --data-dir DIR         Directory to store the master data file (default: ~/.local/share/uniff-gen)
  --no-master-file       Don't use the master data file for exporting

Ligature options:
  --format FORMAT        Output format: csv, json, lua, txt, or all (default: csv)
  --output-dir DIR       Output directory (default: current directory)
  --compress             Compress output files using gzip for maximum compression

Charset commands:
  generate               Generate Unicode character dataset
  info                   Display information about the data formats
  clean-cache            Clean the cache directories
  list-blocks            List all available Unicode blocks

Ligature commands:
  generate               Generate ligature dataset
  info                   Display information about ligature data

Examples:
  # Generate all charset formats
  uniff-charset generate --format all

  # Generate only Lua format with specific Unicode blocks
  uniff-charset generate --format lua --unicode-blocks "Basic Latin" --unicode-blocks "Arrows"

  # Clean the cache
  uniff-charset clean-cache

  # List available Unicode blocks
  uniff-charset list-blocks

  # Generate ligature data
  uniff-ligs generate --format csv

OUTPUT FORMATS
-------------

The charset processor can generate the following output formats:

1. CSV (unicode_data.csv)
   - Tabular format with columns for code point, character, name, category, and aliases
   - Good for viewing in spreadsheet applications

2. JSON (unicode_data.json)
   - Structured format with objects for each character
   - Useful for web applications or further processing

3. Lua (unicode_data.lua)
   - Lua module format for direct use in Neovim plugins
   - Default format used by the Unifill plugin

4. Text (unicode_data.txt)
   - Pipe-separated format optimized for grep-based searching
   - Used by the grep backend in Unifill

The ligature processor generates a CSV file (ligatures.csv) with columns for sequence, glyph, and description.

EXAMPLE DATA
-----------

For the RIGHTWARDS ARROW character (U+2192, →):

Charset data in Lua format:
  {
    code_point = "U+2192",
    character = "→",
    name = "RIGHTWARDS ARROW",
    category = "Sm",
    aliases = {
      "z notation total function",
      "arrow",
      "right",
      "right-pointing",
    },
  }

Ligature data in CSV format:
  sequence,glyph,description
  ->,→,Right Arrow
  =>,⇒,Right Double Arrow
  !=,≠,Not Equal To

CACHE MANAGEMENT
--------------

The package provides several options for managing cached files:

1. Default cache location: ~/.cache/uniff-gen
   - Persistent across sessions
   - Used when --use-cache is specified

2. Temporary cache location: /tmp/uniff-gen-cache
   - Cleared on system reboot
   - Used when --use-temp-cache is specified

3. Custom cache location
   - Specified with --cache-dir
   - Used when both --use-cache and --cache-dir are specified

To clean the cache:
  uniff-charset clean-cache

ERROR HANDLING
------------

The package includes robust error handling:

1. Network errors
   - Retries failed downloads
   - Provides clear error messages
   - Falls back to cached files when available

2. Parsing errors
   - Skips invalid entries
   - Reports parsing errors
   - Continues processing valid data

3. File system errors
   - Creates directories as needed
   - Handles permission issues
   - Reports file system errors

EXTENDING THE DATASET
-------------------

The charset dataset can be extended with additional sources:

1. Additional CLDR languages:
   - Download language-specific annotation files (e.g., fr.xml for French)
   - Parse them similar to the English annotations
   - Store with language tags

2. Other potential sources:
   - HTML/XML entity references (e.g., &rarr; for the right arrow →)
   - LaTeX commands (e.g., \rightarrow for the right arrow →)
   - Programming language escape sequences
   - Emoji database descriptions for emoji characters

The ligature dataset can be extended with additional mappings from various programming fonts and editor configurations.

DEVELOPMENT
----------

To set up the development environment:

1. Install Poetry (https://python-poetry.org/)
2. Clone the repository
3. Run `poetry install` to install dependencies
4. Run `poetry run pytest` to run tests

The project uses:
- pytest for testing
- ruff for linting
- black for code formatting

CONTRIBUTING
-----------

Contributions are welcome! Please feel free to submit a Pull Request.

LICENSE
------

This project is licensed under the MIT License - see the LICENSE file for details.
