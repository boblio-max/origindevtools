"""interpret

Execute an AST node produced by :class:`parser.Parser` by dispatching to the
matching Origin CLI handler module.
"""

import os

from . import ui
from .classes import *
from .folder_gen import run
from .handle_ai import run_ai_chat
from .handle_java import handle_java_file
from .handle_python import handle_python_file
from .handle_origin import handle_origin_file, run_repl
from .install_lang import LANG_MAP, install_lang, uninstall_lang, update_lang
from .install_pkg import install_pkg
from .mcp import give_connectors, list_connectors
from .working_dir import change_working_directory, get_working_directory
from .create_venv import create_venv, init_venv


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_help():
    ui.show_help()


def interpret(node):
    """Execute an AST node by dispatching to the appropriate handler."""
    if isinstance(node, InstallNode):
        if node.type == "install":
            if node.lang.strip().lower() in LANG_MAP:
                install_lang(node.lang)
            else:
                install_pkg(node.lang)
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
        print(ui.banner())

    elif isinstance(node, CompileNode):
        handle_java_file(node.file, "compile")

    elif isinstance(node, VenvNode):
        create_venv(node.name, get_working_directory())

    elif isinstance(node, ActivateNode):
        init_venv(node.name, get_working_directory())

    elif isinstance(node, ChangeDirNode):
        change_working_directory(node.location)

    elif isinstance(node, AINode):
        run_ai_chat(node.model)

    elif isinstance(node, GiveNode):
        give_connectors(node.model, node.connectors)

    elif isinstance(node, ConnectorListNode):
        list_connectors()

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
