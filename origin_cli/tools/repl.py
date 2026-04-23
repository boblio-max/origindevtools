"""origin repl - Interactive Origin language REPL."""

import os
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, print_command_header


REPL_HELP = """
  .help     Show this help
  .clear    Clear screen
  .vars     Show declared variables
  .save F   Save session to file F
  .load F   Load and run file F
  .exit     Exit REPL
"""


@click.command("repl")
def command():
    """Start an interactive Origin REPL."""
    print_command_header("repl", "Interactive Origin shell")
    console.print("  [origin.dim]Type .help for commands, .exit to quit[/]\n")

    variables = {}
    history = []

    while True:
        try:
            line = console.input("[origin.accent]or> [/]")
        except (KeyboardInterrupt, EOFError):
            console.print()
            info("REPL closed.")
            break

        stripped = line.strip()
        if not stripped:
            continue

        history.append(stripped)

        # Meta-commands
        if stripped == ".exit":
            info("REPL closed.")
            break
        elif stripped == ".help":
            console.print(REPL_HELP)
            continue
        elif stripped == ".clear":
            os.system("cls" if os.name == "nt" else "clear")
            continue
        elif stripped == ".vars":
            if variables:
                for k, v in variables.items():
                    console.print(f"  [origin.key]{k}[/] = [origin.value]{v!r}[/]")
            else:
                info("No variables declared.")
            continue
        elif stripped.startswith(".save "):
            fname = stripped[6:].strip()
            try:
                Path(fname).write_text("\n".join(history[:-1]), encoding="utf-8")
                success(f"Session saved to {fname}")
            except Exception as e:
                error(f"Save failed: {e}")
            continue
        elif stripped.startswith(".load "):
            fname = stripped[6:].strip()
            try:
                content = Path(fname).read_text(encoding="utf-8")
                for fline in content.splitlines():
                    console.print(f"  [origin.dim]>>> {fline}[/]")
                    _eval_line(fline.strip(), variables)
            except FileNotFoundError:
                error(f"File not found: {fname}")
            continue

        _eval_line(stripped, variables)


def _eval_line(line: str, variables: dict):
    """Evaluate a single Origin line in the REPL context."""
    try:
        # let x = <expr>
        if line.startswith("let "):
            parts = line[4:].split("=", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                val = _eval_expr(parts[1].strip(), variables)
                variables[name] = val
                console.print(f"  [origin.dim]{name} = {val!r}[/]")
                return

        # print(...)
        if line.startswith("print(") and line.endswith(")"):
            expr = line[6:-1].strip()
            val = _eval_expr(expr, variables)
            console.print(f"  {val}")
            return

        # Variable reassignment: x = <expr>
        if "=" in line and not any(op in line for op in ["==", "!=", "<=", ">="]):
            parts = line.split("=", 1)
            name = parts[0].strip()
            if name in variables:
                val = _eval_expr(parts[1].strip(), variables)
                variables[name] = val
                console.print(f"  [origin.dim]{name} = {val!r}[/]")
                return

        # Expression evaluation
        val = _eval_expr(line, variables)
        if val is not None:
            console.print(f"  [origin.value]{val!r}[/]")
    except Exception as e:
        error(str(e))


def _eval_expr(expr: str, variables: dict):
    """Safely evaluate an expression with variable substitution."""
    if not expr:
        return None

    # String literal
    if (expr.startswith('"') and expr.endswith('"')) or \
       (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    # Boolean
    if expr == "true":
        return True
    if expr == "false":
        return False

    # Number
    try:
        if "." in expr:
            return float(expr)
        return int(expr)
    except ValueError:
        pass

    # Variable lookup
    if expr in variables:
        return variables[expr]

    # Simple arithmetic with variable substitution
    safe_expr = expr
    for var, val in variables.items():
        safe_expr = safe_expr.replace(var, repr(val))
    try:
        return eval(safe_expr, {"__builtins__": {}}, {})
    except Exception:
        pass

    return expr
