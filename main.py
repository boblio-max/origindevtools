"""Origin Dev Tools - Backward compatibility shim.

This file preserves the old `python main.py` workflow.
The primary interface is now `origin <command>` after pip install.

Usage:
    python main.py          -> launches the new CLI
    pip install -e .        -> installs the `origin` command globally
"""

import sys


def main():
    try:
        from origin_cli.main import cli
        cli()
    except ImportError:
        print("Origin Dev Tools v2.0.0")
        print()
        print("Dependencies not installed. Run:")
        print("  pip install -e .")
        print()
        print("Then use: origin --help")
        sys.exit(1)


if __name__ == "__main__":
    main()
