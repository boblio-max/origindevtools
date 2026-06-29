import os

from .folder_gen import run
from .handle_java import handle_java_file
from .handle_python import handle_python_file
from .handle_origin import handle_origin_file, run_repl

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


def cli():
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
    cli()
