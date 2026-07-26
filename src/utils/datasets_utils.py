"""
Module that contains helper files and functions to transform datasets 
"""
import pandas as pd
import geopandas as gpd
import re

from pathlib import Path 
from datetime import datetime, date

def extract_year_range(df: pd.DataFrame) -> pd.DataFrame:
    """  Generate a daily date range covering full calendar years based on the
    minimum and maximum acquisition dates in the input DataFrame.

    The function identifies the earliest and latest dates in the input data
    and expands the range to include complete calendar years.

    For example:
        - If the minimum date is `2024-04-10` and the maximum date is `2025-10-05`
        - The output date range will span from `2024-01-01` to `2025-12-31`

    A constant `join_key` column is added to facilitate later joins with
    the UK spatial grid.

    Args:
        df (pd.DataFrame): Input DataFrame containing an acquisition date column named `date`

    Returns:
        pd.DataFrame: A DataFrame with:
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

def get_latest_missing_sentinel_log_filepath(files_paths: list[Path], file_name_pattern: str = r"missing_sentinel2_images") -> Path:
    """Takes a list of file paths, containing multiple logs from Sentinel-2 data download process
    It iterates thru the list of file paths and finds only the files that matches the value in parameter `file_name_pattern` 
    Extracts the date from the file name and finds the latest / most recent file name based on the date used in the file name

    Args:
        files_paths (list[Path]): List of file paths - Assumes file names contains a time stamp in format `YYYY-mm-dd`
        file_name_pattern (str, optional): Pattern of the files the funciton is interested in. Defaults to r"missing_sentinel2_images".

    Raises:
        ValueError: When no date value can be extracted from file name. This means the file name does not contain the pattern "%Y-%m-%d"
        FileNotFoundError: Raises when, if after finishing the iteration and processes no file path is found 

    Returns:
        Path: File path of the latest file to load
    """
    # Initialise objects
    latest_file_date = None
    file_to_load     = None
    file_date        = None

    # Find latest files
    for f in files_paths:
        # Skip if the file does not match the expected pattern 
        if re.search(file_name_pattern, str(f)) is None:
            continue
    
        # Extract date
        file_date = re.search(r"\d{4}-\d{2}-\d{2}", str(f))
    
        # Raise value error if no date value could be parsed from filename
        if file_date is None:
            raise ValueError(f"\n❌  ERROR  \nCould not extract date value from filename {f}")
    
        # Extract date from file to find latest file 
        file_date = datetime.strptime(file_date.group(), "%Y-%m-%d")
        # Update latest file object to match latest file
        if latest_file_date is None or file_date > latest_file_date:
            latest_file_date = file_date
            file_to_load     = f

    # IF there is no file to load, then raise value error         
    if file_to_load is None:
        raise FileNotFoundError(f"\n❌  ERROR  \nCould not find a Sentinel-2 missing files log file to load")
    
    # Return succesfully found file path
    print(f"📂 Loaded Failed Sentinel-2 log from: {file_date}\nFile Name: {file_to_load}")
    return file_to_load 

def combine_dict_to_geodf(dict_in: dict[int, pd.DataFrame], crs: str) -> gpd.GeoDataFrame: 

    df_sampled_all             = pd.concat(dict_in.values(), ignore_index = True)
    df_sampled_all['date']     = pd.to_datetime(df_sampled_all['date'])
    df_sampled_all['geometry'] = gpd.GeoSeries.from_wkt(df_sampled_all['geometry'])
    df_sampled_geodf = gpd.GeoDataFrame(df_sampled_all,
                                        geometry = 'geometry',
                                        crs = crs)
    return df_sampled_geodf

def get_temporal_label(date_obj: pd.Timestamp, split_by: str) -> str:

    temporal_extract_map = {'year': '%Y',
                            'quarter': '%Y-Q%q',
                            'month': '%Y-%b'}

    date_pattern = temporal_extract_map.get(split_by, None)
    return str(date.strftime(date_pattern))