"""parser

Recursive-descent parser for the Origin CLI command language.

Consumes the flat token sequence produced by :func:`lexer.lex` and constructs
an Abstract Syntax Tree (AST) comprised of the node classes in ``classes.py``.
"""

from .lexer import Token
from .classes import *


class Parser:
    """Deterministic recursive-descent parser."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _set_line(self, node, line):
        if node and hasattr(node, '__dict__'):
            node.line = line
        return node

    def current_token(self):
        """Return the next non-whitespace token, skipping WHITESPACE."""
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == "WHITESPACE":
            self.pos += 1
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", "", -1, -1)

    def eat(self, type_=None, value=None):
        """Consume and return the current token when it matches ``type_`` and/or ``value``."""
        tok = self.current_token()
        if type_ is not None and tok.type != type_:
            raise SyntaxError(f"Expected type {type_}, got {tok.type} ({tok.value}) at {tok.line}:{tok.col}")
        if value is not None and tok.value != value:
            raise SyntaxError(f"Expected {value}, got {tok.value} ({tok.type}) at {tok.line}:{tok.col}")
        self.pos += 1
        return tok

    def skip_newlines(self):
        """Skip optional newline tokens."""
        while self.current_token().type == "NEWLINE":
            self.eat("NEWLINE")

    def _arg(self):
        """Consume a single argument token and return its unquoted value."""
        tok = self.current_token()
        if tok.type in ("STRING", "FILE", "PATH", "IDENT"):
            self.pos += 1
            if tok.type == "STRING":
                return tok.value[1:-1]
            return tok.value
        raise SyntaxError(f"Expected an argument, got {tok.type} ({tok.value}) at {tok.line}:{tok.col}")

    def install_stmt(self, kw):
        """Parse an install/uninstall/update statement."""
        lang = self._arg()
        return InstallNode(lang, kw)

    def gen_folder(self):
        """Parse a folder generation statement (origin create <structure> <location>)."""
        structure = self._arg()
        location = self._arg()
        return FolderNode(structure, location)

    def command(self):
        """Parse a single 'origin ...' command line into an AST node."""
        self.skip_newlines()
        line = self.current_token().line
        self.eat("ORIGIN", "origin")

        tok = self.current_token()
        if tok.type in ("NEWLINE", "EOF"):
            node = ReplNode()
        elif tok.type == "KEYWORD":
            kw = tok.value
            self.eat("KEYWORD")
            if kw == "help":
                node = HelpNode()
            elif kw in ("exit", "oe"):
                node = ExitNode()
            elif kw == "clear":
                node = ClearNode()
            elif kw == "c":
                node = CompileNode(self._arg())
            elif kw == "install":
                node = self.install_stmt(kw)
            elif kw == "uninstall":
                node = self.install_stmt(kw)
            elif kw == "update":
                node = self.install_stmt(kw)
            elif kw == "create":
                node = self.gen_folder()
            elif kw == "venv":
                node = VenvNode(self._arg())
            elif kw == "activate":
                node = ActivateNode(self._arg())
            elif kw == "in":
                node = ChangeDirNode(self._arg())
            else:
                raise SyntaxError(f"Unknown command '{kw}' at {tok.line}:{tok.col}")
        elif tok.type == "FILE":
            self.eat("FILE")
            node = RunFileNode(tok.value)
        else:
            raise SyntaxError(f"Unexpected token {tok}")

        return self._set_line(node, line)

    def program(self):
        """Parse an entire block of commands into a ProgramNode."""
        nodes = []
        while self.current_token().type != "EOF":
            nodes.append(self.command())
            self.skip_newlines()
        return ProgramNode(nodes)
