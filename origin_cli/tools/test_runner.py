"""origin test - Test runner with Rich output."""

import subprocess
import time
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, print_command_header, make_table
from origin_cli.utils import format_duration


@click.command("test")
@click.argument("path", default=".")
@click.option("--coverage", "-c", is_flag=True, help="Run with coverage report.")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output.")
@click.option("--pattern", "-k", default=None, help="Filter tests by pattern.")
@click.option("--failfast", "-x", is_flag=True, help="Stop on first failure.")
def command(path, coverage, verbose, pattern, failfast):
    """Run project tests."""
    print_command_header("test", "Test runner")

    target = Path(path).resolve()
    cmd = ["python", "-m", "pytest", str(target)]

    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov", "--cov-report=term-missing"])
    if pattern:
        cmd.extend(["-k", pattern])
    if failfast:
        cmd.append("-x")

    cmd.append("--tb=short")

    info(f"Running: {' '.join(cmd)}")
    console.print()

    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=False)
    elapsed = time.perf_counter() - start

    console.print()
    if result.returncode == 0:
        success(f"All tests passed in {format_duration(elapsed)}")
    elif result.returncode == 5:
        info(f"No tests found at {target}")
    else:
        error(f"Tests failed (exit code {result.returncode}) in {format_duration(elapsed)}")
    console.print()

    raise SystemExit(result.returncode)
