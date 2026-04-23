"""YAML-based configuration system for Origin Dev Tools.

Searches for configuration in this priority order:
  1. CLI flags (highest)
  2. .originrc.yml in project root
  3. ~/.originrc.yml global config (lowest)
"""

import os
from pathlib import Path

import yaml

CONFIG_FILENAME = ".originrc.yml"
GLOBAL_CONFIG_DIR = Path.home() / ".origin"
GLOBAL_CONFIG_PATH = GLOBAL_CONFIG_DIR / CONFIG_FILENAME

DEFAULTS = {
    "fmt": {
        "indent": 4,
        "line_length": 100,
        "extensions": [".or", ".py"],
    },
    "lint": {
        "severity": "warning",
        "ignore_rules": [],
        "extensions": [".or", ".py"],
    },
    "watch": {
        "debounce_ms": 300,
        "extensions": [".or", ".py", ".json", ".yaml", ".yml"],
        "ignore_dirs": ["__pycache__", ".git", "node_modules", ".venv", "venv"],
    },
    "create": {
        "default_template": "standard",
        "auto_git_init": True,
        "auto_venv": False,
    },
    "test": {
        "runner": "pytest",
        "coverage": False,
        "verbose": True,
    },
    "snippet": {
        "storage_dir": str(GLOBAL_CONFIG_DIR / "snippets"),
    },
    "env": {
        "default_python": "python",
    },
    "general": {
        "color": True,
        "verbose": False,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts, override wins on conflicts."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def find_project_root() -> Path | None:
    """Walk up from cwd to find the nearest directory containing .originrc.yml or .git."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / CONFIG_FILENAME).exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return None


def load_config() -> dict:
    """Load and merge configuration from all sources.

    Returns:
        Merged configuration dictionary.
    """
    config = DEFAULTS.copy()

    # Layer 1: Global config
    if GLOBAL_CONFIG_PATH.exists():
        try:
            with open(GLOBAL_CONFIG_PATH, "r", encoding="utf-8") as f:
                global_cfg = yaml.safe_load(f) or {}
            config = _deep_merge(config, global_cfg)
        except (yaml.YAMLError, OSError):
            pass  # Silently fall back to defaults

    # Layer 2: Project-local config
    project_root = find_project_root()
    if project_root:
        local_path = project_root / CONFIG_FILENAME
        if local_path.exists():
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    local_cfg = yaml.safe_load(f) or {}
                config = _deep_merge(config, local_cfg)
            except (yaml.YAMLError, OSError):
                pass

    return config


def save_config(config: dict, path: Path | None = None):
    """Save configuration to a YAML file.

    Args:
        config: Configuration dictionary to save.
        path: Target path. Defaults to project root or cwd.
    """
    if path is None:
        project_root = find_project_root()
        path = (project_root or Path.cwd()) / CONFIG_FILENAME

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_config_value(config: dict, dotpath: str, default=None):
    """Get a value from config using dot notation (e.g., 'fmt.indent').

    Args:
        config: Configuration dictionary.
        dotpath: Dot-separated key path.
        default: Default value if key not found.

    Returns:
        The config value, or default.
    """
    keys = dotpath.split(".")
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def set_config_value(config: dict, dotpath: str, value) -> dict:
    """Set a value in config using dot notation.

    Args:
        config: Configuration dictionary (modified in place).
        dotpath: Dot-separated key path.
        value: Value to set.

    Returns:
        The modified config dictionary.
    """
    keys = dotpath.split(".")
    current = config
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return config
