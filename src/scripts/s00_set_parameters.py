"""
Module to set the parameters for the run and ensure user is updating the file before running pipeline(s)
"""
from datetime import date, datetime
from pathlib import Path

# Project Root
PROJ_HOME = Path(__file__).resolve().parents[2]
# Enter date as yyyy, m, d
VALIDATION_DATE = date(2026, 8, 8)

PARAMETERS = {"YEAR_FILTER"      : [2018, 2019, 2020, 2021, 2022, 2023, 2024],
              "CRS"              : "EPSG: 4326",          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
              "SATELLITE_IMAGES" : "COPERNICUS/S2_SR_HARMONIZED",
              "SATELLITE_BANDS"  : ["B3","B4","B8"],
              "SATELLITE_SCALE"  : 80,
              "SATELLITE_FORMAT" : 'GEO_TIFF',
              "GRB_NAME"         : "Forest fire weather index (as defined by the Canadian Forest Service)",
              "PROJ_HOME"        : PROJ_HOME,
              "DATA_DIR"         : Path(PROJ_HOME)/"data",
              "RUN_ID"           : f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M')}",
              "RANDOM_SEED"      : 42,
              "RUN_TIMESTAMP"    : datetime.today().strftime('%Y-%m-%d'),

              "VIIRS_DIR"                : "VIIRS",
              "FWI_DIR"                  : "FWI",
              "FIRENOFIRE_SAMPLED_DIR"   : "SampledFireNoFire",
              "FIRENOFIRE_SAMPLED_FNAME" : "sampled_firenofire.csv",
              "SP_FILENAME"              : "ukcp18-uk-land-12km.shp",
              "GEE_PROJECT"              : "ee-enmanuelmorego"}

ML_CLEANED_MODELS_NAMES = {'logistic_reg_fwi': 'Logistic Regression - FWI',
                           'logistic_reg_hybrid_default': 'Logistic Regression - Hybrid (Default)',
                           'logistic_reg_hybrid_fineTuned': 'Logistic Regression - Hybrid (Fine-Tuned)',
                           'logistic_reg_sentinel_default': 'Logistic Regression - Sentinel (Default)',
                           'logistic_reg_sentinel_fineTuned': 'Logistic Regression - Sentinel (Fine-Tuned)',
                           'random_forest_fwi': 'Random Forest - FWI',
                           'random_forest_hybrid_default': 'Random Forest - Hybrid (Default)',
                           'random_forest_hybrid_fineTuned': 'Random Forest - Hybrid (Fine-Tuned)',
                           'random_forest_sentinel_default': 'Random Forest - Sentinel (Default)',
                           'random_forest_sentinel_fineTuned': 'Random Forest - Sentinel (Fine-Tuned)'}
if __name__ == "__main__":
    print(PROJ_HOME)
    print(type(PARAMETERS['DATA_DIR']))