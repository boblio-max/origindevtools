"""origin snippet - Code snippet manager."""

import os
import time
from pathlib import Path

import click
import yaml

from origin_cli.console import console, success, error, info, print_command_header, make_table
from origin_cli.config import GLOBAL_CONFIG_DIR


SNIPPETS_DIR = GLOBAL_CONFIG_DIR / "snippets"


def _ensure_dir():
    SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)


def _snippet_path(name: str) -> Path:
    return SNIPPETS_DIR / f"{name}.yml"


def _load_snippet(name: str) -> dict | None:
    p = _snippet_path(name)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_snippet(name: str, data: dict):
    _ensure_dir()
    with open(_snippet_path(name), "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


@click.group("snippet")
def command():
    """Manage code snippets."""
    pass


@command.command("save")
@click.argument("name")
@click.option("--file", "-f", "filepath", help="Read snippet from file.")
@click.option("--tag", "-t", multiple=True, help="Tags for the snippet.")
@click.option("--desc", "-d", default="", help="Description.")
def snippet_save(name, filepath, tag, desc):
    """Save a code snippet."""
    print_command_header("snippet save", "Save snippet")

    if filepath:
        p = Path(filepath)
        if not p.exists():
            error(f"File not found: {filepath}"); return
        code = p.read_text(encoding="utf-8")
        lang = p.suffix.lstrip(".")
    else:
        info("Enter snippet (empty line to finish):")
        lines = []
        while True:
            try:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            except EOFError:
                break
        code = "\n".join(lines).rstrip()
        lang = "text"

    data = {
        "name": name,
        "code": code,
        "language": lang,
        "tags": list(tag),
        "description": desc,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _save_snippet(name, data)
    success(f"Snippet '{name}' saved ({len(code)} chars)")


@command.command("get")
@click.argument("name")
def snippet_get(name):
    """Display a saved snippet."""
    print_command_header("snippet get", "Retrieve snippet")
    data = _load_snippet(name)
    if not data:
        error(f"Snippet '{name}' not found."); return

    from rich.syntax import Syntax
    lang = data.get("language", "text")
    code = data.get("code", "")
    console.print()
    if data.get("description"):
        info(data["description"])
    console.print(Syntax(code, lang, theme="monokai", line_numbers=True, padding=1))
    console.print()


@command.command("list")
def snippet_list():
    """List all saved snippets."""
    print_command_header("snippet list", "Browse snippets")
    _ensure_dir()

    files = sorted(SNIPPETS_DIR.glob("*.yml"))
    if not files:
        info("No snippets saved yet. Use: origin snippet save <name>"); return

    rows = []
    for f in files:
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            rows.append([
                data.get("name", f.stem),
                data.get("language", "?"),
                ", ".join(data.get("tags", [])) or "-",
                data.get("created", "?"),
            ])
        except Exception:
            rows.append([f.stem, "?", "-", "?"])

    table = make_table(
        "Saved Snippets",
        [("Name", "origin.key"), ("Language", "origin.value"),
         ("Tags", "origin.dim"), ("Created", "origin.dim")],
        rows,
    )
    console.print(table)


@command.command("search")
@click.argument("query")
def snippet_search(query):
    """Search snippets by name, tag, or content."""
    print_command_header("snippet search", "Search snippets")
    _ensure_dir()
    query_lower = query.lower()
    matches = []

    for f in SNIPPETS_DIR.glob("*.yml"):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            searchable = " ".join([
                data.get("name", ""), data.get("description", ""),
                " ".join(data.get("tags", [])), data.get("code", ""),
            ]).lower()
            if query_lower in searchable:
                matches.append(data.get("name", f.stem))
        except Exception:
            pass

    if matches:
        info(f"Found {len(matches)} match(es):")
        for m in matches:
            console.print(f"    [origin.key]{m}[/]")
    else:
        info(f"No snippets matching '{query}'")


@command.command("delete")
@click.argument("name")
def snippet_delete(name):
    """Delete a saved snippet."""
    p = _snippet_path(name)
    if not p.exists():
        error(f"Snippet '{name}' not found."); return
    p.unlink()
    success(f"Snippet '{name}' deleted.")
