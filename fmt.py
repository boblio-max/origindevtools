import os

def fmt(file:str):
    lines = ""
    with open(file, "r") as f:
        lines = f.readlines()
    
    print(lines)