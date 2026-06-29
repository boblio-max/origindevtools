import subprocess
import shutil
from pathlib import Path


def run_command(cmd, file_path):
    try:
        print(f"Running {file_path}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Error output:")
            print(result.stderr)
    except FileNotFoundError:
        print(f"Error: Command '{cmd[0]}' not found. Please ensure it is installed and in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_java_file(file, action):
    file_path = Path(file).resolve()

    if action == "run":
        java_executable = shutil.which("java")
        if not java_executable:
            print("Java is not installed or not in PATH.")
            return

        if file.endswith(".java"):
            javac_executable = shutil.which("javac")
            if not javac_executable:
                print("Java compiler (javac) not found. Cannot compile .java file.")
                return

            print(f"Compiling {file_path}...")
            compile_result = subprocess.run([javac_executable, str(file_path)], capture_output=True, text=True)
            if compile_result.returncode == 0:
                print("Compilation successful.")
                run_command([java_executable, file_path.stem], file_path.with_suffix(".class"))
            else:
                print("Compilation failed:")
                print(compile_result.stderr)
        elif file.endswith(".class"):
            run_command([java_executable, file_path.stem], file_path)
        else:
            print("Error: Expected .java or .class file.")

    elif action == "compile":
        if not file.endswith(".java"):
            print("Error: Only .java files can be compiled.")
            return

        javac_executable = shutil.which("javac")
        if javac_executable:
            print(f"Compiling {file_path}...")
            result = subprocess.run([javac_executable, str(file_path)], capture_output=True, text=True)
            if result.returncode == 0:
                print("Compilation successful.")
            else:
                print("Compilation failed:")
                print(result.stderr)
        else:
            print("Java compiler (javac) not found.")
