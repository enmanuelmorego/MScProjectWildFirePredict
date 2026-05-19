"""
Method that contains all the functions to load the VIIRS data
"""
from pathlib import Path
import pandas as pd

def select_viirs_files(files: list[Path], year_load: list[int] | None = None) -> list[Path]:
    """  Function to select the VIIRS files to load from local storage. The list of files is filtered if a year is specified

    Args:
        files (list[Path]): List of strings containing a full file path for each of the files to load
        year_load (list[int] | None, optional): An integer representing a year to load the data - If not provided, the default with load all data. Defaults to None.

    Returns:
        list[Path]: List of paths to be loaded
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

def load_viirs(paths_to_load: list[Path]) -> dict[str, pd.DataFrame]:
    """  Function to load the VIIRS data and store them in a dictionary. 
    It loads NOAA-20 and SNPP separately

    Args:
        paths_to_load (list[Path]): List of Path objects to load 

    Returns:
        dict[str, pd.DataFrame]: dictionary containing both data frames from both used products 
    """    
    viirs_noaa: list[pd.DataFrame] = []
    viirs_snpp: list[pd.DataFrame] = []

    for p in paths_to_load:
        if "snpp" in p.name:
            df_in_v = pd.read_csv(p)
            viirs_snpp.append(df_in_v)
        elif 'jpss' in p.name:
            df_in_n = pd.read_csv(p)
            viirs_noaa.append(df_in_n)

    df_viirs = pd.concat(viirs_snpp, ignore_index=True)
    df_noaa  = pd.concat(viirs_noaa,ignore_index=True)
    return {'snpp': df_viirs, 'noaa': df_noaa}