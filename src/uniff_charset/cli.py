"""
Command-line interface for the uniff-charset package.

This module handles all CLI-related functionality including argument parsing,
command definitions, and usage information.
"""

import logging

import click
from uniff_core.logging import setup_logging
from uniff_core.types import FetchOptions

from .config import (
    DATASET_EVERYDAY,
    DATASET_TYPES,
    DEFAULT_CACHE_DIR,
    DEFAULT_DATA_DIR,
    TMP_CACHE_DIR,
)
from .fetcher import clean_cache
from .processor import get_master_file_path
from .types import CharsetExportOptions


@click.group()
def cli():
    """
    uniff-charset: Download and process Unicode character data.

    This tool downloads Unicode character data from various sources,
    processes it, and generates output in different formats for use
    with text editors and plugins.
    """
    pass


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["csv", "json", "lua", "txt", "all"]),
    default="csv",
    help="Output format (default: csv)",
)
@click.option(
    "--output-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default=".",
    help="Output directory (default: current directory)",
)
@click.option(
    "--use-cache/--no-cache",
    default=False,
    help="Use cached files if available",
)
@click.option(
    "--cache-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default=DEFAULT_CACHE_DIR,
    help=f"Directory to store cached files (default: {DEFAULT_CACHE_DIR})",
)
@click.option(
    "--use-temp-cache",
    is_flag=True,
    default=False,
    help=f"Use temporary cache directory ({TMP_CACHE_DIR})",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force regeneration of master data file even if cached version exists",
)
@click.option(
    "--unicode-blocks",
    multiple=True,
    help="Unicode block(s) to include (can be specified multiple times). "
    "If not specified, all blocks are included.",
)
@click.option(
    "--exit-on-error",
    is_flag=True,
    default=False,
    help="Exit with code 1 on error",
)
@click.option(
    "--data-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default=None,
    help=f"Directory to store the master data file (default: {DEFAULT_DATA_DIR})",
)
@click.option(
    "--no-master-file",
    is_flag=True,
    default=False,
    help="Don't use the master data file for exporting",
)
@click.option(
    "--dataset",
    type=click.Choice(DATASET_TYPES),
    default=DATASET_EVERYDAY,
    help=f"Dataset to use (default: {DATASET_EVERYDAY})",
)
@click.option(
    "--compress",
    is_flag=True,
    default=False,
    help="Compress output files using gzip for maximum compression",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging to /tmp/unifill.log",
)
def generate(
    format,
    output_dir,
    use_cache,
    cache_dir,
    use_temp_cache,
    force,
    unicode_blocks,
    exit_on_error,
    data_dir,
    no_master_file,
    dataset,
    compress,
    debug,
):
    """
    Generate Unicode character dataset in the specified format.

    Downloads Unicode data files, processes them, and generates output
    in the specified format. The output can be in CSV, JSON, Lua, or
    text format, or all formats at once.

    You can filter the output to include only specific Unicode blocks
    by using the --unicode-blocks option. For example:

    \b
    uniff-charset generate --unicode-blocks "Basic Latin" \\
        --unicode-blocks "Greek"

    You can also select a predefined dataset using the --dataset option:

    \b
    uniff-charset generate --dataset every-day  # Default, common
                                                # (6618 characters)
    uniff-charset generate --dataset complete   # Includes all Unicode blocks
    """
    # Set up logging if debug mode is enabled
    if debug:
        log_file = "/tmp/uniff.log"

        # Create a file handler only, no stdout/stderr handlers
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Get the root logger and configure it
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Remove any existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add only the file handler, no stdout handlers
        root_logger.addHandler(file_handler)

        # Log to the file only
        logging.debug(f"Debug mode enabled, logging to {log_file}")
    else:
        # If not in debug mode, disable all logging
        logging.basicConfig(level=logging.ERROR)
        for handler in logging.root.handlers[:]:
            handler.setLevel(logging.ERROR)

    # Create options objects
    fetch_options = FetchOptions(
        use_cache=use_cache,
        cache_dir=cache_dir,
        use_temp_cache=use_temp_cache,
        data_dir=data_dir,
        force=force,
    )

    # Convert unicode_blocks tuple to list if specified
    blocks_list = list(unicode_blocks) if unicode_blocks else None

    export_options = CharsetExportOptions(
        format_type=format,
        output_dir=output_dir,
        unicode_blocks=blocks_list,
        use_master_file=not no_master_file,
        master_file_path=(
            get_master_file_path(fetch_options) if not no_master_file else None
        ),
        dataset=dataset,
        compress=compress,
    )

    # Import here to avoid circular imports
    from .core import process_unicode_data

    # Setup logging
    setup_logging(debug)

    # Process the data with progress display
    success, output_files = process_unicode_data(
        fetch_options, export_options, verbose=True, debug=debug
    )

    # Final output
    if success:
        if output_files:
            click.echo(
                click.style(
                    "✓ Unicode data processing completed successfully!",
                    fg="green",
                )
            )
            click.echo("Generated files:")
            for file_path in output_files:
                click.echo(f"  - {file_path}")
            return 0
        else:
            click.echo(click.style("✗ Unicode data processing failed.", fg="red"))
            if exit_on_error:
                return 1
            return 0


@cli.command()
def info():
    """
    Display information about the Unicode data formats.

    Shows details about the available output formats and their uses.
    """
    click.echo("uniff-charset: Unicode Data Format Information")
    click.echo("==============================================")
    click.echo("")
    click.echo("Available output formats:")
    click.echo("")
    click.echo("1. CSV (unicode_data.csv)")
    click.echo("   - Tabular format with columns for code point, character, name")
    click.echo("   - Also includes category and aliases")
    click.echo("   - Good for viewing in spreadsheet applications")
    click.echo("")
    click.echo("2. JSON (unicode_data.json)")
    click.echo("   - Structured format with objects for each character")
    click.echo("   - Useful for web applications or further processing")
    click.echo("")
    click.echo("3. Lua (unicode_data.lua)")
    click.echo("   - Lua module format for direct use in Neovim plugins")
    click.echo("   - Default format used by the Unifill plugin")
    click.echo("")
    click.echo("4. Text (unicode_data.txt)")
    click.echo("   - Pipe-separated format optimized for grep-based searching")
    click.echo("   - Used by the grep backend in Unifill")
    click.echo("")
    click.echo(
        "Use the 'generate' command with the --format option to create these files."
    )
    click.echo("")
    click.echo("Unicode Block Filtering:")
    click.echo("------------------------")
    click.echo("You can filter the output to include only specific Unicode blocks")
    click.echo("using the --unicode-blocks option. Common blocks include:")
    click.echo("")
    click.echo("  - Basic Latin")
    click.echo("  - Latin-1 Supplement")
    click.echo("  - Latin Extended-A")
    click.echo("  - Greek and Coptic")
    click.echo("  - Cyrillic")
    click.echo("  - General Punctuation")
    click.echo("  - Mathematical Operators")
    click.echo("  - Miscellaneous Symbols")
    click.echo("  - Emoticons")
    click.echo("")
    click.echo("Example:")
    click.echo('  uniff-charset generate --unicode-blocks "Basic Latin" \\')
    click.echo('  --unicode-blocks "Emoticons"')


@cli.command()
@click.option(
    "--use-temp-cache",
    is_flag=True,
    default=False,
    help=f"Clean temporary cache directory ({TMP_CACHE_DIR})",
)
@click.option(
    "--cache-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default=DEFAULT_CACHE_DIR,
    help=f"Directory to clean (default: {DEFAULT_CACHE_DIR})",
)
def clean_cache_cmd(use_temp_cache, cache_dir):
    """
    Clean the cache directories.

    Removes all cached Unicode data files to ensure a fresh download
    on the next run. Useful for testing or when Unicode data is updated.
    """
    fetch_options = FetchOptions(
        use_cache=True,  # Not actually used for cleaning, but required
        cache_dir=cache_dir,
        use_temp_cache=use_temp_cache,
    )

    clean_cache(fetch_options)
    click.echo(click.style("✓ Cache cleaned successfully!", fg="green"))
    return 0


@cli.command()
def list_blocks():
    """
    List all available Unicode blocks.

    Displays a list of all Unicode blocks that can be used with the
    --unicode-blocks option in the generate command.
    """
    # This is a simplified list of common Unicode blocks
    # In a real implementation, this would be generated from the Unicode data
    blocks = [
        "Basic Latin",
        "Latin-1 Supplement",
        "Latin Extended-A",
        "Latin Extended-B",
        "IPA Extensions",
        "Spacing Modifier Letters",
        "Combining Diacritical Marks",
        "Greek and Coptic",
        "Cyrillic",
        "Cyrillic Supplement",
        "Armenian",
        "Hebrew",
        "Arabic",
        "Devanagari",
        "Bengali",
        "Gurmukhi",
        "Gujarati",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Thai",
        "Lao",
        "Tibetan",
        "Georgian",
        "Hangul Jamo",
        "Latin Extended Additional",
        "Greek Extended",
        "General Punctuation",
        "Superscripts and Subscripts",
        "Currency Symbols",
        "Combining Diacritical Marks for Symbols",
        "Letterlike Symbols",
        "Number Forms",
        "Arrows",
        "Mathematical Operators",
        "Miscellaneous Technical",
        "Control Pictures",
        "Optical Character Recognition",
        "Enclosed Alphanumerics",
        "Box Drawing",
        "Block Elements",
        "Geometric Shapes",
        "Miscellaneous Symbols",
        "Dingbats",
        "Miscellaneous Mathematical Symbols-A",
        "Supplemental Arrows-A",
        "Braille Patterns",
        "Supplemental Arrows-B",
        "Miscellaneous Mathematical Symbols-B",
        "Supplemental Mathematical Operators",
        "Miscellaneous Symbols and Arrows",
        "CJK Radicals Supplement",
        "Kangxi Radicals",
        "Ideographic Description Characters",
        "CJK Symbols and Punctuation",
        "Hiragana",
        "Katakana",
        "Bopomofo",
        "Hangul Compatibility Jamo",
        "Kanbun",
        "Bopomofo Extended",
        "CJK Strokes",
        "Katakana Phonetic Extensions",
        "Enclosed CJK Letters and Months",
        "CJK Compatibility",
        "CJK Unified Ideographs Extension A",
        "Yijing Hexagram Symbols",
        "CJK Unified Ideographs",
        "Yi Syllables",
        "Yi Radicals",
        "Hangul Syllables",
        "High Surrogates",
        "High Private Use Surrogates",
        "Low Surrogates",
        "Private Use Area",
        "CJK Compatibility Ideographs",
        "Alphabetic Presentation Forms",
        "Arabic Presentation Forms-A",
        "Variation Selectors",
        "Vertical Forms",
        "Combining Half Marks",
        "CJK Compatibility Forms",
        "Small Form Variants",
        "Arabic Presentation Forms-B",
        "Halfwidth and Fullwidth Forms",
        "Specials",
        "Linear B Syllabary",
        "Linear B Ideograms",
        "Aegean Numbers",
        "Ancient Greek Numbers",
        "Ancient Symbols",
        "Phaistos Disc",
        "Emoticons",
        "Ornamental Dingbats",
        "Transport and Map Symbols",
        "Alchemical Symbols",
        "Geometric Shapes Extended",
        "Supplemental Arrows-C",
    ]

    click.echo("Available Unicode Blocks:")
    click.echo("=========================")
    click.echo("")
    for block in blocks:
        click.echo(f"- {block}")
    click.echo("")
    click.echo(
        "Use these block names with the --unicode-blocks option in the generate command."
    )
    click.echo("Example:")
    click.echo('  uniff-charset generate --unicode-blocks "Basic Latin" \\')
    click.echo('  --unicode-blocks "Arrows"')


def parse_args():
    """
    Parse command-line arguments and return the appropriate options.

    This function is used by __main__.py to get the parsed arguments.

    Returns:
        The result of cli() which is the Click command group execution
    """
    return cli()


def get_generate_options(
    format="csv",
    output_dir=".",
    use_cache=False,
    cache_dir=DEFAULT_CACHE_DIR,
    use_temp_cache=False,
    force=False,
    unicode_blocks=None,
    exit_on_error=False,
    data_dir=None,
    no_master_file=False,
    dataset=DATASET_EVERYDAY,
    compress=False,
    debug=False,
):
    """
    Create and return options for the generate command.

    This function is a non-CLI version of the generate command that can be
    called directly from Python code.

    Args:
        format: Output format (csv, json, lua, txt, all)
        output_dir: Output directory
        use_cache: Whether to use cached files if available
        cache_dir: Directory to store cached files
        use_temp_cache: Whether to use temporary cache directory
        force: Whether to force regeneration of master data file even if cached
        version exists
        unicode_blocks: List of Unicode block names to include
        exit_on_error: Whether to exit with code 1 on error
        data_dir: Directory to store the master data file
        no_master_file: Whether to use the master data file for exporting
        dataset: Dataset to use (every-day or complete)
        compress: Whether to compress output files
        debug: Whether to enable debug logging

    Returns:
        Tuple of (fetch_options, export_options, exit_on_error)
    """
    # Create options objects
    fetch_options = FetchOptions(
        use_cache=use_cache,
        cache_dir=cache_dir,
        use_temp_cache=use_temp_cache,
        data_dir=data_dir,
        force=force,
    )

    # Convert unicode_blocks to list if specified
    blocks_list = list(unicode_blocks) if unicode_blocks else None

    export_options = CharsetExportOptions(
        format_type=format,
        output_dir=output_dir,
        unicode_blocks=blocks_list,
        use_master_file=not no_master_file,
        master_file_path=(
            get_master_file_path(fetch_options) if not no_master_file else None
        ),
        dataset=dataset,
        compress=compress,
        debug=debug,
    )

    return fetch_options, export_options, exit_on_error
