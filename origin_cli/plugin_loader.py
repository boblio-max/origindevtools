"""Plugin loader for Origin Dev Tools.

Discovers built-in tool commands from origin_cli/tools/ and
third-party plugins registered via the 'origin_cli.plugins' entry point.
"""

import importlib
import pkgutil
from pathlib import Path

import click


def load_builtin_tools(cli_group: click.Group):
    """Discover and register all built-in tool modules from origin_cli.tools.

    Each module in origin_cli/tools/ should expose a Click command or group
    at module level via a variable matching the module name, or a generic
    'cli' or 'command' variable.

    Args:
        cli_group: The root Click group to attach commands to.
    """
    tools_package = "origin_cli.tools"
    tools_path = Path(__file__).parent / "tools"

    if not tools_path.exists():
        return

    for importer, module_name, is_pkg in pkgutil.iter_modules([str(tools_path)]):
        if module_name.startswith("_"):
            continue

        try:
            module = importlib.import_module(f"{tools_package}.{module_name}")
        except ImportError as e:
            click.echo(f"Warning: Failed to load tool '{module_name}': {e}", err=True)
            continue

        # Look for a Click command/group in the module
        command = None
        for attr_name in ("command", "cli", module_name):
            attr = getattr(module, attr_name, None)
            if isinstance(attr, (click.Command, click.Group)):
                command = attr
                break

        # Fallback: scan all module attributes for a Click command
        if command is None:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, (click.Command, click.Group)) and attr_name != "click":
                    command = attr
                    break

        if command is not None:
            cli_group.add_command(command)


def load_external_plugins(cli_group: click.Group):
    """Load third-party plugins registered via entry points.

    Plugins should register under the 'origin_cli.plugins' group
    in their pyproject.toml:

        [project.entry-points."origin_cli.plugins"]
        my_tool = "my_package.module:command"

    Args:
        cli_group: The root Click group to attach commands to.
    """
    try:
        if hasattr(importlib.metadata, "entry_points"):
            eps = importlib.metadata.entry_points()
            # Python 3.12+ returns a SelectableGroups or dict
            if hasattr(eps, "select"):
                plugin_eps = eps.select(group="origin_cli.plugins")
            elif isinstance(eps, dict):
                plugin_eps = eps.get("origin_cli.plugins", [])
            else:
                plugin_eps = [ep for ep in eps if ep.group == "origin_cli.plugins"]

            for ep in plugin_eps:
                try:
                    command = ep.load()
                    if isinstance(command, (click.Command, click.Group)):
                        cli_group.add_command(command)
                except Exception as e:
                    click.echo(
                        f"Warning: Failed to load plugin '{ep.name}': {e}", err=True
                    )
    except Exception:
        pass  # Entry points not available, skip gracefully
