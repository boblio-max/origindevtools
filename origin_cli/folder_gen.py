import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def clean_line(line: str) -> str:
    return (
        line.replace("├──", "")
            .replace("└──", "")
            .replace("│", "")
            .strip()
    )


def get_indent(line: str) -> int:
    """Count leading spaces after stripping box-drawing characters."""
    stripped = line.lstrip("│ ")
    return len(line) - len(stripped)


def get_indent_level(line: str, unit: int) -> int:
    """Convert a leading-space count into a depth using the file's indent unit."""
    return get_indent(line) // unit


def is_dir(name: str) -> bool:
    return name.endswith("/")


def detect_indent_unit(lines: list) -> int:
    """
    Pick the smallest positive indent across all non-empty lines.
    Falls back to 2 spaces if every child line uses the same depth as a parent.
    """
    indents = [get_indent(l) for l in lines if get_indent(l) > 0]
    if not indents:
        return 2
    return min(indents)


def create_structure(file_path: str, base_path: str):
    base_path = os.path.abspath(base_path)
    os.makedirs(base_path, exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    unit = detect_indent_unit(lines)

    # stack stores (depth, full_path)
    stack = [(-1, base_path)]

    for raw_line in lines:
        if not raw_line.strip():
            continue

        name = clean_line(raw_line)
        depth = get_indent_level(raw_line, unit)

        # find correct parent
        while stack and stack[-1][0] >= depth:
            stack.pop()

        parent_path = stack[-1][1]
        full_path = os.path.join(parent_path, name)

        if is_dir(name):
            os.makedirs(full_path, exist_ok=True)
            stack.append((depth, full_path))
            print(f"[DIR]  {full_path}")

        else:
            os.makedirs(parent_path, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                pass
            print(f"[FILE] {full_path}")


def run(file_name: str, location: str):
    create_structure(file_name, location)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <structure.txt> <location>")
        sys.exit(1)

    run(sys.argv[1], sys.argv[2])