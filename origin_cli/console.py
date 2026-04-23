"""Centralized Rich console with Origin Dev Tools theming."""

import sys
import os

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# -- Origin color palette --
ORIGIN_THEME = Theme({
    "origin.title":     "bold bright_cyan",
    "origin.accent":    "bold magenta",
    "origin.success":   "bold green",
    "origin.error":     "bold red",
    "origin.warning":   "bold yellow",
    "origin.info":      "bold blue",
    "origin.dim":       "dim white",
    "origin.highlight": "bold bright_white",
    "origin.path":      "underline cyan",
    "origin.key":       "bold bright_yellow",
    "origin.value":     "bright_white",
    "origin.header":    "bold bright_magenta on grey11",
})

console = Console(theme=ORIGIN_THEME, force_terminal=True)

BANNER = r"""
   ____       _       _         ____             _____           _
  / __ \     (_)     (_)       |  _ \           |_   _|         | |
 | |  | |_ __ _  __ _ _ _ __  | | | | _____   __ | | ___   ___ | |___
 | |  | | '__| |/ _` | | '_ \ | | | |/ _ \ \ / / | |/ _ \ / _ \| / __|
 | |__| | |  | | (_| | | | | || |_| |  __/\ V /  | | (_) | (_) | \__ \
  \____/|_|  |_|\__, |_|_| |_||____/ \___| \_/   |_|\___/ \___/|_|___/
                 __/ |
                |___/                                          v2.0.0
"""


def print_banner():
    """Display the Origin Dev Tools ASCII banner."""
    console.print(BANNER, style="origin.accent")


def success(message: str):
    """Print a success message."""
    console.print(f"  [origin.success]OK[/]  {message}")


def error(message: str):
    """Print an error message."""
    console.print(f"  [origin.error]ERR[/] {message}")


def warning(message: str):
    """Print a warning message."""
    console.print(f"  [origin.warning]WARN[/] {message}")


def info(message: str):
    """Print an informational message."""
    console.print(f"  [origin.info]--[/]  {message}")


def header(title: str):
    """Print a section header."""
    console.print()
    console.print(Panel(
        Text(title, justify="center", style="origin.title"),
        border_style="bright_cyan",
        box=box.ASCII,
        padding=(0, 2),
    ))
    console.print()


def make_table(title: str, columns: list[tuple[str, str]], rows: list[list[str]]) -> Table:
    """Create a styled Rich table.

    Args:
        title: Table title.
        columns: List of (name, style) tuples.
        rows: List of row data (list of strings).

    Returns:
        A Rich Table object.
    """
    table = Table(
        title=title,
        box=box.ASCII,
        border_style="bright_cyan",
        header_style="origin.header",
        title_style="origin.title",
        show_lines=True,
        padding=(0, 1),
    )
    for name, style in columns:
        table.add_column(name, style=style)
    for row in rows:
        table.add_row(*row)
    return table


def print_command_header(name: str, description: str):
    """Print a styled header for a command execution."""
    console.print()
    console.print(
        f"  [origin.accent]origin {name}[/] [origin.dim]|[/] {description}"
    )
    console.print(f"  [origin.dim]{'-' * 60}[/]")
