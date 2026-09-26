import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path


def handle_origin_file(file):
    if not file.endswith(".or"):
        print("Error: Mismatch file type. Expected .or file.")
        return

    file_path = Path(file).resolve()
    if not file_path.exists():
        print(f"Error: File '{file}' not found.")
        return

    # Use the bundled `origin` package inside origindevtools/origin/ directly,
    # instead of shelling out to whatever `origin` is on PATH (which recurses).
    # This makes `origin foo.or` run via the local interpreter/VM without needing
    # a separate `origin-or` pip install.
    devtools_root = Path(__file__).resolve().parent.parent
    if str(devtools_root) not in sys.path:
        sys.path.insert(0, str(devtools_root))
    # Shim: origindevtools/origin/* uses flat imports `from classes import *`
    # so alias them to `origin.classes` when loaded as `origin.*` package.
    try:
        import origin.classes as _oc  # noqa: F401
        sys.modules.setdefault("classes", _oc)
        import origin.lexer as _ol  # noqa: F401
        sys.modules.setdefault("lexer", _ol)
        import origin.parser as _op  # noqa: F401
        sys.modules.setdefault("parser", _op)
        import origin.errors as _oe  # noqa: F401
        sys.modules.setdefault("errors", _oe)
        import origin.interpreter as _oi  # noqa: F401
        sys.modules.setdefault("interpreter", _oi)
    except Exception:
        pass

    try:
        from origin.lexer import lex
        from origin.parser import Parser
        from origin.errors import ParseError, report_error, translate_python_error
    except ImportError as e:
        # Fallback: try external `origin` on PATH if bundled import fails
        print(f"[origindevtools] Failed to import bundled origin: {e} - trying external 'origin' on PATH")
        origin_executable = shutil.which("origin")
        if origin_executable:
            from .handle_java import run_command
            cmd = [origin_executable, str(file_path)]
            if os.name == 'nt':
                cmd = ["cmd", "/c"] + cmd
            run_command(cmd, file_path)
        else:
            print("Origin is not installed or not in PATH. Please install Origin to run .or files.")
            print("Visit https://www.docs-origin.onrender.com/download.html to download Origin.")
        return

    # Read and run via the bundled interpreter (mirrors origin/origin/runner.py but without VM dependency)
    try:
        code_lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"[System Error] Could not read '{file_path}': {e}")
        return

    # chdir to file's directory so relative imports / file ops work
    original_cwd = Path.cwd()
    try:
        if file_path.parent:
            os.chdir(file_path.parent)
        try:
            tokens = lex(code_lines)
            parser = Parser(tokens)
            ast = parser.program()

            # Try VM first if bundled origin has bc/ (future), else fall back to interpreter
            try:
                from origin.bc.to_byte import Compiler  # type: ignore
                from origin.bc.svm import sVM  # type: ignore
                compiler = Compiler()
                compiler.compile(ast)
                sVM(compiler.bytecode, compiler.constants).run()
                return
            except ImportError:
                pass
            except Exception as e:
                # VM compile/runtime error -> show and fall back to interpreter for diagnostics
                print(f"[VM Error] {e}")

            # Interpreter path (origin/origin/interpreter.py style)
            import random
            import math
            from origin.interpreter import Interpreter
            # hardware helpers may not exist in devtools bundle - import optionally
            try:
                from origin.interpreter import _execute_set_pin, _execute_i2c_read, _execute_i2c_write
            except ImportError:
                _execute_set_pin = lambda pin, state: print(f"[SIM] Pin {pin} set to {state}")
                _execute_i2c_read = lambda addr, reg, size=1: 0
                _execute_i2c_write = lambda addr, reg, data: None

            interp = Interpreter()
            generated_python = interp.generate(ast)
            runtime_globals = {
                "random": random,
                "math": math,
                "__name__": "__main__",
                "__file__": str(file_path),
                "_execute_set_pin": _execute_set_pin,
                "_execute_i2c_read": _execute_i2c_read,
                "_execute_i2c_write": _execute_i2c_write,
                "_origin_runtime_line": 0,
            }
            exec(generated_python, runtime_globals)
        except ParseError as pe:
            report_error(
                file_path=str(file_path),
                error_message=pe.message,
                line_num=pe.line,
                col_num=pe.col,
                error_type="Syntax Error",
                suggestion=pe.suggestion,
            )
            sys.exit(1)
        except Exception:
            exc_type, exc_value, _ = sys.exc_info()
            error_type, friendly_message, suggestion = translate_python_error(exc_type, exc_value)
            report_error(
                file_path=str(file_path),
                error_message=friendly_message,
                error_type=error_type,
                suggestion=suggestion,
            )
            sys.exit(1)
    except SyntaxError as se:
        print(f"\n[Syntax Error] {se}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error] {e}")
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def run_repl():
    init_msg = """
    Welcome to the Origin Interactive Shell!
    Type 'exit' or 'quit' to log off.

    """
    print(init_msg)

    while True:
        try:
            line = input("origin >>> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        if line.strip().lower() in ["exit", "quit"]:
            break
        if not line.strip():
            continue
        _run_repl_line(line)


def _run_repl_line(line: str) -> None:
    """Execute a single REPL line via the bundled interpreter."""
    devtools_root = Path(__file__).resolve().parent.parent
    if str(devtools_root) not in sys.path:
        sys.path.insert(0, str(devtools_root))
    try:
        import origin.classes as _oc  # noqa: F401
        sys.modules.setdefault("classes", _oc)
        import origin.lexer as _ol  # noqa: F401
        sys.modules.setdefault("lexer", _ol)
        import origin.parser as _op  # noqa: F401
        sys.modules.setdefault("parser", _op)
        import origin.errors as _oe  # noqa: F401
        sys.modules.setdefault("errors", _oe)
        import origin.interpreter as _oi  # noqa: F401
        sys.modules.setdefault("interpreter", _oi)
    except Exception:
        pass
    try:
        from origin.lexer import lex
        from origin.parser import Parser
        from origin.interpreter import Interpreter
        import random
        import math
        try:
            from origin.interpreter import _execute_set_pin, _execute_i2c_read, _execute_i2c_write
        except ImportError:
            _execute_set_pin = lambda pin, state: print(f"[SIM] Pin {pin} set to {state}")
            _execute_i2c_read = lambda addr, reg, size=1: 0
            _execute_i2c_write = lambda addr, reg, data: None
        tokens = lex([line])
        ast = Parser(tokens).program()
        generated_python = Interpreter().generate(ast)
        runtime_globals = {
            "random": random,
            "math": math,
            "__name__": "__main__",
            "_execute_set_pin": _execute_set_pin,
            "_execute_i2c_read": _execute_i2c_read,
            "_execute_i2c_write": _execute_i2c_write,
            "_origin_runtime_line": 0,
        }
        exec(generated_python, runtime_globals)
    except ImportError:
        origin_repl_executable = shutil.which("origin")
        if origin_repl_executable:
            with tempfile.NamedTemporaryFile("w", suffix=".or", delete=False, encoding="utf-8") as tmp:
                tmp.write(line + "\n")
                tmp_path = tmp.name
            try:
                result = subprocess.run(
                    [origin_repl_executable, tmp_path],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    print(result.stdout, end="")
                if result.stderr:
                    print(result.stderr, end="")
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        else:
            print("Origin is not installed or not in PATH. Please install Origin to run .or files.")
    except Exception as e:
        print(f"Error: {e}")
