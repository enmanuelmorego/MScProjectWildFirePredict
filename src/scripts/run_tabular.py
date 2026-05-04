"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

import src.scripts.validation_checks as vc
import src.utils.datasets_utils as du

from src.scripts.set_parameters import VALIDATION_DATE, PARAMETERS
from pipelines.viirs_pipeline import load_viirs_main
from pipelines.ukgrid_pipeline import load_ukgrid_main
from pipelines.fwi_pipeline import load_fwi_main

def run_tabular():
    # Validation rule
    vc.validate_params_update(VALIDATION_DATE)
    # Extract parameter values
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    SP_FILENAME = PARAMETERS['SP_FILENAME']
    GRB_NAME    = PARAMETERS['GRB_NAME']


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
    df_fwi = load_fwi_main(df_uk_grid_in = df_ukgrid, data_dir = DATA_DIR, requested_years = YEAR_FILTER, grb_name = GRB_NAME, crs = CRS)




    return df_fwi

if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    
    x = run_tabular()
    print(x.head())
    
