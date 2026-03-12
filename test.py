import sys

def format_code(code):
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

    return "\n".join(result)


def main():
    file = input()

    with open(file) as f:
        code = f.read()

    formatted = format_code(code)

    with open(file, "w") as f:
        f.write(formatted)


if __name__ == "__main__":
    main()
    