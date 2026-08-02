from .interpret import interpret as _interpret
from .classes import *


class interpret:
    """Backwards-compatible wrapper around :func:`interpret.interpret`."""
    def __init__(self):
        pass
    def generate(self, node):
        _interpret(node)
