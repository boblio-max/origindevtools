import os

def fmt(file:str):
    code = ""
    with open(file, "r") as f:
        lines = f.readlines()
    
    lines = code.splitlines()
    indent = 0
    result = []

    for line in lines:
        line = line.strip()

        if line.endswith("}"):
            indent -= 1

        result.append("    " * indent + line)

        if line.endswith("{"):
            indent += 1