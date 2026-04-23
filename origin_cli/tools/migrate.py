"""origin migrate - Project migration assistant."""

import re
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, warning, print_command_header


@click.group("migrate")
def command():
    """Project migration assistant."""
    pass


@command.command("requirements")
@click.option("--dry-run", is_flag=True, help="Show changes without writing.")
def migrate_requirements(dry_run):
    """Convert requirements.txt to pyproject.toml dependencies."""
    print_command_header("migrate requirements", "requirements.txt -> pyproject.toml")

    req_file = Path.cwd() / "requirements.txt"
    if not req_file.exists():
        error("No requirements.txt found."); return

    lines = req_file.read_text(encoding="utf-8").splitlines()
    deps = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]

    if not deps:
        info("No dependencies found in requirements.txt"); return

    pyproject = Path.cwd() / "pyproject.toml"
    deps_str = ", ".join(f'"{d}"' for d in deps)

    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        if "dependencies" in content:
            warning("pyproject.toml already has dependencies section.")
            info("Add manually:")
            console.print(f"  dependencies = [{deps_str}]")
            return

        # Add dependencies to existing pyproject.toml
        if "[project]" in content:
            new_content = content.replace(
                "[project]",
                f"[project]\ndependencies = [{deps_str}]",
                1
            )
        else:
            new_content = content + f"\n[project]\ndependencies = [{deps_str}]\n"
    else:
        new_content = (
            '[build-system]\nrequires = ["setuptools>=68.0"]\n'
            'build-backend = "setuptools.build_meta"\n\n'
            f'[project]\nname = "{Path.cwd().name}"\nversion = "0.1.0"\n'
            f'dependencies = [{deps_str}]\n'
        )

    if dry_run:
        console.print("\n  [origin.dim]Would write to pyproject.toml:[/]\n")
        for line in new_content.splitlines():
            console.print(f"  {line}")
    else:
        pyproject.write_text(new_content, encoding="utf-8")
        success(f"Migrated {len(deps)} dependencies to pyproject.toml")

    console.print()


@command.command("structure")
@click.option("--dry-run", is_flag=True, help="Show changes without modifying.")
def migrate_structure(dry_run):
    """Suggest project structure improvements."""
    print_command_header("migrate structure", "Structure analysis")

    cwd = Path.cwd()
    suggestions = []

    if not (cwd / ".gitignore").exists():
        suggestions.append(("Missing .gitignore", "origin create standard generates one"))
    if not (cwd / "README.md").exists():
        suggestions.append(("Missing README.md", "Add project documentation"))
    if not any((cwd / n).exists() for n in ["tests", "test"]):
        suggestions.append(("No tests directory", "Create tests/ with test files"))
    if not (cwd / "pyproject.toml").exists() and not (cwd / "setup.py").exists():
        suggestions.append(("No package config", "Add pyproject.toml for proper packaging"))
    if (cwd / "setup.py").exists() and not (cwd / "pyproject.toml").exists():
        suggestions.append(("Legacy setup.py", "Migrate to pyproject.toml"))

    py_files = list(cwd.glob("*.py"))
    if len(py_files) > 5:
        suggestions.append((
            f"{len(py_files)} Python files in root",
            "Consider organizing into a package directory"
        ))

    if not suggestions:
        success("Project structure looks good.")
    else:
        console.print()
        for title, fix in suggestions:
            console.print(f"  [yellow]>[/] [bright_white]{title}[/]")
            console.print(f"    [origin.dim]{fix}[/]")
        console.print()
        info(f"{len(suggestions)} suggestion(s)")
    console.print()
