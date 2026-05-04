"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

import src.scripts.validation_checks as vc
import src.utils.datasets_utils as du

from src.scripts.set_parameters import VALIDATION_DATE, PARAMETERS
from src.datasets.viirs.pipeline import load_viirs_main
from src.datasets.ukgrid.pipeline import load_ukgrid_main

def run_tabular():
    # Validation rule
    vc.validate_params_update(VALIDATION_DATE)
    # Extract parameter values
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    SP_FILENAME = PARAMETERS['SP_FILENAME']

    # Load VIIRS data
    dict_viirs = load_viirs_main(years_to_load = YEAR_FILTER, data_dir = DATA_DIR, crs = CRS)
    df_viirs = dict_viirs['df_viirs']
    # Generate dataframe with every day from min to max of df_viirs
    df_days = du.extract_year_range(df_viirs)

    # Load UK Grid data
    dict_ukgrid     = load_ukgrid_main(df_days_in = df_days, data_dir = DATA_DIR, file_name = SP_FILENAME, crs = CRS)
    df_ukgrid       = dict_ukgrid['df_ukgrid']
    df_daily_grid   = dict_ukgrid['df_daily_grid']

    # Load FWI




    return None

if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    
    x = run_tabular()
    #print(x.head())
    
