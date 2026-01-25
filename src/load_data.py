from pathlib import Path

def get_filepaths(working_dir: str, dir_name: str) -> list[str]: 
  """
  Function to get all the files in a directory inside the data folder

  Args: 
    working_dir (str): String containing the current working directory for the project
    dir_name (str): Name of the directory inside of data folder to get all the files names from 

  Returns: List containing all the files inside the given folder
  """
  dir_path = Path(working_dir)/'data'/dir_name
  files = list(dir_path.iterdir())
  return files
  
def to_load_viirs(files: list[str], year_load: list[int] | None = None):
  """
  Function to select the VIIRS files to load from GoogleDrive storage
  - It filters the list of files to a given year (if specified)

  Args:
    files (list): List of strings containing a full file path for each of the files to load
    year_load (int): An integer representing a year to load the data - If not provided, the default with load all data
  """
  if len(year_load) > 0:
    files_out = []
    for year in year_load:
      str_search = str(year)
      files_out.extend([f for f in files if str_search in f.name])
    if not files_out:
      print(f"⚠️ WARNING:\nNo files found for year {str_search}")
    return files_out
  
  return files