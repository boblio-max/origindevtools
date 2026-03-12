import os


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
        try:
            import main
            main.add_logs(f"Failed to find template {com}")
        except Exception:
            pass
