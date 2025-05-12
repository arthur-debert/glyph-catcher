GLYPH-CATCHER 
==============

This project downloads and processes Unicode character data from multiple sources
to create a comprehensive dataset for the Unifill Neovim plugin. The dataset
includes character code points, actual characters, official names, categories,
and various aliases.

OVERVIEW
--------

Glyph-catcher is a Python package that:

1. Downloads Unicode data files from official sources
2. Processes the data to create a normalized dataset
3. Saves the complete dataset to a master JSON file
4. Exports the data to various formats for use in applications

The package is designed to be used both as a command-line tool and as a library
in other Python applications.

DATA SOURCES
-----------

The script fetches and processes data from the following sources:

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

DATA PROCESSING PIPELINE
-----------------------

The data processing pipeline consists of three main stages:

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

MASTER DATA FILE
---------------

The master data file is a JSON file that contains the complete processed dataset.
It serves as an intermediate representation between the raw Unicode data files
and the exported formats. The master file:

- Contains all Unicode characters and their aliases
- Is not filtered by Unicode blocks
- Is stored in a persistent location (by default in ~/.local/share/glyph-catcher)
- Is used as the source for exporting to different formats

This approach provides several benefits:
- Faster exports since the data is already processed
- Consistent data across different export formats
- Ability to filter the data without reprocessing the raw files

USAGE
-----

Basic usage:
  poetry run glyph-catcher generate --format all

Options:
  --format FORMAT        Output format: csv, json, lua, txt, or all (default: csv)
  --output-dir DIR       Output directory (default: current directory)
  --use-cache            Use cached files if available
  --cache-dir DIR        Directory to store cached files (default: ~/.cache/glyph-catcher)
  --use-temp-cache       Use temporary cache directory (/tmp/glyph-catcher-cache)
  --unicode-blocks BLOCK Unicode block(s) to include (can be specified multiple times)
  --exit-on-error        Exit with code 1 on error
  --data-dir DIR         Directory to store the master data file (default: ~/.local/share/glyph-catcher)
  --no-master-file       Don't use the master data file for exporting

Commands:
  generate               Generate Unicode character dataset
  info                   Display information about the data formats
  clean-cache            Clean the cache directories
  list-blocks            List all available Unicode blocks

Examples:
  # Generate all formats
  glyph-catcher generate --format all
  
  # Generate only Lua format with specific Unicode blocks
  glyph-catcher generate --format lua --unicode-blocks "Basic Latin" --unicode-blocks "Arrows"
  
  # Clean the cache
  glyph-catcher clean-cache
  
  # List available Unicode blocks
  glyph-catcher list-blocks

OUTPUT FORMATS
-------------

The script can generate the following output formats:

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

EXAMPLE DATA
-----------

For the RIGHTWARDS ARROW character (U+2192, →):

- Official name: "RIGHTWARDS ARROW"
- Category: "Sm" (Symbol, Math)
- Aliases:
  - From NamesList.txt: "z notation total function"
  - From CLDR: "arrow", "right", "right-pointing"

The combined data in Lua format looks like:

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

CACHE MANAGEMENT
--------------

The package provides several options for managing cached files:

1. Default cache location: ~/.cache/glyph-catcher
   - Persistent across sessions
   - Used when --use-cache is specified

2. Temporary cache location: /tmp/glyph-catcher-cache
   - Cleared on system reboot
   - Used when --use-temp-cache is specified

3. Custom cache location
   - Specified with --cache-dir
   - Used when both --use-cache and --cache-dir are specified

To clean the cache:
  glyph-catcher clean-cache

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

The dataset can be extended with additional sources:

1. Additional CLDR languages:
   - Download language-specific annotation files (e.g., fr.xml for French)
   - Parse them similar to the English annotations
   - Store with language tags

2. Other potential sources:
   - HTML/XML entity references (e.g., &rarr; for the right arrow →)
   - LaTeX commands (e.g., \rightarrow for the right arrow →)
   - Programming language escape sequences
   - Emoji database descriptions for emoji characters

To add a new source, implement a parser function similar to the existing ones
and merge the results into the aliases_info dictionary.

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
