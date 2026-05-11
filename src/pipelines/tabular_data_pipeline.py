"""
Module that contains all the pipelines to load and transform the raw tabular data
"""
import data_io.ukgrid_loader as l
from pathlib import Path
import pandas as pd
import geopandas as gpd

from pipelines.viirs_pipeline import load_viirs_main
from pipelines.ukgrid_pipeline import load_ukgrid_main
#from pipelines.fwi_pipeline import load_fwi_main
from pathlib import Path

import utils.datasets_utils as du
# ------------------------
# LOAD TABULAR DATASETS
# ------------------------
def load_ukgrid_main(df_days_in: pd.DataFrame, data_dir: Path, file_name: str, crs: str) -> dict[str, gpd.GeoDataFrame]:
    """Wrapper function to load uk grid dataset. It calls the function to load the uk grid file, it creates a single row for each grid+date pair given 
    the `df_days_in` object

    Args:
        df_days_in (pd.DataFrame): A dataframe containing all of the days covered by the period of study
        data_dir (Path): Directory of where the data is stored
        file_name (str): Name of file
        crs (str): Coordinate Reference System to ensure spatial data is processed uniformly

    Returns:
        dict[str, gpd.GeoDataFrame]: Dictionary of dataframes containing the grid and daily grid dfs
    """    
    df_ukgrid                 = l.load_uk_grid(data_dir, file_name, crs)
    df_daily_grid             = df_ukgrid.copy()
    df_daily_grid['join_key'] = 1
    df_daily_grid             = df_daily_grid.merge(df_days_in, on='join_key').drop(columns='join_key')
    return {'df_ukgrid'   : df_ukgrid,
            'df_daily_grid': df_daily_grid}

def load_tabular_data(year_filter: list[int], data_dir: Path, crs: str, sp_filename: str, grb_name: str):
    """Wrapper function that calls all the pipelines to load all tabular data

    Args:
        year_filter (list[int]): list containg the required years for the current processing run
        data_dir (Path): Path of data directory
        crs (str): CRS value to be used across the full project
        sp_filename (str): Name of Shape file containing the UK grid
        grb_name (str): NAme of Grib file to fetch FWI 

    Returns:
        Dictionary containing all of the dataframes with the tabular data
        
        `{'df_viirs': df_viirs,
          'df_ukgrid': df_ukgrid,
          'df_daily_grid': df_daily_grid,
          'df_fwi': df_fwi}`
    """
    # Load VIIRS data
    dict_viirs = load_viirs_main(years_to_load = year_filter, data_dir = data_dir, crs = crs)
    df_viirs   = dict_viirs['df_viirs']
    # Generate dataframe with every day from min to max of df_viirs
    df_days    = du.extract_year_range(df_viirs)

    # Load UK Grid data
    dict_ukgrid     = load_ukgrid_main(df_days_in = df_days, data_dir = data_dir, file_name = sp_filename, crs = crs)
    df_ukgrid       = dict_ukgrid['df_ukgrid']
    df_daily_grid   = dict_ukgrid['df_daily_grid']

    # Load FWI
    df_fwi = load_fwi_main(df_uk_grid_in = df_ukgrid, data_dir = data_dir, requested_years = year_filter, grb_name = grb_name, crs = crs)

    return{'df_viirs': df_viirs,
           'df_ukgrid': df_ukgrid,
           'df_daily_grid': df_daily_grid,
           'df_fwi': df_fwi}

if __name__ == "__main__":
    from scripts.set_parameters import  PARAMETERS
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    SP_FILENAME = PARAMETERS['SP_FILENAME']
    GRB_NAME    = PARAMETERS['GRB_NAME']
    d = load_tabular_data(YEAR_FILTER, DATA_DIR, CRS, SP_FILENAME, GRB_NAME)
    print(d)