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

if __name__ == "__main__":

    param_file = Path(__file__).parents[1]/"scripts"/"set_parameters.py"
    print(param_file)
    open_file(param_file)