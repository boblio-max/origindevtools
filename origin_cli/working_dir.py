import os

def change_working_directory(location: str) -> None:
    try:
        os.chdir(location)
        print(f"Changed working directory to: {os.getcwd()}")
    except Exception as e:
        print(f"Error changing directory: {e}")

def get_working_directory() -> str:
    return os.getcwd()