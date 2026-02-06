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
  Function that takes a data frame, extracts the earliest and latest dates
  and generates a dataframe with a date for each date in the given range

  Args:
    df (dataframe): Dataframe containing a date column (acq_date as in VIIRS dataframe)

  Returns:
    df (dataframe): Dataframe containing dates for each date between min-max of given data frame, and key = 1
      { date: [....], key: [1,1,1,...] }

  Note: 
    join_key column is later used to join with UK grid
  """
  min_date, max_date = df['acq_date'].min(), df['acq_date'].max()

  dates_covered = pd.date_range(start = f"{datetime.strptime(min_date, "%Y-%m-%d").year}-01-01", 
                                end   = f"{datetime.strptime(max_date, "%Y-%m-%d").year}-12-31",
                                freq  = "D")
  dates_df = pd.DataFrame({'date': dates_covered})
  dates_df['join_key'] = 1
  return dates_df
