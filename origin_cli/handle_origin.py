import os
import subprocess
import shutil
from pathlib import Path

from .handle_java import run_command


def handle_origin_file(file):
    if not file.endswith(".or"):
        print("Error: Mismatch file type. Expected .or file.")
        return

    origin_executable = shutil.which("origin")
    if origin_executable:
        file_path = Path(file).resolve()
        cmd = ["origin", str(file_path)]
        if os.name == 'nt':
            cmd = ["cmd", "/c"] + cmd
        run_command(cmd, file_path)
    else:
        print("Origin is not installed or not in PATH. Please install Origin to run .or files.")
        print("Visit https://www.docs-origin.onrender.com/download.html to download Origin.")


def run_repl():
    init_msg = """
    Welcome to the Origin Interactive Shell!
    Type 'exit' or 'quit' to log off.

    """
    print(init_msg)

    code = []
    while True:
        try:
            line = input("origin >>> ")
            if line.lower() in ["exit", "quit"]:
                break
            else:
                code.append(line)
                origin_repl_executable = shutil.which("origin")
                if origin_repl_executable:
                    result = subprocess.run([origin_repl_executable, str()], capture_output=True, text=True)
                    if result.returncode == 0:
                        print(code)
                    else:
                        print(result.stderr)
        except:
            break
