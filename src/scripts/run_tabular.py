"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""
from scripts.set_parameters import VALIDATION_DATE, PARAMETERS

import scripts.validation_checks as vc
import pipelines.tabular_load_pipeline as lp
import transforms.preprocessing_transforms as pp
import reporting.data_profiler as dp
import reporting.sampling_reporter as sr
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
    # ------------------------
    # SAMPLE DATA
    # ------------------------
    dict_samples  = sp.create_samples_dict(df_composite_key)
    samples_stats = sr.create_sampling_statistics(dict_samples)
    # TODO Create function to write samples_stats to json file
    # TODO Write function that generates histogram of distances from sampled
    # TODO Write wrapper function that calls create_sampling_statistics + json writer + histogram create + histogram saver
    
    #df_sampled_y = sf.create_y_target_sampled_df(dict_samples, df_composite_key)

    # TODO Extract t-1 as the observations used for prediction X values
    # TODO Build final data set with X and Y values where Y is only the fire lbl (leave composite Key for ref)
    #       Please note Composite Key value in Y cannot exist in X
    return dict_samples, df_composite_key

if __name__ == "__main__":

    x = run_tabular()
   # print(x.head())
    #data_profile = dp.extract_dataset_metadata(x, 'fulldata', True)
    #print(x['fire_lbl'].unique())
    
