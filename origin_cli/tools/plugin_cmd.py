"""origin plugin - Plugin management commands."""

import click

from origin_cli.console import console, info, print_command_header, make_table


@click.group("plugin")
def command():
    """Manage Origin Dev Tools plugins."""
    pass


@command.command("list")
def plugin_list():
    """List installed plugins."""
    print_command_header("plugin list", "Installed plugins")

    import importlib
    import importlib.metadata

    builtin = []
    external = []

    # List built-in tools
    try:
        import origin_cli.tools
        import pkgutil
        for importer, name, is_pkg in pkgutil.iter_modules(origin_cli.tools.__path__):
            if not name.startswith("_"):
                builtin.append(name)
    except Exception:
        pass

    # List external plugins
    try:
        eps = importlib.metadata.entry_points()
        if hasattr(eps, "select"):
            plugin_eps = eps.select(group="origin_cli.plugins")
        elif isinstance(eps, dict):
            plugin_eps = eps.get("origin_cli.plugins", [])
        else:
            plugin_eps = [ep for ep in eps if ep.group == "origin_cli.plugins"]
        for ep in plugin_eps:
            external.append(ep.name)
    except Exception:
        pass

    rows = [[name, "built-in"] for name in sorted(builtin)]
    rows.extend([[name, "external"] for name in sorted(external)])

    if rows:
        table = make_table(
            "Installed Tools",
            [("Name", "origin.key"), ("Type", "origin.dim")],
            rows,
        )
        console.print(table)
    else:
        info("No tools found.")

    console.print()
    if external:
        info(f"{len(builtin)} built-in, {len(external)} external")
    else:
        info(f"{len(builtin)} built-in tools loaded")
    console.print()


@command.command("info")
@click.argument("name")
def plugin_info(name):
    """Show details about a plugin/tool."""
    print_command_header("plugin info", f"Tool: {name}")

    try:
        import importlib
        mod = importlib.import_module(f"origin_cli.tools.{name}")
        doc = mod.__doc__ or "No description available."
        console.print(f"\n  [origin.key]{name}[/]")
        console.print(f"  [origin.dim]{doc.strip()}[/]")
        console.print(f"  [origin.dim]Module: origin_cli.tools.{name}[/]\n")
    except ImportError:
        from origin_cli.console import error
        error(f"Tool '{name}' not found.")
