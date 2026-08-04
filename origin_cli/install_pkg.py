import json
import os
import shutil
import tempfile
import time
import urllib.request
import zipfile

from .create_venv import in_venv
from .version import ConstraintType, VersionError, parse_package_spec

PKG_MAP = {
    "calc": "https://github.com/boblio-max/Calculus-origin-lib",
}

def _venv_root():
    env = os.environ.get("ORIGIN_ENV", "")
    if not env:
        return None
    if os.path.basename(env) == "scripts":
        return os.path.dirname(env)
    return env

def _zip_url(repo_or_url: str) -> str:
    repo_or_url = repo_or_url.strip()
    if repo_or_url.endswith(".zip"):
        return repo_or_url
    if "github.com/" in repo_or_url:
        return repo_or_url.rstrip("/") + "/archive/refs/heads/main.zip"
    return repo_or_url

def _resolve(pkg_name: str):
    name = pkg_name.strip().lower()
    if "://" in pkg_name:
        return pkg_name
    return PKG_MAP.get(name)

def _download(url: str, dest: str) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "origin-cli"})
    with urllib.request.urlopen(request) as response, open(dest, "wb") as f:
        shutil.copyfileobj(response, f)

def _top_level_dir(extract_dir: str) -> str:
    dirs = [os.path.join(extract_dir, e) for e in os.listdir(extract_dir)
            if os.path.isdir(os.path.join(extract_dir, e))]
    if len(dirs) == 1:
        return dirs[0]
    return extract_dir

def _record_install(venv_root: str, spec, source: str, pkg_dir: str) -> None:
    installed_path = os.path.join(venv_root, "installed.json")
    data = {}
    if os.path.exists(installed_path):
        try:
            with open(installed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}
    entry = {
        "source": source,
        "path": pkg_dir,
        "installed": time.strftime("%Y-%m-%d"),
        "spec": spec.raw,
    }
    if spec.has_constraint:
        entry["constraint"] = spec.constraint.value
        entry["version"] = str(spec.version)
    data[spec.name.lower()] = entry
    with open(installed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def install_pkg(pkg_spec: str) -> None:
    """Install a GitHub-hosted Origin package into the active virtual environment.

    ``pkg_spec`` may be a plain package name or include a version constraint
    (``name@1.2.3``, ``name>=1.2.0``, ``name<=2.0.0``, ``name^2.1``). Invalid
    constraint syntax is rejected before anything is downloaded.
    """
    if not in_venv():
        print("Error: No Origin virtual environment is active. Run 'origin activate <venv_name>' first.")
        return

    try:
        spec = parse_package_spec(pkg_spec)
    except VersionError as e:
        print(f"Error: {e}")
        return

    source = _resolve(spec.name)
    if not source:
        print(f"Unknown package: '{spec.name}'. No matching GitHub repository found.")
        return

    venv_root = _venv_root()
    packages_dir = os.path.join(venv_root, "packages")
    os.makedirs(packages_dir, exist_ok=True)
    pkg_dir = os.path.join(packages_dir, spec.name.lower())

    url = _zip_url(source)
    print(f"Downloading {url} ...")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "pkg.zip")
            _download(url, zip_path)
            extract_dir = os.path.join(tmp, "extract")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            source_dir = _top_level_dir(extract_dir)
            if os.path.exists(pkg_dir):
                shutil.rmtree(pkg_dir)
            shutil.copytree(source_dir, pkg_dir)
    except Exception as e:
        print(f"Failed to install '{spec.name}': {e}")
        return

    _record_install(venv_root, spec, source, pkg_dir)
    label = spec.raw if spec.has_constraint else spec.name
    print(f"Package '{label}' installed to {pkg_dir}")
