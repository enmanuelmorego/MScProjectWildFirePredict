"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

import scripts.validation_checks as vc
import pipelines.tabular_load_pipeline as lp
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

import transforms.preprocessing_transforms as pp
import reporting.data_profiler as dp

def run_tabular():
    # ------------------------
    # VALIDATE RUN PARAMETERS
    # ------------------------
    vc.validate_params_update(VALIDATION_DATE)
    # ------------------------
    # EXTRACT PARAMETERS 
    # ------------------------
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    CRS         = PARAMETERS['CRS'] 
    SP_FILENAME = PARAMETERS['SP_FILENAME']
    GRB_NAME    = PARAMETERS['GRB_NAME']
    # ------------------------
    # LOAD TABULAR DATA
    # ------------------------
    dict_tabular_data = lp.load_tabular_data(YEAR_FILTER, DATA_DIR, CRS, SP_FILENAME, GRB_NAME)
    # ------------------------
    # PROCESS INPUTS
    # ------------------------
    df_viirs_w_grid      = pp.aggregate_viirs_to_grid(dict_tabular_data['df_viirs'], dict_tabular_data['df_ukgrid'])
    df_combined          = pp.build_tabular_dataset(df_viirs_w_grid, dict_tabular_data)
    df_combined_filtered = pp.remove_na_fwi_grid1(df_combined)
    df_composite_key     = pp.create_composite_key(df_combined_filtered)

    return df_composite_key

if __name__ == "__main__":

    x = run_tabular()
    #print(type(x))
    #print(x.head())
    data_profile = dp.extract_dataset_metadata(x, 'fulldata', True)
    print(x.shape[0])
    
