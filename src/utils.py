from pathlib import Path
import os
import pandas as pd
from datetime import datetime

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

def drive_sentinel(geo_df: gpd.GeoDataFrame,
                         available_files: List[Path]) -> dict[str, List]:
  """"
  Checks whether Sentinel-2 .csv files already exist in GoogleDrive ready to use for a given date range

  The required date range is inferred from the input GeoDataFrame, which represents the UK grid expanded across daily timestamps. 
  The function compares this required knowing date range against Sentinel-2 metadata files already available in local storage (Google Drive).
  
  Args:
    df (GeoDataFrame): Geo data frame containing the whole UK Map split by grids, with grid_id, and for each day in the given range
                       Expects a continuos date range
    available_file (List): A list contaning all the available files in GoogleDrive 
                           Format of filenames expected <yyyymmdd-yyyymmdd_sentinel_images_layer1

  Returns
    A dictionary with the following entries:

      "available_files":
      A list of filenames corresponding to Sentinel-2 metadata CSVs that can be reused directly for the requested date range.

      "required_ranges":
      A list of date objects representing each of the days that need to be retrieved from Google Earth Engine 

  Example:
    `df_geo <Date range 2019-01-01 - 2019-01-20>`

    Assume that in Google Drive there are Sentinel files for:`2019-01-01` to `2019-01-05` AND `2019-01-10` to `2019-01-20`::

      out_dict = {'available_files' : ['20190101-20190105_sentinel_images_layer1.csv', 
                                       '20190110-20190120_sentinel_images_layer1.csv'],
                  'required_ranges'  : [datetime.date(2019, 1, 6), datetime.date(2019, 1, 7)
                                        datetime.date(2019, 1, 8), datetime.date(2019, 1, 9)]}
  """
  # Extract date range
  geo_dates = pd.to_datetime(geo_df['date']).dt.date
  min_d, max_d = geo_dates.min(), geo_dates.max()

  requested_days = set(pd.date_range(start = min_d, 
                                     end   = max_d,
                                     freq  = "D").date)
  # If no files exists, all are required
  if not available_files:
    return {"available_files": [],
            "required_days": sorted(requested_days)}

  available_days: set[date] = set()
  used_files: List[Path] = []

   # Find files relevant to current date range 
  for f in available_files:
    try:
      avail_min = datetime.strptime(f[:8],   "%Y%m%d").date() 
      avail_max = datetime.strptime(f[9:17], "%Y%m%d").date()
    except ValueError:
      continue

    if avail_max < min_d or avail_min > max_d:
      continue

    used_files.append(f)
    available_days.update(pd.date_range(start = avail_min,
                                        end   = avail_max,
                                        freq  = "D")
                                        .date)
  # Find missing dates
  required_days = sorted(requested_days - available_days)

  return {"available_files": used_files,
          "required_days": sorted(required_days)}