"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

from src.scripts.set_parameters import VALIDATION_DATE, PARAMETERS
import src.scripts.validation_checks as vc
from src.datasets.viirs.pipeline import load_viirs_main

def run_tabular():
    # Validation rule
    vc.validate_params_update(VALIDATION_DATE)
    # Extract parameter values
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    # Load VIIRS data
    dict_viirs = load_viirs_main(years_to_load = YEAR_FILTER, data_dir = DATA_DIR, crs = CRS)
    df_viirs = dict_viirs['df_viirs']


    return df_viirs

if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    
    x = run_tabular()
    print(x.head())
    
