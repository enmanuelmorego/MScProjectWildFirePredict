from pathlib import Path
import os
import pandas as pd
from datetime import datetime
from typing import List 
import geopandas as gpd
import json
from matplotlib.figure import Figure
import re

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

def extract_year_range(df: pd.DataFrame) -> pd.DataFrame:
  """
  Generate a daily date range covering full calendar years based on the
  minimum and maximum acquisition dates in the input DataFrame.

  The function identifies the earliest and latest dates in the input data
  and expands the range to include complete calendar years.

  For example:
    - If the minimum date is `2024-04-10` and the maximum date is `2025-10-05`
    - The output date range will span from `2024-01-01` to `2025-12-31`

  A constant `join_key` column is added to facilitate later joins with
  the UK spatial grid.

  Args:
    df (pd.DataFrame):
      Input DataFrame containing an acquisition date column named `date`.

  Returns:
    pd.DataFrame:
      A DataFrame with:
        - `date`: daily dates covering the full-year range
        - `join_key`: constant value (1) used for joining with the UK grid
  """
  min_date, max_date = df['date'].min(), df['date'].max()

  start = pd.Timestamp(year = min_date.year, month =  1, day =  1)
  end   = pd.Timestamp(year = max_date.year, month = 12, day = 31)

  dates_covered = pd.date_range(start = start, 
                                end   = end,
                                freq  = "D")
  dates_df = pd.DataFrame({'date': dates_covered})
  dates_df['join_key'] = 1
  return dates_df

def dfs_metadata(dfs_dict: dict):
  """
  Function to validate the loaded data before combining into the df_model data frame 
  Extracts key relevant information that is useful to ensure the data was loaded as expected
  Saves it to the run report folder in outputs

  Args:
    dfs_dict (dict): A dictionary containing all the data frames to inspect

  Returns:
    dict_out (dict): A dictionary containing data details of each of the processed data frames
  """
  # loop over each item in the dictionary and extract objects
  dict_out = {}
  for name, df in dfs_dict.items():
    # Skip df uk grid as the checks are not relevant for this object 
    if name == 'df_uk_grid':
      continue
    current_dict = {'df_type'  : type(df).__name__,
                    'columns'  : list(df.columns),
                    'date_from': df['date'].min().strftime("%Y-%m-%d"),
                    'date_to'  : df['date'].max().strftime("%Y-%m-%d"),
                    'total_rows': int(df.shape[0])}
    if 'grid_id' in df.columns:
      current_dict['total_grids'] = len(df['grid_id'].unique())
      current_dict['grid_min']    = int(df['grid_id'].min())
      current_dict['grid_max']    = int(df['grid_id'].max())

    dict_out[name] = current_dict

  return dict_out

def save_json(dict_save: dict, obj_name:str, run_id: str) -> None:
  """
  Helper function that saves a simple dictionary as a json file in the outputs folder

  Args:
    - dict_save (dict): Dictionary to save as json file
    - obj_name (str): The string with the file name
    - run_id (str): ID for specific run of project, set at the start of the script

  Returns: 
    None
  """
  path = f"outputs/{run_id}"
  os.makedirs(path, exist_ok = True)
  fout = f"{path}/{run_id}_{obj_name}.json"
  try:
    with open(fout, "w") as f:
      json.dump(dict_save, f, indent = 4)
      print(f"\t✅ Succesfully saved {fout}")
  except IOError as e:
    print(f"❌ ERROR {e}")

def save_plots(plot_obj: Figure, plot_title: str, run_id: str) -> None:
  """
  Helper function that takes a plot and saves them in the outputs folder

  Args:
    - plot_obj (Figure): Figure/Plot to save
    - plot_title (str): Title of the plot to be used as file name as well
    - run_id (str): ID for specific run of project, set at the start of the script

  Returns 
    None
  """
  path = f"outputs/{run_id}"
  os.makedirs(path, exist_ok = True)
  plot_title = re.sub(r"[\n\t]","", plot_title)
  fout = f"{path}/{run_id}_{plot_title}.pdf"
  try:
    plot_obj.savefig(fout, bbox_inches = "tight")
    print(f"\t✅ Succesfully saved {fout}")
  except IOError as e: 
    print(f"❌ ERROR {e}")
  
def split_df_by_year(df: pd.DataFrame) -> dict:
  """
  Function that takes a data frame and splits it into separate dataframes for each year available in the data
  Each data frame is saved on a dictionary where the `key` values are the corresponding years of the data extract
  
  Args:
    - df (dataframe): A dataframe containing a `date` column
  
  Returns:
    - dict: A dictionary containing a each year of the df as keys and the data frames as values
  """
  df_year         = df.copy()
  df_year['year'] = df['date'].dt.strftime("%Y")
  unique_years    = set(df_year['year'])
  out_dict        = dict()
  for y in unique_years:
    df_subset   = df_year[df_year['year'] == y].copy()
    df_subset   = df_subset.drop(columns = ['year'])
    out_dict[y] = df_subset
  return out_dict

def df_to_csv(df: pd.DataFrame, file_name: str, directory: str) -> None:
  """
  Function that takes a dataframe along with the relevant parameters and saves the df as a `csv` 

  Args:
    - df (pd.DataFrame): Dataframe to save as csv
    - file_name(str): A string value containing the name of the file
    - directory (str): Name of the directory to save the file at

  Returns: 
    - None
  """
  os.makedirs(directory, exist_ok = True)
  fout = Path(directory)/file_name
  df.to_csv(fout, index = False)
  print(f"✅ Succesfully saved {fout}")

def available_files_by_year(data_directory: str, file_type: str) -> set:
    """
    Function to get the available data from a given directory containing yearly data.
    It returns a set of years which can be compared with the YEAR input to check whether data download is required or not

    Args:
      - data_directory(str): A string containg the specific data directory of the required data
      - file_type(str): A string containing the file extension that determines the type of files to search for in the directory

    Returns:
      - Set: A set containing the available years
    """
    folder          = Path(os.getenv("DATA_DIR"))/data_directory
    files           = get_filepaths(folder)
    file_extension  = f"{file_type}$"
    available_years = [f for f in files if re.search(file_extension, str(f)) is not None]
    available_years = [int(re.search(r"\d{4}", str(y)).group()) for y in available_years if re.search(r"\d{4}", str(y)) is not None]
    return set(available_years)

if __name__ == "__main__":
  df = pd.DataFrame({'a': [1,2,3,4],
                     'b': [5,6,7,8]})
  df_to_csv(df, 
            'TEST_sampledfirenofire.csv',
            "data/SampledFireNoFire")
            #Path(os.environ.get("DATA_DIR"))/"SampledFireNoFire")