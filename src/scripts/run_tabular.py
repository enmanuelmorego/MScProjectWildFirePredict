"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

import scripts.validation_checks as vc

import pipelines.tabular_load_pipeline as lp
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS


def run_tabular():
    # Validation rule
    vc.validate_params_update(VALIDATION_DATE)
    # Extract parameter values
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    SP_FILENAME = PARAMETERS['SP_FILENAME']
    GRB_NAME    = PARAMETERS['GRB_NAME']

    # Load all tabular data
    dict_tabular_data = lp.load_tabular_data(YEAR_FILTER, DATA_DIR, CRS, SP_FILENAME, GRB_NAME)

    return dict_tabular_data

if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    x = run_tabular()

    
