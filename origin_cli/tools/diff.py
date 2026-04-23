"""origin diff - Side-by-side diff viewer with Rich highlighting."""

import subprocess
from pathlib import Path

import click

from origin_cli.console import console, error, info, print_command_header


@click.command("diff")
@click.argument("file1", required=False)
@click.argument("file2", required=False)
@click.option("--staged", is_flag=True, help="Show staged git changes.")
@click.option("--head", "head_n", type=int, default=None, help="Compare with HEAD~N.")
def command(file1, file2, staged, head_n):
    """View diffs with syntax highlighting."""
    print_command_header("diff", "Diff viewer")

    # Git mode
    if staged or head_n is not None:
        _git_diff(staged, head_n)
        return

    if not file1 or not file2:
        error("Usage: origin diff <file1> <file2>")
        info("Or: origin diff --staged / origin diff --head 1")
        return

    p1, p2 = Path(file1), Path(file2)
    if not p1.exists():
        error(f"Not found: {p1}"); return
    if not p2.exists():
        error(f"Not found: {p2}"); return

    content1 = p1.read_text(encoding="utf-8").splitlines()
    content2 = p2.read_text(encoding="utf-8").splitlines()

    console.print(f"\n  [origin.path]{p1}[/] vs [origin.path]{p2}[/]\n")

    import difflib
    diff = difflib.unified_diff(
        content1, content2,
        fromfile=str(p1), tofile=str(p2),
        lineterm=""
    )

    has_diff = False
    for line in diff:
        has_diff = True
        if line.startswith("+++") or line.startswith("---"):
            console.print(f"  [bold]{line}[/]")
        elif line.startswith("@@"):
            console.print(f"  [cyan]{line}[/]")
        elif line.startswith("+"):
            console.print(f"  [green]{line}[/]")
        elif line.startswith("-"):
            console.print(f"  [red]{line}[/]")
        else:
            console.print(f"  {line}")

    if not has_diff:
        info("Files are identical.")
    console.print()


def _git_diff(staged: bool, head_n: int | None):
    """Run git diff and display with highlighting."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--staged")
    elif head_n is not None:
        cmd.append(f"HEAD~{head_n}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error(f"git diff failed: {result.stderr.strip()}")
        return

    if not result.stdout.strip():
        info("No changes.")
        return

    for line in result.stdout.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            console.print(f"  [bold]{line}[/]")
        elif line.startswith("@@"):
            console.print(f"  [cyan]{line}[/]")
        elif line.startswith("+"):
            console.print(f"  [green]{line}[/]")
        elif line.startswith("-"):
            console.print(f"  [red]{line}[/]")
        elif line.startswith("diff"):
            console.print(f"  [bold bright_cyan]{line}[/]")
        else:
            console.print(f"  {line}")
    console.print()
