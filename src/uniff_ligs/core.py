"""
Core functionality for the uniff-ligs package.

This module handles the core processing and generation of ligature data.
"""

import csv
import json
import os
import shutil
from pathlib import Path

from uniff_core.progress import ProgressDisplay, ProgressStatus
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
    progress.start()

    try:
        # Create main task
        main_task = "Processing ligature data"
        progress.add_root_item(main_task)

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
            csv_task = "Generating CSV output"
            progress.add_child_item([main_task], csv_task)

            try:
                # Create output filename
                output_filename = os.path.join(options.output_dir, "ligatures.csv")

                # If the dataset file exists, copy it to the output
                if dataset_to_use.exists():
                    shutil.copy(dataset_to_use, output_filename)
                    output_files.append(output_filename)
                    progress.update_item(
                        [main_task, csv_task],
                        ProgressStatus.SUCCESS,
                        f"Created {output_filename}",
                    )
                else:
                    # Generate a simple default CSV with common ligatures
                    with open(
                        output_filename, "w", newline="", encoding="utf-8"
                    ) as csvfile:
                        writer = csv.writer(csvfile)

                        # Write header
                        # Write header row
                        header = [
                            "unicode_codepoint",
                            "unicode_name",
                            "unicode_utf8",
                            "sequence",
                            "category",
                            "description",
                        ]
                        writer.writerow(header)

                        # Write some example ligatures
                        writer.writerow(
                            [
                                "U+2192",
                                "RIGHTWARDS ARROW",
                                "→",
                                "->",
                                "arrows",
                                "Right Arrow",
                            ]
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
                        # Write comparison operators
                        less_than_equal = [
                            "U+2264",
                            "LESS-THAN OR EQUAL TO",
                            "≤",
                            "<=",
                            "comparison",
                            "Less Than or Equal To",
                        ]
                        writer.writerow(less_than_equal)

                        greater_than_equal = [
                            "U+2265",
                            "GREATER-THAN OR EQUAL TO",
                            "≥",
                            ">=",
                            "comparison",
                            "Greater Than or Equal To",
                        ]
                        writer.writerow(greater_than_equal)
                        writer.writerow(
                            [
                                "U+2237",
                                "PROPORTION",
                                "∷",
                                "::",
                                "punctuation",
                                "Proportion",
                            ]
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
                    progress.update_item(
                        [main_task, csv_task],
                        ProgressStatus.SUCCESS,
                        f"Created {output_filename} (fallback data)",
                    )
            except Exception as e:
                progress.update_item(
                    [main_task, csv_task], ProgressStatus.FAILURE, f"Error: {str(e)}"
                )
                return False, []

        # Generate other formats if needed
        if options.format_type in ["json", "all"]:
            json_task = "Generating JSON output"
            progress.add_child_item([main_task], json_task)

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
                            # Extract and process sequences
                            sequence = row.get("sequence", "")
                            sequences = sequence.split(",") if sequence else []
                            sequences = [seq.strip() for seq in sequences if seq.strip()]

                            # Build JSON entry
                            entry = {}
                            for field in [
                                "unicode_codepoint",
                                "unicode_name",
                                "unicode_utf8",
                                "category",
                                "description",
                            ]:
                                entry[field] = row.get(field, "")
                            entry["sequences"] = sequences
                            data.append(entry)

                    # Write to JSON
                    with open(output_filename, "w", encoding="utf-8") as jsonfile:
                        json.dump(data, jsonfile, indent=2, ensure_ascii=False)

                    output_files.append(output_filename)
                    progress.update_item(
                        [main_task, json_task],
                        ProgressStatus.SUCCESS,
                        f"Created {output_filename}",
                    )
                else:
                    progress.update_item(
                        [main_task, json_task],
                        ProgressStatus.FAILURE,
                        "Source data file not found",
                    )
            except Exception as e:
                progress.update_item(
                    [main_task, json_task], ProgressStatus.FAILURE, f"Error: {str(e)}"
                )

        # Mark main task as successful
        progress.update_item([main_task], ProgressStatus.SUCCESS)

        # Stop the progress display
        progress.stop()

        return True, output_files

    except Exception as e:
        if main_task:
            progress.update_item([main_task], ProgressStatus.FAILURE, f"Error: {str(e)}")
        progress.stop()
        return False, []
