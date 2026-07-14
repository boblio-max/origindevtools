import shutil
from pathlib import Path

from .handle_java import run_command


def handle_python_file(file):
    if not file.endswith(".py"):
        print("Error: Mismatch file type. Expected .py file.")
        return

    python_executable = shutil.which("python") or shutil.which("python3")
    if python_executable:
        file_path = Path(file).resolve()
        run_command([python_executable, str(file_path)], file_path)
    else:
        print("Python is not installed or not in PATH. Please install Python to run .py files.")
        print("Visit https://www.python.org/downloads/ to download Python.")
