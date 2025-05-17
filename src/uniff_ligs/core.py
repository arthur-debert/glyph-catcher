"""
Core functionality for the uniff-ligs package.

This module handles the core processing and generation of ligature data.
"""

import csv
import json
import os
import shutil
from pathlib import Path

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

    # Get path to data files (stored within the package)
    package_dir = Path(__file__).parent
    everyday_dataset = package_dir / "data" / "ligatures_everyday.csv"
    complete_dataset = package_dir / "data" / "ligatures_complete.csv"

    # Ensure the data directory exists
    data_dir = package_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Determine which dataset to use
    dataset_to_use = complete_dataset
    if options.dataset == "everyday":
        dataset_to_use = everyday_dataset

    # Determine which formats to export
    if options.format_type in ["csv", "all"]:
        csv_task = progress.add_child_item(main_task, "Generating CSV output")

        try:
            # Create output filename
            output_filename = os.path.join(options.output_dir, "ligatures.csv")

            # If the dataset file exists, copy it to the output
            if dataset_to_use.exists():
                shutil.copy(dataset_to_use, output_filename)
                output_files.append(output_filename)
                csv_task.set_success(f"Created {output_filename}")
            else:
                # Generate a simple default CSV with common ligatures
                with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)

                    # Write header
                    writer.writerow(
                        [
                            "unicode_codepoint",
                            "unicode_name",
                            "unicode_utf8",
                            "sequence",
                            "category",
                            "description",
                        ]
                    )

                    # Write some example ligatures
                    writer.writerow(
                        ["U+2192", "RIGHTWARDS ARROW", "→", "->", "arrows", "Right Arrow"]
                    )
                    writer.writerow(
                        [
                            "U+21D2",
                            "RIGHTWARDS DOUBLE ARROW",
                            "⇒",
                            "=>",
                            "arrows",
                            "Right Double Arrow",
                        ]
                    )
                    writer.writerow(
                        [
                            "U+2260",
                            "NOT EQUAL TO",
                            "≠",
                            "!=",
                            "comparison",
                            "Not Equal To",
                        ]
                    )
                    writer.writerow(
                        [
                            "U+2264",
                            "LESS-THAN OR EQUAL TO",
                            "≤",
                            "<=",
                            "comparison",
                            "Less Than or Equal To",
                        ]
                    )
                    writer.writerow(
                        [
                            "U+2265",
                            "GREATER-THAN OR EQUAL TO",
                            "≥",
                            ">=",
                            "comparison",
                            "Greater Than or Equal To",
                        ]
                    )
                    writer.writerow(
                        ["U+2237", "PROPORTION", "∷", "::", "punctuation", "Proportion"]
                    )
                    writer.writerow(
                        [
                            "U+2026",
                            "HORIZONTAL ELLIPSIS",
                            "…",
                            "...",
                            "punctuation",
                            "Ellipsis",
                        ]
                    )
                    writer.writerow(
                        ["U+2013", "EN DASH", "–", "--", "punctuation", "En Dash"]
                    )
                    writer.writerow(
                        ["U+2014", "EM DASH", "—", "---", "punctuation", "Em Dash"]
                    )

                output_files.append(output_filename)
                csv_task.set_success(f"Created {output_filename} (fallback data)")
        except Exception as e:
            csv_task.set_failure(f"Error: {str(e)}")
            return False, []

    # Generate other formats if needed
    if options.format_type in ["json", "all"]:
        json_task = progress.add_child_item(main_task, "Generating JSON output")

        try:
            # Create output filename
            output_filename = os.path.join(options.output_dir, "ligatures.json")

            # Convert CSV to JSON format
            if dataset_to_use.exists():
                # Load the CSV data
                with open(dataset_to_use, encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    data = []

                    # Process the rows
                    for row in reader:
                        # Handle multiple sequences if present (comma-separated)
                        sequences = (
                            row.get("sequence", "").split(",")
                            if row.get("sequence")
                            else []
                        )
                        sequences = [seq.strip() for seq in sequences if seq.strip()]

                        # Create the JSON entry with multiple sequences
                        entry = {
                            "unicode_codepoint": row.get("unicode_codepoint", ""),
                            "unicode_name": row.get("unicode_name", ""),
                            "unicode_utf8": row.get("unicode_utf8", ""),
                            "sequences": sequences,
                            "category": row.get("category", ""),
                            "description": row.get("description", ""),
                        }
                        data.append(entry)

                # Write to JSON
                with open(output_filename, "w", encoding="utf-8") as jsonfile:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False)

                output_files.append(output_filename)
                json_task.set_success(f"Created {output_filename}")
            else:
                json_task.set_failure("Source data file not found")
        except Exception as e:
            json_task.set_failure(f"Error: {str(e)}")

    # Mark main task as successful
    main_task.set_success()

    return True, output_files
