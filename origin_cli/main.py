"""Origin Dev Tools - Main CLI entry point.

Usage:
    origin <command> [options]
    origin --help
"""

import click

from origin_cli import __version__
from origin_cli.console import console, print_banner
from origin_cli.plugin_loader import load_builtin_tools, load_external_plugins


class OriginCLI(click.Group):
    """Custom Click group that shows the banner on --help."""

    def format_help(self, ctx, formatter):
        print_banner()
        console.print(
            "  [origin.dim]Professional developer toolkit for the Origin language and beyond[/]\n"
        )
        super().format_help(ctx, formatter)


@click.group(cls=OriginCLI, invoke_without_command=True)
@click.version_option(__version__, prog_name="Origin Dev Tools")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.pass_context
def cli(ctx, verbose, no_color):
    """Origin Dev Tools - Professional developer toolkit."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["no_color"] = no_color

    if no_color:
        console.no_color = True

    if ctx.invoked_subcommand is None:
        print_banner()
        console.print(
            "  [origin.dim]Type[/] [origin.accent]origin --help[/] "
            "[origin.dim]to see available commands.[/]\n"
        )


# Register all tools
load_builtin_tools(cli)
load_external_plugins(cli)


def main():
    """Entry point for the origin command."""
    cli()


if __name__ == "__main__":
    main()
