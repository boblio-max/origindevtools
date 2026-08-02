"""interpret

Execute an AST node produced by :class:`parser.Parser` by dispatching to the
matching Origin CLI handler module.
"""

import os

from .classes import *
from .folder_gen import run
from .handle_java import handle_java_file
from .handle_python import handle_python_file
from .handle_origin import handle_origin_file, run_repl
from .install_lang import install_lang, uninstall_lang, update_lang
from .working_dir import change_working_directory, get_working_directory
from .create_venv import create_venv, init_venv


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


def show_help():
    print("\nAvailable commands:")
    print("  origin help                                    - Show this help message")
    print("  origin clear                                   - Clear the console")
    print("  origin exit / oe                               - Exit the CLI")
    print("  origin <file>.or                               - Run an Origin file")
    print("  origin <file>.py                               - Run a Python file")
    print("  origin <file>.java                             - Compile and run a Java file")
    print("  origin <file>.class                            - Run a Java class file")
    print("  origin c <file>.java                           - Compile a Java file")
    print("  origin create <file_structure>.otxt <location> - Generates folder structure")
    print("  origin install <language>                      - Install a language")
    print("  origin uninstall <language>                    - Uninstall a language")
    print("  origin update <language>                       - Update a language")
    print("  origin in <location>                           - Change working directory")
    print("  origin venv <venv_name>                        - Creates a python virtual environment")
    print("  origin activate <venv_name>                    - Activate a python virtual environment")
    print("-" * 56)


def interpret(node):
    """Execute an AST node by dispatching to the appropriate handler."""
    if isinstance(node, InstallNode):
        if node.type == "install":
            install_lang(node.lang)
        elif node.type == "uninstall":
            uninstall_lang(node.lang)
        elif node.type == "update":
            update_lang(node.lang)

    elif isinstance(node, FolderNode):
        run(node.structure, node.location)

    elif isinstance(node, HelpNode):
        show_help()

    elif isinstance(node, ClearNode):
        clear_screen()
        print(title)

    elif isinstance(node, CompileNode):
        handle_java_file(node.file, "compile")

    elif isinstance(node, VenvNode):
        create_venv(node.name, get_working_directory())

    elif isinstance(node, ActivateNode):
        init_venv(node.name, get_working_directory())

    elif isinstance(node, ChangeDirNode):
        change_working_directory(node.location)

    elif isinstance(node, RunFileNode):
        if node.file.endswith(".or"):
            handle_origin_file(node.file)
        elif node.file.endswith(".py"):
            handle_python_file(node.file)
        elif node.file.endswith(".java") or node.file.endswith(".class"):
            handle_java_file(node.file, "run")
        else:
            print(f"Error: Unknown file type '{node.file}'")

    elif isinstance(node, ReplNode):
        run_repl()

    elif isinstance(node, ExitNode):
        return  # handled by the CLI loop

    else:
        raise RuntimeError(f"Unknown node type: {type(node)}")
