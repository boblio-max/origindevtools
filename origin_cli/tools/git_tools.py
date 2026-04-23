"""origin git - Git workflow shortcuts with Rich display."""

import subprocess

import click

from origin_cli.console import console, success, error, info, warning, print_command_header


def _run_git(*args, check=True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git"] + list(args), capture_output=True, text=True
        )
    except FileNotFoundError:
        raise RuntimeError("git not found. Make sure git is installed and on your PATH.")
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {args[0]} failed")
    return result


@click.group("git")
def command():
    """Git workflow shortcuts."""
    pass


@command.command("status")
def git_status():
    """Enhanced git status with Rich formatting."""
    print_command_header("git status", "Repository status")
    try:
        result = _run_git("status", "--porcelain=v1")
    except RuntimeError as e:
        error(str(e)); return

    lines = result.stdout.strip().splitlines()
    if not lines:
        success("Working tree clean."); return

    staged = []
    modified = []
    untracked = []

    for line in lines:
        status = line[:2]
        filepath = line[3:]
        if status[0] in "MADRC":
            staged.append((status[0], filepath))
        if status[1] in "MD":
            modified.append((status[1], filepath))
        if status == "??":
            untracked.append(filepath)

    if staged:
        console.print("\n  [green]Staged:[/]")
        for s, f in staged:
            console.print(f"    [green]{s}[/] {f}")

    if modified:
        console.print("\n  [yellow]Modified:[/]")
        for s, f in modified:
            console.print(f"    [yellow]{s}[/] {f}")

    if untracked:
        console.print("\n  [red]Untracked:[/]")
        for f in untracked:
            console.print(f"    [red]?[/] {f}")

    console.print()
    info(f"{len(staged)} staged, {len(modified)} modified, {len(untracked)} untracked")


@command.command("save")
@click.argument("message")
@click.option("--push/--no-push", default=True, help="Push after commit.")
def git_save(message, push):
    """Add all, commit, and push in one command."""
    print_command_header("git save", "Quick save")
    try:
        _run_git("add", "-A")
        info("Staged all changes")

        _run_git("commit", "-m", message)
        success(f"Committed: {message}")

        if push:
            info("Pushing...")
            _run_git("push")
            success("Pushed to remote")
    except RuntimeError as e:
        error(str(e))


@command.command("branch")
@click.argument("name")
def git_branch(name):
    """Create and switch to a new branch."""
    print_command_header("git branch", "Create branch")
    try:
        _run_git("checkout", "-b", name)
        success(f"Created and switched to: {name}")
    except RuntimeError as e:
        error(str(e))


@command.command("log")
@click.option("--count", "-n", default=10, help="Number of commits to show.")
def git_log(count):
    """Show recent git log with Rich formatting."""
    print_command_header("git log", "Commit history")
    try:
        result = _run_git(
            "log", f"-{count}",
            "--pretty=format:%h|%an|%ar|%s",
            check=False
        )
    except RuntimeError as e:
        error(str(e)); return

    if not result.stdout.strip():
        info("No commits yet."); return

    console.print()
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            hash_, author, time_, msg = parts
            console.print(
                f"  [yellow]{hash_}[/] [origin.dim]{time_:>15}[/]  "
                f"[bright_white]{msg}[/]  [origin.dim]({author})[/]"
            )
    console.print()


@command.command("undo")
def git_undo():
    """Undo the last commit (soft reset)."""
    print_command_header("git undo", "Undo last commit")
    try:
        result = _run_git("log", "-1", "--pretty=format:%s")
        msg = result.stdout.strip()
        _run_git("reset", "--soft", "HEAD~1")
        success(f"Undone: {msg}")
        info("Changes are back in staging area.")
    except RuntimeError as e:
        error(str(e))


@command.command("clean")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
def git_clean(force):
    """Remove untracked files."""
    print_command_header("git clean", "Clean untracked files")
    try:
        result = _run_git("clean", "-dn")
        files = result.stdout.strip().splitlines()
        if not files:
            success("No untracked files to clean."); return

        console.print("\n  [yellow]Files to remove:[/]")
        for f in files:
            console.print(f"    [red]{f}[/]")

        if not force:
            console.print()
            if not click.confirm("  Remove these files?"):
                info("Cancelled."); return

        _run_git("clean", "-df")
        success(f"Removed {len(files)} untracked file(s)")
    except RuntimeError as e:
        error(str(e))
