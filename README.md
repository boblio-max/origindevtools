# origindevtools

`origin-cli` (v2.1.1) — an interactive developer shell for the Origin language. think of it as a REPL that ate a terminal multiplexer: you get Origin-aware commands plus full passthrough to your normal shell.

## how it actually works

- `origin_cli/main.py` is the shell loop. any line starting with `origin` gets lexed/parsed/dispatched by the bundled `origin_cli/{lexer,parser,interpret}.py` — subcommands include `handle_origin`, `python`, `java`, `ai`, venv management, folder-gen, and MCP tooling. anything else passes straight through to the host shell, so it works as your daily driver terminal.
- `run_origin.py` + `cli.py` are alternate entry points, `mcp.py` wires Model Context Protocol tools, and there's even an `installer.iss` for a Windows installer build.
- `.or` files execute on the installed Origin VM backend.

```bash
pip install -e .
origin-cli
```

## stack

Python 3.8+, setuptools, bundled Origin lexer/parser, MCP. from the `pyproject.toml` description since there was never a README till now — fixed that.
