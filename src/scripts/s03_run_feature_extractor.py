"""
Module that runs and performs the feature extraction of Sentinel2 data using ResNet18
"""
from scripts.s00_set_parameters import PARAMETERS, VALIDATION_DATE
from transforms.resnet_feature_extractor import ResNetFeatExtractor, extract_resnet_features

import utils.validation_checks as vc
import utils.file_utils as fu
import data_io.sampled_loader as sl
import data_io.sentinel2_io as s2l
import pandas as pd

def run_feature_extractor():
    # ------------------------
    # VALIDATE RUN PARAMETERS
    # ------------------------    
    vc.validate_params_update(VALIDATION_DATE)
    # ------------------------
    # EXTRACT PARAMETERS 
    # ------------------------
    PROJ_HOME     = PARAMETERS['PROJ_HOME']
    DATA_DIR      = PARAMETERS['DATA_DIR']
    YEAR_FILTER   = PARAMETERS['YEAR_FILTER']
    RUN_TIMESTAMP = PARAMETERS['RUN_TIMESTAMP']
    # -------------------------------
    # LOAD DATA
    # -------------------------------
    files_sentinel      = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
    df_no_sentinel_data = s2l.load_missing_sentinel2_from_log(PROJ_HOME, "outputs/logs")
    df_sampled          = pd.concat(sl.load_sampled_pre_sentinel(YEAR_FILTER, DATA_DIR))
    vc.validate_composite_keys_structure(df_sampled)
    # -------------------------------
    # RESNET-18 MODEL
    # -------------------------------
    # Initialise model
    resnet_model = ResNetFeatExtractor()
    # Disable training behaviour since the model is used only for feature extraction
    resnet_model.eval()
    # Perform feature extraction
    df_features = extract_resnet_features(files_sentinel, resnet_model)
    # -------------------------------
    # VALIDATE PROCESSING
    # -------------------------------
    # Check if there are duplicates, and if composite keys are duplicated, all values in the 512 features should also be duplicated. else error
    vc.validate_resnet_feature_extractor(df_features)
    # Ensure that the composite keys were not corrupted in the processing
    vc.validate_composite_keys_structure(df_features)
    # Ensure that all composite keys in [df_sampled - non fetched from sentinel] are in the feature extraction dataframe 
    vc.validate_composite_keys_mapping(df_features, df_sampled, df_no_sentinel_data)
    # -------------------------------
    # CREATE ML DATASET 
    # -------------------------------
    # If data passes all validation tests, then the data is combined to generate the final dataframe to be used in the ML process
    # Remove REAL duplicates from dataset
    df_cleaned_features =  df_features.drop_duplicates()
    # Create ML dataset
    df_ml = pd.merge(df_sampled, df_cleaned_features, on = 'composite_key', how = 'inner')
    # Save data
    fu.write_df_to_csv(df_in = df_ml, file_path = DATA_DIR/'MLInputs', fname = f'{RUN_TIMESTAMP}_ml_input')

if __name__ == "__main__":
    run_feature_extractor()


