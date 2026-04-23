"""Shared utility functions for Origin Dev Tools."""

import os
import time
import subprocess
import functools
from pathlib import Path


def discover_files(
    root: str | Path,
    extensions: list[str] | None = None,
    ignore_dirs: list[str] | None = None,
) -> list[Path]:
    """Recursively discover files under a root directory.

    Args:
        root: Root directory to search.
        extensions: File extensions to include (e.g., ['.py', '.or']).
                    None means include all files.
        ignore_dirs: Directory names to skip (e.g., ['__pycache__', '.git']).

    Returns:
        Sorted list of matching file paths.
    """
    root = Path(root)
    if ignore_dirs is None:
        ignore_dirs = ["__pycache__", ".git", "node_modules", ".venv", "venv", ".tox"]

    ignore_set = set(ignore_dirs)
    results = []

    if root.is_file():
        if extensions is None or root.suffix in extensions:
            return [root]
        return []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_set]
        for filename in filenames:
            filepath = Path(dirpath) / filename
            if extensions is None or filepath.suffix in extensions:
                results.append(filepath)

    return sorted(results)


def is_git_repo(path: str | Path | None = None) -> bool:
    """Check if a path is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=path or ".",
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_git_root(path: str | Path | None = None) -> Path | None:
    """Get the root directory of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path or ".",
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def safe_read_file(path: str | Path) -> str | None:
    """Safely read a file, trying common encodings.

    Returns:
        File contents as string, or None on failure.
    """
    path = Path(path)
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        except OSError:
            return None
    return None


def safe_write_file(path: str | Path, content: str, encoding: str = "utf-8"):
    """Safely write content to a file, creating parent directories.

    Args:
        path: Target file path.
        content: Content to write.
        encoding: File encoding (default utf-8).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def timer(func):
    """Decorator that times a function and returns (result, elapsed_seconds)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
    return wrapper


def format_duration(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}us"
    if seconds < 1:
        return f"{seconds * 1_000:.1f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def truncate(text: str, max_length: int = 80) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_path(path: str, must_exist: bool = True) -> Path:
    """Validate and resolve a path.

    Args:
        path: Path string to validate.
        must_exist: If True, raises FileNotFoundError if path doesn't exist.

    Returns:
        Resolved Path object.

    Raises:
        FileNotFoundError: If must_exist is True and path doesn't exist.
    """
    resolved = Path(path).resolve()
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path not found: {resolved}")
    return resolved
