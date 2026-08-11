"""handle_ai

Interactive AI chat with local models through Ollama (origin run <model>).

Ensures Ollama is installed and running, pulls the requested model if needed,
attaches any connectors granted with ``origin give`` (the built-in Origin MCP),
and opens an interactive tool-calling chat session.
"""

import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
import urllib.request

from . import ui
from .mcp import start_connectors

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


def _request(method, path, payload=None, stream=False):
    url = OLLAMA_HOST + path
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req, timeout=None if stream else 10)


def _ollama_alive():
    try:
        with _request("GET", "/api/tags") as resp:
            return resp.status == 200
    except Exception:
        return False


def _wait_for_ollama(timeout=30.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _ollama_alive():
            return True
        time.sleep(0.5)
    return False


def _install_ollama():
    if platform.system() == "Windows":
        dest = os.path.join(tempfile.gettempdir(), "OllamaSetup.exe")
        print(ui.dim("Downloading Ollama..."))
        urllib.request.urlretrieve("https://ollama.com/download/OllamaSetup.exe", dest)
        print(ui.dim("Installing Ollama (silent)..."))
        subprocess.run([dest, "/silent"], check=True)
    else:
        print(ui.dim("Running the official Ollama install script..."))
        subprocess.run(["bash", "-c", "curl -fsSL https://ollama.com/install.sh | sh"], check=True)


def ensure_ollama():
    """Make sure the Ollama server is reachable, installing it if necessary."""
    if _ollama_alive():
        return True
    if shutil.which("ollama"):
        print(ui.dim("Starting the Ollama server..."))
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if _wait_for_ollama():
            return True
    try:
        answer = input(ui.warn("Ollama is required to chat with models. Install it now? [y/N] ")).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if answer not in ("y", "yes"):
        return False
    try:
        _install_ollama()
    except Exception as e:
        print(ui.error(f"Could not install Ollama: {e}"))
        print(ui.muted("Download it manually from https://ollama.com/download"))
        return False
    if shutil.which("ollama"):
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return _wait_for_ollama()


def ensure_model(model):
    """Pull ``model`` from Ollama if it is not already installed."""
    try:
        with _request("GET", "/api/tags") as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        data = None
    if data:
        names = {m["name"] for m in data.get("models", [])}
        short = model.split(":")[0]
        if short in {n.split(":")[0] for n in names}:
            return
    print(ui.warn(f"Model '{model}' is not installed. Pulling it..."))
    _pull_model(model)


def _pull_model(model):
    try:
        with _request("POST", "/api/pull", {"model": model, "stream": True}, stream=True) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line:
                    continue
                chunk = json.loads(line)
                status = chunk.get("status", "")
                total = chunk.get("total")
                completed = chunk.get("completed")
                if status == "success":
                    print(ui.success(f"Model '{model}' ready."))
                elif total:
                    pct = completed / total * 100 if total else 0
                    print(ui.dim(f"  {status}: {pct:5.1f}%"), end="\r", flush=True)
                else:
                    print(ui.muted(f"  {status}"), flush=True)
        print()
    except Exception as e:
        print(ui.error(f"Failed to pull model '{model}': {e}"))


def _stream_chat(model, messages, tools):
    """Stream one assistant turn, appending it to ``messages`` and returning tool calls."""
    payload = {"model": model, "messages": messages, "stream": True}
    if tools:
        payload["tools"] = tools
    content = ""
    tool_calls = []
    with _request("POST", "/api/chat", payload, stream=True) as resp:
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            chunk = json.loads(line)
            msg = chunk.get("message") or {}
            delta = msg.get("content") or ""
            if delta:
                content += delta
                print(delta, end="", flush=True)
            for call in msg.get("tool_calls") or []:
                tool_calls.append(call)
            if chunk.get("done"):
                break
    print()
    entry = {"role": "assistant", "content": content}
    if tool_calls:
        entry["tool_calls"] = tool_calls
    messages.append(entry)
    return tool_calls


def _invoke_tool(providers, name, arguments):
    for provider in providers:
        if name in provider.tool_names:
            return provider.call_tool(name, arguments)
    return json.dumps({"error": f"Unknown tool '{name}'"})


def run_ai_chat(model):
    """Interactive tool-calling chat with ``model`` through Ollama."""
    if not ensure_ollama():
        print(ui.error("Ollama is required to chat with AI models."))
        return
    ensure_model(model)

    providers = start_connectors(model)
    tools = []
    for provider in providers:
        tools.extend(provider.tools)
        if provider.tools:
            print(ui.success(f"Connector '{provider.name}' ready ({len(provider.tools)} tools)"))
    if tools:
        print(ui.muted(f"Tool-calling enabled with {len(tools)} tool(s)."))

    print(ui.muted(f"Chatting with {ui.bright(model)} - type /help for commands, /exit to leave."))
    messages = []
    try:
        while True:
            try:
                prompt = input(ui.prompt(model)).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not prompt:
                continue
            if prompt in ("/exit", "/quit"):
                break
            if prompt == "/clear":
                messages.clear()
                print(ui.dim("Conversation context cleared."))
                continue
            if prompt == "/help":
                print(ui.muted("  /exit - leave the chat"))
                print(ui.muted("  /clear - reset the conversation context"))
                continue

            messages.append({"role": "user", "content": prompt})
            while True:
                try:
                    tool_calls = _stream_chat(model, messages, tools)
                except Exception as e:
                    print(ui.error(f"Chat request failed: {e}"))
                    break
                if not tool_calls:
                    break
                for call in tool_calls:
                    name = call["function"]["name"]
                    args = call["function"].get("arguments") or {}
                    print(ui.bright(f"  tool {name}({json.dumps(args)})"))
                    result = _invoke_tool(providers, name, args)
                    messages.append({"role": "tool", "content": result})
    finally:
        for provider in providers:
            provider.close()
