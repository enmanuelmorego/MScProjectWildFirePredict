from pathlib import Path
import os 
import pandas as pd
import geopandas as gpd
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple
import math
import re
#from config import CRS
import utils as u
import google_ee as gee
import cdsapi
import pygrib
import time

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
                   ].copy()
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
                        crs: str,
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
  df_viirs_geo =    geo_viirs(df_viirs, crs)
  return {'df_viirs': df_viirs_geo,
          'data_report': df_viirs_report}

# -------------------------
# UK GRID DATA
# -------------------------  
def load_uk_grid(file_name: str, crs: str) -> gpd.GeoDataFrame:
  """
  Function to load the shapefile containing the UK grid to use as base

  Args:
    file_name (str): Name of the file to load
    crs (str): Coordinate Reference System, ensure all data is consistent across the project

  Returns:
    df (GeoPandasDataFrame)
  """
  grid_path = Path(os.environ.get('DATA_DIR'))/'UKGrid'/file_name
  uk_grid = gpd.read_file(grid_path)
  uk_grid = uk_grid.rename(columns = {'id': 'grid_id'})
  uk_grid = uk_grid.to_crs(crs)
  return uk_grid

#sentinel_batch_create
# -------------------------
# GOOGLE EE SENTINEL-2
# -------------------------  
def check_drive_sentinel(geo_df: gpd.GeoDataFrame,
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

def batch_create_sentinel(df: pd.DataFrame, required_days: list, batch_size: int = 10) -> dict:
  """
  Takes the UK Grid by day, along with the computed required_days list from `check_drive_sentinel` and
  splits the data frame into batches of 14 days max. This allows for each data frame to be approximately 
  20k-25k rows max
  This is to ensure that the request is under the max size set by Google EE engine

  Args:
    df (DataFrame): UK grid data frame by day

    required_days (list): List of dates to request from google earth

    batch_size (int): Number of days allowed in each batch. this controls the size of the data to be processed
                      defaults to 10 days

  Returns:
    dict_out (dict): A dictionary of data frames, each containing `batch_size` days worth of data
  """
  min_i       = 0
  max_i       = batch_size - 1
  batch       = 1
  total_dates = len(required_days)
  df['date'] = pd.to_datetime(df['date']).dt.date
  required_days = sorted(required_days)

  # Get total batches required
  total_batches = math.ceil(total_dates / batch_size)
  dict_out = {}
  total_rows = 0

  for _ in range(1, total_batches + 1):
    if max_i >= total_dates:
      max_d = required_days[total_dates - 1]
    else:
      max_d = required_days[max_i]
    min_d = required_days[min_i]

    df_batch = df[(df['date'] >= min_d) &
                  (df['date'] <= max_d)].copy()
    dict_out[f"batch_{batch}"] = df_batch
    # Update values
    min_i += batch_size
    max_i += batch_size
    batch += 1
    total_rows += df_batch.shape[0]

  total_minutes = 0.012 * total_rows
  dur = timedelta(minutes=total_minutes)
  hrs, rmdr = divmod(dur.total_seconds(), 3600)
  mins = rmdr // 60
  print(f"\t⏱️  Google Earth Engine will take approximately {int(hrs)}hrs {int(mins)}mins to process {total_rows} rows of data")
  return dict_out

def load_from_drive_sentinel(sentinel_2_path: Path, relevant_files: list) -> pd.DataFrame:
  """
  Loads previously downloaded Sentinel-2 files from GoogleDrive 
  It combines all the files into a single data frame

  Please note, this function loads only the relevant files, not all available files. 
  This is to allow users to run small batch tests, and flexibility

  Args:
    sentinel_2_path (Path): A Path object contaning the parent location of where all the Sentinel-2 files are stored 

    relevant_files (List): A list of strings containing the files names of the relevant files for the current processing pipeline

  Returns:
    Dataframe: A data frame containing all the data from all relevant files 
  """
  df = pd.DataFrame()
  for f in relevant_files:
    file_path = Path(sentinel_2_path)/f
    df_in = pd.read_csv(file_path)
    df = pd.concat([df, df_in])
  return df

def sentinel_load_pipeline(data_dir_sentinel: Path,
                           df_uk_daily_grid: gpd.GeoDataFrame,
                           sat_img: str) -> pd.DataFrame:
  """
  Wrapper function to load the Sentinel data
  - Takes the input data of the UK Gridded df by day
  - Checks if there are any dates to request from GoogleEE
  - If data is needed, sends the request to Google EE
  - Loads the available files from GoogleDrive
  - Returns a dataframe with a single df containing all the data from all files covering the requested period 

  Args:
    data_dir_sentinel (Path): Path contaning the directory of where the Sentinel data is stored in Google Drive

    df_uk_daily_grid (DataFrame): Data frame contaning all the 12x12 grids for the UK for each of the relevant days in the analysis

    sat_img (str): A string containing the name of the satelites images used 

  Returns:
    DataFrame containing all the Sentinel-2 metadata in a single data frame for the relevant period defined in df_uk_daily_grid

  """

  sentinel_files = os.listdir(data_dir_sentinel)

  # Get required dates to fetch from Google EE
  avail_files_req_days = check_drive_sentinel(df_uk_daily_grid, sentinel_files)
  available_files = avail_files_req_days['available_files']
  required_days   = avail_files_req_days['required_days']
  if required_days:
      print("\t🌍  Google EE connect ")
      gee.google_ee_request_runner(satelite      = sat_img,
                                   df_grid_date  = df_uk_daily_grid,
                                   required_days = required_days)
  else:
    print(f"\t🗂️  All data available in Drive - No connection to Google Earth required")
    
  df_sentinel = load_from_drive_sentinel(data_dir_sentinel, available_files)
  return df_sentinel

# -------------------------
# FIRE WEATHER INDEX
# -------------------------  
def check_drive_fwi(df_uk_daily_grid: gpd.GeoDataFrame, available_files: list) -> dict:
  """
  Function to check .csv and .grib file availability in Google Drive for Fire Weather Index data
  Each FWI file corresponds to a full year worth of data, therefore, the checks are performed in a year by year basis 
  - Extracts the unique years in the input data frame (which sets the dates required)
  - Compare the years with a list of available files provided 
  - It extracts the csv that matches the requested years
  - Then it extracts the .grib files if the year is part of the `requested_years` set and `not in` the extracted/available .csv files
  - Then it extract the years for which no .csv nor .grib are available (this is later used to download the .grib from the API)

  Purpose:
    Reduce the computational load of donwloading the .grib files from the API anytime time the analysis is ran
    - For the required analysis, extract the .csv file names to be used if available 
    - Identify any .grib files that have not yet been transformed to .csv so these can be transformed rather than downlaoding new data again
    - Identify gaps in the data and download data only relevant for the present analysis

  Args:
    df_uk_daily_grid (GeoDataFrame): Data frame containing the full range of dates required for the analysis

    available_files (Path): A list of available files in GoogleDrive, ready for use 

  Returns:
    Dictionary with available files (if there are existing files in storage that matches the required years) and required years if the prior is not true
    
  Example::

    out_dict = {'available_csv' : ['2017FWI.csv', '2018FWI.csv'],
                'available_grib': ['2019FWI.grib', '20202FWI.grib']
                'required_years': {'2021', '2022'}}
  """
  # Get the requested years for each of the files types
  requested_years      = set(df_uk_daily_grid['date'].dt.strftime("%Y"))
  available_years_csv  = set([fy[0:4] for fy in available_files if re.search(r".csv$" , fy) and fy[0:4] in requested_years])
  available_years_grib = set([fy[0:4] for fy in available_files if re.search(r".grib$", fy) and fy[0:4] in requested_years and fy[0:4] not in available_years_csv])
  available_all        = available_years_csv | available_years_grib

  matched_csv_files   = [f for f in available_files if f[0:4] in available_years_csv  and re.search(r".csv$", f)]
  matched_grib_files  = [f for f in available_files if f[0:4] in available_years_grib and re.search(r".grib$", f)]

  return {'available_csv' : matched_csv_files,
          'available_grib': matched_grib_files,
          'required_years': requested_years - available_all}

def fetch_fwi_api(required_years: set, fwi_data_dir: Path) -> None:
  """
  Function to fetch the FWI data from CEMS Early Warning Data Store for the required years passed in the argument
  Uses cdsapi to fetch the data and download the corresponding .grib file

  Args:
    required_years (set): A set of strings containing the years required to download

    fwi_data_dir (path): Path of the FWI data folder

  Returns:
    None 
  """
  for y in required_years:
    fname = f"{y}FWI.grib"
    out_file_path = Path(fwi_data_dir)/fname

    dataset = "cems-fire-historical-v1"
    request = {
        "product_type": "reanalysis",
        "variable": ["fire_weather_index"],
        "dataset_type": "consolidated_dataset",
        "system_version": ["4_1"],
        "year": [y],
        "month": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12"
        ],
        "day": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12",
            "13", "14", "15",
            "16", "17", "18",
            "19", "20", "21",
            "22", "23", "24",
            "25", "26", "27",
            "28", "29", "30",
            "31"
        ],
        "grid": "original_grid",
        "data_format": "grib"
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request, out_file_path.as_posix())

def transform_grib_to_csv(fwi_path: Path, grib_fname: str, grb_name: str, df_uk_grid, crs_val: str) -> None:
  """
  Function that transform a grib file into a csv file. It takes the .grib file, and iterates thru all its elements/message 
  to extract the corresponding data. 
  Then it joins the data to the UK Grid data frame, retaining the `grid_id` to later match using primary key of
  (`df_grid`, `date`)
  For each 12km x 12km grid, it computes both the Max FWI and Mean FWI to be later used for analysis
  It saves the transformed data as a csv file 

  Args:
    fwi_path (Path): Path of the directory containing all the FWI data
  
    grib_fname (str): String containing the file name to load 

    grb_name (str): name of the object to extract from the grib file

    df_uk_grid (df): Data frame contaning the UK grid coordinates. Not dated

    crs_val (str): CRS value used across the project 

  Returns:
    None
  """
  fname_path = Path(fwi_path)/grib_fname
  grbs       = pygrib.open(fname_path)
  fwi_msgs   = grbs.select(name=grb_name)

  # Initialise object to store data
  list_fwi = []
  total = len(fwi_msgs)
  i = 1
  # Process data
  for grb in fwi_msgs:
    print(f"\r\t...⚙️  [{grib_fname}] Processing {i} of {total} [{round((i/total)*100,2)}]%", end="")
    # Extract variables
    date       = grb.validDate
    date       = datetime.strptime(f"{grb.dataDate}{grb.dataTime:04d}", "%Y%m%d%H%M")
    lats, lons = grb.latlons()
    fwi_values = grb.values
    n          = fwi_values.size
    # Load onto a temp dataframe
    df_grib = pd.DataFrame({'date'     : [date] * n,
                            'longitude': lons.ravel(),
                            'latitude' : lats.ravel(),
                            'fwi'      : fwi_values.ravel()})
    # Transform longitude from [0, 360] range (as in grib files) to [-180, 180] range as in UK grid file
    df_grib["longitude"] = df_grib["longitude"].where(df_grib["longitude"] <= 180,
                                                      df_grib["longitude"] - 360)
    df_geo_grib = gpd.GeoDataFrame(df_grib,
                                   geometry = gpd.points_from_xy(df_grib.longitude,
                                                                 df_grib.latitude),
                                   crs = crs_val)
    # Join FWI to UK Grid to get value per Grid
    df_join = gpd.sjoin(df_geo_grib, df_uk_grid, how = 'inner', predicate = 'within')
    df_grouped = (df_join
                  .groupby(['grid_id', 'date'], as_index = False)
                  .agg(fwi_max  = ('fwi', 'max'),
                       fwi_mean = ('fwi', 'mean')))
    list_fwi.append(df_grouped)
    # User Messages objects
    i += 1
  
  df_fwi = pd.concat(list_fwi, ignore_index = True)
  fname_out = Path(fwi_path)/grib_fname.replace(".grib", ".csv")
  df_fwi.to_csv(fname_out, index = False)
  print(f"\n\t...✅  Succesfully processed {grib_fname}")


def fwi_load_pipeline(fwi_path: Path,
                      df_uk_daily_grid: gpd.GeoDataFrame,
                      df_uk_grid: gpd.GeoDataFrame,
                      crs: str,
                      grb_name: str) -> pd.DataFrame:
  """
  Function to load, fetch, and prepare Fire Weather Index (FWI) data for analysis.

  For the relevant period of time, check for the FWI data as follows:
  
  The function performs the following steps:
    - Inspects available FWI files (.csv and .grib) in the specified directory
    - Determines which years are already available as CSV files
    - Identifies GRIB files that require transformation to CSV
    - Detects any missing years and downloads the corresponding GRIB files
      from the CEMS API
    - Transforms GRIB files to grid-level daily summaries (mean and max FWI)
    - Loads all relevant CSV files and concatenates them into a single dataframe

  Purpose:
    Provide a reproducible and efficient mechanism to load Fire Weather Index
    data aligned to the UK grid and daily time step, while minimising unnecessary
    API calls and repeated transformations across multiple runs of the analysis.

  Args:
    fwi_path (Path): Path to the directory containing Fire Weather Index data
                     files (.csv and .grib)

    df_uk_daily_grid (GeoDataFrame): Data frame defining the full spatio-temporal
                                     backbone of the analysis (UK grid × date),
                                     used to infer the required range of years

    df_uk_grid (GeoDataFrame): Static UK grid geometry used to spatially join
                               FWI values to grid cells during GRIB processing

    crs (str): Coordinate Reference System (CRS) used consistently across
               spatial datasets in the project

    grb_name (str): Name of the Fire Weather Index variable to extract from
                    the GRIB files

  Returns:
    DataFrame containing Fire Weather Index data aggregated to daily UK grid
    cells, with one row per (grid_id, date) and corresponding summary statistics
    (e.g. mean and maximum FWI values)

  Example::

    df_fwi = fwi_load_pipeline(
        fwi_path          = Path("data/FWI"),
        df_uk_daily_grid  = df_daily_grid,
        df_uk_grid        = df_uk_grid,
        crs               = "EPSG:4326",
        grb_name          = "Fire Weather Index"
    )
  
  """
  # Get available .csv files
  fwi_files = os.listdir(fwi_path)
  # Find available and required files/years
  requirements = check_drive_fwi(df_uk_daily_grid, fwi_files)

  # 1. Check if any files are required from CEMS API
  fetch_from_api = requirements['required_years']
  if fetch_from_api:
    print("\t📈 Fetching FWI data from CDS API...")
    fetch_fwi_api(fetch_from_api, fwi_path)
    # Refresh requirements to include newly downloaded data
    fwi_files = os.listdir(fwi_path)
    requirements = check_drive_fwi(df_uk_daily_grid, fwi_files)
  
  # 2. If Grib file needs to be transformed to csv
  grib_to_csv = requirements['available_grib']
  if grib_to_csv:
    print("\t➡️ Transforming .grib to .csv...")
    for g in grib_to_csv:
      transform_grib_to_csv(fwi_path   = fwi_path, 
                            grib_fname = g,
                            grb_name   = grb_name,
                            df_uk_grid = df_uk_grid,
                            crs_val    = crs)
    # Refresh requirements to include newly transformed data
    fwi_files = os.listdir(fwi_path)
    requirements = check_drive_fwi(df_uk_daily_grid, fwi_files)

  # 3. Load csv data
  fwi_csv_files = requirements['available_csv']
  # Initialise object to store data
  fwi_list = []
  for f in fwi_csv_files:
    fname_load = Path(fwi_path)/f
    df_load = pd.read_csv(fname_load)
    fwi_list.append(df_load)
  df_fwi = pd.concat(fwi_list, ignore_index = True)
  return df_fwi


if __name__ == "__main__":
    os.environ.setdefault("RUN_DEMO", "ON")
    import config as c
    DATA_DIR = os.environ.get("DATA_DIR")
    CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs


    dates = pd.to_datetime(['2019-01-01', '2019-02-02','2019-02-02', '2019-12-10'])
    df_uk_grid = pd.DataFrame({'date': dates})


    fwi_p    = Path(DATA_DIR)/"FWI"
    f = fwi_load_pipeline(fwi_p, df_uk_grid)
    print(f)