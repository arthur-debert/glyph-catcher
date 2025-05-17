"""
Command-line interface for the uniff-ligs package.

This module handles all CLI-related functionality including argument parsing,
command definitions, and usage information.
"""

import click
from uniff_core.types import ExportOptions


@click.group()
def cli():
    """
    uniff-ligs: Generate ligature data.

    This tool generates ligature data for mapping sequences of ASCII characters
    to single glyphs for use with text editors and plugins.
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
    "--compress",
    is_flag=True,
    default=False,
    help="Compress output files using gzip for maximum compression",
)
def generate(format, output_dir, compress):
    """
    Generate ligature dataset in the specified format.

    Creates a mapping of ASCII sequences to ligature glyphs and saves
    the output in the specified format.
    """
    # Create options objects
    export_options = ExportOptions(
        format_type=format,
        output_dir=output_dir,
        compress=compress,
    )

    # Import here to avoid circular imports
    from .core import process_ligature_data

    # Process the data with progress display
    success, output_files = process_ligature_data(export_options, verbose=True)

    # Final output
    if success:
        click.echo(
            click.style("✓ Ligature data processing completed successfully!", fg="green")
        )
        click.echo("Generated files:")
        for file_path in output_files:
            click.echo(f"  - {file_path}")
        return 0
    else:
        click.echo(click.style("✗ Ligature data processing failed.", fg="red"))
        return 1


@cli.command()
def info():
    """
    Display information about ligature data.

    Shows details about ligatures and their usage.
    """
    click.echo("uniff-ligs: Ligature Data Information")
    click.echo("=======================================")
    click.echo("")
    click.echo("Ligatures are special character combinations that are")
    click.echo("rendered as a single glyph. For example:")
    click.echo("")
    click.echo("  -> can be rendered as →")
    click.echo("  => can be rendered as ⇒")
    click.echo("  != can be rendered as ≠")
    click.echo("")
    click.echo("These are particularly useful in programming fonts and code editors.")
