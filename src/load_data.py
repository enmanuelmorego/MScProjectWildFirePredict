from pathlib import Path
import os 
import pandas as pd
import geopandas as gpd
from config import CRS
import utils as u

# -------------------------
# VIIRS DATA
# -------------------------  
def to_load_viirs(files: list[Path], year_load: list[int] | None = None) -> list[Path]:
  """
  Function to select the VIIRS files to load from GoogleDrive storage
  - It filters the list of files to a given year (if specified)

  Args:
    files (list): List of strings containing a full file path for each of the files to load
    year_load (int): An integer representing a year to load the data - If not provided, the default with load all data

  Returns:
    A list of paths
  """
  if not year_load:
    return files
  
  files_out = []
  for year in year_load:
    str_search = str(year)
    files_out.extend([f for f in files if str_search in f.name])
  if not files_out:
    print(f"⚠️ WARNING:\nNo files found for years {year_load}")
  return files_out

def load_viirs(paths_to_load: list[Path]) -> dict[pd.DataFrame]:
  """
  Function to load the VIIRS data and store them in a dictionary
  It loads NOAA-20 and SNPP separately

  Args:
    paths_to_load: List of Path objects to load 

  Returns:
    dictionary containing both data frames from both used products 

    `{'snpp': df_viirs, 'noaa': df_noaa}`

  """
  viirs_noaa = []
  viirs_snpp = []

  for p in paths_to_load:
    if "snpp" in p.name:
      df_in_v = pd.read_csv(p)
      viirs_snpp.append(df_in_v)
    elif 'jpss' in p.name:
      df_in_n = pd.read_csv(p)
      viirs_noaa.append(df_in_n)

  df_viirs = pd.concat(viirs_snpp, ignore_index=True)
  df_noaa = pd.concat(viirs_noaa,ignore_index=True)
  return {'snpp': df_viirs, 'noaa': df_noaa}

def merge_viirs(viirs_dict: dict[pd.DataFrame], append_noaa: bool = True) -> dict[str, object]:
  """
  Takes a dictionary containing data frame from VIIRS products (NOAA and SNPP) and merged
  them into a single data frame
  Data from SNPP takes precedence over NOAA as SNPP data is more robust and undergoes more strict QA
  
  Args:
    viirs_dict (dict): Dictionary containing NOAA and SNPP data frames
  
  Returns:
    dict containing two objects: 
      df: Data frame merged
      data_report: a dictionary containing information on the rows and data origin

      `{'df': df_out, 'data_report': data_report}`

  Raises:
    ValueError if SNPP data is not provided 
  """
  cols_merge = ['longitude','latitude','acq_date']
  df_snpp = viirs_dict.get('snpp', 'SNPP: No data available')
  df_noaa = viirs_dict.get('noaa', 'NOAA: No data available')

  if df_snpp is None:
    raise ValueError("❌ SNPP data is required")

  if append_noaa:
    # Find values in NOAA not in SNPP 
    df_diff = df_noaa.loc[~df_noaa.set_index(cols_merge).index.isin(df_snpp.set_index(cols_merge).index)]
    df_out = pd.concat([df_snpp, df_diff], ignore_index = True)
    data_report = {'total_rows_snpp': df_snpp.shape[0],
                   'total_rows_noaa': df_diff.shape[0]}
    return {'df': df_out,
            'data_report': data_report}
  else:
      return {'df': df_snpp,
              'data_report': None}

def filter_viirs(viirs_data: pd.DataFrame) -> pd.DataFrame:
  """
  Filters the VIIRS data to only the desired rows to ensure data quality
  - Filter only Vegetation Fires:                     `type == 0`
  - Filter to keep Nominal and high Confidence class: `confidence == 'N' or confidence == 'H'`

  Returns
    DataFrame
  """
  df_viirs = viirs_data.copy()
  df_viirs['confidence'] = df_viirs['confidence'].str.lower().str.strip()
  df_out = df_viirs[(df_viirs['type'] == 0) & 
                    (df_viirs['confidence'].isin(['h','n']))
                   ]
  return df_out

def geo_viirs(viirs_data: pd.DataFrame, crs: str) -> gpd.GeoDataFrame:
  """
  Function to transform the VIIRS input data to a GeoPandasDataFrame

  Args:
    viirs_data (pd.DataFrame): Dataframe with VIIRS data, filtered and cleaned
    crs (str): A string containing the EPSG value to set the CRS

  Returns:
    pd.GeoDataFrame 
  """
  viirs_geo = gpd.GeoDataFrame(viirs_data, geometry=gpd.points_from_xy(viirs_data.longitude, viirs_data.latitude), crs=crs)
  return viirs_geo

def viirs_load_pipeline(dir_name: str,
                        date_range: list[int] = [] ):
  """
  Pipeline to load VIIRS data
  Cleaning and data transformation steps included in each of the individual functions

  Args:
    dir_name (str): The directory to load the data. Required for `get_filepaths()`
    date_range (list): List of integers representing the year of data to load.
                       
                       Default to an empty list (load everything) if not provided

  Returns:
    Dictionary containing the final data frame and the data report (the dataframe returned is a GeoPandas df)
    `{'df_viirs': df_viirs, 'data_report': df_viirs_report}`
  """
  viirs_files =     u.get_filepaths(dir_name)
  viirs_to_load =   to_load_viirs(viirs_files,date_range)
  viirs_data =      load_viirs(viirs_to_load)
  df_viirs_raw =    merge_viirs(viirs_data)
  df_viirs_report = df_viirs_raw.get('data_report')
  df_viirs_temp =   df_viirs_raw.get('df')
  df_viirs =        filter_viirs(df_viirs_temp)
  df_viirs_geo =    geo_viirs(df_viirs, CRS)
  return {'df_viirs': df_viirs_geo,
          'data_report': df_viirs_report}

# -------------------------
# UK GRID DATA
# -------------------------  
def load_uk_grid(file: str) -> gpd.GeoDataFrame:
  pass
if __name__ == "__main__":
  os.environ.setdefault("RUN_DEMO", "ON")
  import config as c
  YEAR_LIST = []
  # dir_name = 'VIIRS'
  # files = u.get_filepaths(dir_name)
  # to_load = to_load_viirs(files)
  # data = load_viirs(to_load)
  # print(data)