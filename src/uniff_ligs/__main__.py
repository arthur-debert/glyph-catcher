"""
Entry point for the uniff-ligs package.

This module serves as the entry point for the package when run as a command-line tool.
It uses cli.py to process command line arguments and core.py to execute the
core functionality.
"""

from .cli import cli


def main():
    """Entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    main()
