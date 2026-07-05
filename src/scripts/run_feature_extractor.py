"""
Module that runs and performs the feature extraction of Sentinel2 data using ResNet18
"""
from scripts.set_parameters import PARAMETERS, VALIDATION_DATE
from transforms.resnet_feature_extractor import ResNetFeatExtractor, extract_resnet_features

import utils.validation_checks as vc
import utils.file_utils as fu

def run_feature_extractor():
    # ------------------------
    # VALIDATE RUN PARAMETERS
    # ------------------------    
    # vc.validate_params_update(VALIDATION_DATE)
    # ------------------------
    # EXTRACT PARAMETERS 
    # ------------------------
    DATA_DIR      = PARAMETERS['DATA_DIR']
    # -------------------------------
    # LOAD SENTINEL DATA
    # -------------------------------
    files_sentinel = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
    # -------------------------------
    # RESNET-18 MODEL
    # -------------------------------
    # Initialise model
    resnet_model = ResNetFeatExtractor()
    # Disable training behaviour since the model is used only for feature extraction
    resnet_model.eval()
    # Perform feature extraction
    df_features = extract_resnet_features(files_sentinel[0:2], resnet_model)

    vc.validate_resnet_feature_extractor(df_features)

    return(df_features)

if __name__ == "__main__":
    test = run_feature_extractor()
    print(test.head())

