"""origin lint - Static analysis and linting for .or and .py files."""

import re
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, warning, print_command_header, make_table
from origin_cli.utils import discover_files, safe_read_file
from origin_cli.config import load_config


class LintIssue:
    def __init__(self, file, line, severity, rule, message):
        self.file = file
        self.line = line
        self.severity = severity  # error, warning, info
        self.rule = rule
        self.message = message


def lint_origin_file(filepath: Path, content: str) -> list[LintIssue]:
    """Lint an Origin (.or) file for common issues."""
    issues = []
    lines = content.splitlines()
    declared_vars = set()
    used_vars = set()
    declared_fns = set()
    brace_depth = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Trailing whitespace
        if line != line.rstrip():
            issues.append(LintIssue(filepath, i, "warning", "W001", "Trailing whitespace"))

        # Line too long
        if len(line) > 120:
            issues.append(LintIssue(filepath, i, "info", "I001", f"Line too long ({len(line)} > 120)"))

        # Track brace depth
        brace_depth += stripped.count("{") - stripped.count("}")
        if brace_depth < 0:
            issues.append(LintIssue(filepath, i, "error", "E001", "Unmatched closing brace"))

        # Variable declarations
        let_match = re.match(r'let\s+(\w+)', stripped)
        if let_match:
            var = let_match.group(1)
            if var in declared_vars:
                issues.append(LintIssue(filepath, i, "warning", "W002", f"Variable '{var}' redeclared"))
            declared_vars.add(var)

        # Function declarations
        fn_match = re.match(r'fn\s+(\w+)\s*\(', stripped)
        if fn_match:
            fn_name = fn_match.group(1)
            if fn_name in declared_fns:
                issues.append(LintIssue(filepath, i, "warning", "W003", f"Function '{fn_name}' redeclared"))
            declared_fns.add(fn_name)

        # Empty blocks
        if stripped == "{}":
            issues.append(LintIssue(filepath, i, "info", "I002", "Empty block"))

        # Comparison with assignment operator
        if re.search(r'if\s*\([^=]*[^=!<>]=[^=]', stripped):
            issues.append(LintIssue(filepath, i, "warning", "W004", "Possible assignment in condition (use ==)"))

        # Missing spaces around operators
        if re.search(r'\w[=<>!]+\w', stripped) and not re.search(r'[=<>!]=', stripped) and '==' not in stripped:
            if '=' in stripped and 'let' not in stripped and 'fn' not in stripped:
                issues.append(LintIssue(filepath, i, "info", "I003", "Consider spaces around operators"))

    if brace_depth != 0:
        issues.append(LintIssue(filepath, len(lines), "error", "E002", f"Unbalanced braces (depth: {brace_depth})"))

    return issues


def lint_python_file(filepath: Path, content: str) -> list[LintIssue]:
    """Lint a Python file for common issues."""
    issues = []
    lines = content.splitlines()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if line != line.rstrip():
            issues.append(LintIssue(filepath, i, "warning", "W001", "Trailing whitespace"))

        if len(line) > 120:
            issues.append(LintIssue(filepath, i, "info", "I001", f"Line too long ({len(line)} > 120)"))

        if stripped.startswith("import *") or "import *" in stripped:
            issues.append(LintIssue(filepath, i, "warning", "W010", "Wildcard import"))

        if "except:" in stripped and "except Exception" not in stripped:
            issues.append(LintIssue(filepath, i, "warning", "W011", "Bare except clause"))

        if re.match(r'^\s*print\(', line) and "debug" not in filepath.name.lower():
            issues.append(LintIssue(filepath, i, "info", "I010", "Print statement (use logging?)"))

        if "TODO" in stripped or "FIXME" in stripped or "HACK" in stripped:
            issues.append(LintIssue(filepath, i, "info", "I011", f"TODO/FIXME comment found"))

        if "\t" in line:
            issues.append(LintIssue(filepath, i, "warning", "W012", "Tab indentation (use spaces)"))

    return issues


LINTERS = {".or": lint_origin_file, ".py": lint_python_file}
SEVERITY_STYLE = {"error": "bold red", "warning": "yellow", "info": "blue"}


@click.command("lint")
@click.argument("path", default=".")
@click.option("--severity", "-s", type=click.Choice(["error", "warning", "info"]),
              default="warning", help="Minimum severity to show.")
def command(path, severity):
    """Lint source files for common issues."""
    print_command_header("lint", "Static analysis")

    config = load_config()
    extensions = config.get("lint", {}).get("extensions", [".or", ".py"])
    extensions = [e for e in extensions if e in LINTERS]

    target = Path(path).resolve()
    if not target.exists():
        error(f"Path not found: {target}"); return

    files = discover_files(target, extensions=extensions)
    if not files:
        info("No files found to lint."); return

    severity_order = {"error": 3, "warning": 2, "info": 1}
    min_sev = severity_order.get(severity, 2)
    all_issues = []

    for filepath in files:
        content = safe_read_file(filepath)
        if content is None:
            continue
        linter = LINTERS.get(filepath.suffix)
        if linter:
            file_issues = linter(filepath, content)
            all_issues.extend([i for i in file_issues if severity_order.get(i.severity, 0) >= min_sev])

    if not all_issues:
        console.print()
        success(f"No issues found in {len(files)} file(s).")
        console.print()
        return

    # Display results
    rows = []
    for issue in sorted(all_issues, key=lambda i: (str(i.file), i.line)):
        sev_style = SEVERITY_STYLE.get(issue.severity, "white")
        rows.append([
            str(issue.file.name),
            str(issue.line),
            f"[{sev_style}]{issue.severity.upper()}[/]",
            issue.rule,
            issue.message,
        ])

    table = make_table(
        f"Lint Results ({len(all_issues)} issues)",
        [("File", "origin.path"), ("Line", "origin.dim"), ("Severity", ""),
         ("Rule", "origin.key"), ("Message", "origin.value")],
        rows,
    )
    console.print(table)

    errors = sum(1 for i in all_issues if i.severity == "error")
    warns = sum(1 for i in all_issues if i.severity == "warning")
    infos = sum(1 for i in all_issues if i.severity == "info")
    console.print()
    info(f"Summary: {errors} errors, {warns} warnings, {infos} info in {len(files)} file(s)")

    if errors > 0:
        raise SystemExit(1)
