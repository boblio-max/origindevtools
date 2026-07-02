from classes import InstallNode
from install_lang import install_lang, uninstall_lang


def interpret(node):
    """Execute an AST node by dispatching to the appropriate handler."""
    if isinstance(node, InstallNode):
        if node.type == "install":
            install_lang(node.lang)
        elif node.type == "uninstall":
            uninstall_lang(node.lang)
