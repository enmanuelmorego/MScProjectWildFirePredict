"""
Module that fetches the Sentinel2 data from GEE
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

import pandas as pd
import scripts.validation_checks as vc
import data_io.sampled_loader as sl



def run_sentinel2_fetch():
    # ------------------------
    # VALIDATE RUN PARAMETERS
    # ------------------------
    vc.validate_params_update(VALIDATION_DATE)
    # ------------------------
    # EXTRACT PARAMETERS 
    # ------------------------
    YEAR_FILTER = PARAMETERS['YEAR_FILTER']
    DATA_DIR    = PARAMETERS['DATA_DIR']
    # ------------------------
    # LOAD SAMPLED DATA
    # ------------------------
    dict_sampled_tabular = sl.load_sampled_pre_sentinel(YEAR_FILTER, DATA_DIR)
    vc.validate_data_load_dict(dict_sampled_tabular)
    df_sampled_all       = pd.concat(dict_sampled_tabular.values(), ignore_index = True)

    return df_sampled_all
    
if __name__ == "__main__":
    d = run_sentinel2_fetch()
    print(d.head())