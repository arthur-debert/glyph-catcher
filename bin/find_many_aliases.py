#!/usr/bin/env python3
"""
Script to parse Unicode character data and find characters with more than 5 aliases.

This script reads Unicode character data from a CSV file and analyzes the aliases,
allowing you to find characters with the most aliases and explore the data in
various ways.
"""

import argparse
import csv
import sys
import textwrap
from typing import Any, Optional


def format_aliases(
    aliases: list[str], limit: Optional[int] = None, wrap_width: int = 80
) -> str:
    """Format a list of aliases for pretty printing with optional wrapping."""
    if limit is not None and limit > 0:
        displayed_aliases = aliases[:limit]
        suffix = f" (and {len(aliases) - limit} more)" if len(aliases) > limit else ""
    else:
        displayed_aliases = aliases
        suffix = ""

    joined = ", ".join(displayed_aliases)

    if wrap_width and len(joined) > wrap_width:
        # Wrap text and indent subsequent lines
        wrapped = textwrap.fill(
            joined, width=wrap_width, initial_indent="    ", subsequent_indent="    "
        )
        return f"{wrapped}{suffix}"
    else:
        return f"    {joined}{suffix}"


def find_character_by_code_point(
    data: list[dict[str, Any]], code_point: str
) -> Optional[dict[str, Any]]:
    """Find a character by its code point."""
    code_point = code_point.upper()
    if not code_point.startswith("U+"):
        code_point = f"U+{code_point}"

    for char in data:
        if char["code_point"].upper() == code_point:
            return char
    return None


def process_unicode_data(
    input_file: str, min_aliases: int, specific_code_point: Optional[str] = None
) -> list[dict[str, Any]]:
    """Process the Unicode CSV file and extract character data."""
    characters_with_many_aliases = []

    with open(input_file, encoding="utf-8") as f:
        reader = csv.reader(f)

        # Read the header to determine column structure
        next(reader)

        # Process each row in the file
        for row in reader:
            if len(row) < 6:  # Skip rows that don't have enough columns
                continue

            # Get the standard fields
            code_point = row[0]
            character = row[1]
            name = row[2]
            category = row[3] if len(row) > 3 else ""
            block = row[4] if len(row) > 4 else ""

            # Count non-empty aliases (from column 5 onwards)
            aliases = [a for a in row[5:] if a.strip()]
            alias_count = len(aliases)

            # If looking for a specific code point or it has enough aliases
            if (
                specific_code_point
                and code_point.upper() == specific_code_point.upper()
            ) or (alias_count > min_aliases and not specific_code_point):
                characters_with_many_aliases.append(
                    {
                        "code_point": code_point,
                        "character": character,
                        "name": name,
                        "category": category,
                        "block": block,
                        "alias_count": alias_count,
                        "aliases": aliases,
                    }
                )

    # Sort by number of aliases (descending) unless looking for a specific code point
    if not specific_code_point:
        characters_with_many_aliases.sort(key=lambda x: x["alias_count"], reverse=True)

    return characters_with_many_aliases


def display_single_character(
    char_data: dict[str, Any], show_all_aliases: bool = False
) -> None:
    """Display detailed information for a single character."""
    print(
        f"\n--- {char_data['code_point']} - {char_data['character']} - "
        f"{char_data['name']} ---"
    )
    print(f"Category: {char_data['category']}")
    print(f"Block: {char_data['block']}")
    print(f"Total aliases: {char_data['alias_count']}")

    print("\nAliases:")
    aliases_to_show = (
        char_data["aliases"] if show_all_aliases else char_data["aliases"][:10]
    )
    print(format_aliases(aliases_to_show, None if show_all_aliases else 10))


def display_characters(
    chars_data: list[dict[str, Any]],
    limit: int,
    min_aliases: int,
    show_all_aliases: bool = False,
) -> None:
    """Display a list of characters with their information."""
    print(f"Found {len(chars_data)} characters with more than {min_aliases} aliases")
    print("\nTop characters with most aliases:")
    print("-" * 80)

    for i, char_data in enumerate(chars_data[:limit], 1):
        print(
            f"{i}. {char_data['code_point']} - {char_data['character']} - "
            f"{char_data['name']}"
        )
        print(f"   Total aliases: {char_data['alias_count']}")

        aliases_sample = (
            char_data["aliases"] if show_all_aliases else char_data["aliases"][:5]
        )
        limit_display = None if show_all_aliases else 5
        print(
            f"   Aliases: {format_aliases(aliases_sample, limit_display,
                                         wrap_width=70)[4:]}"
        )
        print()

    if len(chars_data) > limit:
        print(f"... and {len(chars_data) - limit} more")


def save_to_file(
    chars_data: list[dict[str, Any]],
    output_file: str,
    min_aliases: int,
    show_all_aliases: bool = False,
) -> None:
    """Save character data to an output file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            f"Found {len(chars_data)} characters with more than {min_aliases} aliases\n\n"
        )

        for i, char_data in enumerate(chars_data, 1):
            f.write(
                f"{i}. {char_data['code_point']} - {char_data['character']} - "
                f"{char_data['name']}\n"
            )
            f.write(f"   Category: {char_data['category']}\n")
            f.write(f"   Block: {char_data['block']}\n")
            f.write(f"   Total aliases: {char_data['alias_count']}\n")

            aliases = (
                char_data["aliases"] if show_all_aliases else char_data["aliases"][:10]
            )
            limit_display = None if show_all_aliases else 10
            f.write(f"   Aliases: {', '.join(aliases[:limit_display])}")

            if not show_all_aliases and len(aliases) > limit_display:
                f.write(f" (and {len(aliases) - limit_display} more)")

            f.write("\n\n")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Unicode characters and find those with many aliases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
        Examples:
          # Find characters with more than 10 aliases
          ./find_many_aliases.py -m 10

          # Show all aliases for characters with more than 5 aliases
          ./find_many_aliases.py -a

          # Save results to a file
          ./find_many_aliases.py -o unicode_aliases.txt

          # Show details for a specific code point
          ./find_many_aliases.py -c U+1F9D1

          # Show the top 50 characters with most aliases
          ./find_many_aliases.py -l 50
        """
        ),
    )

    parser.add_argument(
        "-m",
        "--min-aliases",
        type=int,
        default=5,
        help="Minimum number of aliases a character must have (default: 5)",
    )

    parser.add_argument(
        "-o", "--output", type=str, help="Save results to this output file"
    )

    parser.add_argument(
        "-a",
        "--all-aliases",
        action="store_true",
        help="Show all aliases for each character, not just a sample",
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=20,
        help="Number of characters to display (default: 20)",
    )

    parser.add_argument(
        "-c",
        "--code-point",
        type=str,
        help="Show details for a specific Unicode code point (e.g., U+1F9D1)",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="data/unicode.every-day.csv",
        help="Path to the Unicode CSV file (default: data/unicode.every-day.csv)",
    )

    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_arguments()

    try:
        # Process specific code point if provided
        if args.code_point:
            code_point = args.code_point.upper()
            if not code_point.startswith("U+"):
                code_point = f"U+{code_point}"

            chars_data = process_unicode_data(args.file, 0, code_point)

            if not chars_data:
                print(f"No character found with code point {code_point}")
                return 1

            # Display detailed information for the single character
            display_single_character(chars_data[0], args.all_aliases)

            if args.output:
                save_to_file(chars_data, args.output, 0, args.all_aliases)
                print(f"\nResults saved to {args.output}")
        else:
            # Process all characters with more than min_aliases aliases
            chars_data = process_unicode_data(args.file, args.min_aliases)

            if not chars_data:
                print(f"No characters found with more than {args.min_aliases} aliases")
                return 0

            # Display characters in the terminal
            display_characters(
                chars_data, args.limit, args.min_aliases, args.all_aliases
            )

            # Save to file if requested
            if args.output:
                save_to_file(
                    chars_data, args.output, args.min_aliases, args.all_aliases
                )
                print(f"\nResults saved to {args.output}")

    except FileNotFoundError:
        print(f"Error: Could not find file {args.file}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
