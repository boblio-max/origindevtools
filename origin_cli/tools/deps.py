"""origin deps - Dependency manager."""

import re
import subprocess
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, warning, print_command_header, make_table


def _find_deps_file() -> tuple[Path | None, str]:
    """Find the dependency file in the project."""
    cwd = Path.cwd()
    if (cwd / "pyproject.toml").exists():
        return cwd / "pyproject.toml", "pyproject"
    if (cwd / "requirements.txt").exists():
        return cwd / "requirements.txt", "requirements"
    return None, "none"


def _read_requirements(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def _write_requirements(path: Path, deps: list[str]):
    content = "\n".join(sorted(set(deps))) + "\n"
    path.write_text(content, encoding="utf-8")


@click.group("deps")
def command():
    """Manage project dependencies."""
    pass


@command.command("add")
@click.argument("packages", nargs=-1, required=True)
def deps_add(packages):
    """Add dependencies to the project."""
    print_command_header("deps add", "Add dependencies")
    dep_file, dep_type = _find_deps_file()
    if dep_file is None:
        # Create requirements.txt
        dep_file = Path.cwd() / "requirements.txt"
        dep_file.write_text("", encoding="utf-8")
        dep_type = "requirements"

    if dep_type == "requirements":
        existing = _read_requirements(dep_file)
        existing_names = {re.split(r'[><=!~]', d)[0].lower() for d in existing}
        added = []
        for pkg in packages:
            pkg_name = re.split(r'[><=!~]', pkg)[0].lower()
            if pkg_name not in existing_names:
                existing.append(pkg)
                added.append(pkg)
            else:
                warning(f"'{pkg_name}' already in dependencies")
        _write_requirements(dep_file, existing)
        for pkg in added:
            success(f"Added: {pkg}")
    else:
        info("Add to pyproject.toml dependencies manually for now.")

    # Install
    if packages:
        info("Installing...")
        subprocess.run(["pip", "install"] + list(packages), capture_output=False)


@command.command("remove")
@click.argument("packages", nargs=-1, required=True)
def deps_remove(packages):
    """Remove dependencies from the project."""
    print_command_header("deps remove", "Remove dependencies")
    dep_file, dep_type = _find_deps_file()
    if dep_file is None:
        error("No dependency file found."); return

    if dep_type == "requirements":
        existing = _read_requirements(dep_file)
        pkg_lower = {p.lower() for p in packages}
        kept = [d for d in existing if re.split(r'[><=!~]', d)[0].lower() not in pkg_lower]
        removed = len(existing) - len(kept)
        _write_requirements(dep_file, kept)
        success(f"Removed {removed} package(s)")


@command.command("list")
def deps_list():
    """List all project dependencies."""
    print_command_header("deps list", "Dependencies")
    dep_file, dep_type = _find_deps_file()
    if dep_file is None:
        error("No dependency file found."); return

    deps = _read_requirements(dep_file) if dep_type == "requirements" else []
    if not deps:
        info("No dependencies found."); return

    rows = [[d, re.split(r'[><=!~]', d)[0]] for d in deps]
    table = make_table(
        "Project Dependencies",
        [("Specification", "origin.value"), ("Package", "origin.key")],
        rows,
    )
    console.print(table)


@command.command("check")
def deps_check():
    """Check for outdated packages."""
    print_command_header("deps check", "Dependency audit")
    info("Checking for outdated packages...")
    result = subprocess.run(
        ["pip", "list", "--outdated", "--format=columns"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        console.print(f"\n{result.stdout}")
    else:
        success("All packages up to date.")


@command.command("sync")
def deps_sync():
    """Install all dependencies from the project file."""
    print_command_header("deps sync", "Sync dependencies")
    dep_file, dep_type = _find_deps_file()
    if dep_file is None:
        error("No dependency file found."); return
    if dep_type == "requirements":
        info(f"Installing from {dep_file.name}...")
        subprocess.run(["pip", "install", "-r", str(dep_file)])
        success("Dependencies synced.")
    else:
        info("Installing from pyproject.toml...")
        subprocess.run(["pip", "install", "-e", "."])
        success("Dependencies synced.")
