"""
Module to manage and interact with files and directory
"""
from pathlib import Path
import os
import platform
import subprocess

def get_filepaths(data_dir: Path, dir_name: str, file_extension: str) -> list[Path]: 
    """  Function to get all the files in a directory inside the data folder based on the specified file extension

    Args:
        dir_name (str): Name of the directory inside of data folder to get all the files names from 
        file_extension (str): File extension to look for in the directory. Pass file extension without '.'

    Returns:
        list[Path]: List containing all the files inside the given folder
    """  
    dir_path = data_dir/dir_name
    files = list(dir_path.glob(f"*.{file_extension}"))
    return files

def open_file(filename):
    """Function that opens the file specified

    Args:
        filename (_type_): Full path of the file to open
    """    
    current_system = platform.system()
    if current_system == "Windows":
        os.startfile(filename) #type: ignore
    elif current_system == "Darwin":
        subprocess.call(["open","-a", "Visual Studio Code",  str(filename)])
# -------------------------
# ARCHITECTURE FUNCTIONS
# ------------------------- 
def build_dir_tree(path: Path, show_files: bool,  indent:str = "", ignore_suffixes: list = [".egg-info", ".ignore", ".git"]) -> str:
    """Function to generate a tree directory for a given location

    Args:
        path (Path): Parent folder to generate tree from
        show_files (bool): Indicates whether files should be shown on tree or not
        indent (str, optional): Separator for | . Defaults to "".
        ignore_suffixes (list, optional): List of suffixes to ignore. Defaults to [".egg-info", ".ignore", ".git"].

    Returns:
        str: A string containing the directory files/folder tree
    """
    lines = []
    items = sorted(path.iterdir())
    for item in items:
      if item.name == "__pycache__" or item.suffix in ignore_suffixes or item.name.startswith(".") or item.name.endswith("RUNNING_DEMO_ON"):
         continue
      if not show_files and item.is_file():
         continue
      lines.append(f"{indent}|   |- {item.name}")
    
      #if show_files and item.is_dir():
      if item.is_dir():
          subtree = build_dir_tree(item, show_files, indent + "|   ")
          lines.extend(subtree.splitlines())

    return "\n".join(lines)

if __name__ == "__main__":
  root = Path(__file__).resolve().parents[2]
  print(build_dir_tree(root, False))
