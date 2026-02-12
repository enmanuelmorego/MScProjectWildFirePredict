from pathlib import Path
import os
import pandas as pd
from datetime import datetime
from typing import List 
import geopandas as gpd

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

