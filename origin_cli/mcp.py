"""mcp

Connector registry and the built-in Origin MCP.

The Origin MCP gives a model pure control over the system it is running on
(shell commands, files, directories, environment). External MCP servers can be
linked later; for now the registry only ships the built-in ``origin``
connector.

Attachments live in ``~/.origin/connectors.json``:

    {
      "connectors": {
        "origin": {"type": "builtin"}
      },
      "given": {
        "llama3.2": ["origin"]
      }
    }

``origin give <model> <connector>`` writes to the ``given`` map so that
``origin run <model>`` exposes the connector's tools to the model.
"""

import json
import os
import platform
import shutil
import subprocess

from . import ui

REGISTRY_DIR = os.path.join(os.path.expanduser("~"), ".origin")

ORIGIN_CONNECTOR_NAME = "origin"

PRESET_CONNECTORS = {
    ORIGIN_CONNECTOR_NAME: {
        "type": "builtin",
        "description": "Pure control over the running system",
    },
}


def _registry_path():
    override = os.environ.get("ORIGIN_CONNECTORS_FILE")
    if override:
        return override
    return os.path.join(REGISTRY_DIR, "connectors.json")


def load_registry():
    """Load the connector registry, seeding the built-in Origin MCP on first run."""
    path = _registry_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        data = {"connectors": dict(PRESET_CONNECTORS), "given": {}}
        save_registry(data)
        return data
    except (json.JSONDecodeError, OSError):
        return {"connectors": {}, "given": {}}


def save_registry(data):
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    with open(_registry_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def connectors_for(model):
    """Return the list of connector configs attached to ``model``."""
    data = load_registry()
    names = data.get("given", {}).get(model, [])
    known = data.get("connectors", {})
    result = []
    for name in names:
        cfg = known.get(name)
        if cfg:
            result.append(dict(cfg, name=name))
        else:
            print(ui.warn(f"Connector '{name}' is given to '{model}' but is not defined."))
    return result


def give_connectors(model, connectors):
    """Attach ``connectors`` to ``model``, or list current attachments."""
    data = load_registry()
    known = data.get("connectors", {})

    if not connectors:
        current = data.get("given", {}).get(model, [])
        if current:
            print(ui.muted(f"'{model}' has access to: {', '.join(current)}"))
        else:
            print(ui.muted(f"'{model}' has no connectors. Use: origin give {model} <connector>"))
        return

    missing = [c for c in connectors if c not in known]
    if missing:
        print(ui.error(f"Unknown connector(s): {', '.join(missing)}"))
        if known:
            print(ui.muted(f"Defined connectors: {', '.join(sorted(known))}"))
        return

    given = data.setdefault("given", {})
    current = given.get(model, [])
    added = [c for c in connectors if c not in current]
    given[model] = current + added
    save_registry(data)
    if added:
        print(ui.success(f"Gave '{model}' access to: {', '.join(added)}"))
    else:
        print(ui.dim(f"'{model}' already had access to all of those connectors."))


def list_connectors():
    """Print the connectors defined in the registry."""
    data = load_registry()
    known = data.get("connectors", {})
    if not known:
        print(ui.muted("No connectors defined."))
        return
    print(ui.bold("Defined connectors:"))
    for name, cfg in sorted(known.items()):
        desc = cfg.get("description", "")
        print(f"  {ui.accent(name, bold=True)}  {ui.muted(desc)}")


def start_connectors(model):
    """Start the providers for the connectors attached to ``model``."""
    providers = []
    for cfg in connectors_for(model):
        ctype = cfg.get("type")
        if ctype == "builtin":
            providers.append(OriginMCP(cfg["name"]))
        else:
            print(ui.warn(
                f"Connector '{cfg['name']}' uses unsupported type '{ctype}'. "
                "Linking external MCP servers is not supported yet."
            ))
    return providers


class OriginMCP:
    """Built-in connector exposing pure control over the running system."""

    def __init__(self, name=ORIGIN_CONNECTOR_NAME):
        self.name = name
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Run a shell command on the host system and return its stdout, stderr and exit code.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The shell command to execute."},
                            "cwd": {"type": "string", "description": "Working directory for the command."},
                            "timeout": {"type": "integer", "description": "Timeout in seconds (default 120)."},
                        },
                        "required": ["command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "List the entries of a directory with type and size.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory to list (default current directory)."},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a text file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path of the file to read."},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Overwrite a text file, creating parent directories if needed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path of the file to write."},
                            "content": {"type": "string", "description": "Full content to write."},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "append_file",
                    "description": "Append text to the end of a file, creating it if missing.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path of the file to append to."},
                            "content": {"type": "string", "description": "Text to append."},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_dir",
                    "description": "Create a directory (and any missing parents).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory to create."},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file (asks for confirmation first).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path of the file to delete."},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_dir",
                    "description": "Recursively delete a directory (asks for confirmation first).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory to delete."},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cwd",
                    "description": "Return the current working directory of the CLI.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_env",
                    "description": "Return the value of an environment variable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Environment variable name."},
                        },
                        "required": ["key"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_env",
                    "description": "List the names of all environment variables.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "system_info",
                    "description": "Return basic information about the host system.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]
        self.tool_names = {t["function"]["name"] for t in self.tools}

    def call_tool(self, name, arguments):
        handler = getattr(self, "_" + name, None)
        if handler is None:
            return json.dumps({"error": f"Unknown tool '{name}'"})
        try:
            return json.dumps(handler(arguments or {}), indent=2)
        except Exception as e:
            return json.dumps({"error": f"{type(e).__name__}: {e}"})

    def close(self):
        pass

    def _confirm(self, message):
        try:
            answer = input(ui.warn(f"{message} [y/N] ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        return answer in ("y", "yes")

    def _run_command(self, arguments):
        command = arguments.get("command")
        if not command or not isinstance(command, str):
            return {"error": "Missing 'command' argument"}
        cwd = arguments.get("cwd")
        timeout = arguments.get("timeout") or 120
        print(ui.dim(f"    $ {command}"))
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=timeout,
                cwd=cwd or None,
            )
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout}s"}
        for line in (result.stdout or "").splitlines():
            print(ui.muted("    " + line))
        for line in (result.stderr or "").splitlines():
            print(ui.warn("    " + line))
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def _list_dir(self, arguments):
        path = arguments.get("path") or "."
        entries = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            if os.path.isdir(full):
                entries.append({"name": name, "type": "dir"})
            else:
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = None
                entries.append({"name": name, "type": "file", "size": size})
        return {"path": os.path.abspath(path), "entries": entries}

    def _read_file(self, arguments):
        path = arguments.get("path")
        if not path:
            return {"error": "Missing 'path' argument"}
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"path": os.path.abspath(path), "lines": len(content.splitlines()), "content": content}

    def _write_file(self, arguments):
        path = arguments.get("path")
        content = arguments.get("content") or ""
        if not path:
            return {"error": "Missing 'path' argument"}
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        return {"path": os.path.abspath(path), "written": len(content), "status": "ok"}

    def _append_file(self, arguments):
        path = arguments.get("path")
        content = arguments.get("content") or ""
        if not path:
            return {"error": "Missing 'path' argument"}
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="") as f:
            f.write(content)
        return {"path": os.path.abspath(path), "appended": len(content), "status": "ok"}

    def _create_dir(self, arguments):
        path = arguments.get("path")
        if not path:
            return {"error": "Missing 'path' argument"}
        os.makedirs(path, exist_ok=True)
        return {"path": os.path.abspath(path), "status": "ok"}

    def _delete_file(self, arguments):
        path = arguments.get("path")
        if not path:
            return {"error": "Missing 'path' argument"}
        if not self._confirm(f"Delete file '{path}'?"):
            return {"path": os.path.abspath(path), "status": "cancelled"}
        os.remove(path)
        return {"path": os.path.abspath(path), "status": "deleted"}

    def _delete_dir(self, arguments):
        path = arguments.get("path")
        if not path:
            return {"error": "Missing 'path' argument"}
        if not self._confirm(f"Recursively delete directory '{path}'?"):
            return {"path": os.path.abspath(path), "status": "cancelled"}
        shutil.rmtree(path)
        return {"path": os.path.abspath(path), "status": "deleted"}

    def _get_cwd(self, arguments):
        return {"cwd": os.getcwd()}

    def _get_env(self, arguments):
        key = arguments.get("key")
        if not key:
            return {"error": "Missing 'key' argument"}
        return {"key": key, "value": os.environ.get(key)}

    def _list_env(self, arguments):
        return {"names": sorted(os.environ.keys())}

    def _system_info(self, arguments):
        return {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "hostname": platform.node(),
        }
