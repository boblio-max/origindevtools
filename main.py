import os

print(".OR Dev Tools")

logs = []

def comp(com: str):
    return com.split()

def printLogs():
    for log in logs:
        print(f" - {log}")
    if not logs:
        print("No logs available.")

def helpMe(error=None):
    if error:
        logs.append(error)
    print(".OR Dev Tools")
    print("Commands:")
    print(" - origin folder <template>")
    print("   Available templates: tinyCli, standard, web")
    print(" - origin log")
    print(" - origin help")
    print(" - exit / quit")

def match(com: str):
    comm = ""
    types = "None"
    commands = comp(com)
    
    if not commands:
        return "/"
        
    if commands[0] in ["exit", "quit"]:
        return "exit/none"
        
    if commands[0] == "origin":
        if len(commands) < 2:
            helpMe("Incomplete origin command")
            return "/"
            
        if commands[1] == "folder":
            types = "folder"
            if len(commands) > 2:
                comm = " ".join(commands[2:])
            else:
                helpMe("Missing folder template name")
                return "/"
        elif commands[1] == "help":
            helpMe()
        elif commands[1] == "log":
            printLogs()
        else:
            helpMe(f"Unknown origin command: {commands[1]}")
            
    return comm + "/" + types

def orchestration_layer(com: str):
    if com == "/":
        return True
        
    comm_parts = com.split("/")
    if len(comm_parts) < 2:
        return True
        
    com_val = comm_parts[0].strip()
    types = comm_parts[1].strip()
    
    if com_val == "exit" and types == "none":
        return False
        
    if types == "folder":
        folder_tool(com_val)
    elif types != "None":
        helpMe("NoToolFound")
        
    return True

def folder_tool(com: str):
    com = com.strip()
    if not com:
        print("Error: No template specified.")
        return
        
    print(f"Generating folder structure for template: '{com}'...")
    
    if com == "tinyCli":
        with open("cli.py", "w") as file:
            file.write("# Tiny CLI template\n")
        with open("pyproject.toml", "w") as file:
            file.write("[project]\nname = \"tinycli\"\n")
        with open("README.md", "w") as file:
            file.write("# Tiny CLI\n")
        print("-> Created cli.py, pyproject.toml, README.md")
        
    elif com == "standard":
        os.makedirs("tests", exist_ok=True)
        with open("main.py", "w") as file:
            file.write("def main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()\n")
        with open("tests/__init__.py", "w") as file:
            pass
        with open("requirements.txt", "w") as file:
            pass
        with open("README.md", "w") as file:
            file.write("# Standard Project\n")
        print("-> Created tests directory, main.py, requirements.txt, README.md")
        
    elif com == "web":
        os.makedirs("templates", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        with open("app.py", "w") as file:
            file.write("# Web App Main\n")
        with open("requirements.txt", "w") as file:
            file.write("flask\n")
        with open("README.md", "w") as file:
            file.write("# Web Project\n")
        print("-> Created templates and static directories, app.py, requirements.txt, README.md")
        
    else:
        print(f"Unknown template: '{com}'. Available templates: tinyCli, standard, web")
        logs.append(f"Failed to find template {com}")

if __name__ == "__main__":
    while True:
        try:
            dev = input("> ")
            should_continue = orchestration_layer(match(dev))
            if not should_continue:
                break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            logs.append(str(e))
