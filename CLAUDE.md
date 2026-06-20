# origindevtools

origindevtools is the `origin` CLI — a professional developer toolkit for the Origin language and general Python projects. It is a Click-based CLI (entry point `origin`) that provides project scaffolding (`origin create`), formatting (`origin fmt`), linting (`origin lint`), file watching (`origin watch`), a REPL, dependency management, a test runner, snippet management, diffs, venv management, git shortcuts, benchmarking, docs generation, migration, config, and plugin support. Distributed as the `origin-devtools` Python package.

## Build / Test / Lint Commands

- Install: `pip install -e .` (uses `pyproject.toml`; pulls `click`, `rich`, `watchdog`, `pyyaml`)
- Build: `python -m build` (produces wheel + sdist)
- Test: `pip install -e ".[dev]" && pytest`
- Lint: not configured (the CLI itself provides `origin lint .`)
- Dev / run: `origin --help`, `origin create standard --path ./my-project`, `origin fmt .`, `origin test`

## Code Style Rules

- Language/version: Python 3.9+ (per `pyproject.toml` classifiers; tested on 3.9–3.13)
- Paradigm: Click-command tree under `origin_cli.main:cli`; subcommands are organized by domain
- Types: type hints on public APIs; standard library typing
- Formatting: PEP 8 (no formatter configured for the toolkit itself, even though it ships a formatter command)
- Imports / module style: `origin_cli` package; plugin discovery via `[project.entry-points."origin_cli.plugins"]`
- Dependencies: `click`, `rich`, `watchdog`, `pyyaml`; dev extras: `pytest`, `pytest-cov`

## Verification Criteria

Before claiming any task done, Claude MUST:
1. Run `pip install -e .` and confirm it succeeds in a clean venv.
2. Run `origin --help` and confirm the CLI lists the documented subcommands.
3. Run `pytest` (after `pip install -e ".[dev]"`) and confirm the test suite passes.
4. Report the exact commands run and their outcomes in the final message.
