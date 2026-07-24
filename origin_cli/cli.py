import random
import csv
import math
import sys
import os
import subprocess
from multiprocessing import Process
from pathlib import Path
from lexer import lex
from classes import *
from parser import Parser
import folder_gen as fg
import install_lang as il
class interpret:
    def __init__(self):
        pass
    def generate(self, node):
        if isinstance(node, InstallNode):
            if node.type == "install":
                il.install_lang(node.lang)
            elif node.type == "uninstall":
                il.uninstall_lang(node.lang)
            elif node.type == "update":
                il.update_lang(node.lang)
        
        elif isinstance(node, FolderNode):
            fg.run(node.structure, node.location)
            
    