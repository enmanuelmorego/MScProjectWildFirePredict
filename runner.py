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

# --------------------------
# VARIABLES
# --------------------------
YEAR_FILTER = [2020,2021]
CRS = "EPSG: 4326"          # Set Coordinate Reference System (CRS) so it is uniform across all data inputs
         
# --------------------------
# VIIRS DATA
# --------------------------
viirs_dict = ld.viirs_load_pipeline(dir_name = 'VIIRS',
                                    crs = CRS,
                                    date_range = YEAR_FILTER)
df_viirs = viirs_dict.get('df_viirs')
print(f"{'='*80}")
print(f"VIIRS Data")
print(f"\tData Type: {type(df_viirs)}")
print(f"\t📅 Date Range: {df_viirs['acq_date'].min()} to {df_viirs['acq_date'].max()}")


# --------------------------
# UK GRID 
# --------------------------
grid_path = Path(os.environ.get('DATA_DIR'))/'UKGrid'/'ukcp18-uk-land-12km.shp'
uk_grid = gpd.read_file(grid_path)
print(f"{'='*80}")
print(f"UK Sample")
print(f"\tData Type: {type(uk_grid)}")
#uk_grid_norm = uk_grid.to_crs(epsg=4326)
#uk_grid_norm.explore()

# uk_grid_norm.plot(figsize=(6,8),
#                   edgecolor='white',
#                   linewidth=0.2)
# plt.title("United Kingdom split on 12km x 12km grids")
# plt.show()