import os
from folder_tool import folder_tool
from fmt import fmt

print(".OR Dev Tools")

logs = []

def comp(com: str):
    return com.split()

def printLogs():
    for log in logs:
        print(f" - {log}")
    if not logs:
        print("No logs available.")

def add_logs(log:str):
    logs.append(log)
def helpMe(error=None):
    if error:
        logs.append(error)
    print(".OR Dev Tools")
    print("Commands:")
    print(" - origin create <template>")
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
            
        if commands[1] == "create":
            types = "folder"
            if len(commands) > 2:
                comm = " ".join(commands[2:])
            else:
                helpMe("Missing folder template name")
                return "/"
        elif commands[1] == "help":
            helpMe()
        elif commands[1] == "fmt":
            types = "fmt"
            if len(commands) > 2:
                comm = " ".join(commands[2:])
            else:
                helpMe("Missing folder template name")
                return "/"
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
    if types == "fmt":
        fmt(com_val)
    elif types != "None":
        helpMe("NoToolFound")
        
    return True


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

