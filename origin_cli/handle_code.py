import subprocess

lang_map = {
    "python": ".py",
    "nodejs": ".js",
    "java": ".java",
    "javac": "c .java",
    "origin": ".or",
    "g++": ".cpp",
}
code_map = {}
for k, v in lang_map.items():
    code_map[v] = k

def handle_code(path_to_file, extension):
    if extension not in code_map:
        print(f"Error: Unknown extension '{extension}'")
        return
    executable = code_map[extension]
    if executable == "g++":
        result = subprocess.run([executable, str(path_to_file), "-o", str(path_to_file) + ".out"], capture_output=True, text=True)

    else:
        result = subprocess.run([executable, str(path_to_file)], capture_output=True, text=True)
    print(result)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python handle_code.py <file> <extension>")
    else:
        handle_code(sys.argv[1], sys.argv[2])