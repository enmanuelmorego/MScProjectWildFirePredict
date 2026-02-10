# --------------------------
# SET UP
# --------------------------
import os
os.environ.setdefault("RUN_DEMO", "ON")
import src.config as c
import src.load_data as ld
import src.google_ee as gee
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
# LOAD DATA
# --------------------------
#region
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
print(df_viirs.head())

# --------------------------
# UK GRID 
# --------------------------
df_uk_grid = ld.load_uk_grid(file_name ='ukcp18-uk-land-12km.shp', 
                             crs       = CRS)
print(f"{'='*80}")
print(f"UK Grid")
print(f"Columns: \n\t{df_uk_grid.columns}")
print(f"Shape: \n\t{df_uk_grid.shape}")

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
print(f"{'='*80}")
print(f"🛰️ GOOGLE EE SENTINEL-2")  
# Get stored files 
sentinel_path  = Path(DATA_DIR)/"sentinel2"
df_sentinel = ld.sentinel_load_pipeline(sentinel_path,
                                        df_daily_grid[df_daily_grid['date'] < '2019-01-31'],
                                        SATELITE_IMAGES)
print(df_sentinel.head())

# -------------------------
# FIRE WEATHER INDEX 
# -------------------------
print(f"{'='*80}")
print(f"🌡️ FIRE WEATHER INDEX")  
fwi_path    = Path(DATA_DIR)/"FWI"
df_fwi = ld.fwi_load_pipeline(fwi_path         = fwi_path, 
                              df_uk_daily_grid = df_daily_grid,
                              df_uk_grid       = df_uk_grid,
                              crs              = CRS,
                              grb_name         = 'Forest fire weather index (as defined by the Canadian Forest Service)')
print(df_fwi.shape)
print(df_fwi.head())

#endregion

# --------------------------
# PRE PROCESSING
# --------------------------
#region
##################################
import ee
try:
    ee.Initialize(project = "ee-enmanuelmorego")
except:
    ee.Authenticate()
    ee.Initialize(project = "ee-enmanuelmorego")
df_month = df_daily_grid[(df_daily_grid['date'] >= '2019-01-01') &
                         (df_daily_grid['date'] <= '2019-01-15')]
# Convert df to google feature collection
fc = gee.geodf_to_ee(df_month)
# function to make sentinel patch
def make_sentinel_patch(feature):
    date = ee.Date(feature.get('date'))
    geom = feature.geometry()

    composite_img = (ee.ImageCollection(SATELITE_IMAGES)
                     .filterBounds(geom)
                     .filterDate(date.advance(-7, 'day'), date)
                     .select(['B2','B3','B4','B8'])
                     .median()
                     .clip(geom))
    patch = composite_img.sampleRectangle(region = geom,
                                          defaultValue = 0)
    return feature.set({'patch': patch})

fc_patches = fc.map(make_sentinel_patch)

task = ee.batch.Export.table.toDrive(
    collection=fc_patches,
    description="sentinel_patches_2019_01",
    folder="SentinelPixels",
    fileFormat="TFRecord"
)
task.start()

#endregion