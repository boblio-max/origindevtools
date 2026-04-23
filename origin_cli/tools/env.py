"""origin env - Virtual environment and .env file manager."""

import os
import subprocess
import sys
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, warning, print_command_header, make_table


@click.group("env")
def command():
    """Manage Python virtual environments and .env files."""
    pass


@command.command("create")
@click.argument("name", default=".venv")
@click.option("--python", "python_path", default=None, help="Python interpreter path.")
def env_create(name, python_path):
    """Create a new virtual environment."""
    print_command_header("env create", "Create virtual environment")

    target = Path.cwd() / name
    if target.exists():
        warning(f"Environment '{name}' already exists at {target}")
        return

    python = python_path or sys.executable
    info(f"Creating virtual environment: {name}")
    info(f"Python: {python}")

    result = subprocess.run(
        [python, "-m", "venv", str(target)],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        success(f"Created: {target}")
        if os.name == "nt":
            info(f"Activate: {name}\\Scripts\\activate")
        else:
            info(f"Activate: source {name}/bin/activate")
    else:
        error(f"Failed: {result.stderr}")


@command.command("list")
def env_list():
    """List virtual environments in the project."""
    print_command_header("env list", "Virtual environments")

    venv_names = [".venv", "venv", "env", ".env"]
    found = []

    for name in venv_names:
        p = Path.cwd() / name
        if p.exists() and (p / "pyvenv.cfg").exists():
            cfg = (p / "pyvenv.cfg").read_text(encoding="utf-8")
            version = "?"
            for line in cfg.splitlines():
                if line.startswith("version"):
                    version = line.split("=", 1)[1].strip()
                    break
            found.append([name, str(p), version])

    # Also check for conda
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
    if conda_env:
        found.append([f"conda:{conda_env}", "conda", "?"])

    if not found:
        info("No virtual environments found in project."); return

    table = make_table(
        "Virtual Environments",
        [("Name", "origin.key"), ("Path", "origin.path"), ("Python", "origin.value")],
        found,
    )
    console.print(table)


@command.command("info")
def env_info():
    """Show current environment information."""
    print_command_header("env info", "Environment details")

    rows = [
        ["Python", sys.executable],
        ["Version", sys.version.split()[0]],
        ["Platform", sys.platform],
        ["Virtual Env", os.environ.get("VIRTUAL_ENV", "None")],
        ["Conda Env", os.environ.get("CONDA_DEFAULT_ENV", "None")],
        ["CWD", str(Path.cwd())],
    ]

    # Package count
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            import json
            pkgs = json.loads(result.stdout)
            rows.append(["Packages", str(len(pkgs))])
    except Exception:
        pass

    table = make_table(
        "Environment Info",
        [("Property", "origin.key"), ("Value", "origin.value")],
        rows,
    )
    console.print(table)


@command.command("init-dotenv")
@click.option("--force", is_flag=True, help="Overwrite existing .env file.")
def env_init_dotenv(force):
    """Create a .env file with common variables."""
    print_command_header("env init-dotenv", "Create .env file")

    dotenv = Path.cwd() / ".env"
    if dotenv.exists() and not force:
        warning(".env already exists. Use --force to overwrite.")
        return

    content = (
        "# Environment Variables\n"
        "# Do NOT commit this file to version control.\n\n"
        "DEBUG=true\n"
        "SECRET_KEY=change-me\n"
        "DATABASE_URL=sqlite:///db.sqlite3\n"
        "LOG_LEVEL=info\n"
    )
    dotenv.write_text(content, encoding="utf-8")
    success("Created .env file")
    info("Remember to add .env to your .gitignore")
