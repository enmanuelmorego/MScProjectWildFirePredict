"""
Module that loads sampled data. Please note this module includes both sampled pre and post Sentinel2 data
"""
import pandas as pd
import os

from pathlib import Path
# -----------------------------
# LOAD SAMPLED PRE SENTINEL-2
# -----------------------------
def load_sampled_pre_sentinel(requested_years: list, data_dir: Path, file_name: str = "_sampled_firenofire.csv") -> dict[int, pd.DataFrame | None]:
    """Takes a list of requested years, and loads the corresponding dataframes stored in disk
    If no dataframe is found for a given year, `None` is assigned

    Args:
        requested_years (list): List of years required (defined in `set_parameters.py`)
        data_dir (Path): Directory of where data files are stored
        file_name (str, optional): Name used for stored files. Defaults to "_sampled_firenofire.csv".

    Returns:
        dict[int, pd.DataFrame | None]: Dictionary containing requested years as keys and Dataframe or None as values
    """
    dict_sampled_year = {}
    for y in requested_years:
        fname = f"{y}{file_name}"
        fload = data_dir/"SampledFireNoFire"/ fname
        # Initialise None df 
        df = None
        if os.path.exists(fload):
            df    = pd.read_csv(fload, dtype={"composite_key": str})
        dict_sampled_year[y] = df
    return dict_sampled_year


    
