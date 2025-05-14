"""
Module for displaying hierarchical progress with checkmarks/X marks.
"""

import sys
from enum import Enum
from typing import Optional


class ProgressStatus(Enum):
    """Status of a progress item."""

    PENDING = "* "
    SUCCESS = "✓ "
    FAILURE = "✗ "

    @classmethod
    def get_color_code(cls, status):
        """Get ANSI color code for status."""
        if status == cls.PENDING:
            return "\033[33m"  # Yellow
        elif status == cls.SUCCESS:
            return "\033[32m"  # Green
        elif status == cls.FAILURE:
            return "\033[31m"  # Red
        return ""


class ProgressItem:
    """A progress item in the hierarchical display."""

    def __init__(self, title: str, parent: Optional["ProgressItem"] = None, display=None):
        """
        Initialize a progress item.

        Args:
            title: Title of the progress item
            parent: Parent progress item, or None if this is a root item
            display: The ProgressDisplay instance this item belongs to
        """
        self.title = title
        self.parent = parent
        self.children: list[ProgressItem] = []
        self.status = ProgressStatus.PENDING
        self.details: Optional[str] = None
        self.display = display

        # If parent has a display and we don't, use the parent's display
        if not self.display and parent and hasattr(parent, "display"):
            self.display = parent.display

        # Add this item as a child of its parent
        if parent:
            parent.children.append(self)

    def set_status(self, status: ProgressStatus, details: Optional[str] = None) -> None:
        """
        Set the status of this progress item.

        Args:
            status: New status
            details: Optional details to display
        """
        self.status = status
        self.details = details

        # Update the display if available
        if self.display:
            self.display.update_display()

    def set_success(self, details: Optional[str] = None) -> None:
        """
        Mark this progress item as successful.

        Args:
            details: Optional details to display
        """
        self.set_status(ProgressStatus.SUCCESS, details)

    def set_failure(self, details: Optional[str] = None) -> None:
        """
        Mark this progress item as failed.

        Args:
            details: Optional details to display
        """
        self.set_status(ProgressStatus.FAILURE, details)

    def is_complete(self) -> bool:
        """
        Check if this progress item is complete.

        Returns:
            True if this item and all its children are complete
        """
        if self.status == ProgressStatus.PENDING:
            return False
        return all(child.is_complete() for child in self.children)

    def is_successful(self) -> bool:
        """
        Check if this progress item is successful.

        Returns:
            True if this item and all its children are successful
        """
        if self.status != ProgressStatus.SUCCESS:
            return False
        return all(child.is_successful() for child in self.children)


class ProgressDisplay:
    """Hierarchical progress display."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the progress display.

        Args:
            verbose: Whether to display detailed logging
        """
        self.root_items: list[ProgressItem] = []
        self.verbose = verbose
        self.last_output_lines = 0

    def add_root_item(self, title: str) -> ProgressItem:
        """
        Add a root progress item.

        Args:
            title: Title of the progress item

        Returns:
            The created progress item
        """
        item = ProgressItem(title, display=self)
        self.root_items.append(item)
        self.update_display()
        return item

    def add_child_item(self, parent: ProgressItem, title: str) -> ProgressItem:
        """
        Add a child progress item.

        Args:
            parent: Parent progress item
            title: Title of the progress item

        Returns:
            The created progress item
        """
        item = ProgressItem(title, parent, display=self)
        self.update_display()
        return item

    def update_display(self) -> None:
        """Update the progress display."""
        # Clear the previous output
        if self.last_output_lines > 0:
            sys.stdout.write(f"\033[{self.last_output_lines}A")  # Move cursor up
            sys.stdout.write("\033[J")  # Clear from cursor to end of screen

        # Build the new output
        output_lines = []
        for item in self.root_items:
            self._format_item(item, output_lines, indent=0)

        # Print the new output
        print("\n".join(output_lines))
        self.last_output_lines = len(output_lines)
        sys.stdout.flush()

    def _format_item(
        self, item: ProgressItem, output_lines: list[str], indent: int
    ) -> None:
        """
        Format a progress item for display.

        Args:
            item: Progress item to format
            output_lines: List to append formatted lines to
            indent: Indentation level
        """
        # Format the item's status and title
        indent_str = "    " * indent
        status_str = item.status.value

        # Get color code for the status
        color_code = ProgressStatus.get_color_code(item.status)
        reset_code = "\033[0m"

        # Build the line with color
        line = f"{color_code}{indent_str}{status_str}{item.title}"

        # Add details if available
        if item.details:
            line += f" {item.details}"

        # Add reset code to end of line
        line += reset_code

        output_lines.append(line)

        # Format the item's children
        for child in item.children:
            self._format_item(child, output_lines, indent + 1)

    def log(self, message: str) -> None:
        """
        Log a message if verbose mode is enabled.

        Args:
            message: Message to log
        """
        if self.verbose:
            # Clear the progress display
            if self.last_output_lines > 0:
                sys.stdout.write(f"\033[{self.last_output_lines}A")  # Move cursor up
                sys.stdout.write("\033[J")  # Clear from cursor to end of screen
                self.last_output_lines = 0

            # Print the log message
            print(f"\033[33m[LOG] {message}\033[0m")  # Yellow text for logs

            # Redraw the progress display
            self.update_display()
