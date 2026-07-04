"""
Module to manage and interact with files and directory
"""
from pathlib import Path
from datetime import date, datetime, timedelta
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
    os.makedirs(file_path, exist_ok = True)
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

def fetch_max_sentinel_batch_date(available_sentinel_files: list[Path], max_batch: int) -> date:
    """Takes a list of available npz files in disk and fetched max_batch value and fetches the max date from the file name
    The date is used to resume GEE requests and avoid requesting data that already exists in disk 

    If there is no files available, then the function returns date(1900, 1, 1) which is then used to send the request of sampled data
    later than this date. 

    To align with fetch_max_batch_num convention, +1 is added to allow filtering to use >= rather than = alone

    The +1 operation from fetch_max_batch_num  is undone by -1 to the value 

    Args:
        available_sentinel_files (list[Path]): Availble npz files in disk 

        max_batch (int): Identified Max batch number on disk 

    Returns:
        date: Date to sample data from (>=)
    """
    # Undo the +1 from fetch_max_batch_num
    max_batch = max_batch - 1
    # Recreate batch string to match search
    max_batch_str = f"B{max_batch:03}"
    max_date = datetime(1900,1,1)
    if available_sentinel_files:
        current_batch = [f for f in available_sentinel_files if re.search(r"B\d{3}", f.stem).group() == max_batch_str] # type: ignore
        batch_max_date = str(current_batch).split("_")[3]
        max_date = datetime.strptime(batch_max_date, "%Y%m%d") + timedelta(days=1)
    return max_date

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
