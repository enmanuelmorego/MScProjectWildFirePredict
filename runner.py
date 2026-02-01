# --------------------------
# SET UP
# --------------------------
import os
os.environ.setdefault("RUN_DEMO", "ON")
import src.config as c
import src.load_data as ld
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import utils as u

# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER     = [2019]
CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
SATELITE_IMAGES = "COPERNICUS/S2_SR_HARMONIZED"   
DATA_DIR        = os.environ.get("DATA_DIR")
# --------------------------
# VIIRS DATA
# --------------------------
viirs_dict = ld.viirs_load_pipeline(dir_name   = 'VIIRS',
                                    crs        = CRS,
                                    date_range = YEAR_FILTER)
df_viirs = viirs_dict.get('df_viirs')
print(f"{'='*80}")
print(f"🔥 VIIRS Data")
print(f"\tData Type: {type(df_viirs)}")
print(f"\t📅 Date Range: {df_viirs['acq_date'].min()} to {df_viirs['acq_date'].max()}")


# --------------------------
# UK GRID 
# --------------------------
df_uk_grid = ld.load_uk_grid(file_name ='ukcp18-uk-land-12km.shp', 
                             crs       = CRS)
print(f"{'='*80}")
print(f"UK Grid")
print(f"Shape: {df_uk_grid.shape}")

# Grids by Day
print(f"{'='*80}")
print(f"🇬🇧 UK Grid Daily")
dates = u.extract_year_range(df_viirs)
df_daily_grid = df_uk_grid.copy()
df_daily_grid['join_key'] = 1
df_daily_grid = df_daily_grid.merge(dates, on='join_key').drop(columns='join_key')
print(f"Shape: {df_daily_grid.shape}")

# -------------------------
# GOOGLE EE SENTINEL-2
# -------------------------
from datetime import datetime 
print(f"{'='*80}")
print(f"🛰️ GOOGLE EE SENTINEL-2")  
sentinel_files = os.listdir(Path(DATA_DIR)/"sentinel2")
print(ld.sentinel_check_drive(df_daily_grid, sentinel_files))