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
for k,v in lang_map:
    code_map[v] = k
    
def handle_code(path_to_file, extension):
    executable = code_map[extension]
    if executable == "g++":
        result = subprocess.run([executable, "-o", str(path_to_file)], capture_output=True, text=True)
        
    else:
        result = subprocess.run([executable, str(path_to_file)], capture_output=True, text=True)
    print(result)
    
handle_code("C:\Users\smile\OneDrive\Documents\GitHub\origindevtools\origin_cli\main.py", ".py")