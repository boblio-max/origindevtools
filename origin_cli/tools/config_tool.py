"""origin config - Configuration manager."""

from pathlib import Path

import click
import yaml

from origin_cli.console import console, success, error, info, print_command_header, make_table
from origin_cli.config import (
    load_config, save_config, get_config_value, set_config_value,
    CONFIG_FILENAME, DEFAULTS, GLOBAL_CONFIG_PATH,
)


@click.group("config")
def command():
    """Manage Origin Dev Tools configuration."""
    pass


@command.command("init")
@click.option("--global", "is_global", is_flag=True, help="Create global config.")
def config_init(is_global):
    """Create a configuration file with defaults."""
    print_command_header("config init", "Initialize config")

    if is_global:
        target = GLOBAL_CONFIG_PATH
    else:
        target = Path.cwd() / CONFIG_FILENAME

    if target.exists():
        info(f"Config already exists: {target}")
        return

    save_config(DEFAULTS, target)
    success(f"Created: {target}")


@command.command("get")
@click.argument("key")
def config_get(key):
    """Get a configuration value (dot notation: fmt.indent)."""
    config = load_config()
    value = get_config_value(config, key)
    if value is None:
        error(f"Key not found: {key}")
    else:
        console.print(f"  [origin.key]{key}[/] = [origin.value]{value!r}[/]")


@command.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    print_command_header("config set", "Update config")

    # Auto-convert types
    if value.lower() in ("true", "yes"):
        value = True
    elif value.lower() in ("false", "no"):
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

    config = load_config()
    set_config_value(config, key, value)

    target = Path.cwd() / CONFIG_FILENAME
    save_config(config, target)
    success(f"Set {key} = {value!r}")


@command.command("list")
def config_list():
    """Show all configuration values."""
    print_command_header("config list", "Configuration")

    config = load_config()
    rows = []

    def flatten(d, prefix=""):
        for k, v in d.items():
            full = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
            if isinstance(v, dict):
                flatten(v, full)
            else:
                rows.append([full, repr(v)])

    flatten(config)

    table = make_table(
        "Configuration",
        [("Key", "origin.key"), ("Value", "origin.value")],
        rows,
    )
    console.print(table)
    console.print()

    # Show source info
    local = Path.cwd() / CONFIG_FILENAME
    if local.exists():
        info(f"Project config: {local}")
    if GLOBAL_CONFIG_PATH.exists():
        info(f"Global config: {GLOBAL_CONFIG_PATH}")
    if not local.exists() and not GLOBAL_CONFIG_PATH.exists():
        info("Using defaults. Run 'origin config init' to create config.")
    console.print()
