"""
Module for displaying hierarchical progress with checkmarks/X marks.
"""

import contextlib
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProgressStatus(Enum):
    """Status of a progress item."""

    PENDING = "* "
    SUCCESS = "✓ "
    FAILURE = "✗ "

    @classmethod
    def get_color_code(cls, status: "ProgressStatus") -> str:
        """Get ANSI color code for status."""
        if status == cls.PENDING:
            return "\033[33m"  # Yellow
        elif status == cls.SUCCESS:
            return "\033[32m"  # Green
        elif status == cls.FAILURE:
            return "\033[31m"  # Red
        return ""


@dataclass
class ProgressState:
    """
    Immutable snapshot of progress state.
    This class represents the state of a progress item at a point in time.
    """

    title: str
    status: ProgressStatus
    details: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    from_cache: bool = False
    children: list["ProgressState"] = field(default_factory=list)

    @property
    def elapsed_time(self) -> Optional[float]:
        """Calculate elapsed time in seconds if both start and end times are set."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_complete(self) -> bool:
        """Check if this item and all children are complete."""
        return self.status != ProgressStatus.PENDING and all(
            child.is_complete for child in self.children
        )

    @property
    def is_successful(self) -> bool:
        """Check if this item and all children are successful."""
        return self.status == ProgressStatus.SUCCESS and all(
            child.is_successful for child in self.children
        )

    def format_elapsed_time(self) -> str:
        """Format elapsed time as a string with units."""
        elapsed = self.elapsed_time
        if elapsed is None:
            return ""

        if elapsed < 1:
            # Round to nearest millisecond
            ms = round(elapsed * 1000)
            return f"{ms}ms"
        return f"{int(elapsed)}s"


class ProgressItem:
    """A mutable progress item in the tree."""

    def __init__(self, title: str):
        self.title = title
        self.status = ProgressStatus.PENDING
        self.details: Optional[str] = None
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.from_cache = False
        self.children: dict[str, "ProgressItem"] = {}

    def update(
        self,
        status: ProgressStatus,
        details: Optional[str] = None,
        from_cache: bool = False,
    ) -> None:
        """Update the status of this item."""
        self.status = status
        self.details = details
        self.from_cache = from_cache
        if status != ProgressStatus.PENDING and self.end_time is None:
            self.end_time = time.time()

    def add_child(self, title: str) -> "ProgressItem":
        """Add a child progress item."""
        if title in self.children:
            return self.children[title]
        child = ProgressItem(title)
        self.children[title] = child
        return child

    def to_state(self) -> ProgressState:
        """Convert to an immutable state snapshot."""
        return ProgressState(
            title=self.title,
            status=self.status,
            details=self.details,
            start_time=self.start_time,
            end_time=self.end_time,
            from_cache=self.from_cache,
            children=[child.to_state() for child in self.children.values()],
        )


class ProgressRenderer:
    """Handles display formatting and screen updates."""

    def __init__(self):
        self._last_output = ""
        self._last_lines = 0

    def render(self, states: list[ProgressState]) -> None:
        """Render the current state, only updating screen if output changed."""
        output_lines = []
        for state in states:
            self._format_state(state, output_lines, indent=0)

        output = "\n".join(output_lines)
        if output != self._last_output:
            self._clear_screen()
            print(output)
            self._last_output = output
            self._last_lines = len(output_lines)

    def _format_state(
        self, state: ProgressState, output_lines: list[str], indent: int
    ) -> None:
        """Format a progress state for display."""
        # Format the item's status and title
        indent_str = "    " * indent
        status_str = state.status.value
        color_code = ProgressStatus.get_color_code(state.status)
        reset_code = "\033[0m"

        # Build the line with color
        line = f"{color_code}{indent_str}{status_str}{state.title}"

        # Add details if available
        if state.details:
            line += f" {state.details}"

        # Add timing and cache info for completed items
        if state.status != ProgressStatus.PENDING and state.elapsed_time is not None:
            timing_str = f" {state.format_elapsed_time()}"
            if state.from_cache:
                timing_str += " (from cache)"
            line += timing_str

        # Add reset code to end of line
        line += reset_code

        # Add the line to the output
        output_lines.append(line)

        # Format all children
        for child in state.children:
            self._format_state(child, output_lines, indent + 1)

    def _clear_screen(self) -> None:
        """Clear the previous output from the screen."""
        if self._last_lines > 0:
            # Move cursor up N lines
            sys.stdout.write(f"\033[{self._last_lines}A")
            # Clear from cursor to end of screen
            sys.stdout.write("\033[J")
        sys.stdout.flush()


class ProgressDisplay:
    """Orchestrates updates and rendering with a timer-based update loop."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the progress display.

        Args:
            verbose: Whether to display detailed logging
        """
        self.tree = ProgressTree()
        self.renderer = ProgressRenderer()
        self._update_interval = 0.2  # 200ms between updates
        self._stop_event = threading.Event()
        self._update_thread: Optional[threading.Thread] = None
        self.verbose = verbose

    def start(self) -> None:
        """Start the update loop in a background thread."""
        if self._update_thread is not None:
            return

        self._stop_event.clear()
        self._update_thread = threading.Thread(target=self._update_loop)
        self._update_thread.daemon = True  # Thread will exit when main thread exits
        self._update_thread.start()

    def stop(self) -> None:
        """Stop the update loop."""
        if self._update_thread is None:
            return

        self._stop_event.set()
        self._update_thread.join()
        self._update_thread = None

        # Ensure final state is rendered
        with contextlib.suppress(Exception):
            self.renderer.render(self.tree.get_state())

    def add_root_item(self, title: str) -> str:
        """Add a root progress item."""
        return self.tree.add_root_item(title)

    def add_child_item(self, parent_path: list[str], title: str) -> list[str]:
        """Add a child progress item."""
        return self.tree.add_child_item(parent_path, title)

    def update_item(
        self,
        path: list[str],
        status: ProgressStatus,
        details: Optional[str] = None,
        from_cache: bool = False,
    ) -> None:
        """Update a progress item's status."""
        self.tree.update_item(path, status, details, from_cache)

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(message)
            # Reset the last output lines to 0 so we don't overwrite the log message
            self.renderer._last_lines = 0

    def _update_loop(self) -> None:
        """Main update loop that runs every update_interval seconds."""
        while not self._stop_event.is_set():
            try:
                state = self.tree.get_state()
                self.renderer.render(state)
            except Exception:
                # Log error but don't crash the thread
                pass
            time.sleep(self._update_interval)


class ProgressTree:
    """Manages the progress tree structure."""

    def __init__(self):
        self.root_items: dict[str, ProgressItem] = {}
        self._lock = threading.Lock()

    def add_root_item(self, title: str) -> str:
        """Add a root progress item."""
        with self._lock:
            if title in self.root_items:
                return title
            self.root_items[title] = ProgressItem(title)
            return title

    def add_child_item(self, parent_path: list[str], title: str) -> list[str]:
        """Add a child progress item."""
        with self._lock:
            parent = self._get_item(parent_path)
            if parent is None:
                raise ValueError(f"Parent path not found: {parent_path}")
            parent.add_child(title)
            return parent_path + [title]

    def update_item(
        self,
        path: list[str],
        status: ProgressStatus,
        details: Optional[str] = None,
        from_cache: bool = False,
    ) -> None:
        """Update a progress item's status."""
        with self._lock:
            item = self._get_item(path)
            if item is None:
                raise ValueError(f"Item path not found: {path}")
            item.update(status, details, from_cache)

    def get_state(self) -> list[ProgressState]:
        """Get a snapshot of the current progress state."""
        with self._lock:
            return [item.to_state() for item in self.root_items.values()]

    def _get_item(self, path: list[str]) -> Optional[ProgressItem]:
        """Get a progress item by its path."""
        if not path:
            return None

        # Get root item
        current = self.root_items.get(path[0])
        if current is None:
            return None

        # Traverse children
        for i in range(1, len(path)):
            child_name = path[i]
            found = None
            for name, child in current.children.items():
                if name == child_name:
                    found = child
                    break
            if found is None:
                return None
            current = found

        return current
