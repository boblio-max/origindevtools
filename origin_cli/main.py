import os
import subprocess
from pathlib import Path
import shutil
import webbrowser

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
def run_or(file):
    try:
        if file.endswith(".or"):
            if shutil.which("origin"):
                file_path = Path(file).resolve()
                print(f"Running {file_path}...")
                result = subprocess.run(
                    ["cmd", "/c", "origin", file_path],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
            else:
                print("Origin is not installed or not in PATH. Please install Origin to run .or files (From the Website).")
                yn = input("Open Origin's Website...")
                if yn.lower() in ["y", "yes"]:
                    print("Opening docs-origin.onrender.com..")
                    webbrowser.open("https://www.docs-origin.onrender.com/download.html")
                else:
                    pass
        else:
            print("Mismatch file type.")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_python(file):
    try:
        if file.endswith(".py"):
            if shutil.which("python") or shutil.which("python3"):
                file_path = Path(file).resolve()
                print(f"Running {file_path}...")
                result = subprocess.run(
                    ["python", file_path],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
            else:
                print("Python is not installed or not in PATH. Please install Python to run .py files (From the Website).")
                yn = input("Open Python's Website...")
                if yn.lower() in ["y", "yes"]:
                    print("Opening python.org..")
                    webbrowser.open("https://www.python.org/downloads/")
                else:
                    pass
        else:
            print("Mismatch file type.")
    except Exception as e:
        print(f"An error occurred: {e}")
def run_java(file, type):
    try:
        if file.endswith(".java"):
            if shutil.which("java"):
                file_path = Path(file).resolve()
                print(f"Running {file_path}...")
                result = subprocess.run(
                    ["java", file_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    class_file = file_path.with_suffix('.class')
                    run_result = subprocess.run(
                        ["java", class_file.stem],
                        capture_output=True,
                        text=True
                    )
                    print(run_result.stdout)
                else:
                    print(result.stderr)
            else:
                print("Java is not installed or not in PATH. Please install Java to run .java files (From the Website).")
                yn = input("Open Java's Website...")
                if yn.lower() in ["y", "yes"]:
                    print("Opening java.com..")
                    webbrowser.open("https://www.java.com/en/download/")
                else:
                    pass
        elif file.endswith(".class"):
            if shutil.which("java"):
                file_path = Path(file).resolve()
                print(f"Running {file_path}...")
                result = subprocess.run(
                    ["javac", file_path.stem],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
            else:
                print("Java is not installed or not in PATH. Please install Java to run .class files (From the Website).")
                yn = input("Open Java's Website...")
                if yn.lower() in ["y", "yes"]:
                    print("Opening java.com..")
                    webbrowser.open("https://www.java.com/en/download/")
                else:
                    pass
        else:
            print("Mismatch file type.")
    except Exception as e:
        print(f"An error occurred: {e}")
                

def compile_java(file):
    try:
        if file.endswith(".java"):
            if shutil.which("javac"):
                file_path = Path(file).resolve()
                print(f"Compiling {file_path}...")
                result = subprocess.run(
                    ["javac", file_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("Compilation successful.")
                else:
                    print(result.stderr)
            else:
                print("Java compiler is not installed or not in PATH. Please install Java to compile .java files (From the Website).")
                yn = input("Open Java's Website...")
                if yn.lower() in ["y", "yes"]:
                    print("Opening java.com..")
                    webbrowser.open("https://www.java.com/en/download/")
                else:
                    pass
        else:
            print("Mismatch file type.")
    except Exception as e:
        print(f"An error occurred: {e}")

def install_language(language, version=None):
    if language == "python":
        if version == None:
            result = subprocess.run(
                ["uv", "python", "install", "3"],
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ["uv", "python", "install", version],
                capture_output=True,
                text=True
            )
if __name__ == "__main__":
    print(title)
    print("Welcome to the Origin CLI!")
    running = True
    while running:
        option = input("> ")
        option_parse = option.split(" ")
        if option_parse[0] == "origin":
            try:
                if option_parse[1] == "help":
                    print("Available commands:")
                    print("origin help - Show this help message")
                    print("origin exit - Exit the CLI")
                    print("origin clear - Clear the console")

                elif option_parse[1].endswith(".or"):
                    run_or(option_parse[1])
                
                elif option_parse[1].endswith(".py"):
                    run_python(option_parse[1])
                
                elif option_parse[1].endswith(".java"):
                    run_java(option_parse[1], "o")
                
                elif option_parse[2].endswith(".class"):
                    run_java(option_parse[1], "c")

                elif option_parse[2].endswith(".java") and option_parse[1] == "c":
                    compile_java(option_parse[2])
            
                # !!!
                elif "install" in option_parse[1] and "python" in option_parse[2]:
                    try:
                        install_language("python", option_parse[3])
                    except:
                        install_language("python")
                
                elif option_parse[1] == "exit":
                    print("Exiting...")
                    running = False
                elif option_parse[1] == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
            except IndexError:
                print(f"Unknown command: {option_parse[1]}")