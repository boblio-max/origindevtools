# origin update cli
# origin doctor
# origin version

from pathlib import Path

from . import ui
from .handle_java import handle_java_file
from .handle_python import handle_python_file
from .handle_origin import handle_origin_file
from .lexer import lex
from .parser import Parser
from .classes import ExitNode
from .interpret import interpret, clear_screen


def cli():
    ui.enable_ansi()
    clear_screen()
    print(ui.banner())
    print(ui.status_bar(str(Path.cwd()), ui.active_venv()))

    running = True
    while running:
        try:
            cwd = str(Path.cwd())
            user_input = input(ui.prompt(cwd)).strip()
            if not user_input:
                continue

            tokens = lex([user_input])
            if tokens[0].type != "ORIGIN":
                print(ui.error(f"Unknown command prefix. Did you mean '{user_input}'?"))
                continue

            node = Parser(tokens).command()
            if isinstance(node, ExitNode):
                print(ui.dim("Exiting..."))
                running = False
                continue

            interpret(node)
            print(ui.status_bar(cwd, ui.active_venv()))
        except SyntaxError as e:
            print(ui.error(f"Syntax error: {e}"))
        except EOFError:
            print(ui.dim("\nExiting..."))
            break
        except KeyboardInterrupt:
            print("\n" + ui.muted("Press Ctrl+D or run 'origin exit' to quit."))
        except Exception as e:
            print(ui.error(f"An error occurred: {e}"))


def main():
    import sys
    if len(sys.argv) > 1:
        file_to_run = sys.argv[1]
        if file_to_run.endswith(".py"):
            handle_python_file(file_to_run)
        elif file_to_run.endswith(".java") or file_to_run.endswith(".class"):
            handle_java_file(file_to_run, "run")
        elif file_to_run.endswith(".or"):
            handle_origin_file(file_to_run)
        else:
            print(f"Error: Unknown file type '{file_to_run}'")
    else:
        cli()


if __name__ == "__main__":
    main()
