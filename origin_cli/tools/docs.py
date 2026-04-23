"""origin docs - Documentation generator from source files."""

import re
import ast
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, print_command_header
from origin_cli.utils import discover_files, safe_read_file, safe_write_file


@click.command("docs")
@click.argument("path", default=".")
@click.option("--output", "-o", default="docs.md", help="Output file (default: docs.md).")
@click.option("--title", "-t", default=None, help="Document title.")
def command(path, output, title):
    """Generate markdown documentation from source files."""
    print_command_header("docs", "Documentation generator")

    target = Path(path).resolve()
    if not target.exists():
        error(f"Path not found: {target}"); return

    files = discover_files(target, extensions=[".py", ".or"])
    if not files:
        info("No source files found."); return

    doc_title = title or target.name
    sections = []

    for filepath in files:
        content = safe_read_file(filepath)
        if content is None:
            continue

        if filepath.suffix == ".py":
            section = _document_python(filepath, content)
        elif filepath.suffix == ".or":
            section = _document_origin(filepath, content)
        else:
            continue

        if section:
            sections.append(section)

    if not sections:
        info("No documentable content found."); return

    # Build markdown
    md = [f"# {doc_title}\n"]
    md.append("Auto-generated documentation.\n")
    md.append("## Table of Contents\n")
    for s in sections:
        anchor = s["name"].lower().replace(" ", "-").replace(".", "")
        md.append(f"- [{s['name']}](#{anchor})")
    md.append("")

    for s in sections:
        md.append(f"## {s['name']}\n")
        if s.get("module_doc"):
            md.append(f"{s['module_doc']}\n")
        for item in s.get("items", []):
            md.append(f"### `{item['signature']}`\n")
            if item.get("doc"):
                md.append(f"{item['doc']}\n")
        md.append("---\n")

    doc_content = "\n".join(md)
    safe_write_file(output, doc_content)
    success(f"Generated documentation: {output} ({len(sections)} modules)")
    console.print()


def _document_python(filepath: Path, content: str) -> dict | None:
    """Extract documentation from a Python file using AST."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    section = {
        "name": filepath.name,
        "module_doc": ast.get_docstring(tree) or "",
        "items": [],
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = []
            for arg in node.args.args:
                ann = ""
                if arg.annotation and isinstance(arg.annotation, ast.Name):
                    ann = f": {arg.annotation.id}"
                args.append(f"{arg.arg}{ann}")

            sig = f"{node.name}({', '.join(args)})"
            doc = ast.get_docstring(node) or ""
            section["items"].append({"signature": sig, "doc": doc})

        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            section["items"].append({"signature": f"class {node.name}", "doc": doc})

    if not section["items"] and not section["module_doc"]:
        return None
    return section


def _document_origin(filepath: Path, content: str) -> dict | None:
    """Extract documentation from an Origin (.or) file."""
    section = {
        "name": filepath.name,
        "module_doc": "",
        "items": [],
    }

    lines = content.splitlines()
    comment_buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            comment_buffer.append(stripped[2:].strip())
        elif stripped.startswith("fn "):
            match = re.match(r'fn\s+(\w+)\s*\(([^)]*)\)', stripped)
            if match:
                name = match.group(1)
                params = match.group(2).strip()
                sig = f"fn {name}({params})"
                doc = "\n".join(comment_buffer) if comment_buffer else ""
                section["items"].append({"signature": sig, "doc": doc})
            comment_buffer = []
        else:
            if not stripped:
                pass  # Keep comment buffer across blank lines
            else:
                comment_buffer = []

    if not section["items"]:
        return None
    return section
