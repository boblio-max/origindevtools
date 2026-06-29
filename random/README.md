# Origin Dev Tools

Professional developer toolkit for the Origin language and beyond.

```
   ____       _       _         ____             _____           _
  / __ \     (_)     (_)       |  _ \           |_   _|         | |
 | |  | |_ __ _  __ _ _ _ __  | | | | _____   __ | | ___   ___ | |___
 | |  | | '__| |/ _` | | '_ \ | | | |/ _ \ \ / / | |/ _ \ / _ \| / __|
 | |__| | |  | | (_| | | | | || |_| |  __/\ V /  | | (_) | (_) | \__ \
  \____/|_|  |_|\__, |_|_| |_||____/ \___| \_/   |_|\___/ \___/|_|___/
                 __/ |
                |___/                                          v2.0.0
```

## Installation

```bash
# Clone and install
git clone https://github.com/your-org/origindevtools.git
cd origindevtools
pip install -e .

# Now use from anywhere
origin --help
```

## Quick Start

```bash
# Scaffold a new project
origin create standard --path ./my-project

# Format your code
origin fmt .

# Lint for issues
origin lint .

# Run tests
origin test

# Quick git workflow
origin git save "initial commit"
```

## Commands

| Command | Description |
|---------|-------------|
| `origin create <template>` | Scaffold projects (8 templates) |
| `origin fmt <path>` | Format .or, .py, .json, .yaml files |
| `origin lint <path>` | Static analysis with severity levels |
| `origin watch <path>` | File watcher with auto-actions |
| `origin repl` | Interactive Origin language REPL |
| `origin deps <action>` | Dependency management (add/remove/sync) |
| `origin test <path>` | Test runner (pytest wrapper) |
| `origin snippet <action>` | Save and manage code snippets |
| `origin diff <f1> <f2>` | Side-by-side diff with highlighting |
| `origin env <action>` | Virtual environment manager |
| `origin git <action>` | Git shortcuts (save, branch, undo) |
| `origin bench <file>` | Benchmark and profile scripts |
| `origin docs <path>` | Generate markdown documentation |
| `origin migrate <action>` | Project migration assistant |
| `origin config <action>` | Configuration management |
| `origin plugin <action>` | Plugin management |

## Project Templates

```bash
origin create --list
```

| Template | Description |
|----------|-------------|
| `tinyCli` | Minimal CLI application |
| `standard` | Standard Python project with tests |
| `web` | Flask web application |
| `api` | REST API with FastAPI |
| `library` | Reusable Python package |
| `fullstack` | Full-stack app (Flask + static frontend) |
| `origin` | Origin language project |
| `monorepo` | Multi-package monorepo |

## Configuration

Create a `.originrc.yml` in your project root:

```yaml
fmt:
  indent: 4
  extensions: [".or", ".py"]

lint:
  severity: warning

watch:
  debounce_ms: 300
  extensions: [".or", ".py"]

general:
  verbose: false
```

Global config at `~/.origin/.originrc.yml` applies to all projects.

## Plugin Development

Third-party plugins can register via entry points:

```toml
# In your plugin's pyproject.toml
[project.entry-points."origin_cli.plugins"]
my_tool = "my_package.module:command"
```

Your command must be a Click command or group:

```python
import click

@click.command("my-tool")
@click.argument("name")
def command(name):
    """My custom tool."""
    click.echo(f"Hello, {name}!")
```

## CI Integration

```bash
# Format check (exits 1 if unformatted)
origin fmt . --check

# Lint (exits 1 on errors)
origin lint . --severity error

# Run tests with coverage
origin test --coverage
```

## License

MIT License. See [LICENSE](LICENSE).
