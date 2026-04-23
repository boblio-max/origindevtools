"""origin bench - Performance benchmarker and profiler."""

import subprocess
import time
import cProfile
import pstats
import io
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, print_command_header, make_table
from origin_cli.utils import format_duration


@click.command("bench")
@click.argument("file")
@click.option("--runs", "-n", default=3, help="Number of runs (default 3).")
@click.option("--profile", "-p", is_flag=True, help="Run cProfile and show top functions.")
@click.option("--top", default=15, help="Number of top functions to show in profile.")
def command(file, runs, profile, top):
    """Benchmark a Python script's execution time."""
    print_command_header("bench", "Performance benchmarker")

    target = Path(file).resolve()
    if not target.exists():
        error(f"File not found: {target}"); return
    if target.suffix != ".py":
        error("Only .py files supported for benchmarking."); return

    if profile:
        _run_profile(target, top)
    else:
        _run_bench(target, runs)


def _run_bench(target: Path, runs: int):
    """Run a script multiple times and report timing."""
    info(f"Benchmarking: {target.name} ({runs} runs)")
    console.print()

    times = []
    for i in range(runs):
        start = time.perf_counter()
        result = subprocess.run(
            ["python", str(target)],
            capture_output=True, text=True, timeout=60
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)

        status = "[green]OK[/]" if result.returncode == 0 else f"[red]EXIT {result.returncode}[/]"
        console.print(f"  Run {i+1}/{runs}: {format_duration(elapsed)}  {status}")

        if result.returncode != 0 and result.stderr:
            console.print(f"    [red]{result.stderr.strip()[:100]}[/]")

    if times:
        console.print()
        avg = sum(times) / len(times)
        rows = [
            ["Min", format_duration(min(times))],
            ["Max", format_duration(max(times))],
            ["Average", format_duration(avg)],
            ["Total", format_duration(sum(times))],
            ["Runs", str(len(times))],
        ]
        table = make_table(
            f"Benchmark: {target.name}",
            [("Metric", "origin.key"), ("Value", "origin.value")],
            rows,
        )
        console.print(table)
        console.print()


def _run_profile(target: Path, top: int):
    """Profile a script with cProfile and display top functions."""
    info(f"Profiling: {target.name}")
    console.print()

    code = target.read_text(encoding="utf-8")
    pr = cProfile.Profile()

    try:
        pr.enable()
        exec(compile(code, str(target), "exec"), {"__name__": "__main__", "__file__": str(target)})
        pr.disable()
    except SystemExit:
        pr.disable()
    except Exception as e:
        pr.disable()
        error(f"Script error: {e}")
        return

    stream = io.StringIO()
    stats = pstats.Stats(pr, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(top)

    output = stream.getvalue()
    console.print()
    for line in output.splitlines():
        console.print(f"  {line}")
    console.print()
