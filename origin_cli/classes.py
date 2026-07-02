
class ASTNode:
    """Abstract base type for AST nodes."""
    def __init__(self, line=None):
        self.line = line
    
class InstallNode(ASTNode):
    """AST node for install command."""
    def __init__(self, lang, type):
        super().__init__()
        self.lang = lang
        self.type = type
    def __repr__(self):
        return f"InstallNode({self.lang}, {self.type})"