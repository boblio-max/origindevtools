"""origin fmt - Code formatter for .or, .py, .json, and .yaml files."""

import json
from pathlib import Path

import click
import yaml

from origin_cli.console import console, success, error, info, warning, print_command_header
from origin_cli.utils import discover_files, safe_read_file
from origin_cli.config import load_config


def _format_origin(text: str, indent_str: str = "    ") -> str:
    lines = text.splitlines()
    indent = 0
    result = []
    for raw in lines:
        line = raw.strip()
        if not line:
            result.append("")
            continue
        if line.startswith("}") or line.startswith("]") or line.startswith(")"):
            indent = max(indent - 1, 0)
        result.append((indent_str * indent) + line)
        if line.endswith("{") or line.endswith("[") or line.endswith("("):
            indent += 1
    out = "\n".join(result)
    if text.endswith("\n"):
        out += "\n"
    return out


def _format_python(text: str) -> str:
    lines = text.splitlines()
    result = [line.rstrip() for line in lines]
    cleaned = []
    blank_count = 0
    for line in result:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    out = "\n".join(cleaned)
    if not out.endswith("\n"):
        out += "\n"
    return out


def _format_json(text: str) -> str:
    data = json.loads(text)
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _format_yaml(text: str) -> str:
    data = yaml.safe_load(text)
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


FORMATTERS = {
    ".or": _format_origin, ".py": _format_python,
    ".json": _format_json, ".yaml": _format_yaml, ".yml": _format_yaml,
}


@click.command("fmt")
@click.argument("path", default=".")
@click.option("--check", is_flag=True, help="Check formatting (exit 1 if unformatted).")
@click.option("--diff", "show_diff", is_flag=True, help="Show changes without writing.")
@click.option("--ext", multiple=True, help="Extensions to format.")
def command(path, check, show_diff, ext):
    """Format source code files."""
    print_command_header("fmt", "Code formatter")
    config = load_config()
    indent_size = config.get("fmt", {}).get("indent", 4)
    extensions = list(ext) if ext else config.get("fmt", {}).get("extensions", [".or", ".py"])
    extensions = [e for e in extensions if e in FORMATTERS]
    if not extensions:
        error("No supported extensions."); return
    target = Path(path).resolve()
    if not target.exists():
        error(f"Path not found: {target}"); return
    files = discover_files(target, extensions=extensions)
    if not files:
        info("No files found."); return

    formatted_count = unchanged_count = error_count = 0
    unformatted = []
    for filepath in files:
        formatter = FORMATTERS.get(filepath.suffix)
        if not formatter:
            continue
        original = safe_read_file(filepath)
        if original is None:
            error(f"Could not read: {filepath}"); error_count += 1; continue
        try:
            result = _format_origin(original, " " * indent_size) if filepath.suffix == ".or" else formatter(original)
        except Exception as e:
            error(f"Error in {filepath.name}: {e}"); error_count += 1; continue
        if result == original:
            unchanged_count += 1; continue
        if show_diff:
            _print_diff(filepath, original, result); formatted_count += 1
        elif check:
            unformatted.append(filepath)
        else:
            filepath.write_text(result, encoding="utf-8")
            success(f"Formatted: {filepath}"); formatted_count += 1

    console.print()
    if check:
        if unformatted:
            warning(f"{len(unformatted)} file(s) need formatting:")
            for f in unformatted:
                console.print(f"    [origin.path]{f}[/]")
            raise SystemExit(1)
        else:
            success(f"All {len(files)} file(s) properly formatted.")
    else:
        info(f"Done: {formatted_count} formatted, {unchanged_count} unchanged, {error_count} errors")
    console.print()


def _print_diff(filepath, original, formatted):
    console.print(f"\n  [origin.path]{filepath}[/]")
    orig_lines = original.splitlines()
    fmt_lines = formatted.splitlines()
    for i in range(max(len(orig_lines), len(fmt_lines))):
        orig = orig_lines[i] if i < len(orig_lines) else ""
        fmt = fmt_lines[i] if i < len(fmt_lines) else ""
        if orig != fmt:
            ln = f"{i+1:4d}"
            if i < len(orig_lines): console.print(f"  {ln} [red]- {orig}[/]")
            if i < len(fmt_lines): console.print(f"  {ln} [green]+ {fmt}[/]")
