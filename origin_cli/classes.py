class ASTNode:
    """Abstract base type for AST nodes."""
    def __init__(self, line=None):
        self.line = line

class ProgramNode(ASTNode):
    """Root node holding an ordered list of commands."""
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
    def __repr__(self):
        return f"ProgramNode({self.statements})"

class InstallNode(ASTNode):
    """AST node for install/uninstall/update language commands."""
    def __init__(self, lang, type):
        super().__init__()
        self.lang = lang
        self.type = type
    def __repr__(self):
        return f"InstallNode({self.lang}, {self.type})"

class FolderNode(ASTNode):
    """AST node for folder generation."""
    def __init__(self, structure, location):
        super().__init__()
        self.structure = structure
        self.location = location
    def __repr__(self):
        return f"FolderNode({self.structure}, {self.location})"

class HelpNode(ASTNode):
    """Show the CLI help text."""
    def __repr__(self):
        return "HelpNode()"

class ExitNode(ASTNode):
    """Exit the CLI."""
    def __repr__(self):
        return "ExitNode()"

class ClearNode(ASTNode):
    """Clear the console and redraw the banner."""
    def __repr__(self):
        return "ClearNode()"

class CompileNode(ASTNode):
    """Compile a Java source file (origin c <file>.java)."""
    def __init__(self, file):
        super().__init__()
        self.file = file
    def __repr__(self):
        return f"CompileNode({self.file})"

class VenvNode(ASTNode):
    """Create a virtual environment."""
    def __init__(self, name):
        super().__init__()
        self.name = name
    def __repr__(self):
        return f"VenvNode({self.name})"

class ActivateNode(ASTNode):
    """Activate an existing virtual environment."""
    def __init__(self, name):
        super().__init__()
        self.name = name
    def __repr__(self):
        return f"ActivateNode({self.name})"

class ChangeDirNode(ASTNode):
    """Change the working directory (origin in <location>)."""
    def __init__(self, location):
        super().__init__()
        self.location = location
    def __repr__(self):
        return f"ChangeDirNode({self.location})"

class RunFileNode(ASTNode):
    """Run a source file (.or, .py, .java, .class)."""
    def __init__(self, file):
        super().__init__()
        self.file = file
    def __repr__(self):
        return f"RunFileNode({self.file})"

class ReplNode(ASTNode):
    """Start the interactive Origin shell."""
    def __repr__(self):
        return "ReplNode()"
