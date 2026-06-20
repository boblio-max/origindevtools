import os
import subprocess
from pathlib import Path
import shutil
import webbrowser
import sys
import os
import sys
from pathlib import Path
from origin.lexer import lex
from origin.parser import Parser
from origin.interpreter import Interpreter
from origin.errors import report_error, translate_python_error
from folder_gen import run

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

title = """
========================================================
 ▄██████▄     ▄████████  ▄█    ▄██████▄    ▄█   ███▄▄▄▄
███    ███   ███    ███ ███  ███      ███ ███  ███▀▀▀██▄
███    ███   ███    ███ ███▌ ███      █▀  ███▌ ███   ███
███    ███  ▄███▄▄▄▄██▀ ███▌ ███          ███▌ ███   ███
███    ███ ▀▀███▀▀▀▀▀   ███▌ ███  ▀██████ ███▌ ███   ███
███    ███ ▀███████████ ███  ███      ███ ███  ███   ███
███    ███   ███    ███ ███  ███      ███ ███  ███   ███
 ▀██████▀    ▀█     █▀   █▀   ▀████████▀  █▀    ▀█   █▀
========================================================
"""

def run_command(cmd, file_path):
    try:
        print(f"Running {file_path}...")
        # Use shell=True for 'origin' as it might be a batch file/cmd on Windows
        # But for general use, we'll try direct execution first
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False # We want to handle return codes manually for better output
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

def handle_origin_file(file):
    if not file.endswith(".or"):
        print("Error: Mismatch file type. Expected .or file.")
        return

    origin_executable = shutil.which("origin")
    if origin_executable:
        file_path = Path(file).resolve()
        # The original code used ["cmd", "/c", "origin", file_path]
        # We'll use a safer approach but keep Windows compatibility in mind
        cmd = ["origin", str(file_path)]
        if os.name == 'nt':
            cmd = ["cmd", "/c"] + cmd
        run_command(cmd, file_path)
    else:
        print("Origin is not installed or not in PATH. Please install Origin to run .or files.")
        print("Visit https://www.docs-origin.onrender.com/download.html to download Origin.")

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

def run_origin(code):
    code_lines = code

    try:
        # 1. Lexical Analysis
        tokens = lex(code_lines)
        
        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.program()
        
        # 3. Code Generation
        interp = Interpreter()
        generated_python = interp.generate(ast)
        
        # 4. Execution
        # We store the runtime line in a dictionary that will be shared with the exec globals
        # so it's accessible everywhere.
        runtime_globals = {
            "random": random,
            "math": math,
            "__name__": "__main__",
            "_execute_set_pin": _execute_set_pin,
            "_execute_i2c_read": _execute_i2c_read,
            "_execute_i2c_write": _execute_i2c_write,
            "_origin_runtime_line": 0,  # Default
        }

            
        try:
            exec(generated_python, runtime_globals)
        except Exception as e:
            # Smart Error Handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Get the line number from the runtime globals
            line_num = runtime_globals.get("_origin_runtime_line", 0)
            
            # Translate the error message
            friendly_msg = translate_python_error(exc_type, exc_value)
            
            # Report the error beautifully
            report_error(abs_file_path, friendly_msg, line_num)
            sys.exit(1)
        

    except SyntaxError as se:
        # Lexer or Parser error
        print(f"\n[Syntax Error] {se}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error] {e}")
        sys.exit(1)
        
def run_repl():
    init_msg="""
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
                        run_origin(code)
                    else:
                        print(result.stderr)
        except:
            break

def handle_folder_gen(file_with_structure, location):
    run(file_with_structure, location)
    
def show_help():
    print("\nAvailable commands:")
    print("  origin help                                    - Show this help message")
    print("  origin clear                                   - Clear the console")
    print("  origin exit                                    - Exit the CLI")
    print("  origin <file>.or                               - Run an Origin file")
    print("  origin <file>.py                               - Run a Python file")
    print("  origin <file>.java                             - Compile and run a Java file")
    print("  origin <file>.class                            - Run a Java class file")
    print("  origin c <file>.java                           - Compile a Java file")
    print("  origin create <file_structure>.otxt <location> - Generates folder structure")
    print("-" * 56)


def main():
    clear_screen()
    print(title)
    print("Welcome to the Origin Interactive CLI!")
    print("Type 'origin help' for a list of commands.")

    running = True
    while running:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            if parts[0] != "origin":
                print(f"Unknown command prefix. Did you mean 'origin {user_input}'?")
                continue
            
            if len(parts) < 2:
                run_repl()
                continue

            cmd_or_file = parts[1]

            # Command: help
            if cmd_or_file == "help":
                show_help()
            
            # Command: exit
            elif cmd_or_file == "exit":
                print("Exiting...")
                running = False
            
            # Command: clear
            elif cmd_or_file == "clear":
                clear_screen()
                print(title)

            # Command: compile (origin c <file>.java)
            elif cmd_or_file == "c":
                if len(parts) < 3:
                    print("Error: Please specify a .java file to compile.")
                else:
                    handle_java_file(parts[2], "compile")

            # File execution based on extension
            elif cmd_or_file.endswith(".or"):
                handle_origin_file(cmd_or_file)
            
            elif cmd_or_file.endswith(".py"):
                handle_python_file(cmd_or_file)
            
            elif cmd_or_file.endswith(".java"):
                handle_java_file(cmd_or_file, "run")
            
            elif cmd_or_file.endswith(".class"):
                handle_java_file(cmd_or_file, "run")

            elif cmd_or_file == "create":
                if len(parts) < 4:
                    print("Error: Please use the format: origin <file_with_structure>.otxt <location>")
                else:
                    handle_folder_gen(parts[2], parts[3])
            elif parts[0] is None:
                run_repl()
        except EOFError:
            print("\nExiting...")
            break
        except KeyboardInterrupt:
            print("\nType 'origin exit' to quit.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
