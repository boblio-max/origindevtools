"""origin create - Project scaffolding with multiple templates.

Usage:
    origin create <template> [--name NAME] [--path PATH]
    origin create --list
"""

import os
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, header, make_table, print_command_header


# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

TEMPLATES = {
    "tinyCli": {
        "description": "Minimal CLI application",
        "files": {
            "cli.py": (
                '"""Tiny CLI application."""\n\nimport sys\n\n\ndef main():\n'
                '    args = sys.argv[1:]\n    if not args:\n'
                '        print("Usage: python cli.py <command>")\n'
                '        return\n    print(f"Running: {args[0]}")\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            ),
            "pyproject.toml": (
                '[project]\nname = "tinycli"\nversion = "0.1.0"\n'
                'description = "A tiny CLI application"\n'
                'requires-python = ">=3.9"\n\n'
                '[project.scripts]\ntinycli = "cli:main"\n'
            ),
            "README.md": "# Tiny CLI\n\nA minimal command-line application.\n\n## Usage\n\n```bash\npython cli.py <command>\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\n*.egg-info/\n.venv/\n",
        },
    },
    "standard": {
        "description": "Standard Python project with tests",
        "files": {
            "main.py": (
                '"""Main application entry point."""\n\n\ndef main():\n'
                '    print("Hello, World!")\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            ),
            "tests/__init__.py": "",
            "tests/test_main.py": (
                '"""Tests for main module."""\n\nfrom main import main\n\n\n'
                'def test_main(capsys):\n    main()\n'
                '    captured = capsys.readouterr()\n'
                '    assert "Hello" in captured.out\n'
            ),
            "requirements.txt": "# Add your dependencies here\n",
            "README.md": "# Standard Project\n\nA standard Python project.\n\n## Setup\n\n```bash\npip install -r requirements.txt\npython main.py\n```\n\n## Tests\n\n```bash\npytest\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\n*.egg-info/\n.venv/\nvenv/\n.env\n",
            "pyproject.toml": (
                '[project]\nname = "myproject"\nversion = "0.1.0"\n'
                'requires-python = ">=3.9"\n\n'
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
            ),
        },
    },
    "web": {
        "description": "Flask web application",
        "files": {
            "app.py": (
                '"""Flask web application."""\n\nfrom flask import Flask, render_template\n\n'
                'app = Flask(__name__)\n\n\n@app.route("/")\ndef index():\n'
                '    return render_template("index.html")\n\n\n'
                'if __name__ == "__main__":\n    app.run(debug=True)\n'
            ),
            "templates/index.html": (
                '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
                '    <meta charset="UTF-8">\n'
                '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '    <title>My Web App</title>\n'
                '    <link rel="stylesheet" href="/static/style.css">\n'
                '</head>\n<body>\n    <h1>Welcome</h1>\n'
                '</body>\n</html>\n'
            ),
            "static/style.css": (
                "/* Main stylesheet */\n\n* {\n    margin: 0;\n    padding: 0;\n"
                "    box-sizing: border-box;\n}\n\nbody {\n"
                '    font-family: system-ui, -apple-system, sans-serif;\n'
                "    line-height: 1.6;\n    padding: 2rem;\n}\n"
            ),
            "requirements.txt": "flask>=3.0\n",
            "README.md": "# Web Project\n\nA Flask web application.\n\n## Setup\n\n```bash\npip install -r requirements.txt\npython app.py\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\n*.egg-info/\n.venv/\nvenv/\n.env\ninstance/\n",
        },
    },
    "api": {
        "description": "REST API with FastAPI",
        "files": {
            "main.py": (
                '"""FastAPI application."""\n\nfrom fastapi import FastAPI\n\n'
                'app = FastAPI(title="My API", version="0.1.0")\n\n\n'
                '@app.get("/")\nasync def root():\n'
                '    return {"message": "Hello, World!"}\n\n\n'
                '@app.get("/health")\nasync def health():\n'
                '    return {"status": "ok"}\n'
            ),
            "requirements.txt": "fastapi>=0.100\nuvicorn[standard]>=0.20\n",
            "tests/__init__.py": "",
            "tests/test_api.py": (
                '"""API tests."""\n\nfrom fastapi.testclient import TestClient\n'
                'from main import app\n\nclient = TestClient(app)\n\n\n'
                'def test_root():\n    response = client.get("/")\n'
                '    assert response.status_code == 200\n'
            ),
            "README.md": "# API Project\n\nA REST API built with FastAPI.\n\n## Setup\n\n```bash\npip install -r requirements.txt\nuvicorn main:app --reload\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\n*.egg-info/\n.venv/\nvenv/\n.env\n",
            "pyproject.toml": (
                '[project]\nname = "myapi"\nversion = "0.1.0"\n'
                'requires-python = ">=3.9"\n'
            ),
        },
    },
    "library": {
        "description": "Reusable Python library/package",
        "files": {
            "src/mylib/__init__.py": '"""My library."""\n\n__version__ = "0.1.0"\n',
            "src/mylib/core.py": '"""Core library functionality."""\n\n\ndef hello(name: str = "World") -> str:\n    """Return a greeting."""\n    return f"Hello, {name}!"\n',
            "tests/__init__.py": "",
            "tests/test_core.py": (
                '"""Tests for core module."""\n\nfrom mylib.core import hello\n\n\n'
                'def test_hello():\n    assert hello() == "Hello, World!"\n\n\n'
                'def test_hello_name():\n    assert hello("Origin") == "Hello, Origin!"\n'
            ),
            "pyproject.toml": (
                '[build-system]\nrequires = ["setuptools>=68.0"]\n'
                'build-backend = "setuptools.build_meta"\n\n'
                '[project]\nname = "mylib"\nversion = "0.1.0"\n'
                'description = "My reusable library"\n'
                'requires-python = ">=3.9"\n\n'
                '[tool.setuptools.packages.find]\nwhere = ["src"]\n\n'
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
            ),
            "README.md": "# My Library\n\nA reusable Python library.\n\n## Installation\n\n```bash\npip install .\n```\n\n## Usage\n\n```python\nfrom mylib.core import hello\nprint(hello())\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\nbuild/\n*.egg-info/\n.venv/\nvenv/\n",
            "LICENSE": "MIT License\n\nCopyright (c) 2026\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files.\n",
        },
    },
    "fullstack": {
        "description": "Full-stack app with API backend and static frontend",
        "files": {
            "backend/app.py": (
                '"""Backend API."""\n\nfrom flask import Flask, jsonify, send_from_directory\n\n'
                'app = Flask(__name__, static_folder="../frontend")\n\n\n'
                '@app.route("/api/hello")\ndef hello():\n'
                '    return jsonify({"message": "Hello from the API!"})\n\n\n'
                '@app.route("/")\ndef index():\n'
                '    return send_from_directory(app.static_folder, "index.html")\n\n\n'
                'if __name__ == "__main__":\n    app.run(debug=True)\n'
            ),
            "backend/requirements.txt": "flask>=3.0\n",
            "frontend/index.html": (
                '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
                '    <meta charset="UTF-8">\n'
                '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                '    <title>Full Stack App</title>\n'
                '    <link rel="stylesheet" href="style.css">\n'
                '</head>\n<body>\n'
                '    <div id="app">\n        <h1>Full Stack App</h1>\n'
                '        <p id="message">Loading...</p>\n    </div>\n'
                '    <script src="app.js"></script>\n'
                '</body>\n</html>\n'
            ),
            "frontend/style.css": (
                "* { margin: 0; padding: 0; box-sizing: border-box; }\n"
                "body { font-family: system-ui, sans-serif; padding: 2rem; }\n"
                "#app { max-width: 800px; margin: 0 auto; }\n"
            ),
            "frontend/app.js": (
                '// Frontend application\n'
                'fetch("/api/hello")\n'
                '    .then(res => res.json())\n'
                '    .then(data => {\n'
                '        document.getElementById("message").textContent = data.message;\n'
                '    });\n'
            ),
            "README.md": "# Full Stack App\n\n## Setup\n\n```bash\ncd backend\npip install -r requirements.txt\npython app.py\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\nnode_modules/\n.venv/\nvenv/\n.env\n",
        },
    },
    "origin": {
        "description": "Origin language project (.or files)",
        "files": {
            "main.or": 'fn main() {\n    let message = "Hello, Origin!"\n    print(message)\n}\n',
            "lib.or": '// Shared library functions\n\nfn add(a, b) {\n    return a + b\n}\n\nfn greet(name) {\n    print("Hello, " + name)\n}\n',
            "tests/test_main.or": '// Tests for main module\n\nfn test_greeting() {\n    let result = "Hello, Origin!"\n    assert(result == "Hello, Origin!")\n    print("test_greeting: PASSED")\n}\n',
            "README.md": "# Origin Project\n\nAn Origin language project.\n\n## Running\n\n```bash\norigin run main.or\n```\n\n## Formatting\n\n```bash\norigin fmt .\n```\n",
            ".originrc.yml": "fmt:\n  indent: 4\nlint:\n  severity: warning\n",
            ".gitignore": "__pycache__/\n*.pyc\n.venv/\n",
        },
    },
    "monorepo": {
        "description": "Multi-package monorepo structure",
        "files": {
            "packages/core/src/__init__.py": '"""Core package."""\n\n__version__ = "0.1.0"\n',
            "packages/core/pyproject.toml": '[project]\nname = "core"\nversion = "0.1.0"\n',
            "packages/cli/src/__init__.py": '"""CLI package."""\n\n__version__ = "0.1.0"\n',
            "packages/cli/pyproject.toml": '[project]\nname = "cli"\nversion = "0.1.0"\ndependencies = ["core"]\n',
            "packages/core/tests/__init__.py": "",
            "packages/cli/tests/__init__.py": "",
            "README.md": "# Monorepo\n\nMulti-package monorepo.\n\n## Packages\n\n- `packages/core/` - Core library\n- `packages/cli/` - CLI application\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\ndist/\nbuild/\n*.egg-info/\n.venv/\nvenv/\n",
            "Makefile": "install:\n\tpip install -e packages/core\n\tpip install -e packages/cli\n\ntest:\n\tpytest packages/*/tests/\n",
        },
    },
}


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

@click.command("create")
@click.argument("template", required=False)
@click.option("--name", "-n", help="Project name (defaults to template name).")
@click.option("--path", "-p", default=".", help="Target directory (default: current).")
@click.option("--list", "list_templates", is_flag=True, help="List available templates.")
def command(template, name, path, list_templates):
    """Scaffold a new project from a template."""
    print_command_header("create", "Project scaffolding")

    if list_templates or template is None:
        _show_templates()
        return

    if template not in TEMPLATES:
        error(f"Unknown template: '{template}'")
        info(f"Available: {', '.join(TEMPLATES.keys())}")
        return

    target = Path(path).resolve()
    tmpl = TEMPLATES[template]
    created_files = []

    for filepath, content in tmpl["files"].items():
        full_path = target / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        created_files.append(filepath)

    # Show results
    console.print()
    table = make_table(
        f"Created: {template}",
        [("File", "origin.path"), ("Size", "origin.dim")],
        [
            [f, f"{len(tmpl['files'][f])} bytes"]
            for f in created_files
        ],
    )
    console.print(table)
    console.print()
    success(f"Scaffolded '{template}' project with {len(created_files)} files at {target}")
    console.print()


def _show_templates():
    """Display all available templates in a table."""
    table = make_table(
        "Available Templates",
        [("Template", "origin.key"), ("Description", "origin.value"), ("Files", "origin.dim")],
        [
            [name, tmpl["description"], str(len(tmpl["files"]))]
            for name, tmpl in TEMPLATES.items()
        ],
    )
    console.print(table)
    console.print()
    info("Usage: origin create <template> [--path <dir>]")
    console.print()
