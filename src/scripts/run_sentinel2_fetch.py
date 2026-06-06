"""
Module that fetches the Sentinel2 data from GEE
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

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
    s = sl.load_sampled_pre_sentinel(YEAR_FILTER, DATA_DIR)

    return s
    
if __name__ == "__main__":
    d = run_sentinel2_fetch()
    for k, v in d.items():
        print(f"{k}   \n{v}")
        print("........")