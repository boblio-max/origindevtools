"""origin watch - File watcher with auto-actions on change."""

import time
from pathlib import Path

import click

from origin_cli.console import console, success, error, info, warning, print_command_header
from origin_cli.config import load_config


@click.command("watch")
@click.argument("path", default=".")
@click.option("--action", "-a", type=click.Choice(["fmt", "lint", "test", "run"]),
              default="fmt", help="Action to run on file change.")
@click.option("--ext", multiple=True, help="Extensions to watch.")
@click.option("--debounce", type=int, default=None, help="Debounce ms (default 300).")
def command(path, action, ext, debounce):
    """Watch files and auto-run actions on change."""
    print_command_header("watch", "File watcher")

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        error("watchdog not installed. Run: pip install watchdog")
        return

    config = load_config()
    watch_cfg = config.get("watch", {})
    debounce_ms = debounce or watch_cfg.get("debounce_ms", 300)
    extensions = list(ext) if ext else watch_cfg.get("extensions", [".or", ".py"])
    ignore_dirs = set(watch_cfg.get("ignore_dirs", ["__pycache__", ".git", "node_modules"]))

    target = Path(path).resolve()
    if not target.exists():
        error(f"Path not found: {target}"); return

    info(f"Watching: {target}")
    info(f"Extensions: {', '.join(extensions)}")
    info(f"Action: origin {action}")
    info(f"Debounce: {debounce_ms}ms")
    console.print(f"  [origin.dim]Press Ctrl+C to stop[/]\n")

    import subprocess
    last_trigger = 0

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            nonlocal last_trigger
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.suffix not in extensions:
                return
            if any(part in ignore_dirs for part in p.parts):
                return
            now = time.time()
            if (now - last_trigger) < (debounce_ms / 1000):
                return
            last_trigger = now
            console.print(f"  [origin.dim]{time.strftime('%H:%M:%S')}[/] Changed: [origin.path]{p.name}[/]")
            cmd = ["python", "-m", "origin_cli.main", action, str(p)]
            try:
                subprocess.run(cmd, timeout=30)
            except subprocess.TimeoutExpired:
                warning(f"Action timed out for {p.name}")
            except Exception as e:
                error(f"Action failed: {e}")

    observer = Observer()
    observer.schedule(Handler(), str(target), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n")
        info("Watcher stopped.")
    observer.join()
