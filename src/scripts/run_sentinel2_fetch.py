"""
Module that fetches the Sentinel2 data from GEE
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

import scripts.validation_checks as vc
import pipelines.tabular_load_pipeline as lp
import transforms.preprocessing_transforms as pp
import pipelines.sampling_pipeline as sp
import sampling.sampling_functions as sf



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
    # ------------------------
    # LOAD SAMPLED DATA
    # ------------------------
    