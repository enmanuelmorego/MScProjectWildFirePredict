"""
Module that fetches the Sentinel2 data from GEE
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

import pandas as pd
import scripts.validation_checks as vc
import data_io.sampled_loader as sl
import utils.file_utils as fu



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
    # -------------------------------
    # LOAD SAMPLED DATA
    # -------------------------------
    dict_sampled_tabular = sl.load_sampled_pre_sentinel(YEAR_FILTER, DATA_DIR)
    vc.validate_data_load_dict(dict_sampled_tabular)
    df_sampled_all       = pd.concat(dict_sampled_tabular.values(), ignore_index = True)
    # -------------------------------
    # LOAD SENTINEL2 CURRENT STATE
    # -------------------------------
    avialable_sentinel_files = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
    sentinel_max_batch_num   = fu.fetch_max_batch_num(avialable_sentinel_files)

    return sentinel_max_batch_num
    
if __name__ == "__main__":
    d = run_sentinel2_fetch()
    print(d)
    # d['date'] = pd.to_datetime(d['date'])
    # d['year'] = d['date'].dt.year
    # print(d['year'].unique())