import os


def fmt(file: str):
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    indent = 0
    result = []

    for raw in lines:
        line = raw.strip()

        if line.endswith("}"):
            indent = max(indent - 1, 0)

        result.append(("    " * indent) + line)

        if line.endswith("{"):
            indent += 1

    out = "\n".join(result) + ("\n" if text.endswith("\n") else "")

    with open(file, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"{file} formatted successfully")