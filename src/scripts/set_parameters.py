"""
Module to set the parameters for the run and ensure user is updating the file before running pipeline(s)
"""
from datetime import date, datetime
import os

# Enter date as yyyy, m, d
VALIDATION_DATE = date(2026, 5, 4)

PARAMETERS = {"YEAR_FILTER"      : [2018],
              "CRS"              : "EPSG: 4326",          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
              "SATELLITE_IMAGES" : "COPERNICUS/S2_SR_HARMONIZED",
              "SATELLITE_BANDS"  : ["B3","B4","B8"],
              "SATELLITE_SCALE"  : 80,
              "GRB_NAME"         : "Forest fire weather index (as defined by the Canadian Forest Service)",
              "DATA_DIR"         : os.environ["DATA_DIR"],
              "RUN_ID"           : f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M')}_RUNNING_DEMO_{os.environ.get('RUN_DEMO')}",
              "RANDOM_SEED"      : 42,
              
              "VIIRS_DIR"                : "VIIRS",
              "FWI_DIR"                  : "FWI",
              "FIRENOFIRE_SAMPLED_DIR"   : "SampledFireNoFire",
              "FIRENOFIRE_SAMPLED_FNAME" : "sampled_firenofire.csv",
              "SP_FILENAME"              :"ukcp18-uk-land-12km.shp",
              "GEE_PROJECT"              : "ee-enmanuelmorego"}