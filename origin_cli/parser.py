import textwrap
from lexer import lex, Token
from classes import *


class Parser:
    """Deterministic recursive-descent parser."""
    
    types = {"int": "int", "float": "float", "str": "str", "bool": "bool"}
    
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
    
    def install_stmt(self):
        """Parse an install/uninstall statement."""
        self.eat("ORIGIN", "origin")
        kw = self.eat("KEYWORD")
        lang_token = self.eat("IDENT")
        return InstallNode(lang_token.value, kw.value)