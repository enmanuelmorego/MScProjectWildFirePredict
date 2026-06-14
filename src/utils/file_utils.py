"""
Module to manage and interact with files and directory
"""
from pathlib import Path
import os
import platform
import subprocess
import re
import pandas as pd

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
# WRITER UTILS
# -------------------------
def write_df_to_csv(df_in: pd.DataFrame, file_path: Path, fname: str)-> None:
    """ Writes a dataframe to disk as a csv file

    Args:
        df_in (pd.DataFrame): Dataframe to write
        file_path (Path): Directory where the file will be written
        fname (str): Output file name
    """
    if not fname.endswith(".csv"):
        fname = f"{fname}.csv"
    write_to = file_path/fname
    df_in.to_csv(write_to, index = False)

# -------------------------
# SENTINEL SPECIFIC UTILS
# -------------------------
def fetch_max_batch_num(available_sentinel_files: list[Path])-> int:
    """Takes a list of available npz files in disk and fetches the max batch number of the files
    If there is no files available, then the function returns 1 to be used as the first batch, 
    Else, +1 is added to the latest existing batch to avoid duplication of batches

    Args:
        available_sentinel_files (list[Path]): Availble npz files in disk 

    Returns:
        int: Integer representing the current max batch number 
    """
    max_batch = 0
    for f in available_sentinel_files:
        batch_str = re.search(r"[B]\d{3}", str(f)).group() # type: ignore
        batch_int = int(batch_str[1:])
        if batch_int > max_batch:
            max_batch = batch_int
    max_batch = int(max_batch) + 1
    return max_batch 

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
