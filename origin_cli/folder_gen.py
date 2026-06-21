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

    if not file_path.endswith(".otxt"):
        print("Use otxt files instead por favor")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]

    unit = detect_indent_unit(lines)

    stack = [(-1, base_path)]

    for i, raw_line in enumerate(lines):
        name = clean_line(raw_line)
        depth = get_indent_level(raw_line, unit)

        # Determine if this line is a directory
        is_directory = False

        if i + 1 < len(lines):
            next_depth = get_indent_level(lines[i + 1], unit)
            if next_depth > depth:
                is_directory = True

        while stack and stack[-1][0] >= depth:
            stack.pop()

        parent_path = stack[-1][1]
        full_path = os.path.join(parent_path, name)

        if is_directory:
            os.makedirs(full_path, exist_ok=True)
            stack.append((depth, full_path))
            print(f"[DIR]  {full_path}")

        else:
            os.makedirs(parent_path, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                pass

            print(f"[FILE] {full_path}")

def run(file_name: str, location: str):
    create_structure(file_name.strip('"'), location.strip('"'))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <structure.otxt> <location>")
        sys.exit(1)

    run(sys.argv[1], sys.argv[2])