# --------------------------
# SET UP
# --------------------------
import os
os.environ.setdefault("RUN_DEMO", "ON")
import src.config as c
import src.load_data as ld
import src.google_ee as gee
import src.preprocessing_general as pps
import pp_sentinel as ppsent
import geopandas as gpd
from pathlib import Path
import pandas as pd
import utils as u
from datetime import datetime


# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER     = [2018]
CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
SATELLITE_IMAGES = "COPERNICUS/S2_SR_HARMONIZED"
GRB_NAME        = 'Forest fire weather index (as defined by the Canadian Forest Service)'
DATA_DIR        = os.environ.get("DATA_DIR")
RUN_ID          = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M')}_RUNNING_DEMO_{os.environ.get('RUN_DEMO')}"
RANDOM_SEED     = 42

VIIRS_DIR                = 'VIIRS'
FWI_DIR                  = 'FWI'
FIRENOFIRE_SAMPLED_DIR   = "SampledFireNoFire"
FIRENOFIRE_SAMPLED_FNAME = "sampled_firenofire.csv"
SP_FILENAME              ='ukcp18-uk-land-12km.shp'

# --------------------------
# LOAD DATA
# --------------------------
# Get available sampled data
sampled_available      = u.available_files_by_year(FIRENOFIRE_SAMPLED_DIR, ".csv")
sampled_required_years = set(YEAR_FILTER) - sampled_available
# Load df_uk_grid for reporting values
df_uk_grid = ld.load_uk_grid(file_name = SP_FILENAME, 
                             crs       = CRS)
if not sampled_required_years:
    df_sampled = ld.load_cached_sampled(YEAR_FILTER, FIRENOFIRE_SAMPLED_DIR, FIRENOFIRE_SAMPLED_FNAME)
    print("✨ All requested years are already cached. Skipping load_data pipeline...")
else:
    #region
    # --------------------------
    # VIIRS DATA
    # --------------------------
    viirs_dict = ld.viirs_load_pipeline(dir_name   = VIIRS_DIR,
                                        crs        = CRS,
                                        date_range = YEAR_FILTER)
    df_viirs = viirs_dict.get('df_viirs')
    print(f"{'='*80}")
    print(f"🔥 VIIRS Data")
    print(f"\tVIIRS data report\n\t\t{viirs_dict.get('data_report')}")
    print(f"\tData Type: {type(df_viirs)}")
    print(f"\t📅 Date Range: {df_viirs['date'].min()} to {df_viirs['date'].max()}")
    print(df_viirs.head())

    # --------------------------
    # UK GRID 
    # --------------------------
    print(f"{'='*80}")
    print(f"UK Grid")
    print(f"Columns: \n\t{df_uk_grid.columns}")
    print(f"Shape: \n\t{df_uk_grid.shape}")
    print(df_uk_grid.head())

    # Grids by Day
    print(f"{'='*80}")
    print(f"🇬🇧 UK Grid Daily")
    df_daily_grid = ld.uk_grid_data_pipeline(df_uk_grid, df_viirs)
    print(f"Daily UK Grid Columns: \n\t{df_daily_grid.columns}")
    print(type(df_daily_grid['date'][0]))
    print(f"Shape: \n\t{df_daily_grid.shape}")
    print(df_daily_grid.head())

    # -------------------------
    # GOOGLE EE SENTINEL-2
    # -------------------------
    # print(f"{'='*80}")
    # print(f"🛰️ GOOGLE EE SENTINEL-2")  
    # # Get stored files 
    # sentinel_path  = Path(DATA_DIR)/"sentinel2"
    # df_sentinel = ld.sentinel_load_pipeline(sentinel_path,
    #                                         df_daily_grid[df_daily_grid['date'] < '2019-01-31'],
    #                                         SATELLITE_IMAGES)
    # print(df_sentinel.head())

    # -------------------------
    # FIRE WEATHER INDEX 
    # -------------------------
    print(f"{'='*80}")
    print(f"🌡️ FIRE WEATHER INDEX")  
    fwi_path    = Path(DATA_DIR)/FWI_DIR
    df_fwi = ld.fwi_load_pipeline(fwi_path         = fwi_path,
                                  df_uk_daily_grid = df_daily_grid,
                                  df_uk_grid       = df_uk_grid,
                                  crs              = CRS,
                                  grb_name         = GRB_NAME)
    print(type(df_fwi['date'].max()))
    print(df_fwi.shape)
    print(df_fwi.head())

    #endregion

    # --------------------------
    # PRE PROCESSING
    # --------------------------
    #region
    print(f"{'='*80}")
    print(f"🏗️ PRE PROCESSING")  

    dfs_loaded = {'df_viirs'     : df_viirs,
                'df_uk_grid'   : df_uk_grid,
                'df_daily_grid': df_daily_grid,
                'df_fwi'       : df_fwi}
    df_model_pre = pps.preprocessing_pipeline(dfs_loaded, RUN_ID)
    #endregion

    # --------------------------
    # SAMPLING FIRE/NOFIRE
    # --------------------------
    #region
    print(f"{'='*80}")
    print(f"🔬 SAMPLING FIRE/NOFIRE")  
    df_sampled = pps.sampling_pipeline(df_preprocessed              = df_model_pre, 
                                    nofire_proximity_window_days = 30, 
                                    nofire_total_samples         = 3,
                                    random_seed                  = RANDOM_SEED)

    # Store sampled data as csv
    sampled_by_year = u.split_df_by_year(df_sampled)
    output_dir      = Path(os.environ.get("DATA_DIR"))/FIRENOFIRE_SAMPLED_DIR
    for year, df in sampled_by_year.items():
        u.df_to_csv(df, f"{year}_{FIRENOFIRE_SAMPLED_FNAME}", str(output_dir))

# Generate sampled value report
pps.sampling_reporting_pipeline(df_plot         = df_sampled, 
                                df_uk_grid      = df_uk_grid, 
                                uk_sp_file_name = SP_FILENAME,
                                crs             = CRS, 
                                run_id          = RUN_ID)
# --------------------------
# SENTINEL DATA
# --------------------------
print(f"{'='*80}")
print(f"🛰️ GOOGLE EE SENTINEL-2")  
sentinel_available = ppsent.fetch_available_sentinel_files()
sentinel_comp_keys = ppsent.load_sentinel_composite_keys(sentinel_available)
print(sentinel_comp_keys.head())