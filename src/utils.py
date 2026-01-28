from pathlib import Path
import os

# -------------------------
# GENERAL FUNCTIONS
# -------------------------  
def get_filepaths(dir_name: str) -> list[Path]: 
  """
  Function to get all the files in a directory inside the data folder

  Args: 
    dir_name (str): Name of the directory inside of data folder to get all the files names from 

  Returns: List containing all the files inside the given folder
  """
  dir_path = Path(os.environ['DATA_DIR'])/dir_name
  files = list(dir_path.iterdir())
  return files