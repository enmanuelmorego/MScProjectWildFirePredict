# --------------------------
# SET UP
# --------------------------
import os
os.environ.setdefault("RUN_DEMO", "ON")
import src.config as c
import src.load_data as ld
import src.google_ee as gee
import src.preprocessing_general as pps
import geopandas as gpd
from pathlib import Path
import pandas as pd
import utils as u
from datetime import datetime


# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER     = []
CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
SATELITE_IMAGES = "COPERNICUS/S2_SR_HARMONIZED"   
GRB_NAME        = 'Forest fire weather index (as defined by the Canadian Forest Service)'
DATA_DIR        = os.environ.get("DATA_DIR")
RUN_ID          = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M')}_RUNNING_DEMO_{os.environ.get('RUN_DEMO')}"
RANDOM_SEED     = 42

VIIRS_DIR              = 'VIIRS'
FWI_DIR                = 'FWI'
FIRENOFIRE_SAMPLED_DIR = "SampledFireNoFire"
SP_FILENAME            ='ukcp18-uk-land-12km.shp'

# --------------------------
# LOAD DATA
# --------------------------
viirs_dict      = ld.viirs_load_pipeline(dir_name                   = VIIRS_DIR,
                                         crs                        = CRS,
                                         date_range                 = YEAR_FILTER)     # -> Return None if year_filter is empty
df_viirs        = viirs_dict.get('df_viirs', None)                                      
df_uk_grid      = ld.load_uk_grid(file_name                         = SP_FILENAME, 
                                  crs                               = CRS)
df_daily_grid   = ld.uk_grid_data_pipeline(df_uk_grid, df_viirs)                      # -> Return None if year_filter is empty. no issue if df_viirs is emtpy too
fwi_path        = Path(DATA_DIR)/FWI_DIR
df_fwi          = ld.fwi_load_pipeline(fwi_path                     = fwi_path, 
                                       df_uk_daily_grid             = df_daily_grid,
                                       df_uk_grid                   = df_uk_grid,
                                       crs                          = CRS,
                                       grb_name                     = GRB_NAME)       # -> Return None if year_filter is empty. no issue if df_viirs is emtpy too
dfs_loaded      = {'df_viirs'                                       : df_viirs,
                   'df_uk_grid'                                     : df_uk_grid,
                   'df_daily_grid'                                  : df_daily_grid,
                   'df_fwi'                                         : df_fwi}

df_model_pre    = pps.preprocessing_pipeline(dfs_loaded, RUN_ID)                      # -> Return None if year_filter is empty. no issue if df_viirs is emtpy too
df_sampled      = pps.sampling_pipeline(df_preprocessed              = df_model_pre, 
                                        nofire_proximity_window_days = 30, 
                                        nofire_total_samples         = 3,
                                        random_seed                  = RANDOM_SEED)   # -> Return None if year_filter is empty. no issue if df_viirs is emtpy too
sampled_by_year = u.split_df_by_year(df_sampled)
output_dir      = Path(os.environ.get("DATA_DIR"))/FIRENOFIRE_SAMPLED_DIR

for year, df in sampled_by_year.items():
    u.df_to_csv(df, f"{year}_sampled_firenofire.csv", str(output_dir))

pps.sampling_reporting_pipeline(df_plot                              = df_sampled, 
                                df_uk_grid                           = df_uk_grid, 
                                uk_sp_file_name                      = SP_FILENAME,
                                crs                                  = CRS, 
                                run_id                               = RUN_ID)

