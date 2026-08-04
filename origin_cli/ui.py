"""ui

Claude Code-inspired terminal UI for the Origin CLI.

Centralizes ANSI styling (blue/gray palette), the banner, the prompt,
the bottom status bar, and styled help/error output.
"""

import os
import platform
import re
import shutil
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

BLUE = "\033[38;5;39m"
BLUE_BRIGHT = "\033[38;5;75m"
GRAY = "\033[38;5;245m"
DARK_GRAY = "\033[38;5;240m"
RED = "\033[38;5;196m"
GREEN = "\033[38;5;114m"
YELLOW = "\033[38;5;220m"
BG_STATUS = "\033[48;5;236m"

CHEVRON = "\u276f"
SPARK = "\u2726"
CHECK = "\u2713"
CROSS = "\u2715"
WARN = "\u26a0"
DOT = "\u00b7"

VERSION = "2.0.0"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def enable_ansi():
    """Enable ANSI escape sequences on Windows consoles."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _width(text):
    return len(_ANSI_RE.sub("", text))


def _terminal_width():
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80


def accent(text, bold=False):
    return f"{BOLD if bold else ''}{BLUE}{text}{RESET}"


def bright(text):
    return f"{BLUE_BRIGHT}{text}{RESET}"


def bold(text):
    return f"{BOLD}{text}{RESET}"


def dim(text):
    return f"{DIM}{text}{RESET}"


def muted(text):
    return f"{GRAY}{text}{RESET}"


def error(text):
    return f"{BOLD}{RED}{CROSS} {text}{RESET}"


def warn(text):
    return f"{YELLOW}{WARN} {text}{RESET}"


def success(text):
    return f"{GREEN}{CHECK} {text}{RESET}"


def active_venv():
    """Return the active Origin venv name, or None."""
    env = os.environ.get("ORIGIN_ENV", "")
    if not env:
        return None
    if os.path.basename(env) == "scripts":
        return os.path.basename(os.path.dirname(env))
    return os.path.basename(env)


_ASCII_TITLE = """========================================================
 ▄██████▄     ▄████████  ▄█    ▄██████▄    ▄█   ███▄▄▄▄
███    ███   ███    ███ ███  ███      ███ ███  ███▀▀▀██▄
███    ███   ███    ███ ███▌ ███      █▀  ███▌ ███   ███
███    ███  ▄███▄▄▄▄██▀ ███▌ ███          ███▌ ███   ███
███    ███ ▀▀███▀▀▀▀▀   ███▌ ███  ▀██████ ███▌ ███   ███
███    ███ ▀███████████ ███  ███      ███ ███  ███   ███
███    ███   ███    ███ ███  ███      ███ ███  ███   ███
 ▀██████▀    ▀█     █▀   █▀   ▀████████▀  █▀    ▀█   █▀
========================================================"""


def _sys_info():
    return f"python {platform.python_version()}  {platform.system().lower()} {platform.machine()}"


def banner():
    block = "\n".join(f"{BLUE}{line}{RESET}" for line in _ASCII_TITLE.splitlines())
    info = (
        f"  {accent('origin', bold=True)} {muted('v' + VERSION)}"
        f"  {muted(DOT)}  {muted(_sys_info())}"
        f"  {muted(DOT)}  {accent('developer CLI', bold=True)}\n"
    )
    hint = f"  {muted('Type')} {accent('origin help', bold=True)} {muted('for a list of commands')}\n"
    return f"\n{block}\n\n{info}{hint}"


def prompt(cwd):
    return f"{dim(cwd)} {accent(CHEVRON, bold=True)} "


def status_bar(cwd=None, venv=None):
    parts = [f"{accent(SPARK)} {accent('origin', bold=True)} {muted('v' + VERSION)}"]
    if cwd:
        parts.append(f"{dim('cwd:')} {muted(cwd)}")
    if venv:
        parts.append(f"{dim('venv:')} {accent(venv, bold=True)}")
    content = "  " + f"  {muted(DOT)}  ".join(parts) + "  "
    width = max(40, _terminal_width())
    bar = content + " " * max(0, width - _width(content))
    return f"{BG_STATUS}{bar}{RESET}"


def show_help():
    rows = [
        ("help", "Show this help message"),
        ("clear", "Clear the console"),
        ("exit / oe", "Exit the CLI"),
        ("<file>.or", "Run an Origin file"),
        ("<file>.py", "Run a Python file"),
        ("<file>.java", "Compile and run a Java file"),
        ("<file>.class", "Run a Java class file"),
        ("c <file>.java", "Compile a Java file"),
        ("create <file>.otxt <location>", "Generate a folder structure"),
        ("install <language|package>", "Install a language or Origin package"),
        ("uninstall <language>", "Uninstall a language"),
        ("update <language>", "Update a language"),
        ("in <location>", "Change working directory"),
        ("venv <venv_name>", "Create a Python virtual environment"),
        ("activate <venv_name>", "Activate a Python virtual environment"),
    ]
    width = max(len(cmd) for cmd, _ in rows)
    lines = [f"\n   {accent('origin', bold=True)} {muted('commands')}"]
    lines.append("   " + muted("─" * (width + 22)))
    for cmd, desc in rows:
        lines.append(f"   {bold(cmd.ljust(width))}   {muted(desc)}")
    lines.append("")
    print("\n".join(lines))
