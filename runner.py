# --------------------------
# SET UP
# --------------------------
import os
RUN_DEMO = 'ON'
os.environ.setdefault("RUN_DEMO", RUN_DEMO)
import src.config as c
import src.load_data as ld
import src.google_ee as gee
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import utils as u
from datetime import datetime
import getpass 

# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER     = [2019]
CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
SATELITE_IMAGES = "COPERNICUS/S2_SR_HARMONIZED"   
DATA_DIR        = os.environ.get("DATA_DIR")
FWI_NAME        = 'Forest fire weather index (as defined by the Canadian Forest Service)'
UK_GRID         = 'ukcp18-uk-land-12km.shp'


# --------------------------
# VIIRS DATA
# --------------------------
viirs_dict = ld.viirs_load_pipeline(dir_name   = 'VIIRS',
                                    crs        = CRS,
                                    date_range = YEAR_FILTER)
df_viirs = viirs_dict.get('df_viirs')
# TODO TEMPORARY FILTER
df_viirs = df_viirs[df_viirs['acq_date'] < '2019-02-01']
print(f"{'='*80}")
print(f"🔥 VIIRS Data")
print(f"\tData Type: {type(df_viirs)}")
print(f"\t📅 Date Range: {df_viirs['acq_date'].min()} to {df_viirs['acq_date'].max()}")
print(df_viirs.head())

# --------------------------
# UK GRID 
# --------------------------
df_uk_grid = ld.load_uk_grid(file_name = UK_GRID, 
                             crs       = CRS)
print(f"{'='*80}")
print(f"UK Grid")
print(f"Columns: \n\t{df_uk_grid.columns}")
print(f"Shape: \n\t{df_uk_grid.shape}")

# Grids by Day
print(f"{'='*80}")
print(f"🇬🇧 UK Grid Daily")
dates = u.extract_year_range(df_viirs)
df_daily_grid = df_uk_grid.copy()
df_daily_grid['join_key'] = 1
df_daily_grid = df_daily_grid.merge(dates, on='join_key').drop(columns='join_key')
# TODO TEMPORARY FILTER
df_daily_grid = df_daily_grid[df_daily_grid['date'] < '2019-02-01']

print(f"Daily UK Grid Columns: \n\t{df_daily_grid.columns}")
print(type(df_daily_grid['date'][0]))
print(f"Shape: \n\t{df_daily_grid.shape}")

print(f"Check that grid_id corresponds to same lon-lat across whole df")
grid_id_sample = df_daily_grid['grid_id'].sample(n=1).iloc[0]
print(f"Randomly selected grid_id: {grid_id_sample}")
print(f"DATES: \n\tMin {df_daily_grid['date'].min()} \n\tMax {df_daily_grid['date'].max()}")

# -------------------------
# GOOGLE EE SENTINEL-2
# -------------------------
print(f"{'='*80}")
print(f"🛰️ GOOGLE EE SENTINEL-2")  
# Get stored files 
sentinel_path  = Path(DATA_DIR)/"sentinel2"
df_sentinel = ld.sentinel_load_pipeline(sentinel_path,
                                        df_daily_grid,
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
                              grb_name         = FWI_NAME)
print(df_fwi.shape)
print(df_fwi.head())

data_load_report = {'Run Metadata': {'Demo Run': RUN_DEMO,
                                     'Run Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                     'User': getpass.getuser()},
                    'Variables': {'CRS': CRS,
                                  'Satelite': SATELITE_IMAGES,
                                  'Fire Weather Index': FWI_NAME,
                                  'UK Grid': UK_GRID}}
print(data_load_report)

'''
fwi = date
setinel = date
uk daily = date
viirs = date
'''



df_dict = {
    "df_uk_grid": df_uk_grid,
    "df_daily_grid": df_daily_grid,
    "df_viirs": df_viirs,
    "df_sentinel": df_sentinel,
    "df_fwi": df_fwi
}
dict_report = {}
import re
for name, df in df_dict.items():
    dict_report[name] = {}

    dict_report[name]['Rows'] = df.shape[0]

    colnames = df.columns.tolist()
    date_colname = [c for c in colnames if re.search('date', c)]
    grid_id_colname = [c for c in colnames if re.search('grid_id', c)]
    cols_sum = 0
    if date_colname:
        date_col = date_colname[0] 
        try:   
            min_date = df[date_col].min().strftime("%Y-%m-%d")
            max_date = df[date_col].max().strftime("%Y-%m-%d")
        except:
            min_date = df[date_col].min()
            max_date = df[date_col].max()

        dict_report[name]['Date Range'] = {'min': min_date,
                                           'max': max_date}

        #print(f"DATES\n\tfrom {min_date} to {max_date}")
        cols_sum += 1

    # grid_id + dates
    if grid_id_colname:
        grid_min = df['grid_id'].min()
        grid_max = df['grid_id'].max()

        dict_report[name]['Grid ID Range'] = {'min': int(grid_min),
                                              'max': int(grid_max)}
        cols_sum += 1

    if cols_sum == 2:
        grid_id_dates_pairs = df[['grid_id', date_col]].drop_duplicates().shape[0]
        nrows = len(df)
        date_grid_check = nrows == grid_id_dates_pairs
        dict_report[name]['Grid-Date pair unique'] = date_grid_check

print(dict_report)