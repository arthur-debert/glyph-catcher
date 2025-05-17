"""
Core functionality for the uniff-ligs package.

This module handles the core processing and generation of ligature data.
"""

import csv
import os

from uniff_core.progress import ProgressDisplay
from uniff_core.types import ExportOptions


def process_ligature_data(
    options: ExportOptions, verbose: bool = False
) -> tuple[bool, list[str]]:
    """
    Process ligature data.

    Args:
        options: Export options
        verbose: Whether to display verbose output

    Returns:
        Tuple of (success, list of output files)
    """
    # Create progress display
    progress = ProgressDisplay(verbose=verbose)
    main_task = progress.add_root_item("Processing ligature data")

    # Create output directory if it doesn't exist
    os.makedirs(options.output_dir, exist_ok=True)

    # Track output files
    output_files = []

    # Determine which formats to export
    # For now, just handle CSV as a simple example
    if options.format_type in ["csv", "all"]:
        csv_task = progress.add_child_item(main_task, "Generating CSV output")

        # Generate a dummy CSV file with some example ligatures
        output_filename = os.path.join(options.output_dir, "ligatures.csv")

        try:
            with open(output_filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["sequence", "glyph", "description"])

                # Write some example ligatures
                writer.writerow(["->", "→", "Right Arrow"])
                writer.writerow(["=>", "⇒", "Right Double Arrow"])
                writer.writerow(["!=", "≠", "Not Equal To"])
                writer.writerow(["<=", "≤", "Less Than or Equal To"])
                writer.writerow([">=", "≥", "Greater Than or Equal To"])
                writer.writerow(["::", "∷", "Proportion"])
                writer.writerow(["...", "…", "Ellipsis"])
                writer.writerow(["--", "–", "En Dash"])
                writer.writerow(["---", "—", "Em Dash"])

            output_files.append(output_filename)
            csv_task.set_success(f"Created {output_filename}")
        except Exception as e:
            csv_task.set_failure(f"Error: {str(e)}")
            return False, []

    # Mark main task as successful
    main_task.set_success()

    return True, output_files
