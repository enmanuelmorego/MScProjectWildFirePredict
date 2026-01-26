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
# VIIRS DATA
# --------------------------
viirs_dict = ld.viirs_load_pipeline(dir_name = 'VIIRS',
                                    date_range = [2019])
df_viirs = viirs_dict.get('df_viirs')


# --------------------------
# UK GRID 
# --------------------------
grid_path = Path(os.environ.get('DATA_DIR'))/'UKGrid'/'ukcp18-uk-land-12km.shp'
uk_grid = gpd.read_file(grid_path)
print(uk_grid.head())
print(uk_grid.crs)
print(len(uk_grid))
uk_grid_norm = uk_grid.to_crs(epsg=4326)
uk_grid_norm.plot(figsize=(6,8),
                  edgecolor='white',
                  linewidth=0.2)
plt.title("United Kingdom split on 12km x 12km grids")
plt.show()