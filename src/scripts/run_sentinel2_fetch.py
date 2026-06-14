"""
Module that fetches the Sentinel2 data from GEE
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS
from typing import cast
import ee
import pandas as pd
import scripts.validation_checks as vc
import data_io.sampled_loader as sl
import utils.file_utils as fu
import utils.datasets_utils as du
import transforms.sentinel2_transforms as st
import pipelines.sentinel2_fetch_pipeline as sp


def run_sentinel2_fetch():
    # ------------------------
    # VALIDATE RUN PARAMETERS
    # ------------------------
    vc.validate_params_update(VALIDATION_DATE)
    # ------------------------
    # EXTRACT PARAMETERS 
    # ------------------------
    YEAR_FILTER   = PARAMETERS['YEAR_FILTER']
    DATA_DIR      = PARAMETERS['DATA_DIR']
    # -------------------------------
    # LOAD SAMPLED DATA
    # -------------------------------
    dict_sampled_tabular = sl.load_sampled_pre_sentinel(YEAR_FILTER, DATA_DIR)
    vc.validate_data_load_dict(dict_sampled_tabular)
    dict_sampled_tabular = cast(dict[int, pd.DataFrame], dict_sampled_tabular)
    df_sampled_all       = du.combine_dict_to_geodf(dict_sampled_tabular, PARAMETERS['CRS'])

    df_sampled_all = df_sampled_all.head()
    # -------------------------------
    # LOAD SENTINEL2 CURRENT STATE
    # -------------------------------
    available_sentinel_files = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
    sentinel_max_batch_num   = fu.fetch_max_batch_num(available_sentinel_files)
    dict_sentinel_batches      = st.sampled_to_batch(df_sampled_all, sentinel_max_batch_num)

    # -------------------------------
    # REQUEST DATA
    # -------------------------------
    sp.request_sentinel2_data(df_sampled_all, dict_sentinel_batches, PARAMETERS)
    
if __name__ == "__main__":
    d = run_sentinel2_fetch()
    #print(d)
    # d['date'] = pd.to_datetime(d['date'])
    # d['year'] = d['date'].dt.year
    # print(d['year'].unique())