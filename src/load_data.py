from pathlib import Path
import os 
import pandas as pd

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
  
def to_load_viirs(files: list[str], year_load: list[int] | None = None) -> list[Path]:
  """
  Function to select the VIIRS files to load from GoogleDrive storage
  - It filters the list of files to a given year (if specified)

  Args:
    files (list): List of strings containing a full file path for each of the files to load
    year_load (int): An integer representing a year to load the data - If not provided, the default with load all data

  Returns:
    A list of paths
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

def load_viirs(paths_to_load: list[Path]) -> dict[pd.DataFrame]:
  """
  Function to load the VIIRS data
  It loads NOAA-20 and SNPP separately, and then takes the difference of SNPP - NOAA-20 
  This means lon-lat-date values from SNPP take priority and values not in SNPP but in NOAA-20 are added to the 
  final data frame

  Args:
    paths_to_load: List of Path objects to load 

  Returns:
    dictionary containing both data frames from both used products 

  """
  viirs_noaa = []
  viirs_snpp = []

  for p in paths_to_load:
    if "snpp" in p.name:
      df_in_v = pd.read_csv(p)
      viirs_snpp.append(df_in_v)
    else:
      df_in_n = pd.read_csv(p)
      viirs_noaa.append(df_in_n)

  df_viirs = pd.concat(viirs_snpp, ignore_index=True)
  df_noaa = pd.concat(viirs_noaa,ignore_index=True)
  return {'snpp': df_viirs, 'noaa': df_noaa}