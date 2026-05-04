"""
Module to manage and interact with files and directory
"""
from pathlib import Path
import os

def get_filepaths(dir_name: str, file_extension: str) -> list[Path]: 
    """  Function to get all the files in a directory inside the data folder based on the specified file extension

    Args:
        dir_name (str): Name of the directory inside of data folder to get all the files names from 
        file_extension (str): File extension to look for in the directory. Pass file extension without '.'

    Returns:
        list[Path]: List containing all the files inside the given folder
    """  
    dir_path = Path(os.environ['DATA_DIR'])/dir_name
    files = list(dir_path.glob(f"*.{file_extension}"))
    return files