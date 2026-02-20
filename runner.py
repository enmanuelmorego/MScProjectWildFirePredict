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
import matplotlib.pyplot as plt
import utils as u
from datetime import datetime


# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER     = [2018]
CRS             = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
SATELITE_IMAGES = "COPERNICUS/S2_SR_HARMONIZED"   
DATA_DIR        = os.environ.get("DATA_DIR")
RUN_ID          = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M')}_RUNNING_DEMO_{os.environ.get('RUN_DEMO')}"

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
print(f"\tVIIRS data report\n\t\t{viirs_dict.get('data_report')}")
print(f"\tData Type: {type(df_viirs)}")
print(f"\t📅 Date Range: {df_viirs['date'].min()} to {df_viirs['date'].max()}")
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
#                                         SATELITE_IMAGES)
# print(df_sentinel.head())

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
print(type(df_fwi['date'].max()))
print(df_fwi.shape)
print(df_fwi.head())

#endregion

# --------------------------
# PRE PROCESSING
# --------------------------
#region

import numpy as np
import webbrowser
print(f"{'='*80}")
print(f"++ PRE PROCESSING")  

dfs_loaded = {'df_viirs'     : df_viirs,
              'df_uk_grid'   : df_uk_grid,
              'df_daily_grid': df_daily_grid,
              'df_fwi'       : df_fwi}

df_model_pre = pps.preprocessing_pipeline(dfs_loaded, RUN_ID)
print(df_model_pre.head())

print(df_model_pre['fwi'].describe())








# import webbrowser
# import os

# gdf_grid1 = df_uk_grid.loc[df_uk_grid['grid_id'] == 1]

# m = gdf_grid1.explore(
#     color="red",
#     style_kwds={"fillOpacity": 0.4},
#     tiles="Esri.WorldImagery"
# )

# # Save to file
# fp = os.path.abspath("grid1_check.html")
# m.save(fp)

# # Open in browser
# webbrowser.open("file://" + fp)


# import pandas as pd
# import folium

# random_day = np.random.choice(df_viirs_summary['acq_date'].unique())
# print("Random day selected:", random_day)

# df_day = df_viirs_summary[df_viirs_summary['acq_date'] == random_day]
# print(df_day.shape)



# df_plot = df_uk_grid.merge(df_day,
#                            on = 'grid_id',
#                            how = 'left')
# df_plot["fire_lbl"] = df_plot["fire_lbl"].fillna(False)
# import geopandas as gpd

# gdf_plot = gpd.GeoDataFrame(df_plot, geometry="geometry", crs=df_uk_grid.crs)


# m = gdf_plot.explore(
#         color="#aaaaaa",   # light grey (hex gives more control)
#     style_kwds={
#         "fillOpacity": 0,
#         "weight": 0.5,        # thinner lines
#         "opacity": 0.6        # lighter lines
#     }
# )

# # Overlay: fire grids filled red
# gdf_plot[gdf_plot["fire_lbl"]].explore(
#     m=m,
#     color="red",
#     style_kwds={"fillOpacity": 0.6}
# )

# # folium.LayerControl().add_to(m)
# map_name = f"{datetime.now().strftime("%Y%m%d %H:%M:%S")}_validation_map.html"
# fp = os.path.abspath(f"outputs/maps/" + map_name)
# m.save(fp)
# webbrowser.open("file://" + fp)

# import geopandas as gpd

# # Pick one day
# day = "2019-12-15"

# df_day = df_fwi[df_fwi["date"] == day]

# # Merge geometry back
# gdf_plot = df_uk_grid.merge(df_day, on="grid_id", how="left")

# # m = gdf_plot.explore(
# #     column="fwi_mean", # Assigns a color based gradiaent on the values of the column
# #     #cmap="OrRd",
# #    # legend=True,
# #     tiles="Esri.WorldImagery"
# # )

# m = gdf_plot.explore(
#         color="#aaaaaa",   # light grey (hex gives more control)
#     style_kwds={
#         "fillOpacity": 0,
#         "weight": 0.5,        # thinner lines
#         "opacity": 0.6        # lighter lines
#     }
# )

# map_name = f"{datetime.now().strftime("%Y%m%d %H:%M:%S")}_fwi_validation_map.html"
# fp = os.path.abspath(f"outputs/maps/" + map_name)
# m.save(fp)
# webbrowser.open("file://" + fp)


#endregion