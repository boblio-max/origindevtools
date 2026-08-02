import os
from .folder_gen import run_from_str
import platform

def get_folder_structure(venv_name: str) -> str:
    return f"""{venv_name}/\n
            packages/\n
            cache/\n
            scripts/\n
                activate.sh\n
                activate.bat\n
                activate.ps1\n
                deactivate.sh\n
                deactivate.bat\n
                activate.ps1\n
            config.toml\n
            installed.json"""

def populate_activate_scripts(venv_name: str):
    with open(os.path.join(venv_name, "scripts", "activate.sh"), "w") as f:
        f.write(f"""#!/bin/sh
        #!/bin/sh

        # Save the old prompt
        export _ORIGIN_OLD_PS1="$PS1"

        # Absolute path to this environment
        ORIGIN_DIR="$(cd "$(dirname "$0")" && pwd)"

        # Set Origin environment
        export ORIGIN_ENV="$ORIGIN_DIR"

        # Update prompt
        export PS1="($(basename "$ORIGIN_DIR")) $PS1"

        echo "Activated Origin environment: $(basename "$ORIGIN_DIR")"
        """)
        
    with open(os.path.join(venv_name, "scripts", "activate.bat"), "w") as f:
        f.write(f"""@echo off
                
        REM Save old prompt
        set "_ORIGIN_OLD_PROMPT=%PROMPT%"

        REM Set Origin environment
        set "ORIGIN_ENV=%~dp0"

        REM Remove trailing backslash
        if "%ORIGIN_ENV:~-1%"=="\" set "ORIGIN_ENV=%ORIGIN_ENV:~0,-1%"

        REM Change prompt
        prompt (%~n0) $P$G

        echo Activated Origin environment: %~n0
                """)
    
    with open(os.path.join(venv_name, "scripts", "activate.ps1"), "w") as f:
        f.write(f"""# Save old prompt
        $global:_ORIGIN_OLD_PROMPT = $function:prompt

        # Set Origin environment
        $global:ORIGIN_ENV = Split-Path -Parent $MyInvocation.MyCommand.Definition

        # Change prompt
        function prompt {{
            "($(Split-Path -Leaf $global:ORIGIN_ENV)) " + & $global:_ORIGIN_OLD_PROMPT
        }}

        Write-Host "Activated Origin environment: $(Split-Path -Leaf $global:ORIGIN_ENV)"
                """)
        
def populate_deactivate_scripts(venv_name: str):
    with open(os.path.join(venv_name, "scripts", "deactivate.sh"), "w") as f:
        f.write(f"""#!/bin/sh
        # Restore old prompt
        export PS1="$_ORIGIN_OLD_PS1"
        unset _ORIGIN_OLD_PS1
        unset ORIGIN_ENV
        echo "Deactivated Origin environment."
        """)
        
    with open(os.path.join(venv_name, "scripts", "deactivate.bat"), "w") as f:
        f.write(f"""@echo off
        REM Restore old prompt
        set "PROMPT=%_ORIGIN_OLD_PROMPT%"
        set "_ORIGIN_OLD_PROMPT="
        set "ORIGIN_ENV="
        echo Deactivated Origin environment.
                """)
    
    with open(os.path.join(venv_name, "scripts", "deactivate.ps1"), "w") as f:
        f.write(f"""# Restore old prompt
        function prompt {{
            & $global:_ORIGIN_OLD_PROMPT
        }}
        $global:_ORIGIN_OLD_PROMPT = $null
        $global:ORIGIN_ENV = $null
        Write-Host "Deactivated Origin environment."
                """)
        
def create_venv(venv_name: str, location: str):
    folder_structure = get_folder_structure(venv_name)
    run_from_str(folder_structure, location)
    
    
def init_venv(venv_name: str, location: str):
    system = platform.system()

    if system in ("Linux", "Darwin"):
        print(f"source {venv_name}/scripts/activate.sh")
    elif system == "Windows":
        import psutil
        parent = psutil.Process(os.getppid()).name().lower()

        if parent in ("powershell.exe", "pwsh.exe"):
            print(f".\\{venv_name}\\scripts\\activate.ps1")
        elif parent == "cmd.exe":
            print(f"{venv_name}\\scripts\\activate.bat")
        else:
            print("Unknown Windows shell. Use one of the following:")
            print(f"PowerShell: .\\{venv_name}\\scripts\\activate.ps1")
            print(f"CMD:        {venv_name}\\scripts\\activate.bat")
    