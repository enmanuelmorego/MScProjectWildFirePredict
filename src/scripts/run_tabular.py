"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

from src.scripts.set_parameters import VALIDATION_DATE, PARAMETERS
from src.datasets.viirs.pipeline import load_viirs_main
import src.utils.run_control as rc

def run_tabular():
    # Validation rule
    rc.validate_params_update(VALIDATION_DATE)
    # Load VIIRS data
    dict_viirs = load_viirs_main(years_to_load = PARAMETERS['YEAR_FILTER'], 
                                 data_dir      = PARAMETERS['DATA_DIR'],
                                 crs           = PARAMETERS['CRS'])
    df_viirs = dict_viirs['df_viirs']


    return df_viirs

if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    
    x = run_tabular()
    x.head()
    
